# Metatietovaranto — synteettinen demo, vaihe 2C

Suomenkielinen React/TypeScript-käyttöliittymä, FastAPI, PostgreSQL ja Keycloak. Toteutettu: organisaatiokohtainen ylläpito, yksityiset luonnokset, erillinen hyväksyntä, muuttumattomat julkaisuversiot, haku, JSON-/JSON-LD-vienti ja sisältöprofiilin snapshotit. [ROADMAP](ROADMAP.md) rajaa toteutuksen, [STATUS](STATUS.md) kertoo todella ajetut tarkistukset.

Vain synteettiseen demokäyttöön. Katalogi ei myönnä todistuksia eikä toteuta lompakkoprotokollaa, QEAA-palvelua tai tuotannon tunnistamista. Tavoitearkkitehtuuri on `metatietovaranto_suunnittelu.md`. PR:ien 5 ja 6 sitovat [semanttinen periaate](docs/semanttinen-periaate-1.md) ja [VC-periaate](docs/vc-periaate-2.md) on huomioitu [vaiheen 2C ratkaisussa](docs/phase-2c.md).

## Kokeile selaimessa ennen yhdistämistä

Avaa [vaiheen 2C uusi Codespace](https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2c-publication), valitse haara **feat/phase-2c-publication** ja **Create codespace**. Uusi Codespace pitää main-haaran kokeiludatan erillään. Sovellus, PostgreSQL ja Keycloak käynnistyvät automaattisesti. Selain avautuu automaattisesti tai valitse **PORTS → 8000 → Open in Browser**. Säilytä portin näkyvyys **Private**. Keycloak toimii saman osoitteen `/identity`-polussa; muita portteja ei tarvitse avata.

Osoite on `https://<codespacen-nimi>-8000.app.github.dev`; täsmällinen oman ympäristön osoite näkyy PORTS-näkymässä. Älä vaihda portin sisäistä protokollaa HTTPS:ksi. [Verkkodemon ohje](docs/verkkodemo.md) kertoo pysäyttämisestä ja kiintiöistä.

### Demotunnukset

| Käyttäjä | Salasana | Muokkaus | Tarkastus ja julkaisu |
| --- | --- | --- | --- |
| `vero` | `demo-vero` | Alkuperäinen verotuotteen organisaatio | Yritystuotteen organisaatio |
| `yritys` | `demo-yritys` | Alkuperäinen yritystuotteen organisaatio | Verotuotteen organisaatio |
| `lukija` | `demo-lukija` | Ei | Ei; alkuperäisen verotuotteen organisaation luku |

Julkisia synteettisiä demotunnuksia, eivät tuotantosalaisuuksia. Samassa organisaatiossa kirjoittaja ei saa hyväksyä omaa muutostaan. Tarkastaja voi myös julkaista hyväksymänsä version. Julkaisijarooli ei anna muokkausoikeutta. Lisäjäsenyydet annetaan kerran vain tunnettuihin synteettisiin organisaatio-UUID:ihin; olemassa olevia jäsenyyksiä ei korvata. Kolmannen pätevyysorganisaation tuote säilyy kannassa, mutta sille ei ole valmista muokkaajatunnusta. Jäsenyyksien hallinta: [authentication.md](docs/authentication.md).

### Kokeilupolku

1. Uuden demon julkinen haku on aluksi tyhjä. Kolme synteettistä esimerkkiä (verovelka, yrityksen perustiedot, ammattipätevyys) säilyvät keskeneräisinä yksityisinä luonnoksina. Niille ei keksitä virallista profiilia tai hyväksyntää.
2. Kirjaudu `vero`-käyttäjänä ja avaa **Omat luonnokset → Verovelkatieto → Muokkaa**. Voit myös lisätä oman synteettisen tuotteen. Tarjoajavalikossa ovat vain omat muokkaajaorganisaatiot.
3. Avaa **Tuo Tietomallit-soveltamisprofiili**. Valitse tiedosto `fixtures/semantic-profile-demo.ttl`, profiili-IRI `https://example.org/metatietovaranto/demo/profile` ja OWL-sanaston nimiavaruus `https://example.org/metatietovaranto/demo/`. Kirjaa lähdeilmoitukseksi **Synteettinen testifixture; ei oikea Tietomallit-export, vain ohjelmistodemo.** Tuo profiili ja tallenna tuote. Fixture ei ole Tietomallit-alustan vahvistama profiili. Oikea profiili voidaan antaa vaihtoehtoisesti koneluettavan exportin linkkinä.
4. Tietoelementit johdetaan profiilista. VC-jakelun oletus on `planned`, jolloin tuotesivu näyttää **Lompakkotodistus suunnitteilla**. Lähetä luonnos tarkastukseen.
5. Kirjaudu ulos ja vahvista Keycloakin **Log out**. Kirjaudu `yritys`-käyttäjänä, avaa sama luonnos, tarkasta profiili ja lähdeilmoitus, kirjoita perustelu ja merkitse tarkastuksen valintaruutu. Hyväksy ja julkaise esimerkiksi versiona `1.0.0`.
6. Julkaisu löytyy nyt julkisesta hausta ja sen JSON-/JSON-LD-viennit toimivat. Historiassa on pysyvä version URI ja tarkiste. Profiilin tarkastus on ihmisen arvio lähdeilmoituksesta; se ei ole automaattinen alustatodistus tai myönnetyn VC:n SHACL-validointi.
7. `vero` voi luoda julkaistun rinnalle uuden työkopion. Muokkaus ei muuta aiempaa julkaisua. Uusi julkaisu tarvitsee uuden hyväksynnän ja aiempaa suuremman `major.minor.patch`-numeron. Julkaistua tai tarkastushistoriaa sisältävää tuotetta ei poisteta.

## Windows ja Docker Desktop

Tarvitset Docker Desktopin käynnissä Linux-konteilla, Compose v2:n ja Gitin. Kloonaa repo tai avaa nykyinen checkout PowerShellissä:

```powershell
git fetch origin
git switch feat/phase-2c-publication
docker compose up --build
```

Avaa selaimessa **http://localhost:8000**. API-kuvaus: **http://localhost:8000/docs**, readiness: **http://localhost:8000/health/ready**. Käytä localhost-osoitetta myös kirjautumisessa. Ensimmäinen käynnistys voi kestää useita minuutteja. Vaihtoehto taustalle: `docker compose up --build -d --wait`.

Pysäytä etualan ajo **Ctrl+C**:llä tai aja toisessa terminaalissa `docker compose stop`. Jatka `docker compose up -d --wait`. `docker compose down` säilyttää voluumit. Tuotteet, luonnokset ja versiot ovat `pgdata`-volumessa, Keycloak omassa `keycloakdata`-volumessaan. Tavallinen käynnistys ei palauta fixtureitä tai muutettuja oikeuksia.

**Testidatan tarkoituksellinen palautus (poistaa kaikki oman demon muutokset, julkaisut ja käyttäjäistunnot):**

```powershell
docker compose down -v
docker compose up --build
```

Tätä nollausta ei käytetä päivityksessä. Portit 8000, 5432 ja 8080 sidotaan paikalliseen loopbackiin. Vain 8000 tarvitaan selaimelle. PostgreSQL-tunnukset `demo/demo` ja Keycloakin kehitystila ovat demokäyttöä varten.

## Päivitys vanhasta kannasta

Ota ensin varmuuskopio. Säilytä sama hakemisto, Compose-projektinimi ja voluumit. Pysäytä kirjoittava sovellus, tietokanta jää käyntiin:

```bash
docker compose stop app
docker compose exec -T db sh -c 'pg_dump -U demo -d catalog > /tmp/before-update.sql'
docker compose cp db:/tmp/before-update.sql ./before-update.sql
git fetch origin
git switch feat/phase-2c-publication
docker compose up --build -d --wait
docker compose exec -T app .venv/bin/alembic current
```

Tiedoston kopiointi säilyttää merkistön myös PowerShellissä. Odotettu head on `0004_publication`. Käynnistys ajaa migraatiot transaktiossa advisory-lukon alla ennen readinessia sekä Composessa että Codespacesissa. Virhe estää käynnistymisen ja fixtureiden ajon. Toistuva ajo on sallittu: `docker compose exec -T app .venv/bin/alembic upgrade head`.

- `0001_phase1` tunnistaa ja tarkistaa alkuperäisen skeeman tai luo tyhjän kannan. Tuntematonta skeemaa ei hyväksytä stampilla.
- `0002_organizations` säilyttää tuotteiden UUID:t, kaikki metatiedot ja aikaleimat. Jokainen vanha tarjoaja saa erillisen organisaation; samannimisiä ei yhdistetä. Tuntematon maa on `ZZ`, tunnisteet `[]`, alkuperä näkyy `legacyProductId`-kentässä.
- `0003_auth` lisää organisaatiojäsenyydet ja OIDC-istunnot.
- `0004_publication` säilyttää alkuperäiset tuoterivit, kopioi kuvaukset luonnoksiksi ja lisää muuttumattomat profiili-/julkaisusnapshotit, tarkastukset, auditoinnin ja outboxin. Omistajaorganisaatio lukitaan alkuperäiseen tarjoajaan. Vanhoja tuotteita ei julkaista automaattisesti; anonyymi näkyvyys muuttuu tarkoituksella. Vanhat käsin annetut tietoelementit säilyvät demotietona, kunnes profiili liitetään.

Vain aidosti uusi kanta saa kolme fixtureä. Vanha tyhjä kanta tai poistettu fixture ei palaudu. Migraatio ei tarjoa tuhoavaa downgradea tai offline-SQL-ajoa; palautuminen vaatii testatun varmuuskopion palautuksen erilliseen kantaan. Älä poista vanhaa Codespacea tietoja säilyttävässä päivityksessä. **Rebuild Container** rakentaa haaran imagen uudelleen; pelkkä tiedostojen haaranvaihto ei päivitä ajossa olevaa imagea. Keycloak-realmiä ei tarvitse nollata.

## Rajapinta ja profiilit

Julkiset luku-API:t palauttavat vain julkaistuja snapshotteja. Haku kohdistuu nimeen, kuvaukseen ja tarjoajaan; teema/tarjoaja ovat tarkkoja rajauksia, `limit` oletuksena 20 (enintään 100), `offset` sivuttaa. Haku suodattaa pienessä demossa uusimmat julkaisut muistissa; kuormitustavoitetta ei ole mitattu.

| Pyyntö | Merkitys |
| --- | --- |
| `GET /api/v1/products` | Julkinen haku |
| `GET /api/v1/products/{id}` | Viimeisin julkaisu; julkaisematon 404 |
| `GET /api/v1/products/{id}/versions` | Versiohistoria |
| `GET /api/v1/products/{id}/versions/{semver}` | Muuttumaton versio ja ETag |
| `GET /api/v1/products/{id}/export?format=jsonld&version=1.0.0` | Nimetyn version vienti; ilman version-parametria uusin |
| `GET /api/v1/catalog/export?format=json` | Uusimpien julkisten versioiden katalogi |
| `GET /id/products/{id}` | JSON/JSON-LD tai 303 HTML-tuotesivuun; Vary: Accept |
| `GET /id/products/{id}/versions/{semver}` | Pysyvä version URI; samat esitykset |
| `GET /api/v1/my/products` | Omien organisaatioiden luonnokset, myös tarkastajalle |
| `POST /api/v1/products` | Luo yksityinen luonnos, 201, Location ja ETag |
| `GET /api/v1/products/{id}/draft` | Yksityinen työkopio ja ETag |
| `PUT /api/v1/products/{id}` | Muokkaa vain työkopiota |
| `POST /api/v1/products/{id}/drafts` | Uusi työkopio julkaisun rinnalle |
| `POST /api/v1/drafts/{id}/submit` | Tarkastukseen |
| `POST /api/v1/drafts/{id}/reviews` | Hyväksy tai palauta perustelulla |
| `POST /api/v1/drafts/{id}/publish` | Atominen julkaisu |
| `POST /api/v1/drafts/{id}/validate` | Julkaisuedellytysten tarkistus, ei SHACL-instanssivalidointi |
| `DELETE /api/v1/products/{id}` | Poista vain luonnos, jolla ei ole julkaisu-/tarkastushistoriaa |
| `GET /api/v1/products/{id}/audit-events` | Organisaation muokkaajan/tarkastajan tapahtumat |
| `GET /api/v1/organizations`, `GET /api/v1/organizations/{id}` | Organisaatioiden perustiedot |
| `POST /api/v1/profile-snapshots` | Profiilin tuonti editorin organisaatioon |
| `GET /api/v1/profile-snapshots/{id}` | Snapshotin manifesti, alkuperä ja tarkisteet |
| `GET /api/v1/profile-snapshots/{id}/artifacts/{artifactId}` | Alkuperäinen UTF-8-artefakti |

Kirjoitus tarvitsee palvelinistunnon ja `/auth/me`-vastauksen `csrfToken`-arvon `X-CSRF-Token`-otsakkeessa. Luonti ja julkaisu vaativat lisäksi `Idempotency-Key`-otsakkeen (24 h, sama avain eri sisällölle 409). Työkopion muuttaminen/tilasiirtymä/poisto tarvitsee sen nykyisen `If-Match`-ETagin: puuttuva 428, vanhentunut 412. Käyttöliittymä lähettää nämä. Omistajaorganisaatio ei vaihdu tarjoajavalinnasta; vaihto edellyttää editor-oikeutta myös uuteen tarjoajaan.

POST/PUT ei hyväksy asiakkaan `provider`-, `dataElements`-, tila- tai hyväksyntäkenttiä. Käytä `/docs`-sopimusta ja `providerOrganizationId`-kenttää. Tarjoajanimi säilyy vastauksissa ja vienneissä. Profiilin tuonti tukee Turtlea, RDF/XML:ää ja paikalliskontekstista JSON-LD:tä, enintään 1 MB/artefakti, 2 MB/pyyntö ja 10 000 RDF-kolmikkoa. Linkkituonti hyväksyy vain `tietomallit.suomi.fi` / `iri.suomi.fi` HTTPS-exportit ilman redirecteja. Muut lähteet annetaan tiedostona. HTML-sivulinkki ei ole export.

API tukee riippuvuuksia, ulkoisia OWL-viitteitä ja JSON Schema/OpenAPI -johdannaisia. Käyttöliittymän yksinkertainen tuonti käsittelee yhden pääartefaktin ja yhden sanastoviitteen; moniosainen tuonti tehdään API:lla. Alkuperäiset IRI:t ja koko graafi säilyvät, tietoelementtinäkymä on johdettu osajoukko. Etäkonteksteja tai riippuvuuksia ei noudeta jäsennyksen aikana. Puuttuva lähde/SHACL/riippuvuus estää julkaisun. Pelkkä johdannainen ei riitä. RDF-esitysten ekvivalenssi tarkistetaan graafina; tavutarkisteet ovat erikseen. JSON-LD-katalogivienti on eri asia kuin sisältöprofiili tai myönnetty VC. DCAT-AP-vaatimustenmukaisuutta ei väitetä.

VC-metatietojen editori on tässä vaiheessa JSON-kenttä. `planned`/`suspended` ei näytä toimivaa linkkiä. Käytettävä jakelu tarvitsee myöntäjä-/operaattori-/lähdeorganisaatiot, VC-profiilin ja kartoituksen, pysyvän HTTPS-linkin sekä saatavuus- ja käyttöehdot. Henkilökohtaisia tarjouksia, koodeja tai tokeneita ei tallenneta. Esimerkkiverkkotunnuksia ei hyväksytä toimivaksi myöntämispalveluksi. EUDIW-/EBW-`tested` vaatii nimetyn profiilin, version, näytön ja testipäivän. Demo ei vahvista QEAA-luokkaa.

## Kehitys ja testit

```bash
uv sync --locked
npm ci --prefix apps/web
npm run build --prefix apps/web
docker compose up -d db keycloak --wait
DEMO_MODE=true .venv/bin/uvicorn apps.api.main:app --host 127.0.0.1 --port 8000 --no-access-log
```

Älä aja hostin API:a ja Compose-appia samaan porttiin. Hostin `DATABASE_URL` on `postgresql+psycopg://demo:demo@localhost:5432/catalog`, `KEYCLOAK_INTERNAL_URL` on `http://localhost:8080/identity`, `PUBLIC_BASE_URL` on `http://localhost:8000`. `DEMO_MODE=true` on pakollinen. Compose asettaa omat sisäiset osoitteensa.

Testit käyttävät oikeaa PostgreSQL:ää ja tuhoavaa erillistä `catalog_test`-kantaa; eivät `catalog`-kantaa. Luo testikanta kerran (ohita createdb jos jo olemassa):

```bash
docker compose exec -T db createdb -U demo catalog_test
.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q
```

Älä aja tätä testikantaa käyttäviä pytest-ajoja rinnakkain. `TEST_DATABASE_URL` voi muuttaa yhteysosoitetta mutta kannan pitää olla `catalog_test`. Selaintestit käyttävät erikseen käynnistettyä demoa ja oikeaa Keycloak-kirjautumista:

```bash
.venv/bin/playwright install --with-deps chromium
BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q
```

Valmista paikallista Chromiumia käytetään automaattisesti; `CHROMIUM_EXECUTABLE` voi nimetä sen. Selaintestit luovat yksilöidyn testituotteen; julkaisutesti jättää muuttumattoman synteettisen julkaisun historiaan. Alkuperäisiä kolmea demotuotetta ei muuteta. Ilman `BROWSER_BASE_URL`-asetusta seitsemän selaintestiä ohitetaan. Täysi ajo: `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest -q`. GitHub Actionsin etätulos varmistetaan erikseen.

Tässä pilviympäristössä Docker-build käyttää alustan proxy-/CA-reittiä: `./scripts/cloud-build.sh`, sitten `docker compose up -d --no-build --wait`. Tavallisen Docker Desktopin komento on yllä oleva `docker compose up --build`. Kirjoitussuojatun kotihakemiston yhteydessä aseta `UV_CACHE_DIR=/workspace/.cache/uv`, `npm_config_cache=/workspace/.cache/npm`, `DOCKER_CONFIG=/workspace/.cache/docker`. Nämä eivät kuulu Windowsin normaaliin käynnistykseen.
