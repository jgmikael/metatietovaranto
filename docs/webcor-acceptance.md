# 2H:n realistisen aineiston hyväksymiskoe: WE BUILD Certificate of Residence

18.10.2026. Käyttäjä toimitti Tietomallit-työkalusta ladatun Turtle-tiedoston, osoitteen <https://iri.suomi.fi/model/webcor/> ja version **0.0.2**. Tämä täydentää perus-2H:n PR:n #12 aiemmin avoimen aineistokokeen. Toimeksianto sallii tuetun generointiprofiilin ylittävän aidon aineiston rajoitteiden raportoinnin ja erillisen rajatun kokeen; koko profiilin generointia ei sen perusteella väitetä tuetuksi.

## Alkuperä ja eheys

- Alkuperäinen tiedostonimi: `WE BUILD Certificate of Residence.ttl`.
- Tavuntarkka vastaanotettu kopio: `fixtures/tietomallit/webcor-0.0.2/original.ttl`.
- Koko **29 811 tavua**, SHA-256 **2ad4331272558bb541b7804f194a74e261d8313985554015ccc4e23785286133**.
- Profiili-IRI: `https://iri.suomi.fi/model/webcor/`.
- Tiedoston owl:versionInfo on `0.0.2`, owl:versionIRI on `https://iri.suomi.fi/model/webcor/0.0.2/`. Tila on lähteen mukainen SUGGESTED.
- Käyttäjän ilmoitus ja aineiston sisäiset tiedot täsmäävät. Alkuperä on **käyttäjän ilmoittama alustalta ladattu tiedosto**, ei riippumattomasti verkkopalveluun verrattu tiedosto. Suora verkkonouto saa edelleen ympäristössä 403:n; tiedostoreitti ei edellytä lisäksi onnistuvaa verkkonoutoa.
- Provenienssi ja erillisen testiprojektion muutokset/tarkiste ovat saman hakemiston `provenance.json`-tiedostossa. Lähde sisältää julkisen mallin ylläpitometatietoja, ei testattavia oikeiden henkilöiden asuinpaikkatietoja. Kaikki kokeen sisältöarvot ovat synteettisiä.

Alkuperäistä tiedostoa, sen IRI:jä, metatietoja tai rajoitteita ei korjata, typistetä eikä täydennetä. Aiempi `fi-dcatap-upstream.ttl` jää erilliseksi työkalurepositorion migraatiotestiaineistoksi; sitä ei nimetä tämän exportin korvikkeeksi.

## Koko alkuperäisen profiilin tulos

Graafissa on **429 kolmikkoa, 5 NodeShapea ja 29 PropertyShapea**. Juurimuodot ovat Address, Identifier, Jurisdiction, Location ja Person webcor-nimiavaruudessa. Niiden kohdeluokat ja ominaisuuksien `sh:path`-IRI:t säilyvät alkuperäisessä eu-core-nimiavaruudessa.

**Koko aineistosta ei muodostu valmista teknistä pakettia:**

1. Kaikilta **24 owl:DatatypeProperty-tyyppiseltä ominaisuusmuodolta puuttuu sh:datatype**. Myöskään minCount/maxCount-rajoitteita ei ole. Generaattori ei päättele tietotyyppiä ominaisuuden nimestä, esimerkistä tai OWL-range-päättelyllä. Kaikkien viiden juuren mapping-ehdotus estyy yksilöidyllä `OBJECT_AMBIGUOUS`-havainnolla ja alkuperäisen eu-core-ominaisuuden polulla. Tämä on nykyisen moottorin yleinen puuttuvan literaalityypin/oliorakenteen havainto; se ei väitä lähteen DatatypePropertya ObjectPropertyksi.
2. Tiedosto ilmoittaa `owl:imports skos:`. Lukittu SKOS-riippuvuustiedosto ei sisälly toimitukseen. Tuonti säilyttää lähteen, merkitsee riippuvuuden unresolved-tilaan ja snapshotin needsAttention-tilaan. Varsinainen pakettigenerointi estyy `SOURCE_NOT_READY`-havainnolla ennen paketin muodostusta. Verkosta ei haeta puuttuvia aineistoja.
3. Alkuperäiset `dcterms:requires`-viitteet ncbv 0.0.7-, eu-core- ja webuild-malleihin säilyvät. Niiden sisältöä ei ole toimitettu tai noudettu; viittaus ei merkitse riippuvuuden sisällön tarkistamista. Nykyinen lukittujen riippuvuuksien automaattinen unresolved-tarkistus kattaa owl:importsin ja sh:noden, ei kaikkien dcterms:requires-sanastojen täydellistä sisältöanalyysiä.

Koneellinen luettelo löytyy `coverage.json`-artefaktista testiaineiston vierestä. Julkaisuun ei lisätä tätä aineistoa tai paketteja taustalla. API-testissä alkuperäinen tiedosto tallentuu tavuntarkasti, epäonnistunut generointi säilyttää luonnoksen ennallaan ja tarkastukseen lähettäminen estyy. Rajoituksia ei ohiteta muuttamalla snapshotia tai merkitsemällä pakettia valmiiksi.

## Erillinen rajattu koe

`family-name-test-projection.ttl` on **synteettinen paikallinen testiprojektio**, ei uusi alkuperäiseksi väitetty Tietomallit-export eikä alkuperäisen profiilin hyväksytty päivitys.

- Säilytetään alkuperäiset webcor:Person-, webcor:familyName-, eu-core:Person- ja eu-core:familyName-IRI:t sekä niiden SHACL-suhteet.
- Muut luokat/ominaisuudet ja alkuperäisen ontologian tuonnit jätetään pois vain tästä erikseen nimetystä projektiosta.
- **Lisätään sh:datatype xsd:string paikallisena testioletuksena.** Tätä tyyppiä ei ole alkuperäisessä exportissa eikä sitä väitetä siitä johdetuksi. Alkuperäisen lähteen käyttäjä ei voi tehdä tätä muutosta generaattorin esitysvalinnalla.
- MinCountia/maxCountia ei lisätä: familyName esitetään valinnaisena järjestyksettömänä taulukkona. Alkuperäisen puuttuvaa kardinaliteettia ei keksitä skalaariksi tai pakolliseksi kentäksi.
- Testiprofiilin tunniste on erillinen `urn:metatietovaranto:test:webcor-family-name` ja versio `0.0.2-local-test-1`, ei webcor-profiilin alkuperäinen 0.0.2-identiteetti.

Testisisältö `{"familyName":["Synteettinen Testiperhe"]}` kulkee generaattorin läpi. Syntyvät konteksti, JSON Schema, Type Metadata ja mapping. Type Metadatan alkion Claim Path on `["familyName",null]`, säiliön polku `["familyName"]`. Oikea PyLD-prosessori ja lukittu paikallinen kontekstilataaja muodostavat RDF:n. Graafi vastaa isomorfisesti käsin määriteltyä odotetta:

```turtle
[] a <https://iri.suomi.fi/model/eu-core/Person> ;
   <https://iri.suomi.fi/model/eu-core/familyName> "Synteettinen Testiperhe" .
```

Graafi tarkistetaan sekä paikallisen testiprojektion että **alkuperäisen muuttamattoman SHACL-graafin** kanssa. Molemmissa on yksi todellinen Person-fokussolmu, joten kyse ei ole tyhjään kohdejoukkoon perustuvasta läpäisystä. Alkuperäisen graafin offline-tarkistus ei nouda sen SKOS-importtia eikä siten osoita riippuvuuksien täydellistä tarkistusta. Koska alkuperäinen graafi ei rajoita literaalityyppiä, sen läpäisy ei myöskään todista xsd:stringin olevan alkuperäisen lähteen vaatimus. Verkkoyhteydet estetään kokeessa, ja alkuperäiset tavut tarkistetaan vielä lopuksi.

## Ajettavat komennot ja tulokset

PostgreSQL-testikanta on vain `catalog_test`, ei käyttäjän demokanta. Käynnistä demon tietokanta README:n mukaisesti ja suorita repositorion juuressa:

```sh
.venv/bin/pytest tests/test_technical_packages.py -k webcor -q
```

Ajettu: **8 passed, 34 deselected, 1 warning in 5.45s**. Viisi juurimuotoa ovat erillisiä parametritapauksia; muut kolme testiä kattavat alkuperän, API:n eston ja rajatun oikean JSON-LD/RDF/SHACL-ketjun. Deselected tarkoittaa kohdennetun komennon ulkopuolelle rajattuja vanhoja testejä; ne ajetaan koko regressiosarjassa.

Perus-2H:n koko README/CI:n 12 tiedoston API-/PostgreSQL-/migraatiosarja: **189 passed, 4 warnings in 318.14s (0:05:18)**. Ei epäonnistuneita tai ohitettuja. Sisältää kaikki aiemmat 181 testiä ja 8 uutta aineistotapausta; oikeudet, hyväksyntä, muuttumattomat julkaisut ja vanhan/tyhjän kannan migraatiot säilyivät. Kohdennettu ajo ei ole lisätestimäärä tämän päälle.

## Merkitys yhdistämiselle

Aiempi **puuttuvan aidon aineiston kokeen** este on käsitelty tämän tehtävän sallimalla tavalla: alkuperäinen export on lukittu, koko aineiston raja on raportoitu ja erillinen rajattu koe on ajettu. Se ei lupaa koko WE BUILD 0.0.2 -profiilin generointia. Koko profiilin toimiva generointi vaatisi tietotyyppien hyväksytyt tarkennukset Tietomallit-työkalussa uutena lähdeprofiiliversiona ja riippuvuuksien lukituksen, tai erikseen suunnitellun generointiprofiilin laajennuksen. Tässä ei päätetä puuttuvia tietotyyppejä lähdemallin ylläpitäjän puolesta.

PR #12:n muut tarkistukset ja katselmointi on edelleen hyväksyttävä GitHubissa ennen yhdistämistä. PR #13:n ETSI-/EU-alkutekstien tarkistus jää erilliseksi avoimeksi asiaksi. Automaattista yhdistämistä ei tehdä.
