"""OIDC authorization code + PKCE, opaque DB sessions and organization authorization.

The single configured issuer is the local demo Keycloak, reached through the app's
same-origin proxy. No identity or organization is accepted from client headers.
"""
import base64
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import os
import secrets
from urllib.parse import urlencode, urlsplit

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import RedirectResponse, Response
import httpx
import jwt
from sqlalchemy import delete, select
from sqlalchemy.orm import Session

from apps.api.models import OAuthFlow, Organization, OrganizationMembership, WebSession

REALM = "metatietovaranto"
CLIENT_ID = "catalogue-demo"
SESSION_COOKIE = "mtv_session"
FLOW_COOKIE = "mtv_oidc_flow"
SESSION_SECONDS = 8 * 60 * 60
# Static, synthetic Keycloak subjects; not passwords or client-supplied organization claims.
DEMO_MEMBERS = [
    ("10000000-0000-4000-8000-000000000001", "00000000-0000-4000-8000-000000000001", "editor"),
    ("10000000-0000-4000-8000-000000000002", "00000000-0000-4000-8000-000000000002", "editor"),
    ("10000000-0000-4000-8000-000000000003", "00000000-0000-4000-8000-000000000001", "reader"),
]


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def now():
    return datetime.now(timezone.utc)


def seed_memberships(session):
    """Once only; never infer ownership from an organization's name or reset edits."""
    from uuid import NAMESPACE_URL, uuid5
    from apps.api.models import DemoInitialization
    if session.get(DemoInitialization, "phase-2b-memberships") is not None:
        return
    for subject, product_id, role in DEMO_MEMBERS:
        organization_id = uuid5(NAMESPACE_URL, f"https://example.org/metatietovaranto/legacy-provider/{product_id}")
        organization = session.get(Organization, organization_id)
        # Only known synthetic fixture identities can receive automatic demo membership.
        if organization is not None and organization.synthetic:
            session.add(OrganizationMembership(subject=subject, organization_id=organization_id, role=role))
    session.add(DemoInitialization(name="phase-2b-memberships"))


def current_session(request, session):
    token = request.cookies.get(SESSION_COOKIE, "")
    if not token or len(token) > 128:
        return None
    identity = session.get(WebSession, digest(token))
    return identity if identity is not None and identity.expires_at > now() else None


def require_session(request, session, *, csrf=True):
    identity = current_session(request, session)
    if identity is None:
        raise HTTPException(401, "Kirjaudu sisään")
    if csrf and not hmac.compare_digest(request.headers.get("x-csrf-token", ""), identity.csrf_token):
        raise HTTPException(403, "CSRF-tarkistus epäonnistui")
    return identity


def require_editor(session, identity, organization_id):
    membership = session.get(OrganizationMembership, (identity.subject, organization_id))
    if membership is None or membership.role != "editor":
        raise HTTPException(403, "Ei muokkausoikeutta tähän organisaatioon")


def verify_id_token(encoded, keys, *, issuer, nonce):
    header = jwt.get_unverified_header(encoded)
    if header.get("alg") != "RS256":
        raise jwt.InvalidTokenError("Unsupported signing algorithm")
    key = next((key for key in keys["keys"] if key.get("kid") == header.get("kid") and key.get("kty") == "RSA"), None)
    if key is None:
        raise jwt.InvalidTokenError("Unknown signing key")
    claims = jwt.decode(encoded, jwt.PyJWK.from_dict(key).key, algorithms=["RS256"],
                        audience=CLIENT_ID, issuer=issuer,
                        options={"require": ["sub", "iss", "aud", "exp", "iat", "nonce"]})
    if not hmac.compare_digest(claims["nonce"], nonce) or claims.get("azp", CLIENT_ID) != CLIENT_ID:
        raise jwt.InvalidTokenError("OIDC nonce or authorized party mismatch")
    return claims


def build_router(engine, base_url):
    router = APIRouter()
    internal = os.getenv("KEYCLOAK_INTERNAL_URL", "http://localhost:8080/identity").rstrip("/")
    issuer = f"{base_url}/identity/realms/{REALM}"
    realm_internal = f"{internal}/realms/{REALM}"
    callback_url = f"{base_url}/auth/callback"
    public = urlsplit(base_url)
    forwarded = {"X-Forwarded-Host": public.netloc, "X-Forwarded-Proto": public.scheme,
                 "X-Forwarded-Port": str(public.port or (443 if public.scheme == "https" else 80))}
    secure = public.scheme == "https"

    @router.get("/auth/me")
    def me(request: Request):
        with Session(engine) as session:
            identity = current_session(request, session)
            if identity is None:
                return {"authenticated": False, "memberships": []}
            memberships = session.execute(select(OrganizationMembership, Organization)
                .join(Organization, Organization.id == OrganizationMembership.organization_id)
                .where(OrganizationMembership.subject == identity.subject)).all()
            return {"authenticated": True, "username": identity.username, "csrfToken": identity.csrf_token,
                    "memberships": [{"organizationId": str(member.organization_id),
                                     "legalName": org.legal_name, "role": member.role} for member, org in memberships]}

    @router.get("/auth/login")
    def login():
        state, flow_cookie, nonce, verifier = (secrets.token_urlsafe(32) for _ in range(4))
        with Session(engine) as session:
            session.execute(delete(OAuthFlow).where(OAuthFlow.expires_at < now()))
            session.add(OAuthFlow(state_hash=digest(state), flow_hash=digest(flow_cookie),
                                  nonce=nonce, verifier=verifier, expires_at=now() + timedelta(minutes=5)))
            session.commit()
        challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode()).digest()).decode().rstrip("=")
        query = urlencode({"client_id": CLIENT_ID, "response_type": "code", "scope": "openid profile",
                           "redirect_uri": callback_url, "state": state, "nonce": nonce,
                           "code_challenge": challenge, "code_challenge_method": "S256", "prompt": "login"})
        response = RedirectResponse(f"{issuer}/protocol/openid-connect/auth?{query}", status_code=303)
        response.set_cookie(FLOW_COOKIE, flow_cookie, max_age=300, path="/auth", httponly=True,
                            secure=secure, samesite="lax")
        return response

    @router.get("/auth/callback")
    async def callback(request: Request, state: str = Query("", max_length=512),
                       code: str = Query("", max_length=4096)):
        with Session(engine) as session:
            flow = session.scalar(select(OAuthFlow).where(OAuthFlow.state_hash == digest(state)).with_for_update())
            if (not code or flow is None or flow.expires_at <= now()
                    or not hmac.compare_digest(flow.flow_hash, digest(request.cookies.get(FLOW_COOKIE, "")))):
                raise HTTPException(400, "Virheellinen tai vanhentunut kirjautumisyritys")
            nonce, verifier = flow.nonce, flow.verifier
            session.delete(flow)
            session.commit()  # One-use state is consumed before exchanging the code.
        try:
            async with httpx.AsyncClient(timeout=15, follow_redirects=False) as client:
                tokens = await client.post(f"{realm_internal}/protocol/openid-connect/token", headers=forwarded,
                    data={"grant_type": "authorization_code", "client_id": CLIENT_ID,
                          "code": code, "redirect_uri": callback_url, "code_verifier": verifier})
                tokens.raise_for_status()
                keys = await client.get(f"{realm_internal}/protocol/openid-connect/certs", headers=forwarded)
                keys.raise_for_status()
            claims = verify_id_token(tokens.json()["id_token"], keys.json(), issuer=issuer, nonce=nonce)
        except (httpx.HTTPError, jwt.PyJWTError, KeyError, ValueError, TypeError):
            raise HTTPException(401, "Kirjautumista ei voitu vahvistaa") from None
        token = secrets.token_urlsafe(32)
        with Session(engine) as session:
            session.execute(delete(WebSession).where(WebSession.expires_at < now()))
            old_token = request.cookies.get(SESSION_COOKIE)
            if old_token:
                session.execute(delete(WebSession).where(WebSession.token_hash == digest(old_token)))
            session.add(WebSession(token_hash=digest(token), subject=claims["sub"],
                username=claims.get("preferred_username", claims["sub"]), csrf_token=secrets.token_hex(32),
                expires_at=now() + timedelta(seconds=SESSION_SECONDS)))
            session.commit()
        response = RedirectResponse(f"{base_url}/", status_code=303)
        response.delete_cookie(FLOW_COOKIE, path="/auth")
        response.set_cookie(SESSION_COOKIE, token, max_age=SESSION_SECONDS, path="/", httponly=True,
                            secure=secure, samesite="lax")
        return response

    @router.get("/auth/end-session")
    def end_session():
        query = urlencode({"client_id": CLIENT_ID, "post_logout_redirect_uri": f"{base_url}/"})
        return RedirectResponse(f"{issuer}/protocol/openid-connect/logout?{query}", status_code=303)

    @router.post("/auth/logout")
    def logout(request: Request):
        with Session(engine) as session:
            identity = require_session(request, session)
            session.delete(identity)
            session.commit()
        response = Response(status_code=204)
        response.delete_cookie(SESSION_COOKIE, path="/", secure=secure, httponly=True, samesite="lax")
        return response

    @router.api_route("/identity/{path:path}", methods=["GET", "POST"])
    async def identity_proxy(path: str, request: Request):
        # The browser uses the same forwarded port in Codespaces and localhost.
        # Restrict paths; never proxy arbitrary hosts or Keycloak's admin console.
        if (not (path.startswith(f"realms/{REALM}/") or path.startswith("resources/"))
                or ".." in path.split("/") or "\\" in path or "%" in path):
            raise HTTPException(404)
        body = b""
        async for chunk in request.stream():
            body += chunk
            if len(body) > 65536:
                raise HTTPException(413)
        headers = {k: v for k, v in request.headers.items()
                   if k.lower() in {"accept", "accept-language", "content-type", "cookie", "user-agent"}}
        if "cookie" in headers:
            headers["cookie"] = "; ".join(f"{name}={value}" for name, value in request.cookies.items()
                                         if name not in {SESSION_COOKIE, FLOW_COOKIE})
        headers.update(forwarded)
        try:
            async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
                upstream = await client.request(request.method, f"{internal}/{path}",
                                               params=request.query_params.multi_items(), content=body, headers=headers)
        except httpx.HTTPError:
            raise HTTPException(503, "Kirjautumispalvelu ei ole käytettävissä") from None
        response = Response(upstream.content, status_code=upstream.status_code)
        # httpx decodes compressed responses; recompute Content-Length and omit Content-Encoding.
        response.raw_headers += [(key, value) for key, value in upstream.headers.raw
                                 if key.lower() in {b"content-type", b"location", b"set-cookie", b"cache-control",
                                    b"content-security-policy", b"x-frame-options", b"x-content-type-options",
                                    b"strict-transport-security", b"referrer-policy"}]
        return response

    return router
