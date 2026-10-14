"""Resolve a demo identity URL without trusting request Host headers."""
import os


def public_base_url():
    explicit = os.getenv("PUBLIC_BASE_URL", "").rstrip("/")
    name = os.getenv("CODESPACE_NAME", "")
    if name and explicit in ("", "http://localhost:8000"):
        domain = os.getenv("GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN") or "app.github.dev"
        return f"https://{name}-8000.{domain}"
    return explicit or "http://localhost:8000"
