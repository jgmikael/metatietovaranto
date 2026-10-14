# Vaiheen 2B kirjautuminen ja organisaatiot

OIDC-provider on paikallinen Keycloak 26.4.7, jonka image on lukittu digestillä. Se käynnistyy vain demon development-konfiguraatiolla. Samaa esiasetettua realmiä käytetään Docker Composessa ja Codespacesissa. Demokäyttäjät ja salasanat ovat synteettisiä eikä niitä pidetä salaisuuksina; älä käytä samoja arvoja muualla.

## Selain ja palvelin

Sovellus käyttää Authorization Code + PKCE (S256) -ketjua. `/auth/login` luo kertakäyttöisen state-, nonce- ja verifier-arvon palvelimella. State sidotaan selaimen HttpOnly-evästeeseen, vanhenee viidessä minuutissa ja kulutetaan ennen koodinvaihtoa. Callback vaihtaa koodin sisäistä Keycloak-yhteyttä käyttäen ja tarkistaa ID-tokenin RSA-allekirjoituksen, issuerin, audiencen, exp/iat/sub-vaatimukset, noncen ja authorized party -arvon. Pelkkä asiakkaan lähettämä käyttäjätunnus, organisaatio tai HTTP-otsake ei tunnista käyttäjää.

Selain saa vain satunnaisen opaque-istuntoevästeen. Tietokannassa on sen SHA-256-tiiviste, subject, näyttönimi, CSRF-tunniste ja vanhenemisaika. Käyttäjän access-, refresh- tai ID-tokenia ei tallenneta selaimen localStorageen eikä pysyvään palvelinistuntoon. Istunto vanhenee kahdeksassa tunnissa. Eväste on HttpOnly, SameSite=Lax ja Codespacesin HTTPS-osoitteessa Secure. Paikallisessa localhost-HTTP-demossa Secure on pois käytöstä, jotta kirjautuminen toimii. `/auth/me` palauttaa CSRF-tunnisteen vain saman alkuperän pyynnölle; kirjoituspyynnöt ja uloskirjautuminen vaativat sen `X-CSRF-Token`-otsakkeessa. Auth-vastauksia ei välimuistiteta.

`/auth/logout` (POST + CSRF) poistaa sovellusistunnon heti. Käyttöliittymä jatkaa Keycloakin standardiin end-session-osoitteeseen, jossa käyttäjä vahvistaa **Log out** ja palaa sovellukseen. API-asiakkaan pelkkä POST päättää sovellusistunnon, ei selaimen Keycloak-SSO:ta. Uusi login pyytää aina tunnistautumisen. Istuntojen hallintanäkymä ja Keycloakin back-channel logout eivät kuulu tähän vaiheeseen; esimerkiksi tilin poistaminen IdP:stä ei yksin mitätöi jo myönnettyä sovellusistuntoa. Organisaatiojäsenyyden poistaminen estää kirjoituksen heti seuraavassa pyynnössä.

Uvicornin access-log on deployatussa imagessa pois päältä, jotta callback-koodeja ja kirjautumis-URL:ien tilatietoja ei kirjata. Älä ota tokenien, evästeiden tai salasanojen debug-lokitusta käyttöön.

## Yksi selainportti Codespacesissa

FastAPI välittää vain oman realmin ja Keycloakin resurssien /identity-pyynnöt sisäiselle `keycloak`-palvelulle. Yhteyttä ei voi käyttää muiden hostien tai admin-konsolin yleisenä proxynä. Sovelluksen evästeitä ei välitetä Keycloakille. Paluuosoitteet ovat tarkat, eivät wildcardeja: paikallisesti `http://localhost:8000/auth/callback` ja Codespacesissa kyseisen codespacen HTTPS-osoite + `/auth/callback`.

Keycloakin hostname ja realm-importin paluuosoite saavat Codespacesin nimen Compose-overridesta. Selain käyttää edelleen vain Private-porttia 8000 ja onAutoForward=openBrowser-asetusta. Keycloakin paikallinen debug-/host-kehitysportti 8080 ei saa omaa Codespaces-porttiohjausta; otherPortsAttributes=ignore säilyy.

## Jäsenyydet ja vanhat tiedot

`organization_memberships` sitoo varmennetun OIDC-subjectin organisaation UUID:hen ja editor/reader-rooliin. Jokainen kirjoitus tarkistaa jäsenyyden tietokannasta. PUT tarkistaa sekä nykyisen että pyydetyn tarjoajan organisaation: tuotetta ei voi siirtää toiseen organisaatioon oikeuksien kiertämiseksi. GET-reitit ja viennit pysyvät tämän vaiheen demon luettavina metatietoina. Luonnokset, julkaisuversiot ja näkyvyysrajat toteutetaan myöhemmin.

Demojäsenyydet lisätään kerran `phase-2b-memberships`-merkinnän avulla. Startup ei palauta poistettuja tai muutettuja jäsenyyksiä. Vain tunnetut alkuperäiset synteettiset organisaatio-UUID:t saavat oletusjäsenyyden; samannimisyys ei myönnä oikeuksia. Muut vanhat tuotteet säilyvät kokonaan, mutta niiden muokkaamiseen tarvitaan eksplisiittinen jäsenyys.

| Demokäyttäjä | Keycloakin pysyvä subject | Oletusjäsenyys |
| --- | --- | --- |
| vero | 10000000-0000-4000-8000-000000000001 | Alkuperäisen verotuotteen organisaation editor. |
| yritys | 10000000-0000-4000-8000-000000000002 | Alkuperäisen yritystuotteen organisaation editor. |
| lukija | 10000000-0000-4000-8000-000000000003 | Alkuperäisen verotuotteen organisaation reader. |

Jos ylläpitäjä haluaa antaa esimerkiksi vero-demokäyttäjälle oikeuden johonkin muuhun synteettiseen organisaatioon, hän tarkistaa organisaation UUID:n Organisaatiot-näkymästä ja suorittaa hallitusti kannassa seuraavan operaation korvaten UUID-paikan oikealla arvolla:

```sql
INSERT INTO organization_memberships (subject, organization_id, role)
VALUES ('10000000-0000-4000-8000-000000000001', '<tarkistettu-organisaation-uuid>', 'editor');
```

Poisto samalla subject-/organisaatio-UUID-parilla peruu oikeuden. Toimenpiteitä ei tehdä automaattisesti nimen perusteella. Jäsenyyksien ylläpito-API tai käyttöliittymä ei sisälly vaiheeseen 2B. Kaikkien organisaatioiden oikeuksien antamista yhdelle demokäyttäjälle ei tarvita kokeiluun.

## Tietokanta ja päivitys

Uusi Alembic-revisio on `0003_auth`. Vanhoja 0001/0002-revisioita ei muuteta. Uudet taulut ovat organization_memberships, web_sessions ja oauth_flows; tuotetietoja, organisaatioita tai tunnisteita ei siirretä uudelleen. Keycloakin oma H2-kehityskanta sijaitsee erillisessä keycloakdata-volumessa. Tavallinen rebuild tai restart säilyttää molemmat volumet ja itse tehdyt muutokset. Realm-import tehdään vain ensimmäisellä käynnistyksellä: fixtures/keycloak-realm.json-tiedoston muuttaminen ei korvaa jo käytössä olevan realmin käyttäjiä.

`docker compose down -v` on tarkoituksellinen koko demon nollaus: se poistaa tuotteet, jäsenyydet, sovellusistunnot ja Keycloakin käyttäjä-/SSO-tilan. Älä käytä sitä versionpäivityksen yhteydessä. READMEssä on varmuuskopio- ja päivitysohjeet.

## Rajat

Tämä on yksityinen Codespaces-/paikallisdemoympäristö, ei tuotannon tunnistusjärjestelmä. MFA, tuotannon IdP-liitäntä, hallintakäyttöliittymä, kokonainen auditointi, hyväksyntä ja julkaisu eivät kuulu tähän toimitukseen. Tuotantoon tarvitaan erillinen realm-, käyttäjä-, salaisuus- ja käyttöoikeuskonfiguraatio. DEMO_MODE=true-vaatimus säilyy eikä oikeaa OIDC-ketjua voi ohittaa demo-otsakkeella.
