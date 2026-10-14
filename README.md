# Metatietovaranto — paikallinen demo

## Kokeile ilman asennuksia

Avaa [GitHub Codespaces -käynnistys](https://codespaces.new/jgmikael/metatietovaranto?ref=main), tarkista haara `main` ja valitse **Create codespace**. Sovellus ja PostgreSQL käynnistyvät automaattisesti. Avaa portti **8000** editorin **PORTS → Open in Browser** -toiminnolla, jos demo ei avaudu automaattisesti. Säilytä portin näkyvyys **Private**.

Ohjeet, kokeilupolku, pysäyttäminen ja käyttökiintiöt: [Verkkodemon ohje](docs/verkkodemo.md). Tämä on yksityinen selainkokeilu; se ei julkaise avointa ylläpitoa internetiin.

Viranomaisten tietotuotteiden metatietohakemiston vaihe 2A (vaiheen 1 demo säilyy). Sovellus sisältää suomenkielisen React/TypeScript-käyttöliittymän, FastAPI-rajapinnan, PostgreSQL-tallennuksen, haun, tuotesivun, avoimen ylläpidon ja JSON-/JSON-LD-viennit.

**Vain paikalliseen synteettiseen demokäyttöön.** Kirjautuminen, organisaatiokohtaiset käyttöoikeudet, hyväksyntä, julkaisuversiot ja SHACL jäävät vaiheen 2 myöhempiin osiin. Vaihe 2A lisää vain migraatiot ja tarjoajaorganisaatiot. Ulkoiset lompakko-, QEAA- ja data-avaruusintegraatiot kuuluvat vaiheeseen 3. `ROADMAP.md` rajaa toteutuksen; `metatietovaranto_suunnittelu.md` säilyy tavoitearkkitehtuurina.

## Kokeile vaihetta 2A selaimessa ennen yhdistämistä

Avaa [vaiheen 2A oma Codespace](https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2a-organizations). Valitse haaraksi **feat/phase-2a-organizations** ja **Create codespace**. Käytä uutta codespacea, jotta main-haaran nykyinen kokeiludata säilyy omassa ympäristössään. Sovellus ajaa migraatiot ennen readiness-tilaa, ja nykyinen **openBrowser**-automaattiavaus säilyy. Jos selain ei avaudu, valitse **PORTS → 8000 → Open in Browser**. Portin näkyvyyden on pysyttävä **Private**; älä muuta sitä julkiseksi.

Kokeile **Organisaatiot**-linkkiä ja organisaation perustietoja. Lisää tai muokkaa tietotuotetta ja valitse **Tarjoaja**-valikosta organisaatio. Tuotesivun tarjoajanimi avaa organisaation tiedot. Haku, tuotesivu ja JSON-/JSON-LD-viennit toimivat edelleen. Varsinaisen vanhan kannan päivitys tapahtuu olemassa olevaan volumeen alla kuvatusti; uusi Codespace todentaa tyhjän kannan polun.

## Vaiheen 1 tietokannan päivitys vaiheeseen 2A

**Älä poista volumea, älä käytä `down -v` / `--volumes` -komentoa päivityksen yhteydessä.** Pysäytä vanha app ennen varmuuskopiota; tietokanta saa jäädä käyntiin. Esimerkiksi paikallisessa Compose-käytössä ota kopio ennen haaran vaihtoa ja uudelleenrakennusta:

```bash
docker compose stop app
docker compose exec -T db sh -c 'pg_dump -U demo -d catalog > /tmp/before-2a.sql'
docker compose cp db:/tmp/before-2a.sql ./before-2a.sql
```

SQL-kopio siirretään tiedostona, joten myös PowerShell säilyttää sen merkistön. Säilytä varmuuskopio turvallisessa paikassa. Vaihda tämän jälkeen kokeiluhaaraan ja rakenna **samassa hakemistossa ja samalla Compose-projektinimellä**:

```bash
git fetch origin
git switch feat/phase-2a-organizations
docker compose up --build -d --wait
docker compose exec -T app .venv/bin/alembic current
```

Odotettu versio on `0002_organizations (head)`. Sovelluksen startup suorittaa migraatiot PostgreSQL-transaktiossa advisory-lukon alla. Sama startup on käytössä Docker Composessa, Codespacesissa ja host-kehityksessä. Jos päivitys epäonnistuu, sovellus ei siirry ready-tilaan eikä aja fixtureitä. Tuntematon/puutteellinen vanha rakenne pysäyttää päivityksen sen sijaan, että sitä leimattaisiin oikeaksi.

- `0001_phase1` kuvaa main-haaran alkuperäiset `products`- ja `demo_initialization`-taulut. Tyhjässä kannassa se luo ne. Vanhan kannan olemassa olevat sarakkeet, tyypit, pääavaimet ja indeksit tarkistetaan ennen käyttöönottoa; tuotteita ei kirjoiteta uudelleen.
- `0002_organizations` luo organisaatiot ja tuotteille pakollisen vierasavaimen `provider_organization_id`. Se säilyttää vanhan UUID:n, tarjoajanimen, kaikki metatiedot ja muokkausajan.
- **Samannimisiä tarjoajia ei yhdistetä.** Jokainen vanha tuote saa oman organisaatiotietueen ja deterministisen UUID:n. `legacyProductId` kertoo alkuperän. Sama nimi voi siis näkyä useita kertoja; valikossa näytetään myös organisaation koko UUID ja maa. Mahdollinen organisaatioiden yhdistäminen vaatii erillisen, tunnisteisiin perustuvan päätöksen.
- Vanhan aineiston maa on `ZZ` (ei tiedossa), tunnisteet `[]`; maata tai virallista tunnistetta ei arvata nimestä. Synteettisyys siirtyy alkuperäisestä metatiedosta, muuten se on `false` eli vahvistamatta. Uuden tyhjän demon kolme organisaatiota ovat synteettisiä, maa `FI` ja tunnistejärjestelmä `demo`.
- Vanhan skeeman olemassaolo merkitään jo alustetuksi myös silloin, kun tuotteet on poistettu tai alustusmerkintä puuttuu. Päivitys tai tavallinen uudelleenkäynnistys ei palauta poistettuja fixtureitä. Vain aidosti uusi kanta siemennetään.

Migraatioiden toistuva ajo on sallittu. Myös käsiajo onnistuu `docker compose exec -T app .venv/bin/alembic upgrade head`. Migraatiot tarvitsevat elävän PostgreSQL-yhteyden, eikä offline-SQL-ajoa tai automaattista downgradea tueta tässä toimituksessa. Vanhaan koodiin palaaminen ei peru päivitystä; tietokannan palautus tehdään hallitusti varmuuskopiosta. Älä palauta kopiota käytössä olevan kannan päälle kokeilun vuoksi.

Codespacesissa **Rebuild Container** rakentaa nykyisen haaran imagen uudelleen ja käynnistää saman migraatiopolun. Pelkkä tiedostojen haaranvaihto ei päivitä jo rakennettua app-imagea. Ota olemassa olevasta Codespaces-kannasta varmuuskopio ennen päivitystä; älä poista codespacea tai volumea tiedot säilyttävässä päivityksessä.

### Organisaatioiden API ja yhteensopivuus

`GET /api/v1/organizations` palauttaa `items`-listan, ja `GET /api/v1/organizations/{uuid}` yhden organisaation. Kentät ovat `id`, `legalName`, `country`, `identifiers` (`scheme`/`value`-parit), `synthetic` ja `legacyProductId`. Tässä vaiheessa organisaatioita vain luetaan; niiden ylläpitoprosessi ei kuulu vaiheeseen 2A.

POST/PUT-tuotepyynnössä annetaan pakollinen `providerOrganizationId`, jonka on viitattava olemassa olevaan organisaatioon. Vanha vapaatekstinen `provider` **ei enää ole kirjoitusparametri**. Tuotteen vastauksissa, haussa ja JSON-viennissä `provider`-nimi säilyy yhteensopivasti, ja mukana on uusi `providerOrganizationId`. JSON-LD:n `dct:publisher` säilyttää tarjoajanimen ja saa organisaation URI-tunnisteen. Nimi synkronoidaan valitusta organisaatiosta tuotetta tallennettaessa.

## Käynnistä Docker Composella

Tarvitset Docker Enginen ja Compose v2:n. Aja repositorion juuresta:

```bash
docker compose up --build -d --wait
curl --fail http://127.0.0.1:8000/health/ready
```

Avaa paikallisella koneellasi `http://localhost:8000`. API-dokumentaatio on polussa `/docs`. Compose sitoo sovelluksen portin 8000 ja PostgreSQL:n portin 5432 vain loopbackiin. Demossa ei ole käyttäjätunnuksia: kaikki paikallisen demon käyttäjät voivat muuttaa kaikkia tuotteita.

Ensimmäinen käynnistys ajaa Alembic-migraatiot ja luo kolme synteettistä tuotetta sekä niiden tarjoajaorganisaatiot: verovelkatiedon, yrityksen perustiedot ja ammattipätevyyden. Tavallinen uudelleenkäynnistys säilyttää lisäykset, muokkaukset ja poistot eikä korvaa sisältöä fixtureillä.

```bash
docker compose logs app
docker compose stop
docker compose up -d --wait
```

Tietokanta on `pgdata`-volumessa. Pelkkä `docker compose down` säilyttää datan. **Vain tarkoituksellinen demodatan nollaus:** `docker compose down -v` poistaa koko tietokantavolumen. Seuraava käynnistys luo alkuperäiset esimerkit uudelleen.

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

POST/PUT-runko noudattaa `/docs`-sopimusta. Fixturestä voit ottaa muut kuvauskentät ilman `id`- ja `provider`-kenttiä; lisää niiden tilalle `providerOrganizationId` organisaatioiden API:n palauttamasta UUID:stä. JSON-LD käyttää DCAT-/Dublin Core -termejä ja selvästi paikallisia demotermejä. **DCAT-AP-vaatimustenmukaisuutta tai SHACL-validointia ei väitetä.** Koko katalogin vienti on tarkoitettu pienelle paikalliselle demolle.

## Testit (vaihe 1 ja 2A)

API-testit käyttävät oikeaa PostgreSQL:ää ja erillistä `catalog_test`-kantaa. Luo kanta kerran:

```bash
docker compose up -d db --wait
docker compose exec -T db createdb -U demo catalog_test
uv sync --locked
.venv/bin/pytest tests/test_api.py tests/test_migrations.py tests/test_public_url.py -q
```

Jos kanta on jo olemassa, älä suorita `createdb`-komentoa uudelleen. API-testit tyhjentävät **vain testikannan** tuotteet ja organisaatiot jokaisen testin jälkeen. Migraatiotestit luovat ja poistavat kaikki testikannan taulut ja estävät muun kantanimen käytön. Ne eivät koske `catalog`-kantaan.

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

Ilman `BROWSER_BASE_URL`-asetusta kolme selaintestiä ohitetaan tarkoituksellisesti; sellainen ajo ei todista käyttöliittymän toimivuutta. Testien tulokset ja rajoitukset ovat `STATUS.md`:ssä. GitHub Actions määrittelee vastaavat API-, selain- ja konttibuild-tarkistukset; etä-CI:n tulos raportoidaan vasta sen ajamisen jälkeen.

