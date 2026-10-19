## Muutos ja käyttäjän polku

Pagesin Oma kokeilu pystyi aiemmin valitsemaan vain mukana toimitetun profiilin. Nyt käyttäjä voi tuoda Tietomallit-työkalusta ladatun UTF-8 Turtle -tiedoston sekä tarvittavat paikalliset Turtle-riippuvuudet, tarkastella muotoja/ominaisuuksia/nimiavaruuksia/importteja, valita juuren ja tarkastaa yhteiset JSON-kenttänimet. Tarkastettujen esitys- ja planned-toimitustapavalintojen perusteella Web Worker muodostaa paikallisen kuvauspaketin. Ei kirjautumista, APIa, PostgreSQL:ää, Keycloakia, verkkotuontia tai käyttäjän aineiston lähettämistä verkkoon.

Pohja on ajantasainen main `f1f4de6`, PR #15 yhdistetty. Nykyinen julkinen esittely sekä palvelinsovelluksen generaattori, oikeudet, riippumaton hyväksyntä, muuttumattomat julkaisut ja Private-Codespaces säilyvät. Ei tietokantaskeeman tai aiempien snapshot-/julkaisusisältöjen muutoksia. Tätä PR:ää ei yhdistetä automaattisesti.

## Generointi ja paikallisen paketin tila

N3.js 2.13.12, Ajv 8.20.0 ja jsonld.js 9.0.0 ovat lukittuina npm-lockissa. Palvelimesta johdettu contract.json lukitsee SHACL-profiilin, varatut nimet, tietotyypit, semanttisen laajennuksen ja alkuperäiset standardilähteet. Selainversion tunniste on browser-technical-package/1.0.0. SD-JWT-profiili on edelleen **draft-ietf-oauth-sd-jwt-vc-19**, ei RFC.

Tuettu rakenne: yksi eksplisiittinen juuri/kohdeluokka, suorat ominaisuus-IRI:t, eksplisiittiset tuetut XSD-literaalit, yksiselitteiset syklittömät sisäkkäiset oliot, min/max ja järjestyksettömät taulukot. Deterministinen nimeäminen ja tarkastetut nimet; tyyppejä/kardinaliteetteja ei voi korvata rinnakkaisella mallilla. Suljetut muodot ja sh:ignoredProperties jäävät selainversion ulkopuolelle. Date/dateTime-esimerkin tarkka leksikaalinen tarkistus ei ole toteutettu: tällainen esimerkki estää generoinnin, ei hiljaista string-muunnosta. JSON-kokonaislukujen on oltava JS:n tarkasti esitettävissä.

Tulokset: JSON Schema + x-term/x-mtv-shacl, W3C:n scoped JSON-LD-konteksti, SD-JWT Type Metadata + x-mtv-semantic, yhteiset ja muotokohtaiset mappingit, laajennusprofiili, vct#integrity-kuvaus, synteettiset allekirjoittamattomat esimerkit, RDF-esimerkki, alkuperäiset lähteet, tarkistusraportti ja manifesti. SHACL-validointi ja selaimen graafivertailu ovat **not-run**. Ei hyväksyntää, oikeaa julkaisua, allekirjoituksia, disclosureja tai lompakkotoimitusta.

Käyttäjän antamat HTTPS-osoitteet ovat **suunniteltuja, eivät julkaistuja tai HTTP-varmennettuja**. Pages-demon isäntää ei hyväksytä käyttäjäaineiston julkaisuperustaksi. Blob on vain tiedostolatauksen väliaikainen osoite. Tarkisteketju perustuu lopullisiin UTF-8-tavuihin; osoitteen muuttaminen vaatii uuden paketin. Alkuperäisen esittelypaketin raportit säilyvät erillisenä lähtöesimerkkinä.

Tiedostoja enintään 10 / yhteensä 256 KiB, jäsennettyjä kolmikoita enintään 10 000, puun syvyys 8 / kenttiä 200, esimerkki 100 kB / 20 tasoa / 2 000 arvoa, Worker 15 s + keskeytys. Raja pysäyttää quadien muodostamisen ennen suuren kolmikkolistan kertymistä. Mielivaltaisia konteksteja tai RDF-riippuvuuksia ei haeta; profiilin SPARQLia/JS:ää ei suoriteta. Ulkoinen OWL-ominaisuus ei vaadi koko sanastoa; ratkaisematon tarvittava sh:node estää kyseisen generoinnin.

Oma kokeilu -formaatti 1 säilyttää taaksepäin luettavuuden valinnaisilla localProfiles/generation-kentillä. Lähteet palautuvat kokeilun JSONista eikä File/blob-viitteitä tallenneta. Uudelleenavaus ja tuonti tarkistavat hashit Workerissa. Sama 2 MiB kokonaisraja, kiintiö-/välilehtisuoja ja atominen vahvistettu tuonti säilyvät. Lähteen, juuren, mappingin, asetusten, metadatan tai generaattorisopimuksen muutos vanhentaa paketin; vanha paketti säilyy ladattavana. Tuotteen mappingeja ei ylikirjoiteta generoinnissa.

## Konkreettinen ketju

`fixtures/semantic-profile-demo.ttl` (synteettinen ohjelmistofixture) → `https://example.org/metatietovaranto/demo/ProductShape` → tarkastettu `companyName` / alkuperäinen ominaisuus-IRI → yhteinen mapping → context.jsonld, content.schema.json ja sd-jwt-type-metadata.json → `{"companyName":"Synteettinen selain Oy"}` → paikallinen ladattava paketti.

Sisäkkäinen `fixtures/browser-generation/tree.ttl` käyttää kansallista mallinimiavaruutta ja ulkoisia ominaisuuksia. Samannimiset `city`-kentät kahdessa osoiteroolissa, monikieliset näyttönimet, nimetön PropertyShape sekä sisäkkäiset taulukot vastaavat palvelingeneraattorin vertailua. Oikean JSON-LD-prosessorin RDF vastaa käsin laadittua odotettua graafia. Pakettia **ei julkaista** tämän ketjun seurauksena.

## Todella ajetut tarkistukset

- `bash scripts/build-pages.sh` sekä lopullinen `npm run build:pages --prefix apps/web`: läpäisivät. Normaali `npm run build --prefix apps/web`: läpäisi. Worker on erillinen paikallinen bundle; normaali pääbundle ei sisällä paikallisen generoinnin UI:ta tai worker-kutsua.
- `pytest tests_static -q`: **56 passed in 120.75s**, ei ohituksia. Todellinen staattinen `/metatietovaranto/`-HTTP-palvelin, taustapalvelut/ulkoiset ja kirjoituspyynnöt kielletty, ei JavaScript-/konsolivirheitä. Tuonti, generointi, lataus, reload, lähteiden/paketin vienti ja palautus, hashivirheen atominen hylkäys, vanheneminen, syntaksi/tukirajoitteet, paikallinen riippuvuus, OWL-viitteiden erottelu, aikaraja/keskeytys sekä koko aiempi Oma kokeilu / julkinen esittely.
- Samat selaintestit tarkistavat determinismin ja palvelimen inspect_profile/context_for/schema_for/generate-vertailun, SRI-ketjun ja muutoshavainnon. **Oikea erillinen PyLD**, lukittu lataaja, käsin kirjoitettu odotettu RDF, jsonld.js:n graafi ja offline-lähde-SHACL läpäisivät. Testiajon SHACL-tulosta ei väitetä selaimen toiminnoksi.
- Muuttamaton **WE BUILD Certificate of Residence 0.0.2**, alkuperäinen SHA `2ad4331272558bb541b7804f194a74e261d8313985554015ccc4e23785286133`: jäsentyi, alkuperäiset muodot/IRI:t tarkasteltavissa. Kokonaiset juuret ylittivät tuen (erityisesti puuttuvat eksplisiittiset literaalityypit / tukemattomat rajoitteet). Erikseen merkitty suppea testiprojektio toimii; alkuperäistä ei muutettu tai väitetty kokonaan tuetuksi. Riippumatonta verkkovarmennusta ei tehty.
- README:n koko 13 tiedoston API-/PostgreSQL-/migraatiosarja: **209 passed, 4 warnings in 405.87s**. Erillinen catalog_test; oikeudet, CSRF, hyväksyntä/julkaisu, vanhat/tyhjät kannat, toistuvat migraatiot sekä nykyiset SHACL-/paketti-/attribuuttikokeet.
- Docker-build/startup läpäisi; kaikki palvelut healthy. Ennen/jälkeen uudelleenkäynnistyksen **13 catalog-taulun rivit/tavutarkisteet ja Alembic head säilyivät ennallaan**, ei volumejen poistoa.
- Uudelleenrakennettu palvelinsovellus, oikea Chromium/Keycloak: **13 passed, 1 warning in 134.78s**. Oikeudet, tallennus/uudelleenavaaminen, hyväksyntä/julkaisu, elinkaari ja tekniset artefaktit. **278 eri pytest-testiä**, ei ohituksia. Varoitukset ovat Starlette/httpx ja RDFLib.
- Vanhojen julkaisujen HTTP-koe: **103 versiota, 8 vanhaa pakettia, 78 artefaktia** luettavissa alkuperäisinä tavuina. Selaintestit jättävät omat synteettiset julkaisut historiaan, alkuperäisiä fixturetuotteita ei muutettu.
- Paikallinen dokumentoitu preview: oikea käyttöliittymän tuonti/generointi, desktop-näkymä ja 390 px leveys tarkistettu ilman JS-virheitä. `git diff --check` läpäisi.

## Rajat ja ajamatta jäänyt

Ei Windows-/Firefox-/Safari-ajoa, oikeaa julkista Pages-deployta tai uuden version julkista HTTP-varmistusta. GitHubin PR-CI:n etätulos on varmistettava erikseen. Worker-aikaraja/keskeytys testattiin deterministisesti pysäytetyllä testityöntekijällä; erillistä käyttöjärjestelmän muistikiintiötä ei luvata. Koko kokeilun 2 MiB raja voi estää suuren profiilin johdannaisten tallentamisen: virhe ei korvaa aiempaa kokeilua. Ei uusia myöntäjä-/lompakkointegraatioita tai standardienmukaisuusväitteitä.

## Kokeilu ennen yhdistämistä ja käyttöönotto

Paikallinen staattinen kokeilu ilman taustapalveluja: vaihda tähän haaraan, `uv sync --locked`, `npm ci --prefix apps/web`, `bash scripts/build-pages.sh`, `uv run --locked python -m scripts.preview_pages --port 4173`. Avaa `http://127.0.0.1:4173/metatietovaranto/`. Windows PowerShellissä rakentamisen korvaavat `uv run --locked python -m scripts.build_pages_data` ja `npm run build:pages --prefix apps/web`.

Yhdistämisen jälkeen nykyinen **Public Pages demo** julkaisee mainin. Ei uusia pilviresursseja tai Pages-asetuksia. Tarkista vihreä build/deploy ja Verify published HTTP responses ennen osoitteen ilmoittamista uuden version toimivaksi. Julkisessa sivustossa Aloita oma kokeilu → paikallinen tuote → SHACL-tiedosto.

Tarkka sopimus: `docs/browser-shacl-generation.md`. Lähteet ja geneeriset testifixturet ovat versiohallittuja; käyttäjätietokantaa ei viedä Pagesiin.
