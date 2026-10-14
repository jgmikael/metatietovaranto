# Vaihe 2B — OIDC ja organisaatiokohtainen tuoteylläpito

Tarkistettu 14.10.2026. Pohjana `origin/main` commit `0e6a2a2` (käyttäjän yhdistämä ja selaimessa toimivaksi vahvistama vaihe 2A). Työhaara `feat/phase-2b-auth`. Main-haaraan ei yhdistetä automaattisesti.

## Toteutettu

- Keycloak OIDC Authorization Code + PKCE S256, selainkohtainen kertakäyttöinen state, nonce ja allekirjoitetun ID-tokenin issuer/audience/voimassaolo/azp-tarkistukset. Ei kirjautumisen demo-ohitusta tai luottamusta käyttäjän lähettämään organisaatio-otsakkeeseen.
- Palvelinistunto PostgreSQL:ssä, selaimessa opaque HttpOnly/SameSite=Lax-eväste (HTTPS:ssä Secure), CSRF-otsaketarkistus kirjoituksille ja uloskirjautumiselle. Access-/refresh-/ID-tokenit eivät päädy selaimen localStorageen tai pysyvään sovellusistuntoon. Auth-vastaukset ovat no-store. Deployatun Uvicornin access-log on pois käytöstä.
- Organisaation editor/reader-jäsenyydet tietokannassa. Tuotteen lisäys, muokkaus ja poisto tarkistavat oikeudet palvelimella; PUT tarkistaa sekä alkuperäisen että uuden tarjoajan. Jäsenyyden poisto vaikuttaa seuraavaan kirjoituspyyntöön, eikä restart palauta poistettuja oikeuksia.
- Anonyymi haku, tuotesivu, organisaatiot ja JSON-/JSON-LD-vienti säilyvät. Tässä vaiheessa ei ole luonnoksia tai rajattujen tietotuotteiden näkyvyysmallia.
- Kolme synteettistä demotunnusta: vero/demo-vero, yritys/demo-yritys ja lukija/demo-lukija. Muokkaajat kuuluvat kahteen eri alkuperäiseen demo-organisaatioon; lukija ei voi kirjoittaa. Muut organisaatiot eivät saa oikeuksia nimen perusteella.
- Uloskirjautuminen poistaa sovellusistunnon ja jatkaa Keycloakin standardiin Log out -vahvistukseen. Käyttäjän vaihtaminen samalla selaimella testattu. API:n pelkkä POST /auth/logout päättää vain sovellusistunnon; koko selainuloskirjautuminen sisältää IdP-vahvistuksen.
- Migraatio 0003_auth lisää jäsenyys-/istunto-/OIDC-tilataulut. Aiemmat 0001/0002-revisiot, organisaatioiden UUID:t ja tuotetiedot säilyvät. Demojäsenyydet lisätään vain kerran tunnetuilla UUID:illä.
- Codespaces käyttää edelleen yhtä Private-selainporttia 8000. /identity-proxy välittää vain oman realmin ja resurssien pyynnöt; ei admin-konsolia tai yleistä URL-proxyä. Keycloak lisättiin käynnistyspalveluihin ja saa Codespacesin tarkan hostname-/callback-osoitteen. onAutoForward=openBrowser ja portin 8000 määritys säilyvät.
- Keycloak on digestillä lukittu development-image, erillinen keycloakdata-volume. Java-heap 128–512 MiB hillitsee demon muistinkulutusta; oikean 2-core Codespacen resurssimittausta ei tehty.

## Tässä tehtävässä todella ajettu

- Uusien runtime-riippuvuuksien lukittu uv-asennus onnistui; httpx siirrettiin runtime-riippuvuudeksi, PyJWT/cryptography lisättiin.
- `npm run build --prefix apps/web`: TypeScript ja Vite-tuotantobuild onnistuivat.
- Keycloak-imagen lataus onnistui tarkistetulla digestillä; realm tuotiin omaan uuteen testivolumeen.
- `./scripts/cloud-build.sh` ja `docker compose up -d --no-build --wait`: app, db ja keycloak healthy. Käytettiin pilven olemassa olevaa proxy-/CA-reittiä; TLS-tarkistusta ei ohitettu.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest -q`: **33 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**: 9 API-/PostgreSQL-/RDF, 8 auth, 7 migraatio ja 3 osoitteenmuodostustestiä sekä 6 oikean Chromiumin selainkoetta.
- Selainkokeet: aiempi haku–lisäys–muokkaus–poisto kirjautuneena, mobiili, organisaationäkymä, anonyymi/lukija, toisen organisaation muokkaaja ja vanhentunut sovellusistunto. Oikea Keycloak-kirjautuminen kaikilla kolmella tunnuksella, HttpOnly/SameSite-eväste, uloskirjautuminen ja käyttäjän vaihtaminen samalla selaimella tarkistettu.
- API:n kielteiset testit: anonyymi ja väärennetty eväste, väärä/puuttuva CSRF, lukijan kirjoitus, toisen organisaation muokkaus/poisto, tuotteen siirto toiseen organisaatioon, väärennetyt identity-/organization-otsakkeet, vanhentunut istunto ja poistettu jäsenyys.
- OIDC-testit: PKCE/state/selaincookie-sidonta, state-vanheneminen ja uusintakäytön esto, virheellinen token, väärä issuer/audience/nonce/azp/algoritmi ja exp sekä HTTPS-cookien Secure-asetus. Proxy-rajan admin-/master-/traversal-pyynnöt hylätään.
- Vanhojen vaiheen 1 migraatiotestien lisäksi uusi 2A → 2B -testi säilyttää tuotteen ja organisaation kaikki kentät ja tunnisteet myös toistetussa päivityksessä. Custom-organisaatiolle ei synny automaattisia demooikeuksia.
- Java-heap-asetuksen jälkeen Keycloak käynnistettiin uudelleen samoilla voluumeilla ja kuusi selaintestiä läpäisi uudelleen. PostgreSQL-volumea ei poistettu.
- Alembic current: `0003_auth (head)`. Alembic check: `No new upgrade operations detected.`
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: Keycloak-hostname osoittaa saman portin 8000 HTTPS-osoitteeseen, workspace jakaa app-palvelun verkon.

Testikehityksessä korjattiin puuttunut auth-routerin rekisteröinti, Keycloakin demoprofiilien sähköpostitiedot ja SQL-testifixturen JSON-parametrointi. Selainkoe paljasti, että pelkkä sovellusuloskirjautuminen jätti IdP-SSO:n voimaan; lopulliseen selainpolkuun lisättiin Keycloakin normaali end-session-vahvistus. Uusi, vain tässä tehtävässä luotu Keycloak-testivolume nollattiin fixtureiden korjausten yhteydessä; olemassa oleva PostgreSQL- ja tuotetieto säilyi. Lopullinen 33 testin ajo läpäisi. Neljä aiempaa Starlette/httpx- ja RDFLib-deprekaatiovaroitusta eivät ole ohitettuja testejä.

## Rajat ja ajamattomat tarkistukset

- Oikeaa GitHub Codespacea, sen Private-portin pääsynvalvontaa ja automaattista selainvälilehden avautumista ei ajettu tämän pilvikoneen sisältä. Tarkka ennen yhdistämistä tehtävä kokeilu on READMEssä.
- Windows/Docker Desktop, ensimmäinen build tyhjällä välimuistilla ja GitHub Actions -etäajo jäivät ajamatta. CI päivitettiin käynnistämään oikea Keycloak/Compose-demo selaintesteille erillisellä tietokannalla.
- Keycloak toimii development-konfiguraatiolla synteettisillä salasanoilla. Tuotannon IdP, MFA, jäsenyyksien hallinta-UI, sessionhallinnan UI ja back-channel logout eivät kuulu tähän rajaukseen. IdP-tilin poistaminen ei yksin peru jo myönnettyä kahdeksan tunnin sovellusistuntoa; organisaatiojäsenyyden peruminen estää kirjoittamisen heti.
- Hyväksyntä, julkaisuversiot, auditointi, optimistinen lukitus, SHACL ja ulkoiset integraatiot jäävät erillisiksi vaiheiksi. Julkisista metatiedoista ei tehdä tässä vaiheessa organisaatiolle piilotettuja luonnoksia.
- GitHub API -lukukokeilu palautti Forbidden; PR:n varsinainen luontitulos kirjataan toimituksessa. Kuvaus valmistellaan docs/pull-request.md-tiedostoon.

---

# Aikaisempien toimitusten historiatiedot

Alla ovat aiempien vaiheiden raportit. Vaihe 2A on käyttäjän ilmoituksen ja origin/mainin perusteella yhdistetty ja toimiva. Alla mainittu sen vanha PR-este on ratkaistu käyttäjän tekemällä PR:llä; yllä ovat tämän muutoksen tulokset.

# Vaihe 2A — migraatiot ja tarjoajaorganisaatiot

Tarkistettu 14.10.2026. Pohjana nykyinen `origin/main`, commit `c582dbc` (Codespaces-toimitus mukana). Uusi työhaara: `feat/phase-2a-organizations`. Main-haaraa ei muuteta eikä yhdistetä automaattisesti.

## Toteutettu

- Alembicin `0001_phase1` luo alkuperäisen skeeman tyhjään kantaan tai ottaa tarkistetun vanhan skeeman käyttöön. Tuntemattomat taulut, sarakkeet, tyypit, null-rajoitteet, indeksit tai pääavaimet keskeyttävät käyttöönoton. Ei sokeaa stamp-komentoa tai sovelluksen create_all-kutsua.
- `0002_organizations` lisää organisaatiot (UUID, legalName, country, scheme/value-tunnisteet, synthetic) ja tuotteen NOT NULL -vierasavaimen. Vanhojen tuotteiden kaikki aiemmat sarakkeet, UUID:t ja aikaleimat säilyvät. Jokainen vanha tarjoaja saa erillisen organisaation per tuote; samannimisiä ei yhdistetä. Tuntematon maa on ZZ eikä tunnisteita keksitä. legacyProductId säilyttää siirron alkuperän.
- Migraatiot suoritetaan yhdessä PostgreSQL-transaktiossa advisory-lukolla ennen fixtureitä ja readiness-tilaa. Sama FastAPI-startup toimii Composessa ja Codespacesissa. Migraatiovirhe estää käynnistyksen; tuntemattoman skeeman virhetesti varmisti transaktion peruuntumisen.
- Vanhaa kantaa ei siemennetä uudelleen, myöskään jos tuotteet on poistettu tai alustusmerkintä puuttuu. Uusi tyhjä demo saa edelleen kolme synteettistä tuotetta ja organisaatiota.
- Organisaatioiden listaus- ja yksittäisen organisaation luku-API, selainlista ja perustietonäkymä. Tuotelomakkeessa tarjoaja valitaan organisaation UUID:llä. Tarjoajanimi säilyy haussa, tuotesivulla ja JSON-/JSON-LD-viennissä.
- Tuotteen kirjoitus-API vaatii nyt providerOrganizationId-kentän vapaatekstisen provider-kentän sijaan. Tämä muutos ja migraatioiden rajoitukset on dokumentoitu READMEssä. Organisaatioiden luonti-/muokkausprosessia ei lisätty.
- Codespacesin `.devcontainer`-määritykset ja public_url-logiikka säilyivät muuttumattomina: portti 8000, openBrowser-automaattiavaus ja nykyinen app-verkon jakaminen. Ohje säilyttää portin Private-tilassa.

## Tässä tehtävässä todella ajettu

- Lukittu uv-asennus ja uuden Alembic-riippuvuuden asennus onnistui.
- `npm run build --prefix apps/web`: TypeScript-tarkistus ja Vite-tuotantobuild onnistuivat.
- `./scripts/cloud-build.sh`: Docker-imagen build onnistui pilven tuetulla proxy-/CA-reitillä. TLS-varmennusta ei ohitettu. Tavallisen Docker Desktopin kylmää buildia ei tässä tehtävässä ajettu.
- `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app ja db healthy olemassa olevan vaiheen 1 volumen päällä.
- `BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest -q`: **21 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. 9 API-/PostgreSQL-/RDF-testiä, 6 migraatiotestiä, 3 Chromium-selaintestiä ja 3 Codespaces-/paikallisosoitteen muodostustestiä.
- Migraatiotesteissä vanha rakenne luotiin riippumattomalla phase 1 -DDL:llä. Muokattu demo ja toinen samanniminen tarjoaja säilyttivät kaikki alkuperäiset sarakkeet (myös ylimääräisen sisäkkäisen JSON-metatiedon ja tarkat aikaleimat). Tuotteiden UUID:t ja organisaatioiden viitteet säilyivät uusinta-ajossa. Testi ajettiin sekä olemassa olevan alustusmerkinnän kanssa että ilman sitä.
- Tyhjä kanta, ensimmäinen migraatio erikseen, toistetut upgrade-ajot, tyhjä vanha kanta, FK:n pakollisuus ja tuntemattoman skeeman transaktionaalinen hylkäys testattu. Testit tyhjensivät vain `catalog_test`-kantaa.
- Aiemmat haku–tuotesivu–lisäys–muokkaus–poisto- ja mobiiliselainpolut läpäisivät. Ainoana tarvittavana sopeutuksena vanhan tarjoajatekstin syöttö vaihdettiin organisaatiovalintaan. Uusi organisaatiopolku tarkisti listan, perustiedot, uudelleenlatauksen ja tuotteen tarjoajalinkin.
- `docker compose exec -T app .venv/bin/alembic current`: `0002_organizations (head)`.
- `docker compose exec -T app .venv/bin/alembic check`: `No new upgrade operations detected.`
- Codespacesin Compose-tiedostojen yhdistäminen `docker compose ... config --format json` onnistui; workspace jakaa edelleen app-palvelun verkon. `.devcontainer`-tiedostojen diff on tyhjä.

Ensimmäinen selainajo paljasti valinnan kenttäotsikon kohdistusongelman; korjattu eksplisiittisellä label/htmlFor/id-yhdistelmällä. Alembicin CLI-ajon tiedosto-oikeusongelma korjattiin antamalla pyproject.toml/uv.lock-tiedostot imagessa sovelluskäyttäjän omistukseen. Lopullinen koko 21 testin ajo ja CLI-tarkistukset onnistuivat korjausten jälkeen. Neljä kirjastojen deprekaatiovaroitusta (Starlette/httpx ja RDFLib) eivät ole ohitettuja testejä.

## Ajamattomat ja ulkoiset tarkistukset

- Oikeaa GitHub Codespaces -ympäristöä, sen selainvälilehden automaattista avautumista ja Private-portin GitHub-pääsynvalvontaa ei voitu todentaa tämän Linux-pilvikoneen sisältä. Käyttäjän toimivaksi vahvistamia asetuksia ei muutettu. Kokeilu ennen yhdistämistä: READMEn linkki haaraan feat/phase-2a-organizations, uusi Codespace, PORTS → 8000 → Open in Browser, näkyvyys Private.
- Windows/Docker Desktop -ajoa tai GitHub Actions -etä-CI:tä ei tässä tehtävässä ajettu.
- Vaiheen 2A ulkopuolelle jäivät kirjautuminen, käyttöoikeudet, hyväksyntä, julkaisuversiot, SHACL ja ulkoiset integraatiot. Niiden toimivuutta tai DCAT-AP-vaatimustenmukaisuutta ei väitetä.
- Työ pushattu GitHubiin haaraan `feat/phase-2a-organizations`. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2a-organizations --title "Vaihe 2A: Alembic-migraatiot ja tarjoajaorganisaatiot" --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Ympäristön GitHub API -verkkopääsy on avattava luontia varten, tai PR:n voi avata selaimessa osoitteesta https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2a-organizations . Valmis kuvaus on `docs/pull-request.md`. Main-haaraan ei yhdistetty mitään.

---

# Aiemman toimituksen historiatiedot

Alla olevat vaiheen 1 ja Codespaces-toimituksen raportit ovat aikaisempia ajoja. Tämän muutoksen tulokset ovat yllä.

# Vaiheen 1 tila

## Selainkokeilu GitHub Codespacesissa

Lisätty haaraan `demo/codespaces` Dev Container -määritys. Se käynnistää nykyisen Compose-sovelluksen ja PostgreSQL:n sekä avaa portin 8000. Uusi työtilakontti jakaa sovelluksen verkon, joten porttiohjaus osuu FastAPI-palveluun. Paikallinen Compose säilyy ennallaan. Metatiedon URI voi käyttää Codespacesin välitettyä osoitetta ympäristömuuttujien perusteella.

Tässä muutoksessa ajettu: kolme `tests/test_public_url.py`-testiä onnistui; TypeScript-tarkistus ja Vite-tuotantobuild onnistuivat; Python-tiedostojen käännöstarkistus onnistui. Docker-/PostgreSQL-integraatioita, selaintestejä ja Codespacesin oikeaa käynnistystä ei ajettu tässä ympäristössä, jossa ei ole Dockeria tai PostgreSQL-palvelinta. Alla olevat aiemman toimituksen testitulokset säilyvät historiatietona eivätkä ole tämän muutoksen uusinta-ajo.

Ohje: `docs/verkkodemo.md`. Portti säilytetään Private-tilassa. Sovellukseen ei lisätty vaiheen 2 tunnistus- tai valtuutusjärjestelmää. Käynnistys GitHub-tilillä ja sen Codespaces-kiintiöllä on käyttäjän tehtävä.

Tarkistettu 14.10.2026. Työhaara: `feat/phase-1-local-demo`. Tavoitearkkitehtuuri säilyy alkuperäisessä suunnitteludokumentissa; tämän toimituksen rajaus on ROADMAPin vaihe 1.

## Toteutettu

| Vaiheen 1 vaatimus | Toteutus ja todennus |
| --- | --- |
| Tietotuotteiden ylläpito | React-lomake ja FastAPI CRUD; lisäys, muokkaus, poisto ja virheellisten syötteiden hylkäys testattu. |
| Haku | Tekstihaku, tarkka teema/tarjoaja ja sivutus PostgreSQL-kyselyillä; API- ja selaintestit. |
| Tuotesivu | Kuvaus, lähde, tarjoaja, käyttötarkoitus, rajaukset, käyttöehdot, saatavuus ja tietoelementit; selainpolku ja uudelleenlataus testattu. |
| PostgreSQL | Oikea PostgreSQL 17, pysyvä Compose-volume; tallennus varmistettu erillisellä DB-yhteydellä. |
| JSON-vienti | Tuote ja katalogi; vienti vastaa tallennettua tuotetta. |
| JSON-LD-vienti | Tuote ja DCAT-katalogi; RDFLib jäsentää RDF-graafin ja tarkistaa Dataset-, title- ja semanticUri-merkitykset. |
| Kolme synteettistä tuotetta | Verovelkatieto, yrityksen perustiedot ja ammattipätevyys; idempotentti kertaluonteinen siemennys säilyttää muokkaukset ja poistot. |
| Käynnistys | README: Compose ja host-kehitys; tässä pilvessä testattu cloud-build.sh ja Compose --no-build --wait. |
| Rajaus ja agenttiohjeet | ROADMAP.md, AGENTS.md ja arkkitehtuurikuvaus. |

## Ajettu todennus

- `uv sync --locked`: onnistui Python 3.12:lla.
- `npm ci --prefix apps/web` ja `npm run build --prefix apps/web`: onnistui; TypeScript-tarkistus ja Vite-tuotantobuild.
- `./scripts/cloud-build.sh`: Docker-image rakennettu onnistuneesti; TLS- ja pakettitarkistukset säilytetty.
- `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app ja db healthy.
- `GET /health/ready`: `status=ready`, `database=postgresql`.
- `BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest -q`: **9 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Seitsemän API-/PostgreSQL-/RDF-testiä ja kaksi oikealla Chromiumilla ajettua selaintestiä.
- Selainpolku: haku → tuotesivu → uuden synteettisen tuotteen lisäys → uudelleenlataus → muokkaus → vahvistettu poisto. Reactin skriptitekstin käsittely tekstinä tarkistettu. Mobiilinäkymän vaakasuuntainen mahtuminen tarkistettu.
- `docker compose restart app` ja uusi Compose-readiness: onnistui; toiminnallinen haku palautti edelleen kolme demotuotetta.
- Sovelluksen uudelleenalustustesti varmistaa, että muokkaus ja poistettu demotuote eivät palaudu alkuperäiseen tilaan.
- `git diff --check`: ei whitespace-virheitä.

Ensimmäisessä testikehityksen ajossa fixture-apufunktion matala kopio aiheutti kahden testin epäonnistumisen; korjattu syvällä kopiolla. Ensimmäisen konttikäynnistyksen tiedosto-oikeusongelma korjattu COPY --chown -asetuksella. Koko yhdeksän testin sarja ajettu uudelleen onnistuneesti korjattua Compose-sovellusta vasten. Testikirjastot tuottavat kolme deprekaatiovaroitusta (Starletten TestClient/httpx sekä RDFLibin ConjunctiveGraph); testitulokset eivät ole ohituksia.

## Rajat ja myöhemmät vaiheet

- Ei kirjautumista, organisaatiokohtaisia oikeuksia, hyväksyntää, julkaisuversioita tai SHACL:ia: vaihe 2.
- Ei ulkoisia lompakko-, QEAA- tai data-avaruusintegraatioita: vaihe 3.
- DCAT-AP-vaatimustenmukaisuutta, tuotantovalmiutta, WCAG-vaatimustenmukaisuutta tai kuormitustavoitteiden toteutumista ei ole todennettu. Mobiilin ja lomakkeiden perustestit eivät korvaa saavutettavuusauditointia.
- Vaiheen 1 skeema luodaan SQLAlchemyllä. Lisää Alembic ennen skeeman ensimmäistä muutosta.
- GitHub Actions -workflow on mukana, mutta etä-CI:n suoritusta ei ole tässä todettu.

## Toimitus ja pilviasetukset

Asennusskripti ja palvelujen käynnistysohjeet tallennettu pilviympäristön luonnokseen (`install_script`, `start_skill`); tallennus ei julkaise ympäristöä. Verkkoluonnokseen lisätty GitHub API ja Playwrightin latausosoitteet. Nykyisessä koneessa selaintestit käyttävät valmista Chromiumia, eikä latauksia tarvittu. Haara `feat/phase-1-local-demo` on pushattu onnistuneesti GitHubiin. Pull requestia ei ole luotu: `gh pr create --base main --head feat/phase-1-local-demo` pysähtyi `POST https://api.github.com/graphql: Forbidden` -virheeseen. Aktivoi `api.github.com` ympäristön verkkoasetuksissa ja suorita tämän jälkeen `gh pr create --base main --head feat/phase-1-local-demo --title "Vaihe 1: paikallinen PostgreSQL-metatietohakemisto" --body-file docs/pull-request.md`. PR-kuvaus on tallennettu tiedostoon `docs/pull-request.md`. Main-haaraan ei ole yhdistetty muutoksia eikä vaihetta 2 aloitettu.

