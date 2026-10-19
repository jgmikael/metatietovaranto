# Julkinen staattinen esittelydemo

Tavoiteosoite on **https://jgmikael.github.io/metatietovaranto/**. Tämän työhaaran toteutus ei ole vielä julkinen julkaisu: osoitteen toimivuutta ei väitetä ennen main-julkaisua ja sen oikean HTTP-vastauksen tarkistusta. PR #13:n merge mainiin varmistettiin Gitistä: `6b48536`. Tämä tehtävä on erillinen haara sen päältä.

## Kaksi build-tilaa, sama käyttöliittymä

| Ominaisuus | Tavallinen sovellus | Pages-esittelydemo |
| --- | --- | --- |
| Komponentit, tyypit, ulkoasu, hash-reititys | Yhteiset | Yhteiset |
| Tietolähde | FastAPI, PostgreSQL | Buildin staattinen demo/catalog.json |
| Kirjautuminen/oikeudet | Keycloak ja palvelinistunto | Ei kirjautumista, demotunnuksia tai oikeuksia |
| Luonnokset/hyväksyntä/julkaisut | Varsinainen riippumaton työnkulku | Ei toteuteta; esimerkkiversio ei ole hyväksymispäätös |
| Generointi/validointi | Palvelimen rajattu generaattori ja offline-validointi | Buildin etukäteen muodostamat kuvaukset ja raportit |
| Todistuksen myöntäminen | Ulkoisen myöntäjän vastuulla | Ei myöntämistä, allekirjoitusta tai lompakkotoimitusta |

Vite `--mode pages` valitsee `dataSource.ts`-adapterin ja `/metatietovaranto/`-resurssipolun. Tavallinen build käyttää edelleen nykyistä APIa ja `/`-polkua. Staattinen adapteri hyväksyy vain lukupyynnöt ja tuntee vain esittelyaineiston lukuoperaatiot; se ei lähetä loogisia /api-polkuja HTTP-palvelimelle. /auth/me-kutsua ei tehdä Pages-tilassa. Lomakkeet, kirjautumislinkit, demotunnukset ja ylläpitotoiminnot eivät näy Pagesissa. Myös kirjoituspyynnöt hylätään adapterissa.

Kaikki kolme toimitustapaa ovat **planned**. Metatietojen/artefaktien lataus on kuvausten latausta, ei tietosisällön haku tai todistuksen myöntäminen. Kolme vanhaa fixturetuotetta säilyvät esimerkkeinä ilman keksittyä profiilikytkentää tai uutta pakettia. Neljäs kattava esimerkki näyttää yhteisen SHACL-perustan, W3C-/SD-JWT-/JSON-mappingit, attribuuttiannotaatiot ja teknisen paketin.

## Aineiston alkuperä ja toistettavuus

`fixtures/pages/demo.json` versioi esittelytekstin, esimerkkiversion ja generointivalinnat. Se käyttää vain seuraavia sallittuja versionhallittuja synteettisiä syötteitä:

- `fixtures/products.json`: kolme alkuperäistä synteettistä metatietotuotetta;
- `fixtures/semantic-profile-demo.ttl`, `semantic-example-demo.ttl`, `derived-example-demo.json` ja `distributions-demo.json`: yhteisen yrityssisällön esimerkki;
- nykyisen generaattorin lukitut standardi-/lähdepinnit nykyisen main-toteutuksen mukaisesti.

Rakentaja käyttää samoja ProductWrite-, ProfileInput-, PackageRequest-, SHACL-, JSON Schema-, PyLD-, semanttisen mappingin ja teknisen paketin toimintoja kuin palvelinsovellus. Katalogin JSON-LD-serialisointi on siirretty sellaisenaan yhteiseen tietokannattomaan apumoduuliin. Generaattorin valinnainen `snapshot_url` mahdollistaa oikean staattisen snapshot-osoitteen; osoite kuuluu paketin tarkistettuihin syötteisiin. Oletusarvo ja varsinaisen sovelluksen osoitteet säilyvät.

Rakentaja **ei tuo apps.api.main-moduulia**, avaa tietokantayhteyttä, käynnistä palvelinta, lue .env-tiedostoa eikä vie olemassa olevia julkaisuja/luonnoksia. Organisaatiot muodostetaan vain synteettisistä fixtureistä. Ei istuntoja, tunnuksia, tokeneita, jäsenyyksiä tai auditointitietueita. Staattinen build-testi estää socket-yhteydet ja SQLAlchemy-enginen luonnin.

Uuden synteettisen build-snapshotin artefaktitunnisteet johdetaan SHA:sta UUIDv5:llä; ajokohtaiset acquiredAt/checkedAt-kentät jätetään pois deterministisestä esittelysisällöstä. Aineiston modifiedAt on versionhallittu fixturepäivä, ei ajankohtainen päivitysväite. Alkuperäiset SHACL-tavut ja IRI:t säilyvät. Varsinaisen sovelluksen lukittuja snapshotteja, julkaisuja tai hyväksyntöjä ei muuteta.

`PAGES_PUBLIC_BASE_URL` voi vaihtaa HTTPS-isännän, mutta polku on tässä toteutuksessa `/metatietovaranto`. Oletus on tavoiteosoite. URL muodostetaan **ennen** generointia, joten context/schema/mapping/Type Metadata -viittaukset ja standardin SRI-tarkisteketju vastaavat lopullisia tavuja. Ei jälkikäteistä localhost-korvausta. Alkuperäisiä example.org- ja W3C-IRI:jä ei nimetä uudelleen.

## Build ja paikallinen kokeilu

Tarvitaan Python 3.12, uv 0.12.23, Node 24 ja npm. PostgreSQL:ää, Keycloakia, FastAPI-prosessia tai Codespacea ei tarvita.

```sh
uv sync --locked
npm ci --prefix apps/web
bash scripts/build-pages.sh
uv run --locked python -m scripts.preview_pages --port 4173
```

Paikallisella koneella avattava osoite on `http://127.0.0.1:4173/metatietovaranto/`. Lopetus: Ctrl+C. Palvelin on Pythonin tavallinen staattinen HTTP-palvelin; se ei emuloi APIa.

Windows PowerShellissä build toimii myös ilman Bashia:

```powershell
uv sync --locked
npm ci --prefix apps/web
uv run --locked python -m scripts.build_pages_data
npm run build:pages --prefix apps/web
uv run --locked python -m scripts.preview_pages --port 4173
```

Generoidut tiedostot ovat git-ignoroidussa `.pages-data/`-hakemistossa ja julkaistava valmis sivusto `apps/web/dist-pages/`-hakemistossa. Syötteet ja rakentaja ovat versionhallinnassa; generoituja kuvauksia ei ylläpidetä käsin. Rakentaja hylkää ylimääräiset tiedostot aineistohakemistossa. Workflow lähettää vain dist-pages-hakemiston Pages-artefaktiksi. Tavallinen `npm run build --prefix apps/web` tuottaa edelleen erillisen apps/web/dist-hakemiston.

Suora tuotelinkki käyttää hashia, esimerkiksi `/metatietovaranto/#00000000-0000-4000-8000-000000000004@1.0.0`. Hash ei mene HTTP-palvelimelle, joten uudelleenlataus toimii ilman fallback-palvelua tai 404.html-temppua.

## Koneelliset artefaktit

Paketit löytyvät `id/technical-packages/<pakettitunniste>/`-hakemistosta, esimerkiksi context.jsonld, content.schema.json, sd-jwt-type-metadata.json ja semantic-mapping.json. Ne ovat oikeita tiedostoja ilman hash-reititystä. Profiilisnapshot on demo/profiles/<snapshot>.json ja alkuperäinen SHACL saman snapshotin source.ttl-tiedosto. demo/catalog.json on käyttöliittymän yhteinen aineisto. demo/inventory.json sisältää generoitujen aineistotiedostojen SHA-256:t; manifest.json yksilöi paketin artefaktit ja niiden mediatyypit.

GitHub Pages määrää HTTP-mediatyypit tiedostopäätteen perusteella eikä tue tämän repositorion omia palvelinotsakkeita. Etenkin .schema.json voi saada yleisen application/json-tyypin application/schema+json-tyypin sijaan. Artefaktin ilmoitettu tyyppi on manifestissa; tuotantopalvelun tarkkoja HTTP-mediatyyppitakuita ei väitetä Pagesille. Varsinaisen sovelluksen artefaktiotsakkeet säilyvät. W3C:n alkuperäinen peruskontekstin IRI säilyy esimerkissä; selain ei suorita JSON-LD-prosessointia tai nouda sitä, vaan build käyttää lukittua paikallista lataajaa.

## Julkaisu yhdistämisen jälkeen

1. Yhdistä tarkistettu PR mainiin vasta vihreiden tarkistusten jälkeen.
2. Avaa repositoriossa **Settings → Pages → Build and deployment → Source → GitHub Actions**. Älä valitse Deploy from a branch. Älä muuta repositorion näkyvyyttä tai maksullisia asetuksia tämän työn vuoksi.
3. Avaa **Actions → Public Pages demo → Run workflow**, valitse **main** ja käynnistä ajo. Mainiin yhdistäminen käynnistää saman työnkulun automaattisesti, jos Pages oli jo käytössä. Jos automaattinen ensimmäinen deploy ehti epäonnistua ennen asetusta, käynnistä workflow uudelleen mainista.
4. Jos github-pages-ympäristö pyytää erillistä hyväksyntää, tarkista ja hyväksy GitHubin käyttöliittymässä. Anna vain main-haaran julkaista tähän ympäristöön.
5. Varmista, että build, testit, deploy ja **Verify published HTTP responses** ovat vihreitä. Työnkulku tarkistaa julkaistun HTML:n ja demo/catalog.json-vastauksen. Avaa tämän jälkeen tavoiteosoite ja kokeile tuotelinkkiä, uudelleenlatausta ja context.jsonld-latausta.

PR:n build/test/upload ei julkaise sivustoa. Deploy-jobin ehto estää PR-haarat ja muiden haarojen workflow_dispatch-ajot; vain refs/heads/main voi julkaista. Actions käyttää virallisia configure-pages@v5-, upload-pages-artifact@v3- ja deploy-pages@v4-toimintoja. Build saa contents:read-oikeuden; deploy vain pages:write- ja id-token:write-oikeudet.

**Asetusten tarkistuksen este tässä ympäristössä:** GitHub API:n GET repos/... ja GET repos/.../pages palauttivat Forbidden. Nykyistä Pages-tilaa, näkyvyyttä tai tilauksen tukea ei voitu todeta. Tämä ei todista Pagesin olevan pois käytöstä tai tilauksen olevan riittämätön. Jos GitHub ei tarjoa Pagesin Actions-lähdettä tai ilmoittaa tilaus-/organisaatiopolitiikan rajoituksen, käyttäjän on ratkaistava se repositorion omistajana ennen julkaisua. Tässä ei muuteta maksullisia asetuksia tai luoda uutta julkista repositoriota. Pilviympäristön ”Tallenna ja julkaise” ei julkaise GitHub Pages -sivustoa.

## Tarkistukset

```sh
bash scripts/build-pages.sh
uv run --locked playwright install chromium
uv run --locked pytest tests_static -q
npm run build --prefix apps/web
```

Staattiset testit käyttävät tavallista HTTP-palvelinta aidossa /metatietovaranto/-alipolussa ja hylkäävät selaimen kaikki backend-/ulkoiset verkkopyynnöt. Mukana ovat lista, haku, teema/tarjoaja, mobiilileveys, suora tuoteversiolinkki ja reload, organisaatio, profiili, artefaktilataus, kaikki paketin tarkisteet ja semanttinen kuluttaja. Mukana myös deterministinen offline-build, eri julkaisuosoitteen vaikutus pakettitarkisteeseen sekä credential-/localhost-/tiedostoallowlist-tarkistus. Varsinaisen sovelluksen API-/migraatio- ja Keycloak-selaintestit ajetaan README:n nykyisillä komennoilla erikseen. Toteutuneet tulokset ja ajamattomat tarkistukset ovat STATUSissa.
