## Vaihe 2B: OIDC ja organisaatiokohtainen tuoteylläpito

Vaiheen 2A main-haaran päälle lisätään Keycloak OIDC Authorization Code + PKCE -kirjautuminen, palvelinpuolinen PostgreSQL-istunto ja editor/reader-jäsenyydet organisaatioittain. Haku, tuotesivut ja JSON-/JSON-LD-viennit säilyvät luettavina. Kirjoitus vaatii istunnon, CSRF-tunnisteen ja palvelimen tarkistaman muokkaajaoikeuden sekä tuotteen vanhaan että mahdolliseen uuteen tarjoajaorganisaatioon.

Uusi migraatio 0003_auth lisää vain jäsenyys- ja istuntotaulut. Aiemmat migraatiot ja tuote-/organisaatiotiedot säilyvät. Demooikeuksia ei päätellä organisaation nimestä eikä poistettuja jäsenyyksiä palauteta käynnistyksessä. Mukana kaksi eri organisaation muokkaajaa ja yksi lukija julkisilla synteettisillä demotunnuksilla.

Keycloak käyttää samaa selainporttia 8000 rajatun /identity-proxyn kautta. Codespacesin openBrowser säilyy ja portti pidetään Private-tilassa. Istuntoeväste on HttpOnly/SameSite ja HTTPS:ssä Secure; tunnistustokeneita ei tallenneta localStorageen. Uloskirjautuminen päättää sovellusistunnon ja jatkaa Keycloakin Log out -vahvistukseen, minkä jälkeen käyttäjää voi vaihtaa.

## Todennus

- TypeScript-/Vite-build ja Docker-image onnistuvat; app/db/keycloak healthy.
- 33 testiä läpäisee, ei ohituksia: 9 API/PostgreSQL/RDF, 8 auth, 7 migraatio, 3 osoitteenmuodostus ja 6 Chromium-selainkoetta oikealla Keycloakilla.
- Palvelimen kielteiset oikeustestit kattavat anonyymin, lukijan, toisen organisaation, tarjoajan vaihdon, väärennetyt otsakkeet/evästeen, CSRF:n, istunnon vanhenemisen ja jäsenyyden poiston.
- OIDC:n allekirjoitus/issuer/audience/nonce/azp/exp, state/PKCE/selainsidonta ja uusintakäytön esto testattu.
- Migraatio 2A → 2B säilyttää olemassa olevat tuotteet, organisaatiot ja niiden tunnisteet. Alembic check ei löydä puuttuvia muutoksia.
- Keycloakin rajatun Java-heapin jälkeen kuusi selaintestiä läpäisi uudelleen samoilla voluumeilla.
- Codespacesin yhdistetty Compose validoitu paikallisesti. Oikeaa Codespacea, Windowsia tai etä-CI:tä ei tässä ajettu.

Ei hyväksyntää, julkaisuversioita, SHACL:ia tai tuotantotunnistautumista. Jäsenyyksien hallinta-UI ja back-channel logout jäävät myöhemmiksi. Yksityiskohdat ja rajoitukset: docs/authentication.md, README ja STATUS.

## Selainkokeilu ennen yhdistämistä

Luo uusi Codespace haarasta feat/phase-2b-auth READMEn linkillä. Säilytä portti 8000 Private-tilassa. Hae tuotteita anonyymisti ja kokeile kirjautumista vero/demo-vero, yritys/demo-yritys ja lukija/demo-lukija. Vertaile muokkaus-/poistopainikkeita sekä tarjoajavalintaa. Uloskirjautumisessa vahvista Keycloakin Log out. Vanhan Codespacen päivitys tehdään varmuuskopioinnin ja Rebuild Containerin kautta ilman volumen poistoa.

Ei automaattista mergeä main-haaraan.
