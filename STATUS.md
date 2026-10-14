# Vaiheen 1 tila

Tarkistettu 14.10.2026. Työhaara: `feat/phase-1-local-demo`. Tavoitearkkitehtuuri säilyy alkuperäisessä suunnitteludokumentissa; tämän toimituksen rajaus on ROADMAPin vaihe 1.

## Windows / Docker Desktop -toimituksen lisätodennus

README sisältää nyt PowerShell-ohjeet: Docker Desktopin Linux containers / WSL 2, demohaaran kloonaus, `docker compose up --build`, selainosoite `http://localhost:8000/`, tunnukset, pysäytys ja lähtötilanteen palautus. Windowsiin ei tarvita erillisiä Python-/Node-asennuksia. Kolme synteettistä tuotetta olivat jo fixture-tiedostossa; niitä ei monistettu.

**Todella ajetut kokeet tässä Linux-ympäristössä (Docker Compose 2.40.3, linux/amd64):**

1. Ajoin `docker compose up --build` erillisellä projektinimellä `metatietovaranto-windows-check`. Ilman pilven build-verkon lisäasetuksia käännös pysähtyi `Temporary failure in name resolution` -virheeseen Python-riippuvuuksien latauksessa. Tätä ajoa ei lasketa onnistuneeksi käynnistykseksi. Ennen tämän virheen selvittämistä käynnistetty testiajo tuotti 7 DB-yhteysvirhettä ja 2 selainyhteysvirhettä, koska palvelut eivät olleet käynnistyneet.
2. Ajoin saman `docker compose up --build` -komennon uudelleen. Tässä ajossa `COMPOSE_FILE` yhdisti alkuperäisen compose.yaml-tiedoston ja paikallisen `/tmp/metatietovaranto-compose-cloud.yaml`-lisäasetuksen, joka välitti **vain buildille** pilven host-verkon, proxyosoitteen, proxy-build-argumentit ja CA-varmenteen. Projektinimi ja Dockerin kirjoitettava asetushakemisto annettiin ympäristömuuttujina. Lisätiedosto ei kuulu Windows-jakeluun eikä sitä tarvita normaalissa Docker Desktop -verkossa. TLS-tarkistusta ei poistettu. Build käytti myös olemassa olevaa välimuistia; täysin tyhjää build-välimuistia ei testattu.
3. Tyhjään testiprojektin volumeen käynnistyivät app ja db, molemmat healthy. Readiness palautti PostgreSQL-ready-tilan ja haussa oli täsmälleen kolme synteettistä tuotetta.
4. Ajoin käynnissä olevaa Compose-demoa vasten `BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest -q`: **9 läpäissyttä, 0 epäonnistunutta, 0 ohitettua** (7 API/PostgreSQL/RDF + 2 Chromium). Samat kolme kirjastojen deprekaatiovaroitusta kuin aiemmin. Testikanta luotiin tähän testiprojektiin erikseen.
5. Lisäsin synteettisen palautuskoetuotteen API:lla: tuotteita oli neljä. Ajoin `docker compose down` ja `docker compose up -d --wait`; kaikki neljä tuotetta säilyivät.
6. Ajoin **vain erilliselle testiprojektille** `docker compose down --volumes` ja uudelleen `docker compose up --build` samoilla pilven build-lisäasetuksilla. Varmistin API:sta täsmälleen kolme alkuperäistä fixtureä ja vertasin jokaisen tallennetun kuvauskentän fixture-tiedostoon. Alkuperäisen kehitysprojektin volumea ei poistettu.
7. Ctrl+C lähetettiin pilven PTY-istunnolle; CLI-istunto päättyi, mutta kontit jäivät tässä runnerissa käyntiin. Siksi Ctrl+C-pysäytyksen toimintaa PowerShellissä ei lasketa varmennetuksi. `docker compose down` pysäytti ja poisti testiprojektin kontit onnistuneesti.

**Ei varmennettu:** aito Windows/Docker Desktop/WSL 2 -ajo, PowerShellin Ctrl+C-signaalinkäsittely, ensimmäinen build täysin ilman välimuistia, käyttäjän koneen portit/palomuuri/proxy ja GitHub Actions -etäajo. Oletus-Composen verkkoriippuvuuksien latausta ei saatu toimimaan tämän pilven rajoitetussa build-verkossa ilman lisäasetuksia. Onnistunut pilviajo ei ole väite Windows-testistä.

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
