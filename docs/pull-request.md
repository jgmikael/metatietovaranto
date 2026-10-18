# Vaihe 2H: SHACL-pohjaiset tekniset kuvauspaketit

**Aineistokoe täydennetty 18.10.2026:** käyttäjän toimittama WE BUILD Certificate of Residence 0.0.2 on tallennettu muuttamattomana ja testattu. Koko profiili estyy puuttuvien literaalityyppien ja SKOS-riippuvuuden vuoksi; erillinen, eksplisiittisesti synteettinen testiprojektio läpäisee JSON-LD/RDF/SHACL-ketjun. [Alkuperä, havainnot ja rajoitteet](webcor-acceptance.md). Tämä toteuttaa toimeksiannon sallitun rajatun aineistokokeen, ei koko webcor-profiilin generointitukea.

## Muutos ja rajaus

Aiemmin ylläpitäjä joutui kuvaamaan kunkin toimitustavan tekniset kentät erikseen. Nyt hän valitsee lukitusta SHACL-profiilista yhden juuren, tarkastaa yhteiset tekniset nimet ja esitysvalinnat sekä muodostaa niistä versionhallittavan kuvauspaketin. W3C VC, SD-JWT VC ja JSON käyttävät samoja semanttisia ominaisuuksia ja SHACLista luettuja tyyppejä/kardinaliteetteja.

Paketti sisältää JSON-LD 1.1 -kontekstin, yhteisen JSON Scheman, IETF draft-19 Type Metadatan, erillisen semanttisen mappingin, synteettiset JSON-/väite-/allekirjoittamattomat VC-esimerkit ja tarkistettavan manifestin. PyLD:n oikeasti muodostama RDF verrataan odotettuun graafiin ja validoidaan lähde-SHACLilla. Ulkoisia konteksteja ei noudeta; VCDM 2.0:n peruskonteksti on erillinen lukittu aineisto.

Tämä toteuttaa käyttäjän täsmentämän 2H:n. DCAT-AP-viennit eivät kuulu muutokseen. Lähdetietopalvelu, tunnistaminen, asiointivaltuudet, myöntämispäätös, allekirjoitukset, disclosuret, haltijasidonnan toteutus ja lompakkotoimitus jäävät ulkoiselle tarjoajalle/myöntäjälle.

## Turvarajat ja yhteensopivuus

- Yksi eksplisiittinen juurimuoto ja targetClass, suorat ominaisuus-IRI:t, tuetut eksplisiittiset XSD-literaalit, yksiselitteiset sisäkkäiset oliot ja järjestyksettömät taulukot. [Täsmällinen generointiprofiili ja estävät havainnot](phase-2h.md).
- Tekniset nimet eksplisiittisestä lähdetiedosta tai deterministisesti alkuperäisestä IRI:stä; näyttötekstien käännökset eivät muuta nimiä. Törmäykset ja VCDM/JWT-varatut nimet estetään. Käyttäjä voi hyväksyä esitysvalinnan, mutta ei muuttaa SHACL-tyyppejä/kardinaliteetteja generaatiopyynnössä.
- Luonnoksen omistajan editor, tallennuksessa myös tarjoajan editor, lähdeprofiilin nykyinen lukuoikeus, palvelinistunto, CSRF ja If-Match. Publisher/reader eivät saa uutta kirjoitusoikeutta.
- Mappingien korvaaminen ja muotokohtaiset asetukset hyväksytään eksplisiittisesti. Muuttunut mapping vaatii suuremman version. Per-claim-päätökset ja aina näkyvien väitteiden polut tarkistetaan yhteisiä nimiä vasten.
- Generointi on auditoitu luonnosmuutos ja mitätöi hyväksynnän. Sidottujen syötteiden myöhempi muutos merkitsee paketin vanhentuneeksi ja estää hyväksynnän/julkaisun. Epäonnistunut generointi ei korvaa aiempaa pakettia.
- Paketin artefaktit tulevat julkisiksi vain muuttumattoman ProductVersionin kautta; withdrawn ei poista niitä. Vanhoja julkaisuja/profiilisnapshotteja tai fixtureitä ei kirjoiteta uudelleen. Vanha paketiton julkaisupolku säilyy.
- JSONB riittää, **ei uutta tietokantamigraatiota**; Alembic head `0005_lifecycle`. Käynnistyksen migraatiopolku, Codespacesin openBrowser ja Private-portti säilyvät.
- Käyttöliittymä tukee useita OWL-sanastoviitteitä sijainteineen/versioineen ja riippuvuustiedostoja. Alkuperäiset kansalliset/ulkoiset IRI:t ja vastaavuusviitteet säilyvät lähdeaineistoissa ilman OWL-päättelyä tai termien automaattista korvaamista.

## Konkreettinen ketju, joka todella ajettiin

Tässä ketjussa lähde on **synteettinen Tietomallit-muotoinen SHACL-fixture**, ei todistettu oikea alustalta viety profiili:

1. `fixtures/semantic-profile-demo.ttl`: ProductShape → Company; `companyName` → alkuperäinen `https://example.org/metatietovaranto/demo/companyName`, xsd:string, minCount=maxCount=1.
2. Oikealla `vero`-OIDC-kirjautumisella uusi testituote olemassa olevan kolmen toimitustavan luonnoksen pohjalta. Mapping-ehdotus tarkastetaan selaimessa, yhteinen nimi `companyName`, W3C-polku `/credentialSubject/companyName`, JSON-/SD-JWT-polku `/companyName`, mapping-versio `1.1.0`. Vanhan SD-JWT-nimen korvaaminen hyväksytään erikseen.
3. Synteettinen sisältö `{"companyName":"Synteettinen Esimerkki Oy"}` → JSON-LD-konteksti + Type Metadata (`path:["companyName"]`, `sd:"always"`) + erillinen schema/mapping.
4. JSON Schema, PyLD-laajennus ja RDF-isomorfia, sisältögraafin sekä koko allekirjoittamattoman VC-esimerkin lähde-SHACL: läpäisevät. Paketti tallennetaan, sivu ladataan uudelleen ja tavut tarkistetaan.
5. Oikealla erillisellä `yritys`-OIDC-käyttäjällä artefaktien tarkastus, normaali hyväksyntä ja version `1.0.0` julkaisu. Pysyvä `/id/technical-packages/{packageId}/context.jsonld` palauttaa kontekstin application/ld+json-muodossa; ennen julkaisua sama osoite palauttaa 404.

Paikallisen tarkistuksen konkreettinen julkaisu oli `32a69862-a5e5-4a8b-ba5a-d6f4455bce2a@1.0.0`, paketti `e8aa36c3f935fee13b305d6c71961a7777d46145b91af92668b51ea859309525`, lähdesnapshotin SHA `e52039c7417a8869bee8a315f8d1884ce007c25886ca8082966e9c8b69a62749` ja kontekstin SHA `e0948d85e9fee6ab902aaeab9a4472e2a50ef1ceb66b22105e95f2b17109da69`. Nämä tunnisteet kuuluvat tarkistusympäristöön, eivät uuden Codespacen fixtureihin. Sama ketju on toistettava README:n alun kokeilupolulla omassa Codespacessa. Paikallinen demo käyttää http://localhost:8000-osoitetta. Codespacesin artefaktit käyttävät sen HTTPS-alkuperää, mutta **Private-portti estää ulkoisen myöntäjän anonyymin noudon**. Tuotannollinen käyttö vaatii pysyvän HTTPS-julkaisualustan.

## Ajetut tarkistukset

### Aineistokokeen täydennys 18.10.2026

- `pytest tests/test_technical_packages.py -k webcor -q`: **8 passed, 34 deselected**. Alkuperäiset tavut/tarkiste, viisi juurta, API-tallennus/eston säilyminen sekä erillinen PyLD + odotettu RDF + projektion/alkuperäisen lähteen SHACL offline.
- Perus-2H:n koko README/CI:n 12 tiedoston API-/PostgreSQL-/migraatiosarja: **189 passed, 4 warnings in 318.14s (0:05:18)**. Ei epäonnistuneita tai ohitettuja. Sisältää kaikki aiemmat 181 testiä ja 8 uutta aineistotapausta; oikeudet, hyväksyntä, muuttumattomat julkaisut ja vanhan/tyhjän kannan migraatiot säilyivät. Kohdennettu ajo ei ole lisätestimäärä tämän päälle.
- Sovelluskoodi, skeemamigraatiot ja käyttöliittymä eivät muutu tässä täydennyksessä. Web-buildia, Docker-imagea ja selaintestejä ei ajettu uudelleen; aiemmat tulokset alla ovat alkuperäisen 2H-toteutuksen ajoja, eivät tämän täydennyksen uusia ajoja. Ensimmäisen kohdennetun ajon järjestysoletus Type Metadatan claims-listasta korjattiin molempien polkujen sisältymistarkistukseksi; lopullinen koe läpäisee.

### Alkuperäisen 2H-toteutuksen ajot

- Koko API-/PostgreSQL-/migraatiosarja (README/CI:n 12 tiedostoa): **181 passed, 4 warnings in 298.49s (0:04:58)**. Ei epäonnistuneita tai ohitettuja. Mukana tyhjä/legacy-kanta, toistuvat migraatiot/startup, oikeudet, CSRF, ETag/idempotenssi, SHACL/johdannaiset, hyväksyntä, immutable-julkaisut ja elinkaari.
- Uuden pakettimoduulin erillinen korjauksen jälkeinen ajo: **34 passed**; nämä sisältyvät yllä olevan täyden ajon 181 testiin. Mukana determinismi, kymmenen literaalityyppiä, sisäkkäisyys/moniarvoisuus, varatut/törmäävät nimet, alkuperäiset IRI:t, useat sanastot/lukitut riippuvuudet, Type Metadata, luku-/kirjoitusoikeudet, nykyinen tarjoaja, hyväksynnän mitätöinti ja julkiset artefaktit.
- Oikea Chromium + Keycloak, lopullista Docker-toteutusta vasten: **13 passed, 1 warning in 99.15s (0:01:39)**. Mukana aiemmat 12 selainpolkua ja uusi 2H:n editori → mapping-ehdotus → generointi → tallennus/reload → eri käyttäjän hyväksyntä → julkaisu → artefakti sekä mapping-taulukon mobiilileveys.
- **194 eri pytest-testiä** yhteensä; erillistä 34 testin ajoa ei lasketa uudelleen. Starlette/httpx- ja RDFLib-varoitukset eivät ole ohituksia.
- `uv sync --locked`, `npm ci --prefix apps/web` ja `npm run build --prefix apps/web`: läpäisivät. PyLD 2.0.4 ja transitiiviset riippuvuudet lukittu uv.lockiin.
- `bash scripts/cloud-build.sh` ja `docker compose up -d --no-build --wait`: läpäisivät; TLS-tarkistuksia ei poistettu. Käynnissä olevan imagen **34 lähde-/migraatio-/web-build-/standardiaineisto-/lock-tiedoston** SHA:t vastasivat checkoutia.
- Myös `docker compose up --build -d --wait` todella yritettiin tässä tehtävässä: **epäonnistui build-kontin DNS-virheeseen** (`Temporary failure in name resolution`, pip/uv). Tätä ei ilmoiteta läpäisseeksi. Pilviskripti käyttää ympäristön olemassa olevaa proxy-/CA-reittiä; sama lähde rakentui sillä ja käynnistyi.
- Käytössä olevan `catalog`-kannan 13 metatietotaulun kokonaissisältötarkisteet säilyivät lopullisen imagen restartin yli (ennen viimeistä selainajoa): 66 tuotetta/luonnosta, 59 muuttumatonta julkaisua, 34 profiilisnapshotia, 3 organisaatiota ja 5 jäsenyyttä. Kaikkien **59 julkaisun** sisältötarkiste ja version API vastasivat alkuperäistä; myös yksi varhainen 2C-versio ilman versionUriä. **45 julkista artefaktia** tarkistettiin. Varsinaista demokantaa ei tyhjennetty, auth-istuntoja ei kopioitu.
- Alembic head edelleen `0005_lifecycle`; `alembic check`: **No new upgrade operations detected**. Ei uutta skeemamigraatiota. Startup/tyhjä/vanha kanta testattu; fixturet eivät palaudu tavallisessa restartissa.
- Erillinen julkaistun paketin toimintakoe: yhdeksän artefaktia haettiin oikeista julkisista reiteistä, tavut/tarkisteet tarkistettiin. HTTP:llä haettu konteksti käsiteltiin PyLD:llä **lukitulla paikallisella lataajalla**, RDF vastasi käsin kirjoitettua odotettua graafia ja läpäisi julkaisun alkuperäisen SHACL-snapshotin. Lähteen manifestin SHA vastasi julkaistun paketin viitettä. Tämäkin käytti synteettistä aineistoa.
- Aiemman koko ajon löytämä nykyisen tarjoajan oikeustarkistuksen virhe korjattiin; yllä olevat lopulliset API-tulokset sisältävät regressiotestin. Ensimmäisen uuden selainajon valitsinvirhe korjattiin; lopullinen 13 testin ajo läpäisi.

### Ajamattomat tai varmistamatta jääneet

Alkuperäisessä ajossa nouto puuttui; 18.10. käyttäjän toimittamalla exportilla tehty koe on kuvattu yllä. Riippumatonta verkkopalveluun vertailua ei voitu tehdä (403). Windows Docker Desktopia, oikean uuden Codespacen luontia/automaattista selainavausta/Private-portin ajonaikaista tilaa, ulkoisen pysyvän HTTPS-palvelun noutoa tai GitHub Actions -ajoa ei voitu varmistaa tässä ympäristössä. `.devcontainer`, Compose-portit ja toimitetut Alembic-revisiot säilyvät muuttumattomina. Kuorma-/tietoturva-auditointia tai ulkoisen myöntäjän/allekirjoituksen/lompakon integraatiotestejä ei ajettu; ne eivät ole tämän paikallisen generointivaiheen toteutusväitteitä.


## Aineistokokeen tulos ja yhdistämisjärjestys

Käyttäjän toimittama alkuperäinen export on `fixtures/tietomallit/webcor-0.0.2/original.ttl`, 29 811 tavua / 429 kolmikkoa. SHA-256 on `2ad4331272558bb541b7804f194a74e261d8313985554015ccc4e23785286133`. Profiili-/versio-IRI ja owl:versionInfo täsmäävät käyttäjän ilmoittamaan 0.0.2:een. Alkuperä on käyttäjän ilmoittama tiedostovienti, ei riippumaton palvelusta noudettu vertailu; tiedostoreitti ei edellytä lisäksi toimivaa verkkonoutoa.

Kaikki 24 literaaliominaisuutta ovat ilman sh:datatypea. SKOS owl:imports on unresolved. Kaikki viisi juurimuotoa tuottavat hallitun eston, ja API estää valmiin paketin/tarkastukseen lähetyksen. Alkuperäistä mallia ei täydennetä arvauksilla. Koneellinen raportti ja alkuperä ovat lukittuina fixtureiden vieressä.

Erillinen `family-name-test-projection.ttl` säilyttää Person/familyName-käyttöyhteyden ja alkuperäiset IRI:t mutta lisää **paikallisen xsd:string-testioletuksen**, jota ei ole lähteessä. Se ei ole julkaistava alkuperäinen 0.0.2-profiili: sillä on eri profiili-identiteetti ja paikallinen testiversio. Rajoittamattoman kardinaliteetin JSON-esitys säilyy valinnaisena taulukkona. Oikean JSON-LD-prosessorin graafi vastaa käsin kirjoitettua odotetta ja läpäisee projektion sekä alkuperäisen SHACLin offline-tarkistuksen yhdellä Person-fokussolmulla. SKOSia ei haeta eikä lähteen puuttuvia rajoitteita väitetä tarkistetuiksi.

Tämä täyttää 2H-toimeksiannon vaihtoehdon: aidon aineiston rajoitukset raportoidaan ja rajattu tapaus testataan erikseen. Aiempi puuttuvan export-kokeen este on siten käsitelty. PR #12:n GitHub Actionsin vaadittujen tarkistusten ja katselmoinnin tulee edelleen läpäistä ennen yhdistämistä. Sen jälkeen jatko-PR #13:n pohja vaihdetaan mainiksi ja tarkistetaan; sen ETSI-/EU-alkutekstipuutetta ei suljeta tällä kokeella. Ei automaattista yhdistämistä.
