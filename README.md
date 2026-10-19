# Metatietovaranto — synteettinen demo, vaihe 2H

## 2H:n jatko: attribuuttien semanttiset viittaukset

JSON Scheman `x-term`/`x-mtv-shacl`, SD-JWT Type Metadatan `x-mtv-semantic` ja yhteinen mapping yksilöivät saman SHACL-käyttöyhteyden, alkuperäiset IRI:t ja lähdesnapshotin. Laajennusprofiili 1.0.0, skeema ja mapping löytyvät Type Metadatan omista x-mtv-viitteistä tarkisteineen. Esimerkkikuluttaja lukee yhden väitepolun semantiikan ilman väitearvoja; [sopimus, ajettava esimerkki ja ETSI/EU-vastaavuustaulukko](docs/attribute-semantics.md).

Perus-2H:n PR #12 on nyt mainissa. PR #13:n työhaaraan on tuotu main `9258fff`; PR:n base on vahvistettu `main`-haaraksi. ETSI-alkutekstit ja EU-konsolidointi 11.8.2026 on nyt saatu käyttäjältä ja tarkastettu. [Lähdevertailu ja vastaanotetun asiakirjatietosivun havainnot](docs/pr13-source-comparison.md). Vanhat julkaisut säilyvät muuttumattomina. Katalogiviitteitä voi lisätä **Muokkaa → Ulkoiset attribuutti- ja todistusjärjestelykatalogit** -osiossa. Viitteet tarvitsevat dokumentoidun alkuperän ja normaalin hyväksynnän. 19.10.2026 toimitetun asiakirjatietosivun aikajanassa viimeisin versio on 11.8.2026. Alkuperäisen asetuksen oikaisusuhteiden tarkistus on vielä avoin; täyttä ETSI-profiiliyhteensopivuutta ei väitetä; paikallinen laajennus ei väitä standardienmukaisuutta tai lompakkotukea.

## Vaihe 2H: tekninen kuvauspaketti

SHACL-soveltamisprofiilista voi muodostaa yhteisen JSON-sisältöskeeman, W3C VC:n JSON-LD-kontekstin ja SD-JWT VC:n teknisen kuvauspaketin. [Täsmällinen rajaus, artefaktit ja standardiversiot](docs/phase-2h.md). DCAT-AP-vienti ei kuulu tähän vaiheeseen.

Kokeile ennen yhdistämistä: avaa Codespace haarasta **feat/phase-2h-attribute-semantics** (New with options → Branch), tai valitse haara nykyisessä Codespacessa ja rakenna uudelleen `docker compose up --build -d --wait`. Säilytä portti 8000 Private-tilassa ja avaa sen Forwarded Address selaimessa. Käynnistyksen automaattinen selainavaus säilyy.

1. Kirjaudu `vero / demo-vero`. Avaa **Omat luonnokset** ja kolmen toimitustavan synteettinen yritystuote. Jos se on jo julkaistu, luo ensin uusi työkopio.
2. Avaa **Muodosta SHACL-pohjainen kuvauspaketti**. Juurimuoto on `https://example.org/metatietovaranto/demo/ProductShape`. Muodosta mapping-ehdotus ja tarkasta nimi `companyName`, alkuperäinen IRI, xsd:string ja määrä 1…1.
3. Käytä mapping-versiota `1.1.0` tai aiempaa suurempaa versiota. Anna synteettiseksi sisällöksi `{"companyName":"Synteettinen Esimerkki Oy"}`. Tarkasta toimitustapojen asetukset ja vahvista neljä valintaa. Muodosta paketti ja avaa luonnos uudelleen.
4. Tarkasta artefaktit ja validointiraportti. Lähetä normaaliin tarkastukseen; eri käyttäjä `yritys / demo-yritys` tarkastaa ja julkaisee uuden tuoteversion. Artefaktien koneluettavat linkit näkyvät julkisella tuotesivulla vasta julkaisun jälkeen.

Windowsin paikallinen demo käynnistyy edelleen `docker compose up --build`, selainosoite **http://localhost:8000**. Pysäytys `docker compose down` säilyttää tiedot; testidatan palautusohje on alempana. Kuvauspaketti ei lisää demotunnuksia tai muuta oikeuksia. Artefaktit käyttävät Codespacesissa sen HTTPS-osoitetta, paikallisesti demon HTTP-osoitetta. Private-Codespaces vaatii GitHub-pääsyn myös kontekstinoutoon, joten se ei ole ulkoisen myöntäjän julkinen kontekstipalvelu. Tuotantokäyttö tarvitsee pysyvän HTTPS-alkuperän.

Käyttäjän toimittama **WE BUILD Certificate of Residence 0.0.2** -export on lukittu tavuntarkasti ja testattu. Koko profiilin generointi estyy puuttuvien literaalityyppien ja lukitsemattoman SKOS-riippuvuuden vuoksi; erillinen synteettinen testiprojektio läpäisee oikean JSON-LD/RDF/SHACL-ketjun. [Aineisto, täsmälliset rajoitteet ja testikomennot](docs/webcor-acceptance.md). Allekirjoitusta tai lompakkotoimitusta ei toteuteta.


Suomenkielinen React/TypeScript-käyttöliittymä, FastAPI, PostgreSQL ja Keycloak. Toteutettu: organisaatiokohtainen ylläpito, yksityiset luonnokset, erillinen hyväksyntä, muuttumattomat julkaisuversiot, haku, JSON-/JSON-LD-vienti ja sisältöprofiilin snapshotit sekä offline SHACL Core -validointi synteettisille esimerkeille sekä rinnakkaiset JSON API-, W3C VC- ja SD-JWT VC -toimitustapakuvaukset ja rajattu synteettisen JSON-sisällön RDF-muunnoskokeilu sekä julkaisuversioiden deprecated-/withdrawn-elinkaari. [ROADMAP](ROADMAP.md) rajaa toteutuksen, [STATUS](STATUS.md) kertoo todella ajetut tarkistukset.

Vain synteettiseen demokäyttöön. Katalogi ei myönnä todistuksia eikä toteuta lompakkoprotokollaa, QEAA-palvelua tai tuotannon tunnistamista. Tavoitearkkitehtuuri on `metatietovaranto_suunnittelu.md`. PR:ien 5 ja 6 sitovat [semanttinen periaate](docs/semanttinen-periaate-1.md) ja [VC-periaate](docs/vc-periaate-2.md) on huomioitu [vaiheen 2C perustassa](docs/phase-2c.md) ja [vaiheen 2E ratkaisussa](docs/phase-2e.md).

## Kokeile selaimessa ennen yhdistämistä

Avaa [vaiheen 2H uusi Codespace](https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2h-attribute-semantics), valitse haara **feat/phase-2h-attribute-semantics** ja **Create codespace**. Uusi Codespace pitää main-haaran kokeiludatan erillään. Sovellus, PostgreSQL ja Keycloak käynnistyvät automaattisesti. Selain avautuu automaattisesti tai valitse **PORTS → 8000 → Open in Browser**. Säilytä portin näkyvyys **Private**. Keycloak toimii saman osoitteen `/identity`-polussa; muita portteja ei tarvitse avata.

Osoite on `https://<codespacen-nimi>-8000.app.github.dev`; täsmällinen oman ympäristön osoite näkyy PORTS-näkymässä. Älä vaihda portin sisäistä protokollaa HTTPS:ksi. [Verkkodemon ohje](docs/verkkodemo.md) kertoo pysäyttämisestä ja kiintiöistä.

### Demotunnukset

| Käyttäjä | Salasana | Muokkaus | Tarkastus ja julkaisu |
| --- | --- | --- | --- |
| `vero` | `demo-vero` | Alkuperäinen verotuotteen organisaatio | Yritystuotteen organisaatio |
| `yritys` | `demo-yritys` | Alkuperäinen yritystuotteen organisaatio | Verotuotteen organisaatio |
| `lukija` | `demo-lukija` | Ei | Ei; alkuperäisen verotuotteen organisaation luku |

Julkisia synteettisiä demotunnuksia, eivät tuotantosalaisuuksia. Samassa organisaatiossa kirjoittaja ei saa hyväksyä omaa muutostaan. Tarkastaja voi myös julkaista hyväksymänsä version. Julkaisijarooli ei anna muokkausoikeutta. Lisäjäsenyydet annetaan kerran vain tunnettuihin synteettisiin organisaatio-UUID:ihin; olemassa olevia jäsenyyksiä ei korvata. Kolmannen pätevyysorganisaation tuote säilyy kannassa, mutta sille ei ole valmista muokkaajatunnusta. Jäsenyyksien hallinta: [authentication.md](docs/authentication.md).

### Kokeile kolmea rinnakkaista toimitustapaa

1. Kirjaudu `vero` / `demo-vero`. Avaa **Omat luonnokset → Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo)**. Uusi neljäs esimerkki sisältää saman profiilin ja kolme planned-toimitustapaa. W3C VC on oletuksena ensisijainen.
2. Tarkastele erikseen formaattia, protokollaa, suojausprofiilia, mapping-versiota ja kenttäpolkuja. Suunnitelluilla palveluilla ei ole aktiivista API-/myöntämistoimintoa. SD-JWT VC:llä on oma vct ja väitemapping; siinä ei vaadita JSON-LD-kontekstia.
3. Valitse **Muokkaa**. Toimitustavoilla on omat saatavuus-, vastuu-, palvelu-, tunnistautumis- ja profiilikenttänsä. **Versioitu kenttämapping** kuvaa IRI-polut, oliot/literaalit, tietotyypit ja min/maxCountin. `/*` tarkoittaa taulukon alkiota. Tallenna synteettinen muutos; usean erillisen validointiprosessin ajo voi kestää muutamia sekunteja. Tarkasta kolme erillistä raporttia: RDF-esimerkin SHACL, JSON-johdannaiset sekä toimitustapojen metadata/mapping.
4. Säilytä esimerkin palvelut planned-tilassa; toimivaa lähde- tai myöntäjäpalvelua ei ole. Lähetä tarkastukseen. Kirjaudu ulos ja vahvista Keycloakin **Log out**. Kirjaudu `yritys` / `demo-yritys`, tarkasta kuvaukset, kirjaa perustelu ja hyväksy lähdeilmoituksen tarkastus. Hyväksy ja julkaise `1.0.0`.
5. Tuote tulee julkiseen hakuun. Myös julkaistun esimerkin kolme palvelua ovat suunnitteilla ja ilman aktiivisia palvelutoimintoja. JSON-/JSON-LD-vienti kuvaa metatiedot; se ei palauta yrityksen varsinaista tietosisältöä eikä myönnettyä todistusta.
6. `vero` voi luoda uuden työkopion. Aiempi julkaisu säilyy muuttumattomana. Mappingin sisältömuutos tarvitsee suuremman mapping-version sekä uuden hyväksynnän ja tuoteversion.

Esimerkki lisätään päivityksessä kerran vain tunnettuun synteettiseen demo-organisaatioon. Alkuperäiset kolme tuotetta säilyvät. Poistettua tai muutettua esimerkkiä ei palauteta restartissa. Julkinen haku on uuden kannan alussa tyhjä, kunnes julkaiset ensimmäisen version.

### Oman tuotteen sisältöprofiili ja esimerkit



1. Uuden demon julkinen haku on aluksi tyhjä. Kolme synteettistä esimerkkiä (verovelka, yrityksen perustiedot, ammattipätevyys) säilyvät keskeneräisinä yksityisinä luonnoksina. Niille ei keksitä virallista profiilia tai hyväksyntää.
2. Kirjaudu `vero`-käyttäjänä ja avaa **Omat luonnokset → Verovelkatieto → Muokkaa**. Voit myös lisätä oman synteettisen tuotteen. Tarjoajavalikossa ovat vain omat muokkaajaorganisaatiot.
3. Avaa **Tuo Tietomallit-soveltamisprofiili**. Codespacesissa lataa ensin Explorerista `fixtures/semantic-profile-demo.ttl` omalle koneellesi (hiiren oikea painike → **Download**). Valitse tämä tiedosto tuontilomakkeella, profiili-IRI `https://example.org/metatietovaranto/demo/profile` ja OWL-sanaston nimiavaruus `https://example.org/metatietovaranto/demo/`. Kirjaa lähdeilmoitukseksi **Synteettinen testifixture; ei oikea Tietomallit-export, vain ohjelmistodemo.** Tuo profiili. Lataa Codespacesin Explorerista myös `fixtures/semantic-example-demo.ttl` omalle koneellesi ja valitse se **Esimerkkitiedosto**-kenttään. Vahvista esimerkin synteettisyys ja tallenna tuote. **Esimerkki läpäisee SHACL-tarkistuksen** kertoo onnistumisesta. Fixture ei ole Tietomallit-alustan vahvistama profiili. Oikea profiili voidaan antaa vaihtoehtoisesti koneluettavan exportin linkkinä.
4. Tietoelementit johdetaan profiilista. VC-jakelun oletus on `planned`, jolloin tuotesivu näyttää **Lompakkotodistus suunnitteilla**. Lähetä luonnos tarkastukseen.
5. Kirjaudu ulos ja vahvista Keycloakin **Log out**. Kirjaudu `yritys`-käyttäjänä, avaa sama luonnos, tarkasta profiili ja lähdeilmoitus, kirjoita perustelu ja merkitse tarkastuksen valintaruutu. Hyväksy ja julkaise esimerkiksi versiona `1.0.0`.
6. Julkaisu löytyy nyt julkisesta hausta ja sen JSON-/JSON-LD-viennit toimivat. Historiassa on pysyvä version URI ja tarkiste. Profiilin tarkastus on ihmisen arvio lähdeilmoituksesta; se ei ole automaattinen alustatodistus. Erillinen SHACL-tarkistus koskee tallennettua synteettistä RDF-sisältöä; VC:n kuorta, allekirjoitusta tai myöntämistä ei tarkisteta.
7. `vero` voi luoda julkaistun rinnalle uuden työkopion. Muokkaus ei muuta aiempaa julkaisua. Uusi julkaisu tarvitsee uuden hyväksynnän ja aiempaa suuremman `major.minor.patch`-numeron. Julkaistua tai tarkastushistoriaa sisältävää tuotetta ei poisteta.

## Windows ja Docker Desktop

Tarvitset Docker Desktopin käynnissä Linux-konteilla, Compose v2:n ja Gitin. Kloonaa repo tai avaa nykyinen checkout PowerShellissä:

```powershell
git fetch origin
git switch feat/phase-2h-attribute-semantics
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
git switch feat/phase-2h-attribute-semantics
docker compose up --build -d --wait
docker compose exec -T app .venv/bin/alembic current
```

Tiedoston kopiointi säilyttää merkistön myös PowerShellissä. Odotettu head on `0004_publication`. Käynnistys ajaa migraatiot transaktiossa advisory-lukon alla ennen readinessia sekä Composessa että Codespacesissa. Virhe estää käynnistymisen ja fixtureiden ajon. Toistuva ajo on sallittu: `docker compose exec -T app .venv/bin/alembic upgrade head`.

- `0001_phase1` tunnistaa ja tarkistaa alkuperäisen skeeman tai luo tyhjän kannan. Tuntematonta skeemaa ei hyväksytä stampilla.
- `0002_organizations` säilyttää tuotteiden UUID:t, kaikki metatiedot ja aikaleimat. Jokainen vanha tarjoaja saa erillisen organisaation; samannimisiä ei yhdistetä. Tuntematon maa on `ZZ`, tunnisteet `[]`, alkuperä näkyy `legacyProductId`-kentässä.
- `0003_auth` lisää organisaatiojäsenyydet ja OIDC-istunnot.
- `0004_publication` säilyttää alkuperäiset tuoterivit, kopioi kuvaukset luonnoksiksi ja lisää muuttumattomat profiili-/julkaisusnapshotit, tarkastukset, auditoinnin ja outboxin. Omistajaorganisaatio lukitaan alkuperäiseen tarjoajaan. Vanhoja tuotteita ei julkaista automaattisesti; anonyymi näkyvyys muuttuu tarkoituksella. Vanhat käsin annetut tietoelementit säilyvät demotietona, kunnes profiili liitetään.

Aidosti uusi kanta saa kolme alkuperäistä fixtureä ja 2E:n neljännen kolmen toimitustavan esimerkin. 2E-päivitys lisää vain tämän uuden esimerkin kerran tunnettuun alkuperäiseen demo-organisaatioon; muita vanhoja kantoja ei siemennetä. Vanha tyhjä kanta tai poistettu fixture ei palaudu. Migraatio ei tarjoa tuhoavaa downgradea tai offline-SQL-ajoa; palautuminen vaatii testatun varmuuskopion palautuksen erilliseen kantaan. Älä poista vanhaa Codespacea tietoja säilyttävässä päivityksessä. **Rebuild Container** rakentaa haaran imagen uudelleen; pelkkä tiedostojen haaranvaihto ei päivitä ajossa olevaa imagea. Keycloak-realmiä ei tarvitse nollata.

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
| `POST /api/v1/drafts/{id}/validate` | Julkaisuedellytykset ja tallennetun esimerkin tuore SHACL-esikatselu; ei muuta luonnosta |
| `DELETE /api/v1/products/{id}` | Poista vain luonnos, jolla ei ole julkaisu-/tarkastushistoriaa |
| `GET /api/v1/products/{id}/audit-events` | Organisaation muokkaajan/tarkastajan tapahtumat |
| `GET /api/v1/organizations`, `GET /api/v1/organizations/{id}` | Organisaatioiden perustiedot |
| `POST /api/v1/profile-snapshots` | Profiilin tuonti editorin organisaatioon |
| `GET /api/v1/profile-snapshots/{id}` | Snapshotin manifesti, alkuperä ja tarkisteet |
| `GET /api/v1/profile-snapshots/{id}/artifacts/{artifactId}` | Alkuperäinen UTF-8-artefakti |

Kirjoitus tarvitsee palvelinistunnon ja `/auth/me`-vastauksen `csrfToken`-arvon `X-CSRF-Token`-otsakkeessa. Luonti ja julkaisu vaativat lisäksi `Idempotency-Key`-otsakkeen (24 h, sama avain eri sisällölle 409). Työkopion muuttaminen/tilasiirtymä/poisto tarvitsee sen nykyisen `If-Match`-ETagin: puuttuva 428, vanhentunut 412. Käyttöliittymä lähettää nämä. Omistajaorganisaatio ei vaihdu tarjoajavalinnasta; vaihto edellyttää editor-oikeutta myös uuteen tarjoajaan.

POST/PUT ei hyväksy asiakkaan `provider`-, `dataElements`-, tila- tai hyväksyntäkenttiä. Käytä `/docs`-sopimusta ja `providerOrganizationId`-kenttää. Tarjoajanimi säilyy vastauksissa ja vienneissä. Profiilin tuonti tukee Turtlea, RDF/XML:ää ja paikalliskontekstista JSON-LD:tä, enintään 1 MB/artefakti, 2 MB/pyyntö ja 10 000 RDF-kolmikkoa. Linkkituonti hyväksyy vain `tietomallit.suomi.fi` / `iri.suomi.fi` HTTPS-exportit ilman redirecteja. Muut lähteet annetaan tiedostona. HTML-sivulinkki ei ole export.

API tukee riippuvuuksia, ulkoisia OWL-viitteitä ja JSON Schema/OpenAPI -johdannaisia. Käyttöliittymän yksinkertainen tuonti käsittelee yhden pääartefaktin ja yhden sanastoviitteen; moniosainen tuonti tehdään API:lla. Alkuperäiset IRI:t ja koko graafi säilyvät, tietoelementtinäkymä on johdettu osajoukko. Etäkonteksteja tai riippuvuuksia ei noudeta jäsennyksen aikana. Puuttuva lähde/SHACL/riippuvuus estää julkaisun. Pelkkä johdannainen ei riitä. RDF-esitysten ekvivalenssi tarkistetaan graafina; tavutarkisteet ovat erikseen. JSON-LD-katalogivienti on eri asia kuin sisältöprofiili tai myönnetty VC. DCAT-AP-vaatimustenmukaisuutta ei väitetä.

Uusia rinnakkaisia toimitustapoja muokataan rakenteisilla lomakkeilla. Vanha issuance-JSON-kenttä säilyy vanhoille kuvauksille, kunnes lisäät uuden toimitustapakokoelman. `planned`/`suspended` ei näytä toimivaa linkkiä. Käytettävä jakelu tarvitsee myöntäjä-/operaattori-/lähdeorganisaatiot, VC-profiilin ja kartoituksen, pysyvän HTTPS-linkin sekä saatavuus- ja käyttöehdot. Henkilökohtaisia tarjouksia, koodeja tai tokeneita ei tallenneta. Esimerkkiverkkotunnuksia ei hyväksytä toimivaksi myöntämispalveluksi. EUDIW-/EBW-`tested` vaatii nimetyn profiilin, version, näytön ja testipäivän. Demo ei vahvista QEAA-luokkaa.

## Vaihe 2D: esimerkit ja SHACL Core

Uusi kirjoitusparametri on `syntheticExample`: `serialization` (`turtle`, `rdfxml` tai paikalliskontekstinen `jsonld`), `content` ja pakollinen `synthetic: true`. Yksi esimerkkigraafi voi sisältää useita synteettisiä tietueita. Kokoraja on 100 kB ja 2 000 kolmikkoa. Älä tuo henkilö-/rekisteritietoja, salaisuuksia tai myönnettyjä todistuksia; synteettisyyden vahvistus on käyttäjän ilmoitus, ei automaattinen henkilötietotunnistin. Esimerkki tulee julkiseksi vain hyväksytyn julkaisun mukana. UTF-8-sisältö, mukaan lukien alun/lopun tyhjä tila, säilyy tarkistetta varten sellaisenaan. Nimettyjä JSON-LD-graafeja ei tueta: ne hylätään, jotta rajoitteita tai sisältöä ei katoa oletusgraafin ulkopuolelle.

Tallennus tarkistaa lukitun profiilin ja riippuvuuksien SHACL Core -rakenteen sekä esimerkin kaikki profiilin Core-rajoitteet. Ei OWL-päättelyä. Tyhjä tai kohdistamaton esimerkki ei läpäise. `entryShapeUris`-valinnan jokaisella aktiivisella aloitusmuodolla on oltava kohdetietue; ilman valintaa vaaditaan vähintään yksi aktiivisen luokkamuodon kohde. Tarkistus käy läpi koko graafin kohdistuvat muodot; aloitusmuodot eivät piilota muiden muotojen virheitä.

Palvelin muodostaa `semanticValidation`-raportin: profiilin ja esimerkin tulos, kohdetietueiden määrä, säännön IRI, JSON Pointer, kohteen/polun/muodon tunnisteet, tarkisteet, moottoriversio ja validointikäytäntö. Asiakas ei saa asettaa raporttia. SHACL-havainnon `resultPath` on RDF-polku; `/syntheticExample` on API:n JSON Pointer. Kaikki virhe-, warning- ja info-havainnot estävät tämän demon uuden julkaisun. Raportin näyttö rajataan 100 havaintoon; raja ei muuta epäonnistumista onnistumiseksi.

Esimerkki ja raportti sisältyvät luonnoksen sisältötarkisteeseen, hyväksyntään ja muuttumattomaan julkaisuun. JSON-vienti sisältää alkuperäiset oliot; JSON-LD-katalogiviennissä ne ovat selvästi paikallisten demotermien JSON-tekstiarvoja. Esimerkin tai profiilin muutos vaatii uuden tarkistuksen ja hyväksynnän. Virheellinen esimerkki säilyy luonnoksena korjattavaksi; sitä ei voi lähettää tarkastukseen. Pelkkä `/validate`-esikatselu ei tallenna uutta raporttia: tallenna luonnos päivittääksesi sen.

Tuetut säännöt rajataan offline SHACL Coreen. SPARQL, SHACL-JS, säännöt, mukautetut constraint-komponentit ja tuntemattomat SHACL-predikaatit estävät hyväksynnän. Graafi säilyy alkuperäisenä, vaikka sen laajennuksia ei tueta. Validointiprosessi ei saa avata verkkoyhteyksiä; etäkonteksteja, DTD/ENTITY-määrittelyjä tai etäriippuvuuksia ei seurata. Prosessin rajat: CPU 5 s, muisti 512 MiB, seinäkello 15 s ja validointisyvyys 20. Aika-/resurssivirhe estää julkaisun.

### Päivitys vaiheesta 2C

Sama varmuuskopio-, rebuild- ja käynnistystapa toimii; head pysyy `0004_publication`-revisiona. Uutta migraatiota ei tarvita: esimerkki ja raportti käyttävät jo olemassa olevia luonnoksen/julkaisun JSONB-sisältöjä. Mitään vanhaa riviä, snapshotia tai julkaisua ei kirjoiteta uudelleen. Uudelleenkäynnistys ei lisää esimerkkejä automaattisesti.

Aiempi julkaisu pysyy luettavana alkuperäisine tarkisteineen, vaikka sillä ei ole SHACL-raporttia. Sen rinnalle tehtävä uusi julkaisu sekä vanhat keskeneräiset luonnokset tarvitsevat esimerkin ja uudelleen tallennuksessa muodostuvan raportin. Aiemmin hyväksytty luonnos pitää muokata/tallentaa ja hyväksyä uudelleen. Myös moottorin tai validointikäytännön vaihtuessa vanhentunut raportti estää uuden julkaisun. Ihmisen tekemä lähdeilmoituksen tarkastus säilyy erillisenä vaatimuksena.

Tämä ei vielä kata JSON Schema-/OpenAPI-johdannaisten validointia tai kattavuuskartoitusta, DCAT-AP-vaatimustenmukaisuutta, VC-kuorta ja allekirjoitusta tai ulkoisia palveluita. Ne jäävät jatkovaiheisiin.

## Vaihe 2G: julkaisuversioiden elinkaari

Kokeile uudessa Codespacessa tai nykyisillä Docker Desktop -käynnistysohjeilla. Julkaise ensin synteettinen tuote yllä olevan kahden käyttäjän polun mukaan: `vero` muokkaa/lähettää tarkastukseen, `yritys` hyväksyy ja julkaisee. Valmiin neljännen tuotteen palvelut pidetään planned-tilassa. Julkaisemisen jälkeen `yritys` näkee julkisella tuotesivulla **Version elinkaari → Julkaisijan elinkaarimuutos**.

1. Valitse **Poistumassa käytöstä**, kirjoita julkinen perustelu ja tallenna. Varoitus näkyy kaikille, mutta tuote säilyy oletushaussa. Voit viitata saman tuotteen myöhempään jo julkaistuun versioon korvaajana. Jos sellaista ei ole, kerro tilanne perustelussa.
2. Valitse **Poistettu käytöstä**, kirjoita uusi julkinen perustelu ja vahvista tallennuksen yhteydessä avautuva kysymys. Tämä on version lopullinen tila; sisältö palautetaan tarvittaessa uutena hyväksyttynä julkaisuna.
3. Tuote jää pois oletushausta, jos tämä on sen uusin julkaisu. Hae rajauksella **Version elinkaaritila → Poistettu käytöstä** tai avaa version pysyvä linkki: varoitus ja tapahtumahistoria säilyvät. Palvelutoiminnot on estetty. Planned-palveluilla ei ollut aktiivisia toimintoja alun perinkään.
4. Alkuperäinen JSON/JSON-LD-julkaisu ja sisältötarkiste säilyvät. **Ajantasainen elinkaaritieto JSONina** kertoo erikseen nykytilan ja julkisen historian. Perusteluun ei kirjoiteta henkilötietoja tai salaisuuksia. Sivun uudelleenlataus hakee tuoreen tilan; jo avoin välilehti ei peru ulkoisen palvelun pääsyoikeuksia.

Vain pysyvän omistajaorganisaation publisher voi muuttaa elinkaaritilaa. Editor/reviewer/reader eivät saa oikeutta tästä roolistaan; tarjoajan vaihtaminen ei siirrä oikeutta. Tilamuutos ei muokkaa luonnosta tai sisältöhyväksyntää. Withdrawn-version tilalle ei automaattisesti nosteta vanhempaa versiota. Uusi julkaisu käy tavallisen luonnos-/hyväksymisprosessin.

API: `GET /api/v1/products/{id}/versions/{version}/lifecycle` ja `POST /api/v1/products/{id}/lifecycle-events`, body `{"version":"1.0.0","status":"deprecated","reason":"Julkinen perustelu...","replacementVersion":null}`. Kirjoitus tarvitsee istunnon, CSRF:n, elinkaaren oman If-Match-ETagin sekä Idempotency-Keyn. Haku: `lifecycleStatus=current|published|deprecated|withdrawn|all`; oletus current näyttää published/deprecated. Katalogiviennin `includeWithdrawn=true` sisällyttää poistuneet tilatietoineen.

Nykyversion JSON/JSON-LD-lukuesitys sisältää erillisen lifecycle-tiedon tapahtuman jälkeen; contentHash koskee alkuperäistä snapshotia. Versio-API, version URI ja `export?version=...` säilyttävät alkuperäisen sisältönsä/ETaginsa. Vastauksen `X-Product-Lifecycle-Status` ja `Link: describedby` ohjaavat ajantasaiseen tilaan. Käyttöliittymä hakee sen aina erikseen ennen palvelutoimintojen näyttämistä. [Täsmällinen sopimus](docs/phase-2g.md).

Migraatio `0005_lifecycle` lisää kaksi append-only-taulua. Se ajetaan samassa nykyisessä Compose/Codespaces-startupissa ennen readiness-tilaa. Se ei muuta vanhoja tuotteita, julkaisuja, profiilisnapshotteja tai fixtureitä. Varmuuskopiointi- ja pysäytysohjeet yllä säilyvät.

## Vaihe 2F: synteettinen JSON → RDF -muunnoskokeilu

Kirjaudu `vero` / `demo-vero`, avaa **Omat luonnokset** ja **Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo)**. Tuotesivun **JSON → RDF -muunnoskokeilu** käyttää tallennettuja mappingeja. Valitse **Täytä synteettinen kolmen muodon esimerkki**, vahvista synteettisyys ja valitse **Muunna ja vertaa RDF-sisältöä**. Kaikki kolme tuottavat saman RDF-sisällön. Muuta SD-JWT-esimerkin nimeä: graafit eroavat. Anna nimen arvoksi null: muunnos hylätään. Mapping-muutokset on tallennettava ensin; vanha If-Match estää vanhentuneen kokeilun.

Syötteet, RDF ja raportti ovat vain esikatselussa; niitä ei tallenneta katalogiin tai hyväksyntään. Sivun uudelleenlataus tyhjentää ne. Vanhoja julkaisuja tai fixtureitä ei täydennetä. Planned-palvelut säilyvät planned-tilassa. Kokeilu toimii myös yksittäisellä esimerkillä, mutta ei silloin väitä tehneensä graafivertailua. Edellytyksenä ovat uusi distributions-kuvaus ja yhteinen profiili; vanha issuance näkyy edelleen entisellään.

W3C-syöte on vain mappingin sisältöpolun mukainen olio (esimerkiksi credentialSubject), SD-JWT-syöte erillinen synteettinen väiteolio. Kokonaisia todistuksia, JWT:itä, disclosureja tai salaisuuksia ei käsitellä. JSON API:n liitetyt lukitut skeemat, muunnos ja SHACL raportoidaan erikseen. VC-kuorta, JSON-LD-kontekstin laajennusta ja kryptografiaa ei tarkisteta. [Muunnossopimus ja tarkat rajat](docs/phase-2f.md): yksi juuriluokka, sisäkkäiset oliot, järjestyksettömät moniarvoiset ominaisuudet ja eksplisiittiset XSD-tyypit. Null, kartoittamattomat kentät, häviävät toistuvat literaalit ja tukemattomat rakenteet estävät onnistumisen. Decimal annetaan tarkkana merkkijonona. Vain 1–3 synteettistä esimerkkiä, 100 kB per sisältö / 200 kB yhteensä; verkoton prosessi CPU 5 s / muisti 512 MiB / seinäkello 15 s.

API: `POST /api/v1/drafts/{draftId}/conversion-preview`, body `{"examples":[{"distributionId":"UUID","content":"JSON-teksti","synthetic":true}]}`. Vaatimuksina ovat omistajaorganisaation editor-istunto, CSRF ja nykyinen If-Match. Vastauksen sidonta yksilöi luonnoksen revision/tarkisteen, snapshotin UUID/SHA-256:n sekä mapping- ja syötetarkisteet. Tulosta ei hyväksytä asiakkaan asettamaksi julkaisutodisteeksi. Vaiheen 2D/2E julkaisuehdot säilyvät.

## Vaihe 2E: toimitustavat ja koneluettavat sopimukset

`distributions` on enintään kymmenen tyypitetyn kuvauksen kokoelma (`jsonApi`, `w3cVc`, `sdJwtVc`). `primaryDistributionId` valitsee ensisijaisen; W3C VC on oletus, kun se on mukana. Formaatti, protokolla ja suojausprofiili ovat erillisiä. Omat availability/environment- ja organisaatiokentät, yhteinen profileSnapshotId sekä mapping.version/entries kuvataan jokaiselle. Katalogi ei vaadi kolmea erillistä lähdeintegraatiota: sama lähde-API voi palvella molempia myöntämiskonfiguraatioita.

API-sopimus kenttineen on `/docs`:ssä. `fixtures/distributions-demo.json` näyttää kaikkien kolmen syöttörakenteen. Käytä oman profiilisnapshotin ja organisaatioiden UUID:ita. Palvelin sitoo saman snapshotin kaikkiin toimitustapoihin; poikkeava viite hylätään. Raportit, julkaisuversio ja profileSnapshotSha256 ovat palvelimen kenttiä, eivät syöttöparametreja. `distributionBindings` lukitsee julkaisuun saman profiilitarkisteen ja tuoteversion sekä mapping-versiot.

JSON API:n käyttökuvaus sisältää palveluosoitteen, OpenAPI- ja JSON Schema -artefaktien UUID:t, none/oauth2/apiKey/mtls-tunnistautumistavan, tarvittavat oikeudet ja ajantasaisuuden. W3C VC sisältää VCDM 2.0 -tyypit/kontekstit; SD-JWT VC sisältää vct:n, profiiliversion, paljastamis- ja haltijasidontakäytännöt. Todistusjakeluilla on erilliset konfiguraatiot, suojaus-, voimassaolo- ja tilatietoprofiilit. Samalle OpenID4VCI-palvelulle voi kuvata molemmat muodot. Tokenit, tunnistautumissalaisuudet ja käyttäjäkohtaiset tarjoukset eivät kuulu kenttiin.

Sisäkkäisen mappingin semanticPath on alkuperäisten IRI:en ketju. Vanhemman valueKind on object, lapsella literal/object ja oikea datatype/classUri. Suojaus, oikeudellinen luokka ja lompakkonäyttö ovat erillisiä. Metadata-/mapping-tarkistus ei jäsennä JWT:tä, tarkista allekirjoitusta tai osoita palvelun saavutettavuutta. Rekursiiviset/monimutkaiset mapping-polut jäävät tässä profiilissa arvioimatta ja estävät uuden julkaisun. [Ratkaisukuvaus ja integraation hyväksymiskriteerit](docs/phase-2e.md) erittelevät rajat.

Vanha issuance-luku ja vanhojen luonnosten kirjoitus säilyvät. Uudessa kuvauksessa distributions on määräävä. Kokoelman hiljainen pudottaminen vanhaan issuance-malliin estetään. Jo julkaistuja 2C/2D-versioita ei kirjoiteta uudelleen. Sama varmuuskopio/rebuild toimii; relaatiomigraatiota ei tarvita, head pysyy 0004_publication.

### JSON Schema- ja OpenAPI-johdannaiset

Tuontilomakkeen **Valinnainen JSON-johdannainen** voi liittää yhden JSON-muotoisen teknisen kuvauksen ja erillisen semanticMappings-tiedoston samaan SHACL-snapshotiin. API tukee useita. Esimerkit: `derived-schema-demo.json` (draft-07), `derived-openapi-demo.json` (OpenAPI 3.0.3), `derived-mappings-demo.json` ja `derived-example-demo.json` fixtures-hakemistossa. OpenAPI-valinta on `/components/schemas/DemoCompany`; JSON Scheman tyhjä schemaPointer tarkoittaa juurta. Codespacesissa lataa tiedostot Explorerin **Download**-toiminnolla ennen selaimen tiedostovalintaa.

`derivedExamples` antaa liitetylle artefaktille artifactId:n, JSON-sisällön ja synthetic:true-vahvistuksen. Palvelin tarkistaa alkuperäisen dialektin, JSON-esimerkin sekä erillisen rajatun suoran kenttävertailun. Tämä ei korvaa distributions.mappingin sisäkkäistä metadataa. Valmiissa neljännessä esimerkissä molemmat johdannaiset ja esimerkit ovat mukana. Aiemmin aloitettu johdannaistarkistus ei ole JWT:n eikä kryptografian tarkistus; 2F:n rajattu sisältöolioiden RDF-esikatselu toimii erillisessä muunnoskokeilussa. Varsinainen lähde-/VC-integraatio jää vaiheeseen 3.

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
.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_derived_validation.py tests/test_distributions.py tests/test_conversion.py tests/test_technical_packages.py tests/test_attribute_semantics.py tests/test_lifecycle.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q
```

Älä aja tätä testikantaa käyttäviä pytest-ajoja rinnakkain. `TEST_DATABASE_URL` voi muuttaa yhteysosoitetta mutta kannan pitää olla `catalog_test`. Selaintestit käyttävät erikseen käynnistettyä demoa ja oikeaa Keycloak-kirjautumista:

```bash
.venv/bin/playwright install --with-deps chromium
BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q
```

Valmista paikallista Chromiumia käytetään automaattisesti; `CHROMIUM_EXECUTABLE` voi nimetä sen. Selaintestit luovat yksilöidyn testituotteen; julkaisutesti jättää muuttumattoman synteettisen julkaisun historiaan. Alkuperäisiä kolmea demotuotetta ei muuteta. Ilman `BROWSER_BASE_URL`-asetusta kolmetoista selaintestiä ohitetaan. Täysi ajo: `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest -q`. GitHub Actionsin etätulos varmistetaan erikseen.

Tässä pilviympäristössä Docker-build käyttää alustan proxy-/CA-reittiä: `./scripts/cloud-build.sh`, sitten `docker compose up -d --no-build --wait`. Tavallisen Docker Desktopin komento on yllä oleva `docker compose up --build`. Kirjoitussuojatun kotihakemiston yhteydessä aseta `UV_CACHE_DIR=/workspace/.cache/uv`, `npm_config_cache=/workspace/.cache/npm`, `DOCKER_CONFIG=/workspace/.cache/docker`. Nämä eivät kuulu Windowsin normaaliin käynnistykseen.
