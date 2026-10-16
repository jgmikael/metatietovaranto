# Vaihe 2F — hallittu synteettisen JSON-sisällön RDF-esikatselu

Tarkistettu 16.10.2026. Käyttäjä yhdisti 2E:n PR #9:llä; pohjana main `feca7b8`. Työhaara `feat/phase-2f-json-rdf`. ROADMAP ei nimennyt seuraavaa osatehtävää, joten ennen toteutusta rajattiin hallittu JSON → RDF -muunnos paikalliseksi valmisteluksi. Suunnitelma ja täsmällinen muunnossopimus: [docs/phase-2f.md](docs/phase-2f.md). Vaiheeseen 3 ei siirrytty. Main-haaraan ei yhdistetä automaattisesti.

## Toteutettu

- Editorin yksityinen muunnoslaboratorio luonnossivulla ja POST `/api/v1/drafts/{draftId}/conversion-preview`. Oikea istunto, omistajaorganisaation editor-jäsenyys, CSRF ja If-Match. Kokeilu ei muuta luonnosta, hyväksyntää, auditointisisältöä tai julkaisuja eikä tallenna syötteitä/raporttia.
- Tallennetun luonnoksen toimitustapamappingit ja yhteinen lukittu SHACL-snapshot. JSON API -sisältöolio, W3C:n sisältöpolun mukainen olio ja SD-JWT:n erillinen synteettinen väiteolio. Ei JWT:n purkamista tai kokonaisen todistuksen käsittelyä.
- Yksi juuriluokka, eksplisiittiset IRI-ominaisuuspolut, sisäkkäiset oliot ja vanhempaansa kohdistuvat taulukkoalkiot. Eksplisiittiset XSD-literaalit; decimal tarkkana merkkijonona. Anonyymit RDF-solmut eivät keksi liiketoimintatunnisteita. Null, ylimääräinen kenttä, ristiriitainen mapping, häviävä toistuva literaali tai tukematon rakenne estää onnistumisen.
- JSON API:n liitettyjen alkuperäisen dialektin JSON Schema/OpenAPI -skeemojen rakenne-/sisältötarkistus, hallittu muunnos ja 2D:n SHACL Core erillisinä tuloksina. Vähintään kahden onnistuneen esimerkin RDF-graafien isomorfinen vertailu. Samuus koskee järjestyksettömiä RDF-ominaisuuksia, ei OWL-ekvivalenssia tai yleistä literaalien arvonormalisointia.
- Raportin sidonta luonnoksen revisioon/tarkisteeseen, profiilin UUID/SHA-256:een ja mappingien versioihin/tarkisteisiin sekä syötteiden tarkisteisiin. Raporttia ei hyväksytä asiakkaan asettamaksi julkaisutodisteeksi. Nykyiset 2D/2E-julkaisuehdot säilyvät.
- Verkoton aliprosessi: CPU 5 s, muisti 512 MiB, seinäkello 15 s. 1–3 esimerkkiä, UTF-8 100 kB per sisältö / 200 kB yhteensä, JSON syvyys 20 / solmut 5 000, RDF 2 000 kolmikkoa. Myös raskaan SHACL-regexin oikea prosessirajan testi.
- Selainlomake, synteettisyysvahvistus, valmiin neljännen demon täyttö, eri/virheellisten sisältöjen näyttö, RDF-teksti ja tarkisteet. Muutos tyhjentää vanhan tuloksen ja vahvistuksen. Sivun lataus tyhjentää kokeilun.
- README, ROADMAP, AGENTS, arkkitehtuuri, verkkodemo, 2E-jatkorajaus ja tavoitearkkitehtuurin täsmennys päivitetty. CI:n API-testilistaan lisätty muunnostestit.
- Ei relaatiomigraatiota tai fixtures-muutosta. .devcontainer ja aiemmat migraatiot säilyvät ennallaan. Private-portin ohje ja automaattinen openBrowser säilyvät.

## Tässä tehtävässä todella ajettu

- `UV_CACHE_DIR=/workspace/.cache/uv uv sync --locked`: lukittu asennus onnistui; uusia riippuvuuksia ei lisätty.
- `npm run build --prefix apps/web`: lopullinen TypeScript/Vite-build läpäisi. `./scripts/cloud-build.sh`: lopullinen Docker-build läpäisi pilven proxy-/CA-reitillä. `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app/db/keycloak healthy nykyisillä volyymeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_derived_validation.py tests/test_distributions.py tests/test_conversion.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **127 läpäissyttä**, 0 epäonnistunutta/ohitettua, 266,48 s. Tässä kokoelmassa muunnostestejä oli 37. Aiemmat 90 API-/auth-/julkaisu-/semantiikka-/migraatiotestiä säilyivät.
- Viimeisen aikaleimarajauksen ja kolmen uuden reunatapauksen jälkeen `.venv/bin/pytest tests/test_conversion.py -q`: **40 läpäissyttä**, 0 epäonnistunutta/ohitettua, 52,72 s. Tämä on lopullisen muunnostoteutuksen koko testitiedosto. Laajaa kokoelmaa ja kohdistettua uusinta-ajoa ei ajettu samanaikaisesti samaan catalog_test-kantaan.
- API-puolella yhteensä **130 erilaista testiä** (90 aiempaa + 40 uutta), ei 167. Testattu saman/eri sisällön vertailu, sisäkkäisten taulukko-olioiden korrelaatio, järjestys, eksplisiittiset tyypit ja tarkka decimal, aikaleimarajat, null/puuttuvat/ylimääräiset kentät, häviävät toistot, väärät juuret/mappingit, JSON Schema vs SHACL-koodisto, disclosure-/todistusmateriaalin kielto, resurssiraja, oikeudet/CSRF/If-Match, vanha julkaisu ja esikatselun tallentamattomuus.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: lopullista Docker-imagea vasten **10 läpäissyttä**, 0 epäonnistunutta/ohitettua, 71,38 s. Oikea Chromium/Keycloak; aiemmat yhdeksän polkua ja uusi kolme samaa sisältöä → eri sisältö → null-hylkäys → luonnos ennallaan → uudelleenlataus tyhjentää kokeilun.
- Yhteensä **140 erilaista testiä** läpäisi. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia. Ei suorituskyky-/kuormitusmittaus.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.` Tyhjän ja vanhan muokatun kannan sekä toistuvien migraatioiden säilymistestit läpäisivät osana laajaa ajoa.
- Katalogirivien määrät ja koko sisältö tarkistettiin ennen/jälkeen imagen päivityksen ja tavallisen restartin SHA-256:lla. Viimeisessä tarkistuksessa ennallaan: 24 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 16 profiilisnapshotia, 17 julkaisua/tarkastusta/outboxia ja 116 audit-tapahtumaa. Selainajojen omat synteettiset julkaisut jäävät muuttumattomaan historiaan. Tuotteita, oikeuksia tai volyymeja ei nollattu.
- Kaikkien nykyisten 17 julkaisuversion sisältö vastaa tallennettua SHA-256:ta ja version API palauttaa täsmälleen saman JSON-sisällön. Vanhoja julkaisuja ei kirjoitettu uudelleen.
- Codespacesin yhdistetty Compose tarkistettu synteettisellä CODESPACE_NAME-arvolla: Keycloak saman HTTPS-portin 8000 /identity-polussa, workspace service:app-verkossa ja openBrowser. Migrations- ja .devcontainer-diff tyhjä. `git diff --check` läpäisi.

Kehityksessä korjattiin kaksi uuden testiaineiston ongelmaa (SHACL-koodistorajoitteen sijoitus ja julkaisun jälkeen vanhentunut ETag). Kohdistettu korjausajo läpäisi. Viimeisen buildin ensimmäinen yritys epäonnistui ENOSPC-levytilaan. Poistettiin vain käyttämätöntä Dockerin build-välimuistia ja irrallisia imageja, jolloin vapautui noin 6,6 Gt; tietokantavolyymeihin ei koskettu. Tämän jälkeen lopullinen web-/Docker-build, käynnistys, säilyvyystarkistus ja selaintestit läpäisivät.

## Ajamattomat ja rajat

- Windows/Docker Desktop, tavallinen `docker compose up --build` ilman pilven build-wrapperia, oikea GitHub Codespace/Private-portin pääsynvalvonta/automaattinen välilehti ja GitHub Actions -etäajo jäivät ajamatta. Staattinen määritystarkistus ei todista näitä.
- Ei elävän Tietomallit-palvelun hakua, oikeaa lähde-APIa tai issuer-/wallet-integraatiota. Ei VC-kuoren rakennetarkistusta, JSON-LD-kontekstin laajennusta, SD-JWT-profiilin purkua/disclosurejen todennusta, kryptografiaa tai luottamus-/haltijasidontatarkistusta.
- Ei monijuurisia/rekursiivisia profiileja, RDF-listojen järjestystä, IRI-viitearvoja, kielitunnisteita tai liiketoimintaidentiteettien yhdistämistä. Ne saavat hylkäyksen/arvioimatta-tuloksen. Tuetut tyypit ja tarkkuusrajat on dokumentoitu phase-2f.md:ssä.
- Ei QEAA-, DCAT-AP-, EUDIW-/EBW-, tuotantoturvallisuus-, kuormitus- tai saavutettavuusvaatimustenmukaisuuden väitettä. Synteettisyys perustuu käyttäjän vahvistukseen. Kokeilun läpäisy ei ole julkaisuun tallennettu hyväksymisraportti.

## Toimitus

Työhaara `feat/phase-2f-json-rdf`; valmis PR-kuvaus docs/pull-request.md. PR-avaamisen tulos kirjataan toimituksen lopuksi. Main-haaraan ei yhdistetä automaattisesti.

---

# Aikaisemmat toimitukset (historia, eivät tämän ajon tuloksia)

# Vaihe 2E — rinnakkaiset toimitustavat ja versioidut mappingit

Pohjana yhdistetty main `5611be2` (PR #8 / 2D). Työhaara `feat/phase-2e-derived-validation`. Käyttäjän täsmennetty 2E-suunnitelma esitettiin ensin ja toteutettiin sen jälkeen. Main-haaraan ei yhdistetä automaattisesti. Alla olevat 2D/2C-toimitusten tulokset ovat historiaa.

## Muutos aiempaan suunnitelmaan ja toteutus

- Aiempi 2E-suunnitelma keskittyi JSON Schema/OpenAPI -johdannaisten tarkistuksiin. Käyttäjän täsmennyksen jälkeen pääkohteeksi tuli yksi tietotuote ja kolme tyypitettyä rinnakkaista toimitustapaa: JSON API, W3C VCDM 2.0 JSON-LD VC ja IETF SD-JWT VC. Johdannaistarkistus säilyi erillisenä, rajattuna lisätarkistuksena.
- Distributions erottaa formaatin, protokollan, suojausprofiilin, saatavuuden, ympäristön, vastuuorganisaatiot ja yhteisen profiiliviitteen. W3C VC on oletuksena ensisijainen, kun se on mukana; eksplisiittinen primaryDistributionId tuetaan API:ssa ja käyttöliittymässä.
- JSON API sisältää palvelun ja kuvauksen osoitteet, OpenAPI-/JSON Schema -artefaktiviitteet, tyypitetyn tunnistautumistavan, oikeudet ja ajantasaisuuden. Todistusjakeluilla ovat issuer/aloituslinkki, OpenID4VCI 1.0, erilliset configuration-tunnisteet, suojaus/voimassaolo/status-profiilit, kohdeluokat/edustaminen, maksu, tuki, oikeudellinen luokka ja lompakkonäyttö.
- W3C VC:llä ovat VCDM 2.0, tyypit, kontekstit ja sisältöpolku. SD-JWT VC:llä ovat vct, profiiliversio, erillinen väitemapping sekä paljastamis- ja haltijasidontakäytännöt. SD-JWT:hen ei vaadita JSON-LD-kontekstia eikä sitä esitetä W3C VC:n samana kuorena.
- Sama myöntäjäpalvelu voi tarjota molempia todistusmuotoja erillisillä konfiguraatioilla ja käyttää samaa lähde-APIa/sovitinta. Katalogi kuvaa ja ohjaa; sen metatietovienti ei ole lähdesisällön jakelurajapinta. Uusia lähdeintegraatioita, allekirjoituksia tai lompakkoprotokollaa ei toteutettu.
- Kaikki toimitustavat sidotaan julkaistun tuoteversion samaan SHACL-snapshotiin. DistributionBindings sisältää tuotteen version, yhteisen snapshotin UUID/SHA-256:n ja mappingin version. Muuttunutta mappingia ei julkaista saman toimitustapa-ID:n vanhalla mapping-versiolla eikä versionumeroa alenneta.
- Metadata-/mapping-tarkistus vertaa alkuperäisiä IRI-polkuja, sisäkkäisiä olioita, literaalien tietotyyppejä, luokkia ja min/maxCountia. Moniarvoisuus kuvataan /*-poluilla ja lapset oliovanhemman alle. Puuttuvat/ristiriitaiset/epäselvät mappingit, väärät skeemaviitteet tai JSON API:n skeemasta puuttuvat polut estävät uuden julkaisun.
- 2D:n erillinen SHACL-esimerkki ja hyväksyntä säilyvät. DistributionValidation ja rajattu DerivedValidation kuuluvat sisältötarkisteeseen, erilliseen hyväksyntään ja muuttumattomaan versioon. Metadata, semanttinen esimerkki ja kryptografinen tarkistus erotetaan näkyvästi.
- JSON Schema tukee alkuperäisiä draft 4/6/7/2019-09/2020-12-dialekteja, OpenAPI 3.0.x/3.1.x-versioita. Rajattu suora kenttävertailu ei väitä mallien ekvivalenssia eikä korvaa toimitustapojen sisäkkäistä metadataa. JSON-esimerkit ovat synteettisiä. Viitteitä ei noudeta ulkoisista lähteistä, prosessit ovat resurssirajattuja ja verkottomia.
- Rakenteiset muokkauslomakkeet ja erilliset tuotesivutoiminnot. Planned/suspended ei saa aktiivista palvelutoimintoa. Muotokohtaiset toimintotekstit ovat Käytä JSON-rajapintaa / Tutustu rajapintakuvaukseen / Pyydä W3C VC lompakkoon / Pyydä SD-JWT VC lompakkoon.
- Neljäs synteettinen esimerkki, jossa kaikki kolme ovat planned, lisätään kerran tunnettuun synteettiseen tuote–organisaatio-pariin. UUID-kollisiota, käyttäjän muokkauksia tai poistettua esimerkkiä ei palauteta alkuperäisiksi. Muita organisaatioita ei yhdistetä tai oikeuteta nimen perusteella.
- Vanha issuance-luku ja vanhojen luonnosten kirjoitus säilyvät. Uuden kokoelman hiljainen pudottaminen vanhaan malliin estetään. Jo julkaistuja versioita ja snapshotteja ei kirjoiteta uudelleen. Ei uutta relaatiomigraatiota; head on edelleen 0004_publication.
- ROADMAP, AGENTS, README, verkkodemon/arkkitehtuurin ohjeet, tavoitearkkitehtuuri ja VC-periaate päivitetty. Täsmällinen ratkaisu ja integraatiovaiheen hyväksymiskriteerit: docs/phase-2e.md. Codespacesin määrityksiin ei tehty muutoksia; portti 8000 / openBrowser / Private-ohje säilyvät.

## Tässä tehtävässä todella ajettu

- Lukittu uv-asennus: jsonschema 4.26.0, openapi-spec-validator 0.7.2 ja openapi-schema-validator 0.6.3 sekä niiden riippuvuudet. `UV_CACHE_DIR=/workspace/.cache/uv uv sync --locked` onnistui.
- `npm run build --prefix apps/web`: TypeScript ja Vite-tuotantobuild onnistuivat. `./scripts/cloud-build.sh` rakensi Docker-imagen pilven proxy-/CA-reitillä TLS-tarkistuksia säilyttäen. `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app/db/keycloak healthy samoilla voluumeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_derived_validation.py tests/test_distributions.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **90 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**, lopullinen ajo 211,99 s. Yksi tyhjentävää catalog_test-kantaa käyttävä pytest-ajo kerrallaan.
- Aiemmat 55 API-/auth-/SHACL-/migraatio-/osoitetestiä säilyivät. Lisäksi 18 johdannais- ja 17 toimitustapatestiä: alkuperäiset skeemadialektit, local-ref/OpenAPI/nullable, puuttuvat ja ristiriitaiset kentät, koodistot/taulukot, token-/salaisuusparametrien kielto, kolme muotoa, sama profiili, erilliset konfiguraatiot, sisäkkäiset mappingit, uusi mapping-versio, vanhat muuttumattomat versiot sekä fixtureiden muokkauksen/poiston säilyminen.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **9 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**, lopullinen ajo 55,50 s. Oikea Chromium ja Keycloak: aiemmat seitsemän polkua, JSON-johdannaisen tiedostotuonti/virhe/korjaus/hyväksyntä/julkaisu sekä kolmen toimitustavan muokkaus, eri käyttäjän hyväksyntä, planned-julkaisu ja anonyymi näyttö.
- Aktiivisten muotokohtaisten linkkien renderöinti tarkistettiin selaimessa korvatulla API-vastauksella. Tätä vastausta ei tallennettu katalogiin eikä palvelulinkkejä avattu. Aktiivisen metadatan oikeat backend-ehdot tarkistettiin erillisessä catalog_test-kannassa. Katalogiin jäävät selaintestijulkaisut ovat synteettisiä ja palvelukuvaukset planned-tilassa.
- Yhteensä **99 eri testiä** läpäisi. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia. Kyse on oikeellisuustesteistä, ei latenssi-/kuormitustavoitteen todennuksesta. Selainodotus sallii usean erillisen rajatun validointiprosessin vaatiman ajan.
- Olemassa olevasta demokannasta tarkistettiin neljä aitoa ennen 2E:tä julkaistua versiota. Niiden koko sisältö vastaa alkuperäistä SHA-256:ta ja versio-API palauttaa saman sisällön/UUID:n/version/tarkisteen. Vanhoja julkaisuja ei muutettu.
- Vanhojen vaiheiden 1/2A/2B kantojen migraatio-, alkuperäisten rivien säilymis- ja toistuvien käynnistysten testit läpäisivät. Käyttäjän nyt erikseen tilaama neljäs fixture on lisäys, ei alkuperäisten tuotteiden nollaus.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.` Migrations- ja .devcontainer-diff on tyhjä.
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: Keycloak samalla HTTPS-portin 8000 osoitteella, workspace service:app-verkossa ja openBrowser ennallaan.
- `git diff --check` läpäisi. Tavallinen app-restart ja Compose-readiness läpäisivät. Ennen/jälkeen kaikkien tarkistettujen katalogirivien sisältö/tarkiste säilyi: 18 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 12 profiilisnapshotia, 11 julkaisua/tarkastusta/outboxia ja 80 audit-tapahtumaa. Testien omat synteettiset julkaisut ja keskeneräiset kehitysluonnokset jäivät historiaan; alkuperäisiä tuotteita tai volumeita ei poistettu.

Kehitysajoissa korjattiin vanhimmasta demokannasta puuttuvien maa-/organisaatiotunnisteiden vaikutus uuden fixturen lisäämiseen. Luotettava tunnistus käyttää tunnettua UUID-paria ja synteettisyyttä. Tässä kehitysympäristössä poistettiin kerran vain uuden, epäonnistuneen alustuskokeen oma phase-2e-distribution-demo-merkintä, kun ensin varmistettiin ettei neljättä tuotetta ollut luotu. Tuotteita, julkaisuja tai volumeita ei poistettu. Lisäksi selainkokeen viiden sekunnin odotus oli liian lyhyt usealle peräkkäiselle rajatulle validoinnille; odotus korjattiin ja käyttöliittymä näyttää käsittelyn olevan kesken. Lopulliset yllä raportoidut ajot läpäisivät.

## Ajamattomat ja jatkovaiheen rajat

- Windows/Docker Desktop, tavallinen `docker compose up --build` ilman pilven build-wrapperia, oikea GitHub Codespace/Private-portin pääsynvalvonta/automaattinen selainvälilehti ja GitHub Actions -etäajo jäivät ajamatta. Staattinen määritystarkistus ei todista näitä.
- Ei elävän Tietomallit-palvelun hakua, lähde-APIa, oikeaa issuer-palvelua, todistusten muodostusta/allekirjoitusta, JWT:n tai haltijasidonnan kryptografista tarkistusta, OpenID4VCI/lompakkotoimitusta tai EUDIW-/EBW-yhteentoimivuuskoetta.
- Tässä ei muunneta JSON-/purettuja VC-sisältöjä RDF:ksi eikä anneta JWT-merkkijonoa SHACL-moottorille. Hallittu muunnos ja saman sisällön vertailu kaikissa kolmessa muodossa ovat integraatiovaiheen hyväksymiskriteeri, eivät ajettu ominaisuus.
- Mapping-profiili tukee yksiselitteisiä sisäkkäisiä sh:node/sh:class-polkuja, ei rekursiivisia tai mielivaltaisia SHACL-polkulausekkeita. Johdannaisten suora JSON-kenttävertailu on tätä suppeampi ja näkyvästi erillinen. Rajauksen ulkopuolinen kohta estää hyväksynnän; sitä ei hyväksytä hiljaisesti.
- Ei QEAA-, DCAT-AP-, tuotantoturvallisuus-, kuormitus- tai saavutettavuusvaatimustenmukaisuuden väitettä. Synteettisyys on käyttäjän vahvistus, ei automaattinen henkilötietotunnistin. Palvelun saatavuus on kuvattu metadata, ei saavutettavuus-/luottamusmittaus.

## Toimitus

Haara `feat/phase-2e-derived-validation` on pushattu GitHubiin. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2e-derived-validation --title ... --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Myös REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2e-pr.json` palautti Forbidden-vastauksen. Git-push onnistui; GitHub API -avaus estyi. Valmis kuvaus on docs/pull-request.md. PR:n voi avata selaimessa: https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2e-derived-validation . Main-haaraan ei yhdistetty muutoksia.

---

# Aikaisemmat toimitukset (historia, eivät tämän ajon tuloksia)

# Vaihe 2D — offline SHACL Core ja synteettinen esimerkkisisältö

Tarkistettu 15.10.2026. Pohjana main `61ca4ed` (PR #7, vaihe 2C, yhdistetty käyttäjän hyväksynnällä). Työhaara `feat/phase-2d-shacl`. PR:ien 5 ja 6 semanttinen ja VC-toimituksen periaate säilyvät sitovina. Mainiin ei yhdistetä automaattisesti.

## Toteutettu

- pySHACL 0.31: profiilin ja lukittujen riippuvuuksien meta-SHACL-rakennetarkistus sekä synteettisen RDF-esimerkin oikea SHACL Core -validointi. Tietotyypit, kardinaliteetit, sisäkkäiset muodot ja koodistorajoitteet tarkistuvat alkuperäisestä graafista, eivät litistetystä tietoelementtilistasta.
- Yksi esimerkkigraafi (voi sisältää monta tietuetta), Turtle/RDFXML/paikalliskontekstinen JSON-LD. Pakollinen synthetic:true-ilmoitus, 100 kB/2 000 kolmikkoa. Käyttöliittymän tiedostotuonti ja tekstikenttä sekä erillinen synteettisyyden vahvistus.
- Kohdistumaton/tyhjä esimerkki tai deaktivoitu aloitusmuoto ei tuota väärää onnistumista. Aloitusmuotojen kohdistus tarkistetaan; varsinaiset rajoitteet tarkistetaan koko graafista. Ei OWL-päättelyä.
- Palvelimen semanticValidation: tulos, sääntö-IRI, JSON Pointer, RDF-polku, kohde/muoto, profiili-/esimerkkitarkiste, esitysmuoto, moottoriversio ja validointikäytäntö. Asiakas ei voi asettaa raporttia. Näyttö rajattu 100 havaintoon, mikä ei muuta epäonnistumista onnistumiseksi.
- Esimerkki ja raportti sisältyvät luonnoksen/julkaisun sisältötarkisteeseen. Muutos mitätöi hyväksynnän; uusi julkaisu vaatii ajantasaisen läpäisseen raportin ja aiemman erillisen ihmishyväksynnän. Virheellisen esimerkin voi tallentaa korjattavaksi luonnokseksi. Validate-esikatselu on muuttamaton: uuden raportin tallennus tehdään editorin luonnostallennuksessa.
- Resurssirajattu validointiprosessi: CPU 5 s, muisti 512 MiB, seinäkello 15 s, syvyys 20, verkkoyhteyksien esto. SPARQL/JS/AF/mukautetut komponentit ja tuntemattomat SHACL-predikaatit estävät hyväksynnän. Ulkoisia konteksteja, DTD/ENTITYjä tai riippuvuuksia ei noudeta.
- Alkuperäisen UTF-8-sisällön alun/lopun tyhjää tilaa ei enää normalisoida uusissa tuonneissa; tavutarkiste vastaa tallennettua alkuperäistä tekstiä. Nimetyt JSON-LD-graafit hylätään eksplisiittisesti sen sijaan, että oletusgraafin ulkopuolisia rajoitteita/sisältöä katoaisi.
- Ei uutta migraatiota: 2C:n JSONB-sisällöt riittävät. Head on 0004_publication. Vanhoihin julkaistuihin sisältöihin, profiilisnapshotteihin tai luonnoksiin ei tehdä automaattisia täydennyksiä. Vanhat julkaisut säilyvät; seuraava julkaisu tarvitsee esimerkin ja tallentamalla muodostuvan raportin.
- Nykyinen OIDC, CSRF, organisaatiorajat, If-Match, idempotenssi ja erillinen hyväksyntä säilyvät. Codespacesin määrityksiin ei tehty muutoksia: portti 8000, openBrowser ja service:app-verkko ennallaan; ohje edellyttää Private-tilaa. Ei ulkoisia issuer/wallet-yhteyksiä.
- README, ROADMAP, AGENTS, verkkodemon ja arkkitehtuurin ohjeet sekä CI-testilista päivitetty. Uusi synteettinen fixture fixtures/semantic-example-demo.ttl.

## Tässä tehtävässä todella ajettu

- `uv add` ja `UV_CACHE_DIR=/workspace/.cache/uv uv sync --locked`: runtime-riippuvuudet ja lukitus onnistuivat. `npm run build --prefix apps/web`: TypeScript ja Vite-tuotantobuild onnistuivat.
- `./scripts/cloud-build.sh` rakensi Docker-imagen pilven proxy-/CA-reitillä TLS-tarkistuksia säilyttäen; `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait` käynnisti app/db/keycloak-palvelut healthy-tilaan olemassa olevilla voluumeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **55 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Sisältää aiemmat 39 testiä ja 16 uutta SHACL-testiä. Vanhojen kantojen, muokattujen metatietojen/UUID:iden ja jäsenyyksien säilymistestit läpäisivät.
- Uudet testit: puuttuva kenttä, väärä tietotyyppi, liikaa arvoja, kohdistamaton esimerkki, kolme RDF-esitystä, väärä profiilirakenne, estetty SPARQL/tuntematon rajoite, sisäkkäinen riippuvuus ja koodisto, etäkonteksti/DTD/ENTITY, synteettisyysvahvistus, raportin väärentämiskielto ja sidonta, muuttumaton vanha julkaisu, vanhan raportittoman luonnoksen uudelleentallennus, deaktivoitu muoto, raskaan regexin resurssiraja, UTF-8-tavujen säilyminen ja nimetyn graafin hylkäys.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **7 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Oikea Chromium ja Keycloak; aiemmat CRUD/mobiili/organisaatiot/reader/eristys/session vanheneminen sekä virheellinen esimerkki → korjaus tiedostosta → raportti → toisen käyttäjän hyväksyntä → julkaisu → anonyymi haku. Ei kirjautumisen ohitusreittiä.
- Yhteensä **62 eri testiä** läpäisi. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia. Resurssirajan testin lisätarkistus läpäisi erikseen: VALIDATION_RESOURCE_LIMIT ja palvelimen readiness säilyivät, testikutsu kesti 6,12 s. Tämä ei ole lisätesti kokonaismäärään.
- Olemassa olevasta oikeasta demokannasta tarkistettiin kolme aitoa 2C-julkaisua: sisältö vastaa alkuperäistä SHA-256:ta, version API palauttaa saman snapshotin eikä vanhaan JSON-LD-vientiin ilmesty puuttuvia 2D-kenttiä. Tietoja tai volumeita ei nollattu.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.` Sekä migrations- että .devcontainer-diff on tyhjä.
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: Keycloak samalla portilla 8000, workspace service:app-verkossa ja openBrowser ennallaan.
- `git diff --check`: ei whitespace-virheitä. Tavallinen app-restart ja Compose-readiness läpäisivät. Ennen/jälkeen samat rivit ja tarkisteet: 8 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 5 profiilisnapshotia, 4 julkaisua/tarkastusta/outboxia ja 33 audit-tapahtumaa. Selaintestien synteettiset julkaisut jäävät muuttumattomaan historiaan; epäonnistuneen kehitysajon keskeneräinen synteettinen luonnos säilytettiin.

Selaintestin ensimmäinen uusi tiedostopolku paljasti tekstikentän label-kohdistuksen ongelman. Kentälle lisättiin eksplisiittinen label/htmlFor/id. Lopullinen seitsemän selaintestin ajo läpäisi korjauksen jälkeen.

## Ajamattomat ja rajat

- Oikea GitHub Codespace, GitHubin Private-portin pääsynvalvonta ja automaattinen selainvälilehti, Windows/Docker Desktop, tavallinen `docker compose up --build` ilman pilven build-wrapperia sekä GitHub Actions -etäajo jäivät ajamatta. Asetusten staattinen tarkistus ei todista näitä.
- Elävän Tietomallit-palvelun linkkituontia ei ajettu. Oikea paikallinen tiedostotuonti sekä nykyinen hallitulla verkkovastauksella tehtävä linkkitesti ajettiin. Molemmat fixturet ovat synteettisiä eivätkä oikea Tietomallit-export tai rekisteriote.
- SHACL-tulos ei todista lähdeprofiilin alkuperää, oikeudellista asemaa tai myöntämisoikeutta. Se ei tarkista VC-kuorta, allekirjoitusta, myönnettyä todistusta tai lompakkoyhteentoimivuutta. Ei vaihetta 3.
- Vain offline Core, ei SPARQL/JS/AF- tai mukautettujen komponenttien tukea. Nimettyjä JSON-LD-graafeja ei tueta. JSON Schema/OpenAPI-johdannaisten validointi ja kattavuuskartoitus sekä DCAT-AP-vaatimustenmukaisuus jäävät jatkoon.
- Synteettisyys on käyttäjän vahvistus, ei automaattinen henkilötieto-/salaisuustunnistin. Ei kuormitus-, tuotantoturvallisuus- tai saavutettavuusauditointia.

## Toimitus

Haara `feat/phase-2d-shacl` on pushattu GitHubiin. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2d-shacl --title ... --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`, ja REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2d-pr.json` palautti saman Forbidden-esteen. Git-push onnistuu, GitHub API -pääsy on estynyt. Valmis kuvaus on docs/pull-request.md. Avaa PR selaimessa: https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2d-shacl . Main-haaraan ei yhdistetty muutoksia.

---

# Aikaisemmat toimitukset (historia, eivät tämän ajon tuloksia)

# Vaihe 2C — yksityiset luonnokset ja muuttumattomat julkaisut

Tarkistettu 14.10.2026. Pohjana main `0dd6555`, joka sisältää PR:t 5 ja 6. Työhaara `feat/phase-2c-publication`. Mainiin ei yhdistetä automaattisesti. Alla olevat aiempien toimitusten PR-esteet/testimäärät ovat historiaa.

## Toteutettu ja suunnittelumuutosten vaikutus

- Luonnos → tarkastus → erillinen hyväksyntä → julkaisu. Muokkaus mitätöi hyväksynnän, kaikki luonnoksen kirjoittajat estetään sen hyväksynnästä. Julkaisija voi olla sama kuin erillinen tarkastaja.
- Pysyvä omistajaorganisaatio erotetaan tarjoajasta. Editor muokkaa, reviewer/publisher tarkastaa, publisher julkaisee. Omat luonnokset vaatii jäsenyyden; julkinen haku, URI:t ja viennit palauttavat vain julkaisuja. Anonyymi tyhjä haku uuden kannan alussa on tarkoituksellinen muutos.
- ETag/If-Match, PostgreSQL-rivilukko, luonnin/julkaisun 24 h idempotenssi. Julkaisu, profiiliviite, audit ja outbox samassa transaktiossa. Tietokantatriggerit estävät snapshot-/tarkastus-/tapahtumahistorian UPDATE/DELETE-operaatiot.
- Semver-julkaisut, pysyvä version URI, vanhan version JSON-/JSON-LD-vienti ja uuden työkopion luonti aiemman julkaisun rinnalle. Vanhaa sisältöä ei muokata eikä julkaistua tuotetta poisteta.
- PR 5: SHACL-profiilin tuonti linkillä TAI tiedostolla, lukitut alkuperäiset artefaktit, IRI:t, OWL-viitteet, riippuvuudet ja johdannaisdialektit. Tietoelementit johdetaan profiilista. Vanha dataElements säilyy keskeneräisenä legacy-demotietona. Kolmen RDF-esityksen graafiekvivalenssi tarkistetaan erikseen tavutarkisteista.
- Rakenne-/riippuvuustarkistukset ja lähdeilmoituksen eksplisiittinen ihmistarkastus. Ei automaattista Tietomallit-alkuperän todistusta, ei SHACL-instanssivalidointipalvelua. Parserilla on tiedosto-, kolmikko-, CPU-, muisti- ja aikarajat. Etäkontekstien/DTD:n jäsennys estetään.
- PR 6: W3C VC ensisijaisena toimitusmuotona, oletuksena näkyvästi planned. VC-/issuer-/wallet-metatiedot lukitaan tuoteversioon ja profiilisnapshotiin. Vain käytettävä palvelu saa pysyvän HTTPS-asiointilinkin, ei henkilökohtaisia tarjouksia/tokeneita. Esimerkkidomain tai planned/suspended ei saa toimivaa painiketta. Ei issuer/wallet-integraatiota tai QEAA-vahvistusta.
- Uusi 0004_publication säilyttää vanhat tuoterivit, UUID:t, muokkausajat ja kaikki metatiedot yksityisissä luonnoksissa; vanhoja migraatioita ei muuteta. Kolme alkuperäistä tuotetta siemennetään vain uuteen kantaan. Ei automaattista julkaisua tai tietojen nollausta.
- Keycloakin samoja käyttäjiä käytetään ristikkäiseen tarkastukseen: yritys julkaisee verotuotteita, vero yritystuotteita. Uudet jäsenyydet lisätään kerran tunnettuun synteettiseen organisaatioon; vanhaa realmiä tai oikeuksia ei korvata. Kolmannelle organisaatiolle ei keksitä oikeuksia.
- Codespacesin määritykset säilyvät muuttumattomina: portti 8000, openBrowser ja sovelluksen verkon jakaminen. README ja verkkodemon ohje edellyttävät Private-näkyvyyttä. README, ROADMAP, AGENTS, arkkitehtuuri ja tunnistusohje päivitetty; ratkaisun yksityiskohdat docs/phase-2c.md.

## Tässä tehtävässä todella ajettu

- Lukittu uv-riippuvuuksien asennus onnistui; RDFLib siirrettiin runtime-riippuvuudeksi. TypeScript-tarkistus ja Vite-tuotantobuild `npm run build --prefix apps/web` onnistuivat.
- `./scripts/cloud-build.sh` rakensi Docker-imagen pilven proxy-/CA-reitillä TLS-tarkistuksia säilyttäen. `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app, PostgreSQL ja Keycloak healthy olemassa olevilla voluumeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **39 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Viimeisen auth-testin tiukennuksen jälkeen 8 auth-testiä ajettiin erikseen uudelleen onnistuneesti; kyse ei ole 8 lisätestistä.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **7 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Oikea Chromium ja Keycloak, kaksi käyttäjää profiilitiedoston tuonnista tarkastuksen ja julkaisun kautta anonyymiin hakuun. Myös CRUD, mobiili, organisaationäkymä, reader/anonymous, organisaation muokkauseristys ja vanhentunut istunto.
- Yhteensä **46 eri testiä** läpäisi. Kirjastojen Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohitettuja testejä.
- Vanhan phase 1 -DDL:n muokattu tuotetieto, koko metadata (myös tuntematon sisäkkäinen kenttä), UUID ja aikaleima säilyivät. Erilliset 2A- ja 2B-päivitykset säilyttivät organisaation ja 2B-jäsenyyden. Tyhjä alustus ja toistuva migraatio/restart testattu. Samannimisiä tarjoajia ei yhdistetty.
- Oikeasti rinnakkaiset kaksi If-Match-muokkausta: yksi 200, toinen 412. Oman sisällön hyväksyntäkielto, hyväksynnän mitätöinti, idempotenssi, snapshot-/audit-triggerit ja outbox-virheen aiheuttama koko julkaisun rollback testattu.
- RDF/XML/Turtle/JSON-LD tuottivat saman graafitunnisteen; alkuperäinen tiedosto ladattiin takaisin. Puuttuvat riippuvuudet, pelkkä OWL/konteksti/johdannainen, etäkonteksti, XML DTD/ENTITY, vieras organisaatio ja henkilökohtaisen koodin URL hylättiin odotetusti. Käytettävän VC-palvelun metadata- ja binding-polku testattiin synteettisenä, ilman yhteyttä kyseiseen palveluun.
- Tavallinen app-restart ja Compose-readiness ajettiin. Ennen/jälkeen tarkistetut kaikki katalogirivit säilyivät samoina: 6 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 3 profiilisnapshotia, 3 julkaisua/tarkastusta/outboxia ja 21 audit-tapahtumaa. Kolme lisäjulkaisua ovat selaintestin synteettisiä, tarkoituksella muuttumattomaan historiaan jääviä tietueita. PostgreSQL-/Keycloak-volumea ei poistettu.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.`
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: hostname/callback samalla portilla 8000, workspace service:app-verkossa, openBrowser ennallaan. `.devcontainer`-diff on tyhjä.
- `git diff --check`: ei whitespace-virheitä.

Kehityksen aikaiset epäonnistumiset korjattiin: migraatiotestien siivoukseen jäänyt PostgreSQL-funktio, versio-IRI:n muutosta vastaamattomat vientitestien oletukset ja pitkän julkaistun nimen mobiilirivitys. Lopulliset yllä raportoidut ajot läpäisivät korjausten jälkeen.

## Ajamattomat tarkistukset ja rajat

- Oikeaa GitHub Codespacea, GitHubin Private-portin pääsynvalvontaa ja automaattista selainvälilehteä ei ajettu tämän Linux-pilvikoneen sisältä. Asetusten staattinen tarkistus ei korvaa tätä. README sisältää ennen yhdistämistä käytettävän haaralinkin ja kokeilupolun.
- Windows/Docker Desktop, tavallinen `docker compose up --build` ilman tämän pilven build-wrapperia, tyhjän välimuistin Windows-build ja GitHub Actions -etäajo jäivät ajamatta. Niiden onnistumista ei väitetä. Ohjeen Windows-komento on `docker compose up --build`, osoite http://localhost:8000.
- Elävän Tietomallit-palvelun linkkituontia ei ajettu. Linkki/tiedosto-vaihtoehdon testissä verkkovastaus korvataan hallitulla fixturellä; todellinen tiedostotuonti ajettiin selaimessa. Synteettinen profiilifixture ei ole oikea Tietomallit-export.
- Myöntämistä, todellista issuer-linkin saavutettavuutta, myöntäjän luottamusta, EUDIW/EBW-yhteentoimivuutta, SHACL-instanssivalidointia tai DCAT-AP-vaatimustenmukaisuutta ei todennettu. Ei vaihetta 3.
- Yksi VC-jakelu/tuote; usean myöntäjän valinta, laajempi elinkaari ja jäsenyyksien hallinta jäävät jatkoon. Profiilin selainlomake on yksinkertainen; moniosaiset riippuvuudet/johdannaiset annetaan API:lla. VC-metatietoja ylläpidetään JSON-kentässä. Haku suodattaa demomäärän muistissa, suorituskykyä tai saavutettavuusvaatimusten täyttymistä ei ole auditoitu.

## Toimitus

Haara `feat/phase-2c-publication` on pushattu GitHubiin. Pull requestia **ei luotu**: sekä `gh pr create --base main --head feat/phase-2c-publication --title ... --body-file docs/pull-request.md` että REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2c-pr.json` palauttivat `Post https://api.github.com/...: Forbidden`. Tämä on ympäristön GitHub API -pääsyn este; Git-push onnistui. Valmis kuvaus on docs/pull-request.md. PR:n voi avata selaimessa https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2c-publication . Main-haaraan ei yhdistetty mitään.

---

# Aikaisempien toimitusten historia (ei tämän ajon tuloksia)

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
- Haara `feat/phase-2b-auth` on pushattu GitHubiin. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2b-auth --title "Vaihe 2B: OIDC-kirjautuminen ja organisaatiokohtainen ylläpito" --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Valmis kuvaus on docs/pull-request.md ja PR:n voi avata selaimessa osoitteesta https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2b-auth . Main-haaraan ei yhdistetty mitään.

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

