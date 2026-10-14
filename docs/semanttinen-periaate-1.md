# Suunnitteluperiaate 1 Tietomallit soveltamisprofiili sisällön perustana

Päiväys 14.10.2026. Käyttäjän täsmennys Metatietovarannon suunnitteluun. Tämä päätös koskee ensimmäistä suunnitteluolettamaa; toista olettamaa ei ole vielä käsitelty. Dokumentti täsmentää tavoitearkkitehtuuria eikä väitä ominaisuuden olevan toteutettu vaiheessa 2B.

## Sitova lähtökohta

Jokaisen tietotuotteen semanttinen tietomalli perustuu Yhteentoimivuusalustan Tietomallit-työkalussa laadittuun soveltamisprofiiliin. Soveltamisprofiili on SHACL-muotoinen shapes graph, joka voi sisältää useita luokka- ja ominaisuusrajoitteita. Sen käyttämät luokat ja ominaisuudet perustuvat yhteen tai useampaan OWL-ydintietomalliin tai -sanastoon. OWL voi sijaita Tietomallit-työkalussa tai ulkoisessa nimiavaruudessa. Ulkoista OWLia ei tarvitse kopioida alustalle tai nimetä uudelleen.

Tämä on Metatietovarannon oma hyväksytty suunnitteluvaatimus. Se on tiukempi kuin yleinen mahdollisuus liittää katalogiin mikä tahansa tietomalli. Metatietovaranto kuvaa ja hyödyntää valmista soveltamisprofiilia; se ei toimi kilpailevana tietomallinnustyökaluna.

## Kaksi tasavertaista toimitustapaa

1. **Linkki:** ylläpitäjä antaa profiilin tunnisteen tai sivulinkin Tietomallit-työkaluun. Sivulinkki ja varsinainen koneluettava export-osoite erotetaan toisistaan. Sovellus ratkaisee tai ylläpitäjä täydentää version ja koneluettavan esityksen. Pelkkä HTML-sivu ei ole SHACL-aineisto.
2. **Tiedosto:** ylläpitäjä tuo Tietomallit-työkalusta ladatun exportin. Tiedostossa olevat alkuperäiset tunnisteet säilytetään, ja lähtöprofiili, versio sekä alkuperä tallennetaan. Käyttäjältä ei vaadita lisäksi toimivaa verkkolinkkiä, jos tarvittavat tiedot ja SHACL-aineisto saadaan tiedostosta. Puuttuva alkuperätieto merkitään täydennettäväksi, eikä sitä keksitä.

Linkkireitillä palvelu saa tallentaa noudetun aineiston muuttumattoman kopion versioon sitomista varten. Tämä ei tarkoita, että käyttäjän pitäisi toimittaa sekä linkki että tiedosto. Profiilin verkkopäivitys ei muuta jo käytettyä sisältöversiota automaattisesti.

## Formaattien merkitys

| Työkalun export | Rooli Metatietovarannossa |
| --- | --- |
| JSON-LD | RDF-esitys profiilin SHACL-graafista silloin, kun tiedosto sisältää profiilin varsinaisen kuvauksen. Pelkkä JSON-LD-konteksti ei riitä. |
| RDF | Työkalun RDF-export; tarkka serialisointi kuten RDF/XML tunnistetaan sisällöstä ja mediatyypistä. RDF on myös yleinen tietomalli, ei yksin tarkka tiedostomuoto. |
| Turtle | RDF-esitys profiilin SHACL-graafista. |
| OpenAPI | Profiilista tuotettu rajapintakuvaus. Voi edellyttää lähdeprofiilin API-polkujen määrittelyä. Ei korvaa SHACL-profiilia. |
| JSON Schema | Käyttäjän JSON-exportilla tarkoittama rakenteellinen skeema. Skeeman käyttämä draft/dialekti tallennetaan; lähde-exportia ei oleteta JSON Schema 2020-12 -muotoiseksi. Ei korvaa SHACL-profiilia. |

Kaikki viisi formaattia voidaan liittää saman profiiliversion esityksiksi tai johdannaisiksi. Kaikkia ei tarvitse toimittaa. JSON-LD, RDF/XML ja Turtle voivat esittää saman shapes graphin. OpenAPI ja JSON Schema ovat johdannaisia, joista ei oleteta voitavan palauttaa häviöttömästi alkuperäistä SHACLia tai OWL-semanttiikkaa. JSON-tiedostoa ei hyväksytä semanttiseksi profiiliksi pelkän päätteen perusteella.

Jos käyttäjä tuo aluksi vain JSON Scheman tai OpenAPI-kuvauksen, tuonti voidaan tallentaa keskeneräisenä. Palvelu pyytää lisäksi saman profiilin SHACL-aineiston tai linkin, josta se saadaan. Valmis profiilikytkentä edellyttää SHACL-graafia ja sen alkuperän yksilöintiä.

## Tietomallin täsmennykset

Tuoteversion `primarySemanticProfile` yksilöi käytettävän soveltamisprofiiliversion. Profiili voi käyttää muita profiileja ja useita OWL-sanastoja. Sama profiili voidaan jakaa usean tuotteen kesken. Tarvittaessa `entryShapeUris` yksilöi tuotteen käyttämät aloitusmuodot profiilin sisältä; muut riippuvuudet säilyvät mukana. Luokkamuodon IRI, sen OWL-kohdeluokan IRI, ominaisuusmuodon IRI ja ominaisuuden `sh:path` ovat erillisiä tietoja.

Vähimmäistiedot profiilille:

| Kenttä | Merkitys |
| --- | --- |
| sourcePlatform | Arvo `TietomallitSuomiFi`. |
| profileUri | Alkuperäisen soveltamisprofiilin IRI; erotetaan selaimen sivulinkistä. |
| sourcePageUrl | Valinnainen Tietomallit-työkalun sivulinkki. |
| sourceVersion ja sourceStatus | Lähdeprofiilin oma versio ja tila sellaisinaan, jos saatavilla. Puuttuminen on näkyvä tila. |
| ingestionMethod | `link` tai `upload`. |
| sourceArtifacts | Alkuperäiset tiedostot tai noudetut kopiot; mediaType, serialization, sourceUrl mahdollisuuksien mukaan, sha256 ja hankinta-aika. |
| shapesArtifactId | Täydellisen SHACL-graafin lukittu artefakti. |
| entryShapeUris | Tarvittaessa tietotuotteelle valitut aloitusmuodot. |
| vocabularyReferences | Käytetyt OWL-nimiavaruudet, tunnisteet ja saatavilla olevat versiot; sijainti alustalla tai ulkoisena. |
| dependencies | Muiden profiilien, koodistojen ja kontekstien riippuvuudet sekä niiden ratkaisemisen tila. |
| derivedArtifacts | JSON Schema, OpenAPI ja muut esitykset; lähdeprofiilin version ja snapshotin viite. |
| verificationStatus | `pending`, `verified`, `needsAttention` tai `rejected` perusteluineen. |

Tietoelementtien nimet, tietotyypit, kardinaliteetit, assosiaatiot ja koodistorajoitteet luetaan profiilista. Tietotuotteen ylläpitäjä ei luo näistä erillistä käsin ylläpidettävää totuutta. Käyttöliittymän tietoelementtiluettelo on profiilista johdettu lukuesitys. Tuotteen tarkoitus, vastuulliset, saatavuus ja käyttöehdot ovat edelleen tuotteen omia metatietoja.

Monimutkaisia SHACL-polkuja, sisäkkäisiä muotoja ja tuontityökalulle tuntemattomia rajoitteita ei saa hävittää litistämällä mallia taulukoksi. Säilytä alkuperäinen graafi ja näytä, mitä käyttöliittymä pystyy esittämään. OWL määrittää yhteisten termien merkityksen, SHACL käyttötapauksen rakenteen ja rajoitteet. JSON-skeeman kenttänimi ei yksin määrää semanttista URI:a.

Metatietovarannon katalogin JSON-LD-vienti kuvaa tietotuotetta. Se ei ole tuotteen soveltamisprofiilin JSON-LD-export eikä yksittäinen attribuuttitodistus. Nämä kolme artefaktityyppiä pidetään erillään.

## Versiointi ja tarkistukset

Profiilin tuonnissa tarkistetaan aineiston syntaksi, SHACL-rakenne, alkuperäiset tunnisteet, riippuvuudet ja tieto siitä, onko aineisto soveltamisprofiili vai pelkkä OWL-sanasto. Tiedoston parsiminen tai SHACL-rakenteen tarkistus ei yksin todista alustalta saatua alkuperää. Lähdeilmoitus ja mahdollinen alustalta tehty vertailu ovat erikseen näkyviä tarkistuksia.

Julkaistava tuoteversio sitoutuu tarkistettuun profiilisnapshotiin ja tarkisteeseen. Lähteen versiotunnus tallennetaan sellaisenaan; jos sitä ei ole, sisältötarkiste yksilöi snapshotin ja käyttöliittymä kertoo version puuttuvan. Eri serialisointien raakatavujen tarkisteita ei verrata semanttisena yhdenmukaisuustestinä: saman RDF-graafin vastaavuus arvioidaan jäsennetyistä graafeista.

Pysyvästi ratkaisematon puuttuva profiili tai riippuvuus estää myöhemmin tuoteversion julkaisun. Tilapäinen lähdepalvelun katkos ei mitätöi jo lukittua ja ehjää snapshotia. Aineiston nouto noudattaa suunnitelman sallittujen lähteiden ja lukittujen riippuvuuksien käsittelyä.

## Nykytilan havainto ja eteneminen

Tarkistettu main-haara 14.10.2026: alkuperäinen suunnitelma sisältää SemanticProfile- ja SHACL-ajatuksen mutta ei vaadi alkuperäksi Tietomallit-soveltamisprofiilia. Vaiheen 2B `ProductInput` sisältää edelleen käsin annettavan `dataElements`-listan; `Element` sisältää vain nimen, kuvauksen ja `semanticUri`-arvon. Tuotteella ei vielä ole versioitua soveltamisprofiilikytkentää, linkki-/tiedostotuontia tai SHACL-graafin säilytystä. Nykyinen katalogin JSON-LD-vienti ei toteuta näitä puuttuvia ominaisuuksia.

Suunnitteluperiaate kirjataan nyt. Soveltamisprofiilikytkentä ja tuonnin perusrakenne on suunniteltava ennen 2C:n julkaisuversioiden rakenteen lukitsemista. Toteutus tilataan erikseen vasta perusoletusten käsittelyn jälkeen. Nykyisiä demotuotteita ei poisteta: niille merkitään tulevassa migraatiossa profiilikytkentä keskeneräiseksi, eikä niiden nykyisiä semanticUri-arvoja koroteta automaattisesti vahvistetuksi profiiliksi. Varsinainen esimerkkidatan SHACL-validointipalvelu voidaan vaiheistaa myöhemmin; profiilin identiteettiä ja lähdeasemaa ei lykätä sen mukana.

## Hyväksymisehdot tulevalle toteutukselle

1. Sama Tietomallit-profiili voidaan rekisteröidä joko linkillä tai alustalta ladatulla tiedostolla. Molemmat johtavat samaan profiili-identiteettiin ja yksilöityyn sisältöversioon.
2. Profiili voi viitata alustalla olevaan OWLiin, ulkoiseen OWLiin tai molempiin ilman termien uudelleennimeämistä.
3. JSON-LD-, RDF/XML- ja Turtle-tuonti säilyttää SHACL-graafin, tunnisteet, sisäkkäiset rakenteet ja riippuvuudet. Tuetun esimerkkiprofiilin vastaavat RDF-esitykset tunnistetaan sisällöltään yhtäpitäviksi.
4. Pelkkä JSON-LD-konteksti, JSON Schema, OpenAPI tai OWL ei läpäise valmiin soveltamisprofiilin hyväksyntää. Johdannaiset voidaan silti tallentaa ja liittää myöhemmin oikeaan profiiliin.
5. Tietoelementtiluettelo syntyy profiilista ja erottaa shape- sekä OWL-tunnisteet. Vapaatekstinen rinnakkaismalli ei voi ohittaa profiilia.
6. Profiilin verkossa muuttuminen ei muuta aiempaan tuoteversioon sidottua sisältöä. Päivitys käsitellään eksplisiittisesti uutena profiiliversiona tai snapshotina.
7. Katalogikuvaus, sisältöprofiili ja todistuksen kuori erotetaan käyttöliittymässä ja API:ssa.

## Tarkistetut lähteet

- Tietomallit-työkalun ohjeet: https://kehittajille.suomi.fi/palvelut/yhteentoimivuus/tietomallit
- Soveltamisprofiilin kuvaus, mukaan lukien ulkoiset nimiavaruudet: https://kehittajille.suomi.fi/palvelut/yhteentoimivuus/tietomallit/soveltamisprofiilin-tiedot
- Mallin luominen ja julkaisu: https://kehittajille.suomi.fi/palvelut/yhteentoimivuus/tietomallit/uuden-tietomallin-luominen-ja-julkaisu
- W3C SHACL: https://www.w3.org/TR/shacl/

Tietomallit-ohje vahvistaa exportit JSON-LD, RDF ja Turtle sekä soveltamisprofiileille OpenAPI ja JSON Schema. Ulkoisten nimiavaruuksien hyödyntäminen on dokumentoitu. Linkki-/tiedostoreitit, pakollisuus, snapshotit ja hyväksymisehdot ovat tämän Metatietovaranto-hankkeen suunnitteluratkaisuja.
