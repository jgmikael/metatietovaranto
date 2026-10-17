# Vaihe 2H: SHACL-pohjaiset tekniset kuvauspaketit

**Avoin yhdistämisen este:** käyttäjän vaatima aidon muuttamattoman Tietomallit-exportin koe puuttuu verkkonoutoeston vuoksi. Alla erotellaan toteutuksen testitulokset tästä avoimesta hyväksymiskriteeristä.

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

Aidosta muuttamattomasta Tietomallit-exportista ei voitu tehdä hyväksymiskoetta (HTTP 403); virallisen työkalun migraatiotestifixture ja erillinen suppea projektio testattiin, eikä niitä nimetä aidoksi exportiksi. Windows Docker Desktopia, oikean uuden Codespacen luontia/automaattista selainavausta/Private-portin ajonaikaista tilaa, ulkoisen pysyvän HTTPS-palvelun noutoa tai GitHub Actions -ajoa ei voitu varmistaa tässä ympäristössä. `.devcontainer`, Compose-portit ja toimitetut Alembic-revisiot säilyvät muuttumattomina. Kuorma-/tietoturva-auditointia tai ulkoisen myöntäjän/allekirjoituksen/lompakon integraatiotestejä ei ajettu; ne eivät ole tämän paikallisen generointivaiheen toteutusväitteitä.


## Avoin hyväksymiskriteeri ja yhdistämisen este

**Aidon julkisen, muuttamattoman Tietomallit-exportin hyväksymiskoe on tekemättä.** Tietomallit/iri.suomi.fi:n ja IETF archive/datatrackerin suorat verkkonoudot estyivät ympäristössä HTTP 403:lla. Viralliset Git-repositoriot toimivat: IETF-profiili lukittiin OAuth-työryhmän julkaistuun `draft-ietf-oauth-sd-jwt-vc-19`-tagiin, ei oletettu RFC:ksi.

`fixtures/tietomallit/fi-dcatap-upstream.ttl` on tavuntarkka virallisen työkalurepositorion migraatiotestiaineisto (commit/tarkiste/provenance mukana). Siinä on testimuokkauksia, joten se **ei täytä aidon muuttamattoman exportin vaatimusta**. Koko aineisto hylätään oikein tukemattomien sh:in/pattern-rajoitteiden vuoksi; erikseen merkitty suppea projektio testaa kansallisen shape-IRI:n ja ulkoisen dct:modified-IRI:n säilymisen. Alkuperäistä tiedostoa ei muokata.

En suosittele yhdistämistä ennen kuin oikea julkinen export saadaan, alkuperä ja tarkiste lukitaan ja vastaava realistisen aineiston testi ajetaan. Lisäksi GitHub Actionsin vaadittujen tarkistusten tulee läpäistä. PR on tarkoitettu tarkastettavaksi; automaattista yhdistämistä ei tehdä.
