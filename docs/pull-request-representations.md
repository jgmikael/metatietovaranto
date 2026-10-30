# Rajattu kielimerkitty sisältö ja tarkastettavat IRI-viittaukset

`rdf:langString` esti aiemmin teknisen paketin generoinnin. Rekursiivisen assosiaation ainoa esitys oli sisäkkäinen olio, joka johti syklissä estoon. Nyt käyttäjä voi hyväksyä yhteisen value/language-esityksen ja valita assosiaatiolle IRI-esityksen silloin, kun lähde-SHACL sallii pelkän tyypitetyn kohdesolmun. Molemmat valinnat toimivat palvelimella ja Pagesin paikallisessa kokeilussa, myös ennen onnistunutta mapping-ehdotusta.

## Rajaus ja lähdeaineisto

- Palvelingeneraattori 1.2.0, selain 1.1.0, esitysprofiilit `valueLanguage-v1` ja `classOnlyIri-v1`. JSON Schema, JSON-LD-konteksti, RDF-muunnos ja SD-JWT:n semanttiset annotaatiot johdetaan samasta lähteestä ja samoista valinnoista.
- Kielipari on yksi kielimerkitty literaali, ei uusi sisältöolio. Kielitunnisteen rajattu BCP47-esitys edellyttää pienaakkosia; ei automaattista normalisointia, oletuskieltä, rekisterivarmennusta tai kaikkien BCP47-muotojen tukea.
- Viittaus tarvitsee yhden sh:class-IRI:n, yhteensopivan nodeKindin ja valinnaisen kohdesisällön. sh:node, pakollinen kohdesisältö, laajemmat kohderajoitteet, erityiskohdistukset, implisiittiset luokkakohdistukset, kohteen luokkahierarkia ja rdf:type-ominaisuusrajoitteet estetään konservatiivisesti. Instanssi-IRI ei saa olla kohdeluokan IRI. Ei verkosta haettavia kohteita.
- `rdfs:Literal` ei saa xsd:string-oletusta. Puuttuvaa sh:path-arvoa ei päätellä nimestä tai kohdeluokasta. Havainnot yksilöivät lähteen ja seuraavan toimenpiteen.
- Käyttäjän Ryhti AKR 1.0.5 -alkuperäisexport ja 62 hyväksyttyä termikorjausta säilyvät tavuntarkasti. Alkuperäinen SHA-256 `c41ae51575c63daca16fdbbc07cd619230c4db7be65ee4063b7e76342207ef02`; korjattu `74130d8b542ab11db403b88f393ac704d09334bda3bed93b6de2afe6891034c2`. Historiallista korjausraporttia ei kirjoiteta uudelleen.
- [Juurimuotokohtainen vertailu](https://github.com/jgmikael/metatietovaranto/blob/feat/langstring-iri-references/docs/ryhti-generation.md): 7/15 saa ehdotuksen sekä ennen että jälkeen. Asiakirjan kielieste poistuu hyväksytyllä esityksellä, mutta yleinen lainattu literaali estää kokonaisuuden edelleen. Kasittelytapahtuman ylaluokka-rajoitteen puuttuva polku jää lähdemallin ylläpitäjälle. Koko Ryhti-profiilia ei väitetä tuetuksi.

## Kaksi konkreettista onnistunutta esimerkkiä

1. `fixtures/representations/language.ttl` → hyväksytty valueLanguage-v1 → `labels: [{"value":"Hei","language":"fi"},{"value":"Hej","language":"sv"}]` ja sisäkkäinen `home.notes` → generoitu JSON-LD-konteksti tuottaa alkuperäisen labels-IRI:n kielilitteraalit `"Hei"@fi` ja `"Hej"@sv`. JSON Schema, Type Metadata ja mapping säilyttävät saman SHACL-kytkennän.
2. `fixtures/representations/reference.ttl` → tarkastettu parent-assosiaation IRI-valinta → `parent: ["https://synthetic.example/entities/parent"]` → JSON-LD @id-coercion ja kohteen erillinen `rdf:type https://example.org/representation/Entity`. Kohdeluokka ei korvaa instanssin tunnistetta. Pakollista sisältöä vaativa vastaava kohde hylätään.

Toista molemmat ilman tietokantaa tai tunnistuspalvelua:

```bash
uv sync --locked
uv run --locked python -m scripts.representation_examples --output /tmp/representation-examples
```

Molemmilla oikea lukittua paikallista lataajaa käyttävä JSON-LD-prosessori tuottaa odotetun RDF-graafin ja lähde-SHACL hyväksyy sisällön. Tuloste kertoo `jsonLd: isomorphic`, `shacl: conforms`, `status: ready`. Osoitteet ovat suunniteltuja esimerkkiosoitteita, eivät julkaisuja. Kahden ajon artefaktit ja packageId:t ovat samat. Ei allekirjoituksia, disclosureja tai lompakkotoimitusta.

## Todennus

- `.venv/bin/pytest tests --ignore=tests/test_browser.py -q`: **211 läpäisi**, 462.33 s. API, tietokanta, migraatiot, käyttöoikeudet, riippumaton tarkastus, hyväksynnän mitätöityminen, muuttumattomat julkaisut ja uudet esitysmuodot. Erillinen catalog_test-kanta; neljä nykyisten riippuvuuksien deprekaatiovaroitusta.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **13 läpäisi lopullista Docker-imagea vasten**, 144.97 s, oikea Keycloak; yksi nykyisen riippuvuuden deprekaatiovaroitus.
- Normaali web-build ja `bash scripts/build-pages.sh` läpäisivät; mukana ohjekääntäjän **3 testiä**. Viten >500 kB:n chunk-huomautus säilyy, build onnistuu. Contract-drift, ohjekääntäjän `--check` ja `git diff --check` läpäisivät.
- Lopullinen Docker-build onnistui, image `0fe5598e943e794509408fb412c49202146dcc368c64bb364f7b571dd01abc6b`. Terve käynnistys olemassa olevaan kantaan säilytti kaikkien 13 katalogitaulun rivimäärät/sisältöhashit ja Alembic-headin. HTTP-luku vertasi 149 aiempaa julkaisuversiota ja 22 paketin 246 artefaktin sisältöä/tarkisteita tallennettuihin tavuihin. Ei uutta migraatiota tai volumejen poistoa.
- Esimerkkikomennon kaksi uusintaa: **24/24 artefaktia identtisiä**, molemmat paketit ready, oikea paikallinen JSON-LD-graafivertailu isomorphic ja lähde-SHACL conforms. Tämä ei ole julkinen julkaisu.

`.venv/bin/pytest tests_static -q`: **179 läpäisi, ei ohituksia**, 300.90 s. Koko staattinen sarja kattaa todellisen Workerin, yhteisen selain-/palvelinsopimuksen, sisäkkäiset ja moniarvoiset kieliparit, virheelliset kielet, viittauksen riittävyyden ja resurssirajan, alkuperäiset IRI:t, korjausketjun, 15 todellista juurta, paikallisen tallennuksen/viennin/palautuksen ja paketin vanhenemisen. Oikea lukittu JSON-LD-prosessori tuottaa odotetut graafit ja riippumaton lähde-SHACL hyväksyy molemmat onnistumisesimerkit. Ensimmäinen kokonaisajo löysi puuttuvan kenttäkohtaisen ohjekytkennän (174 läpäisi / 1 epäonnistui); se korjattiin nykyistä ohjejärjestelmää käyttämällä. Korjauksen jälkeiset kokonaisajot 176 ja 177 läpäisivät. Uuden rdf:type-kohderajoitetestin ensimmäinen versio sai jo juuresta RESERVED_NAME-eston (178 läpäisi / 1 epäonnistui estokoodiodotuksesta). Kohdemuoto erotettiin juuresta, jotta testi osoittaa nimenomaan REFERENCE_UNSUPPORTED-eston; molemmat kohdistustestit läpäisivät. Tuotantokoodia ei muutettu tämän testiaineistokorjauksen vuoksi.

**Ajamattomat:** Firefox/Safari, Windows Docker Desktop, Codespaces-käynnistys, fyysinen mobiililaite ja oikea ruudunlukija. Ei GitHub Actions -ajoa, julkista Pages-deployta tai tämän version julkisen URL:n HTTP-varmennusta. Paikalliset selainkokeet käyttävät staattista HTTP-palvelinta /metatietovaranto/-alipolussa ja estävät kaikki API/auth/identity- sekä ulkoiset aineistopyynnöt. Pages-paketti ilmoittaa SHACL-validoinnin suorittamattomaksi; riippumaton testi ei muutu selaimen hyväksynnäksi. Koko Ryhti-mallin generointi jää tarkoituksella estetyksi lähdepuutteiden ja dokumentoitujen tukirajojen osalta. Nämä eivät ole puuttuvia korjauksia ohittamalla ratkaistavia yhdistämisesteitä.

## Yhteensopivuus ja kokeilu ennen yhdistämistä

Ei tietokantamigraatiota tai vanhojen snapshotien/pakettien taustamuutosta. Uusi valinnainen mapping-kenttä jätetään vanhasta serialisoinnista pois. Kokeilun v1-tuonti ja vanhan korjausraportin tarkisteketju säilyvät. Lähteen ja esitysvalintojen muutokset vanhentavat paikallisen paketin; onnistunut palvelingenerointi mitätöi luonnoksen hyväksynnän nykyisen oikeus-/tarkastusprosessin kautta.

```bash
git fetch origin
git switch feat/langstring-iri-references
uv sync --locked
npm ci --prefix apps/web
bash scripts/build-pages.sh
uv run --locked python -m scripts.preview_pages --port 4173
```

Avaa **http://127.0.0.1:4173/metatietovaranto/#kokeilu**, aloita oma kokeilu ja tuo jompikumpi fixtures/representations-hakemiston Turtle. Profiilitunniste `https://example.org/representation/profile`, juuri `https://example.org/representation/Root`. Kielitapauksessa hyväksy value/language-valinta; viittaustapauksessa lisää polku `https://example.org/representation/parent` ja valitse IRI-esitys. JSON-esimerkit löytyvät samannimisistä .json-tiedostoista. Tarkasta toimitustapojen asetukset ja hyväksy ne normaalisti. Pages-tulos on paikallinen kokeilu, ei riippumaton hyväksyntä tai julkinen julkaisu.

Palvelimen voi kokeilla saman haaran komennolla `docker compose up --build`, osoite **http://localhost:8000**; README sisältää nykyiset demotunnukset. Julkista Pages-deployta ei tehdä PR-haarasta. Mainia ei yhdistetä automaattisesti.
