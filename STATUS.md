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

