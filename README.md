# Metatietovaranto — paikallinen demo

Viranomaisten tietotuotteiden metatietohakemiston vaihe 1. Sovellus sisältää suomenkielisen React/TypeScript-käyttöliittymän, FastAPI-rajapinnan, PostgreSQL-tallennuksen, haun, tuotesivun, avoimen ylläpidon ja JSON-/JSON-LD-viennit.

**Vain paikalliseen synteettiseen demokäyttöön.** Kirjautuminen, organisaatiorajat, hyväksyntä, julkaisuversiot ja SHACL kuuluvat vaiheeseen 2. Ulkoiset lompakko-, QEAA- ja data-avaruusintegraatiot kuuluvat vaiheeseen 3. `ROADMAP.md` rajaa toteutuksen; `metatietovaranto_suunnittelu.md` säilyy tavoitearkkitehtuurina.

## Windows: Docker Desktop ja PowerShell

1. Asenna Git sekä Docker Desktop Windowsille. Käynnistä Docker Desktop ja käytä **Linux containers** -tilaa (suositus: WSL 2 -taustajärjestelmä). Odota, että Docker Engine on käynnissä.
2. Avaa PowerShell. Hae demohaara ja siirry hakemistoon:

```powershell
git clone --branch feat/phase-1-local-demo https://github.com/jgmikael/metatietovaranto.git
cd metatietovaranto
```

Jos repositorio on jo koneellasi, käytä sen hakemistossa `git switch feat/phase-1-local-demo` ja `git pull --ff-only`. Säilytä omat paikalliset muutoksesi ennen haaran vaihtoa.

3. Tarkista Docker ja käynnistä repositorion juuresta:

```powershell
docker compose version
docker compose up --build
```

Docker rakentaa käyttöliittymän ja palvelimen sekä käynnistää PostgreSQL:n. Windowsiin ei tarvitse asentaa Pythonia, Node.js:ää tai uv:tä. `.env`-tiedostoa tai pilven shell-skriptiä ei tarvita. Ensimmäinen build tarvitsee internetyhteyden konttien ja riippuvuuksien lataamiseen. Komento jää näyttämään palveluiden lokit; pidä PowerShell-ikkuna auki.

4. Kun appin lokissa näkyy `Application startup complete`, avaa selaimessa täsmälleen **http://localhost:8000/**. API-dokumentaatio on **http://localhost:8000/docs**.

Voit tarkistaa valmiuden toisessa PowerShell-ikkunassa saman repositorion hakemistossa:

```powershell
docker compose ps
Invoke-RestMethod http://localhost:8000/health/ready
```

Molempien palvelujen pitäisi näkyä healthy-tilassa ja readiness-vastauksessa `status: ready`, `database: postgresql`. Compose sitoo sovelluksen portin 8000 ja PostgreSQL:n portin 5432 vain paikalliseen koneeseen. Jos jompikumpi portti on varattu, pysäytä sitä käyttävä toinen paikallinen palvelu ennen demon käynnistystä. Yritysverkon proxy-/varmenneongelmat on ratkaistava Docker Desktopin asetuksissa; älä poista TLS-varmennusta käytöstä.

### Demotunnukset ja kolme esimerkkituotetta

**Käyttöliittymään ei kirjauduta eikä demotunnuksia tarvita.** Kaikki paikallisen demon käyttäjät voivat lisätä, muokata ja poistaa tuotteita. Tietokannan paikalliset demoasetukset ovat käyttäjä `demo`, salasana `demo`, tietokanta `catalog`; näitä ei syötetä selaimeen.

Ensimmäinen käynnistys luo alkuperäisskeeman ja seuraavat kolme synteettistä tuotetta tiedostosta `fixtures/products.json`:

| Tuote | Teema | Tarjoaja |
| --- | --- | --- |
| Verovelkatieto — synteettinen demo | Verotus | Demo-veroviranomainen |
| Yrityksen perustiedot — synteettinen demo | Yritykset | Demo-yritysrekisteri |
| Ammattipätevyys — synteettinen demo | Pätevyydet | Demo-pätevyysviranomainen |

Esimerkit eivät sisällä aitoja henkilö-, yritys- tai rekisteritietoja. Tavallinen uudelleenkäynnistys säilyttää lisäykset, muokkaukset ja poistot eikä korvaa sisältöä fixtureillä.

### Pysäytys ja uudelleenkäynnistys

Paina loki-ikkunassa **Ctrl+C**. Normaali Compose-toiminta pysäyttää kontit ja säilyttää tietokantadatan. Varmista pysäytys ja poista kontit ajamalla repositorion juuresta (tarvittaessa toisessa PowerShell-ikkunassa):

```powershell
docker compose down
```

`down` poistaa kontit ja projektin verkon, mutta säilyttää `pgdata`-volumen. Käynnistä uudelleen samalla komennolla `docker compose up --build`. Jos haluat demon taustalle loki-ikkunan sijaan, vaihtoehto on `docker compose up --build -d --wait`; pysäytä se komennolla `docker compose down`.

### Palauta alkuperäinen testidata

**Seuraava poistaa kaikki tässä demossa lisäämäsi tuotteet ja muokkaukset sekä koko projektin PostgreSQL-volumen, myös mahdollisen testikannan.** Käytä sitä vain, kun haluat palauttaa lähtötilanteen. Aja samasta repositorion hakemistosta:

```powershell
docker compose down --volumes
docker compose up --build
```

Uusi tyhjä volume alustetaan automaattisesti kolmella yllä luetellulla esimerkkituotteella. Tarkista selaimessa http://localhost:8000/, että haussa näkyy kolme tuotetta. Tavalliseen pysäytykseen ei käytetä `--volumes`-valintaa.

### Mitä käynnistyksestä on varmennettu?

Tämä toimitus on testattu Linux-pilviympäristössä, ei Windows-koneessa tai Docker Desktopissa. Tarkka ajoloki, testitulokset ja pilven proxyrajoitus on raportoitu `STATUS.md`:ssä. Windows/WSL 2:n asennusta, koneesi palomuuria, vapaita portteja tai yritysverkon asetuksia ei ole voitu testata. Linuxin onnistunut konttiajo ei yksin todista näitä Windowsin edellytyksiä.

### Pilviympäristön konttikäännös

Tässä Codex-ympäristössä konttikäännöksen DNS ja luottamusketju tarvitsevat alustan välityspalvelimen asetukset. Käytä repositorion juuresta:

```bash
./scripts/cloud-build.sh
DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait
curl --fail http://127.0.0.1:8000/health/ready
```

Skripti välittää nykyiset proxy-asetukset Dockerin build-argumentteina ja nykyisen julkisen CA-varmenteen BuildKit-mounttina. Varmenteen tarkistusta ei ohiteta eikä varmennetta tai tunnuksia tallenneta repoon tai imageen. Käynnissä olevat prosessit on käynnistettävä uudelleen uudessa pilvitehtävässä.

## Kehitä ilman sovelluskonttia

Tarvitset Python 3.12:n, uv:n, Node.js 24:n, npm:n ja Dockerin PostgreSQL:ää varten. Riippuvuudet ovat lukittuina `uv.lock`- ja `package-lock.json`-tiedostoissa.

```bash
docker compose up -d db --wait
uv sync --locked
npm ci --prefix apps/web
npm run build --prefix apps/web
DEMO_MODE=true .venv/bin/uvicorn apps.api.main:app --host 127.0.0.1 --port 8000
```

Käyttöliittymä palvellaan rakennetusta `apps/web/dist`-hakemistosta. Rakenna se uudelleen muutosten jälkeen. API:n kehityksessä voit lisätä `--reload`-valinnan. Älä käynnistä hostin API:a ja Compose-appia samaan porttiin yhtä aikaa.

Jos pilviympäristön kotihakemisto on kirjoitussuojattu, aseta ennen asennusta:

```bash
export UV_CACHE_DIR=/workspace/.cache/uv
export npm_config_cache=/workspace/.cache/npm
export DOCKER_CONFIG=/workspace/.cache/docker
```

| Asetus | Oletus / käyttö |
| --- | --- |
| `DEMO_MODE` | Vaaditaan arvolla `true`; muu arvo estää käynnistyksen. |
| `DATABASE_URL` | Host-kehityksessä `postgresql+psycopg://demo:demo@localhost:5432/catalog`; Compose käyttää hostia `db`. |
| `PUBLIC_BASE_URL` | `http://localhost:8000`, tuotetunnisteiden paikallinen perusosoite. |
| `TEST_DATABASE_URL` | Erillinen `postgresql+psycopg://demo:demo@localhost:5432/catalog_test`. |
| `BROWSER_BASE_URL` | Käynnissä olevan demon osoite selaintesteille. |
| `CHROMIUM_EXECUTABLE` | Valinnainen paikallisen Chromiumin polku, esimerkiksi `/usr/bin/chromium`. |

Compose-tunnukset `demo/demo` ovat vain paikallista synteettistä demoa varten.

## Demopolku

1. Hae esimerkiksi `verovelka`, tai rajaa tarkalla teemalla `Yritykset`.
2. Avaa tuotesivu: sisältö, tarjoaja, synteettinen lähde, käyttötarkoitus, rajaukset, käyttöehdot ja tietoelementit.
3. Avaa JSON- tai JSON-LD-vienti.
4. Palaa hakuun ja valitse **Lisää tietotuote**. Täytä pakolliset kentät ja tallenna.
5. Muokkaa tuotetta tuotesivulla; lataa sivu uudelleen ja varmista tallennus. Poisto pyytää vahvistuksen.

Tekstihaku kohdistuu nimeen, kuvaukseen ja tarjoajaan kirjainkoosta riippumatta. Teema ja tarjoajarajaus ovat täsmällisiä. API sivuttaa `limit`-/`offset`-parametreilla (oletus 20, enintään 100). Kaikki tuotteet näkyvät heti: vaihe 1 ei sisällä luonnos- tai julkaisutiloja.

## Rajapinta ja viennit

| Pyyntö | Toiminto |
| --- | --- |
| `GET /api/v1/products?q=verovelka&theme=Verotus` | Haku: items, total, limit, offset. |
| `POST /api/v1/products` | Lisää tietotuote; 201 ja Location. |
| `GET /api/v1/products/{uuid}` | Tuotteen kuvaus. |
| `PUT /api/v1/products/{uuid}` | Korvaa muokattavat metatiedot. |
| `DELETE /api/v1/products/{uuid}` | Poista; 204. |
| `GET /api/v1/products/{uuid}/export?format=jsonld` | Tuotteen JSON-LD; `format=json` palauttaa JSONin. |
| `GET /api/v1/catalog/export?format=jsonld` | Koko demon katalogivienti, ei hakurajausta. |
| `GET /id/products/{uuid}` | Accept: JSON / JSON-LD tai 303-ohjaus selaimen tuotesivulle. |
| `GET /health/live`, `GET /health/ready` | Prosessin ja PostgreSQL-taulun toimintatarkistus. |

POST/PUT-runko noudattaa `/docs`-sopimusta; käyttökelpoinen esimerkki on `fixtures/products.json` ilman `id`-kenttää. JSON-LD käyttää DCAT-/Dublin Core -termejä ja selvästi paikallisia demotermejä. **DCAT-AP-vaatimustenmukaisuutta tai SHACL-validointia ei väitetä.** Koko katalogin vienti on tarkoitettu pienelle paikalliselle demolle.

## Vaiheen 1 testit

API-testit käyttävät oikeaa PostgreSQL:ää ja erillistä `catalog_test`-kantaa. Luo kanta kerran:

```bash
docker compose up -d db --wait
docker compose exec -T db createdb -U demo catalog_test
uv sync --locked
.venv/bin/pytest tests/test_api.py -q
```

Jos kanta on jo olemassa, älä suorita `createdb`-komentoa uudelleen. API-testit tyhjentävät **vain testikannan** tuotetaulut jokaisen testin jälkeen ja estävät muun kantanimen käytön. Ne eivät koske `catalog`-kantaan.

Selaintestit käyttävät käynnissä olevaa demoa. Ne lisäävät yksilöidyn synteettisen testituotteen ja poistavat sen, eivät muuta siementuotteita. Jos Chromium on jo asennettu, sitä käytetään automaattisesti; muuten asenna Playwrightin selain:

```bash
.venv/bin/playwright install --with-deps chromium
BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest tests/test_browser.py -q
```

API ja käyttöliittymä täytyy käynnistää edellä kuvatusti ennen selaintestejä. Täysi testi- ja build-tarkistus:

```bash
npm run build --prefix apps/web
BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest -q
```

Ilman `BROWSER_BASE_URL`-asetusta kaksi selaintestiä ohitetaan tarkoituksellisesti; sellainen ajo ei todista käyttöliittymän toimivuutta. Testien tulokset ja rajoitukset ovat `STATUS.md`:ssä. GitHub Actions määrittelee vastaavat API-, selain- ja konttibuild-tarkistukset; etä-CI:n tulos raportoidaan vasta sen ajamisen jälkeen.
