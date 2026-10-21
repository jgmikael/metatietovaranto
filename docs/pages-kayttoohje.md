# Public Pages -demon käyttöohje: Oma kokeilu

Kenttäkohtainen ohje ja työnkulku, tarkistettu main-version `8398c02` käyttöliittymästä 20.10.2026.

**Demo:** https://jgmikael.github.io/metatietovaranto/

Käyttöliittymän **Käyttöohje** avaa tämän saman ohjeen sisällysluetteloineen. Kentän vieressä **Ohje** avaa tai sulkee lyhyen selitteen; **Lue lisää** avaa vastaavan ohjeosion. **Palaa edelliseen näkymään** tai selaimen Takaisin palauttaa kenttään ja säilyttää muokkaukset, keskeneräisen tiedostotuonnin ja mapping-ehdotuksen. Kokonaisen sivun uudelleenlataus säilyttää vain paikallisesti tallennetut tiedot, ei vielä liittämätöntä tiedostovalintaa.

Suoran osiolinkin muoto on `/metatietovaranto/#ohje/shacl-tuonti` (SHACL-tuonti) tai `/metatietovaranto/#ohje/generointi` (esitysvalinnat). Markdown-versio on edelleen ladattavissa ohjenäkymästä. Ohje on mukana staattisessa buildissa eikä tarvitse palvelinsovellusta.

Valitse **Aloita oma kokeilu**. Kirjautumista, asennusta tai Codespacea ei tarvita. Käytä vain synteettisiä organisaatioita ja esimerkkitietoja. Omat muutoksesi säilyvät tämän selaimen ja selainprofiilin paikallisessa tallennuksessa. Ne eivät muuta julkista esittelyä tai muiden käyttäjien tietoja.

Ohjeessa **generointiin tarvittava** tarkoittaa nykyisen selaingeneraattorin vaatimusta. Kaikkia kuvattavissa olevia palvelutietoja ei tarvitse täyttää. Tyhjän kentän tallentuminen ei tarkoita, että kuvaus olisi täydellinen tai palvelu toimiva.

## 0. Julkisen esittelyn selaaminen

Julkinen näkymä on kaikkien luettavissa. Haku ja lataukset koskevat mukana toimitettua synteettistä aineistoa, eivät oman kokeilusi tuotteita. Siirry omaan työtilaan Aloita oma kokeilu -painikkeella. Käyttöohjeen paluupainike palauttaa edelliseen näkymään ja kenttään.

| Kenttä | Täyttöohje |
| --- | --- |
| Hakusana | Hae tuotteen nimestä, kuvauksesta, tarjoajasta tai teemasta, esimerkiksi `yritys`. Valinnainen. Käytä Hae-painiketta. |
| Teema | Rajaa aihealueella, esimerkiksi `Yritykset`. Tyhjä näyttää kaikki teemat. |
| Tarjoaja | Rajaa tarjoajan nimellä, esimerkiksi `Demo-veroviranomainen`. Tämä ei vaihda tuotteen tarjoajaa. |
| Version elinkaaritila | Rajaa näytettäviä versioita. Mukana toimitetut esimerkit ovat julkaistun tilan esimerkkejä; Poistumassa käytöstä / Poistettu käytöstä voi antaa tyhjän listan. Tämä valinta ei muuta tilaa. |

## Sanasto ja vastuunjako

| Käsite | Selite |
| --- | --- |
| Metatiedot | Kuvaus siitä, mitä tietotuote sisältää, kuka siitä vastaa ja miten sisältöä suunnitellaan toimitettavan. Katalogin JSON-/JSON-LD-vienti palauttaa näitä kuvauksia, ei rekisterin varsinaisia tietoja. |
| Tietosisältö | Varsinaiset sisältökentät ja arvot, esimerkiksi yrityksen nimi. Kokeilussa vain synteettisiä arvoja. Sisältösopimus perustuu SHACL-lähteeseen. |
| Todistuksen kuori | Sisältöä ympäröivä todistusrakenne, kuten W3C VC:n issuer ja credentialSubject tai SD-JWT VC:n vct. Paikallinen esimerkki ei ole myönnetty tai allekirjoitettu todistus. |
| IRI | Kansainvälistetty resurssitunniste (Internationalized Resource Identifier), esimerkiksi ominaisuuden alkuperäinen URI. Ei sama asia kuin näyttönimi tai ladatun tiedoston polku. |
| SHACL | Shapes Constraint Language: RDF-tietojen rakenteen ja rajoitteiden kuvauskieli. Tuo soveltamisprofiili Tietomallit-työkalusta; demo ei ole SHACL-mallinnustyökalu eikä täydellinen SHACL-validaattori. |
| API | Ohjelmointirajapinta (Application Programming Interface). Tuotteen JSON API kuvaisi tulevaa sisältöpalvelua; Pages-demo ei toteuta sitä. |
| VC | Verifiable Credential, todennettavan todistuksen tietorakenne. W3C VC ja SD-JWT VC ovat eri esitysmuotoja. Pelkkä kuvauksen generointi ei todenna todistusta. |
| SD-JWT VC | Valikoivaa paljastamista tukeva todistusmuoto. JWT tarkoittaa JSON Web Tokenia. Kokeilussa muodostetaan vain sen tekniset kuvaukset, ei allekirjoitettua tokenia tai disclosureja. |
| JSON-LD-konteksti | Sitoo JSON-kenttien nimet alkuperäisiin semanttisiin IRI:hin ja tyyppeihin. Ei korvaa SHACLia tai myöntämispalvelua. |
| Type Metadata | SD-JWT VC:n tyyppikuvaus: vct, väitepolut, näyttönimet ja paljastamismääritykset sekä tämän demon omat semanttiset laajennukset. Ei sisällä myönnettyä todistusta. |
| Semanttiset annotaatiot | x-term, x-mtv-shacl ja x-mtv-semantic kytkevät kentän alkuperäiseen ominaisuus-IRI:hin, SHACL-käyttöyhteyteen ja lukittuun profiiliin. Oma laajennus ei tarkoita kaikkien lompakoiden tukea. |
| Omistajaorganisaatio | Varsinaisen palvelinsovelluksen pysyvä oikeuksien ja hyväksymisprosessin omistaja. Pagesissa ei ole omistajan vaihtokenttää tai käyttöoikeuksien hallintaa. Tarjoajan valinta ei myönnä oikeuksia. |
| Organisaatioroolit | Tarjoaja tarjoaa tuotteen, lähdevastuu vastaa lähdetiedosta, operaattori operoi palvelua ja myöntäjä päättää todistuksesta. Ne voivat olla sama tai eri organisaatio. Nimi ei yksin tee tietueista samaa organisaatiota. |
| UUID ja XSD | UUID on sovelluksen luoma tietueen tunniste. XSD tarkoittaa XML Schema Datatypes -tyyppejä, kuten xsd:string. Tietotyyppi otetaan lähde-SHACLista, ei keksitä itse. |

## 1. Ensimmäinen onnistuva kokeilu valmiilla esimerkillä

Tee ensimmäinen kierros näin. Sen jälkeen voit kokeilla oman profiilisi tuontia tai uuden tuotteen lisäämistä.

1. Valitse **Aloita oma kokeilu** ja avaa tuote **Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo)**. Tässä esimerkissä on jo kolme toimitustapaa ja generointiin sopivia synteettisiä asetuksia.
2. Lataa repositoriosta [semantic-profile-demo.ttl](../fixtures/semantic-profile-demo.ttl) omalle koneellesi. Käyttöliittymän ohjeessa linkki lataa mukana toimitetun tiedoston. Jos luet ohjetta GitHubissa, valitse tiedostonäkymässä **Download raw file** tai **Raw** ja tallenna tekstitiedosto `.ttl`-päätteellä. Älä tallenna GitHubin HTML-sivua Turtle-tiedostoksi. Tämä tiedosto on ohjelmiston synteettinen testiprofiili, ei aito Tietomallit-export.
3. Vieritä tuotteen kohtaan **Tuo SHACL-profiili ja muodosta paikallinen paketti**. Valitse tiedosto kenttään **SHACL Turtle -tiedosto**. Riippuvuustiedostoja ei tarvita tälle esimerkille.
4. Odota ilmoitusta **Turtle jäsennetty**. Tunnisteeksi pitäisi tulla `https://example.org/metatietovaranto/demo/profile`. Lähdeprofiilin version voi tässä esimerkissä jättää tyhjäksi: tiedosto ei ilmoita sitä. Valitse **Liitä tuotu profiili tuotteeseen** ja odota liittämisen vahvistus sekä **Tallennettu**.
5. Valitse **Näytä tuodun profiilin luokkamuodot** ja listasta juureksi `https://example.org/metatietovaranto/demo/ProductShape`. Saman arvon voi kirjoittaa suoraan kenttään **Generoinnin juurimuodon IRI**.
6. Valitse **Tarkista tuki ja muodosta mapping-ehdotus**. Ehdotuksessa pitäisi olla `companyName`, tyyppi `http://www.w3.org/2001/XMLSchema#string` ja määrä `1…1`. Säilytä ehdotettu nimi.
7. Täytä alla olevat arvot:

   | Kenttä | Ensikokeilun arvo |
   | --- | --- |
   | Mappingin paikallinen versio | `1.0.0` |
   | Suunniteltu HTTPS-julkaisemisen perusosoite | `https://julkaisut.example.org` |
   | Synteettinen yhteisen sisällön JSON-esimerkki | Kopioi alla oleva JSON. |

   ```json
   {"companyName":"Synteettinen Esimerkki Oy"}
   ```

   Esimerkkiosoite ei ole toimiva julkaisupalvelu. Sen antaminen ei lähetä tiedostoja sinne.
8. Tarkasta kolme toimitustapaa tarvittaessa **Muokkaa paikallista tuotetta** -näkymästä. Valmiin yritysesimerkin asetuksia ei tarvitse muuttaa tätä kierrosta varten. Jos muutat niitä, sulje muokkaus, palaa generointikohtaan ja tarkasta mapping-ehdotus tarvittaessa uudelleen.
9. Kuittaa generointikohdan kolme valintaruutua vasta tarkastuksen jälkeen: yhteiset kenttänimet, toimitustapojen päätökset ja esimerkin synteettisyys.
10. Valitse **Muodosta paikallinen tekninen paketti**. Odota muodostumisen ilmoitusta ja **Tallennettu**. Tuloksen otsikko on **Paikallinen kokeilupaketti – ei julkaistu**.
11. Lataa yksittäiset artefaktit tai **Lataa koko paikallinen paketti JSONina**. Tee lisäksi **Vie kokeilu JSONina**, jotta voit palauttaa koko työtilan myöhemmin.

**Odotettu tulos:** konteksti, JSON Schema, SD-JWT Type Metadata, semanttiset mappingit, esimerkit ja manifesti syntyvät. Myönnettyä todistusta, allekirjoitusta tai julkista julkaisua ei synny. Tuotteen merkintä **Ei validoitu tässä kokeilussa** säilyy tarkoituksella.

## 2. Työnkulku omalle tuotteelle

**Organisaatio → tuote → SHACL-tuonti → juuri ja mapping-ehdotus → kolme toimitustapaa → esitysvalinnat ja synteettinen esimerkki → paikallinen paketti → lataukset ja varmuuskopio.**

- Jos sopiva tarjoaja puuttuu, luo se ensin kohdassa **Omat organisaatiot**.
- Valitse **Omat tietotuotteet → Lisää paikallinen tietotuote**. Täytä perustiedot.
- Voit tuoda SHACLin ja tarkistaa sen tuen ennen kaikkien palvelumetatietojen täyttämistä. Näin huomaat aikaisin, sopiiko profiilisi nykyiselle generaattorille.
- Lisää tuotteen muokkauksessa täsmälleen yksi JSON API-, W3C VC- ja SD-JWT VC -kuvaus. Täydennä alla **generointiin tarvittaviksi** merkityt valinnat.
- Muodosta paketti vaiheiden 5–11 mukaisesti. Oman profiilin juuri, kenttänimet ja JSON-esimerkki tulevat omasta aineistostasi: älä kopioi `companyName`-esimerkkiä profiiliin, jossa sellaista kenttää ei ole.

## 3. Aloitusnäkymä, tallennus ja varmuuskopiot

| Toiminto tai kenttä | Käyttöohje |
| --- | --- |
| Tallennuksen tila | Muutos tallentuu noin puolen sekunnin viiveellä vain tähän selaimeen. Odota Tallennettu-ilmoitusta; virheessä vie kokeilu JSONiksi. Tämä ei ole julkaisu tai riippumaton hyväksyntä. |
| Omat tietotuotteet | Avaa omien paikallisten tuotteiden lista. Tuotteen nimeä painamalla avaat sen. |
| Lisää paikallinen tietotuote | Luo uuden tuotteen ja vakaan UUID-tunnisteen. Ennen lisäystä pitää olla vähintään yksi organisaatio. |
| Muokkaa paikallista tuotetta / Sulje muokkaus | Avaa tai sulje perustietojen ja toimitustapojen lomake. Muutokset tallentuvat automaattisesti, erillistä Tallenna-painiketta ei ole. |
| Omat organisaatiot | Ylläpidä kokeilun tarjoajia ja muita vastuullisia organisaatioita. |
| Mukana toimitetut profiilit | Tarkastele julkisen esittelyn mukana toimitettuja alkuperäisiä profiileja. Oma tiedostotuonti tehdään tuotteen generointikohdassa. |
| Palaa julkiseen esittelyyn | Palaa alkuperäiseen julkiseen katalogiin. Oma kokeilu säilyy; palaa siihen Aloita oma kokeilu -painikkeella. |
| Vie kokeilu JSONina | Lataa koko työtila: tuotteet, organisaatiot, paikalliset lähdeprofiilit, asetukset ja paketit. Tämä on palautettava varmuuskopio. |
| Tuotava kokeilutiedosto | Avaa **JSON-tuonti ja alkuperäisten esimerkkien palautus**. Valitse aiemmin viety kokeilun JSON, enintään 2 MiB. Tähän ei valita Turtlea, yksittäistä JSON Schemaa eikä kuvauspaketin JSON-latausta. |
| Korvaa kokeilu tuodulla aineistolla | Ilmestyy vasta onnistuneen tarkistuksen jälkeen. Korvaa koko työtilan erillisen vahvistuksen jälkeen; ei yhdistä aineistoja. Vie nykyinen työtila ensin talteen, jos haluat säilyttää sen. |
| Peru tuonti | Hylkää tarkistetun tuontiehdokkaan muuttamatta työtilaa. |
| Palauta alkuperäiset esimerkit | Korvaa oman työtilan demon lähtöaineistolla vahvistuksen jälkeen. Omien tuotteiden/profiilien säilyttämiseksi vie ensin varmuuskopio. Muiden sovellusten selaintietoja ei poisteta. |
| Yritä tallennusta uudelleen | Käytä tallennusvirheen syyn poistuttua. Ei ohita välilehtiristiriitaa. |
| Avaa selaimen tallennettu kokeilu | Virhe-/ristiriitatilanteessa lataa tallennetun version. Muistissa olevat muutokset korvataan vahvistuksen jälkeen; vie ne tarvittaessa ensin. |
| Lataa alkuperäinen tallenne talteen | Vioittuneen/tuntemattoman tallenteen raaka varmuuskopio vian selvittämiseen. Se ei ole tavallinen kokeilun tuontitiedosto. |
| Poista paikallinen tuote | Poistaa valitun paikallisen tuotteen vahvistuksen jälkeen. Ei poista julkista esittelytuotetta. |

**Tallennustilat:** **Tallennetaan…** = odota; **Tallennettu** = paikallinen kirjoitus onnistui; **Tallennus epäonnistui** = vie muistissa oleva työ JSONiksi ja selvitä virhe. Selaintietojen poisto tai yksityisen ikkunan sulkeminen voi hävittää kokeilun. Samanaikaista muokkausta useassa välilehdessä kannattaa välttää: ristiriidassa kirjoittaminen estetään, ei ylikirjoiteta toisen välilehden työtä.

## 4. Organisaation kaikki täytettävät kentät

Valitse **Omat organisaatiot → Lisää paikallinen organisaatio** tai avaa olemassa oleva organisaatio.

| Kenttä | Merkitys ja täyttöohje | Esimerkki |
| --- | --- | --- |
| Organisaation virallinen nimi | Synteettisen organisaation nimi, enintään 200 merkkiä. Nimi näkyy tarjoajavalinnoissa. | `Synteettinen Kuntarekisteri` |
| Maa | Kaksikirjaiminen maatunnus. Syöte muutetaan isoiksi kirjaimiksi; käytä maatunnusta, älä maan koko nimeä. | `FI` |
| Tunnistejärjestelmä | Näkyy, kun valitset Lisää organisaatiotunniste. Kerro, minkä järjestelmän tunnisteesta on kyse; enintään 200 merkkiä. | `synthetic-demo` |
| Organisaatiotunniste | Edellisen järjestelmän mukainen **synteettinen** tunniste, enintään 200 merkkiä. Ei tarvitse olla aito Y-tunnus. | `demo-org-001` |

Tunnistepareja voi olla useita tai ei yhtään. Poista tarpeeton pari **Poista tunniste N** -painikkeella. **Synteettinen: kyllä** ja UUID ovat sovelluksen asettamia tietoja, eivät täytettäviä kenttiä. Samannimiset organisaatiot voivat olla eri tietueita. Käytössä olevan organisaation poistaminen estetään: vaihda ensin kaikki tuotteen ja toimitustapojen tarjoaja-, operaattori-, lähdevastuu- ja myöntäjäviittaukset toiseen organisaatioon.

## 5. Tuotteen perustietojen kaikki kentät

Valitse tuote → **Muokkaa paikallista tuotetta**. Keskeneräisiä tekstejä voi tallentaa; täytä kuitenkin seuraavat tiedot, jotta kuvaus on ymmärrettävä.

| Kenttä | Täyttöohje | Esimerkki / raja |
| --- | --- | --- |
| Tarjoaja | Valitse olemassa oleva organisaatio. Viittauksen on pysyttävä ehjänä. | `Synteettinen Kuntarekisteri` |
| Nimi | Kuvaava tietotuotteen nimi. Nimi tulee myös generoidun Type Metadatan nimeksi. | `Synteettinen yrityksen perustieto`; 200 merkkiä |
| Kuvaus | Mitä sisältö kuvaa ja kenelle? Kuvaus tulee Type Metadataan. | `Esimerkki yrityksen nimestä kolmessa toimitusmuodossa.`; 5 000 merkkiä |
| Teema | Tuotteen aihealue. | `Yritykset`; 100 merkkiä |
| Synteettinen lähde | Kuvaa kuviteltu tietolähde tai ohjelmistofixture. Tämä ei ole SHACL-tiedoston latauskenttä. | `Synteettinen testirekisteri`; 500 merkkiä |
| Käyttötarkoitus | Mihin tietoa on tarkoitus käyttää? | `Teknisten kuvausten kokeilu`; 2 000 merkkiä |
| Rajaukset — mitä tuote ei todista | Mitä tiedosta ei voi päätellä? | `Ei oikea rekisteriote eikä todista edustamisoikeutta.`; 2 000 merkkiä |
| Käyttöehdot | Kuvaa kokeilukäytön ehdot. | `Vain synteettiseen kokeiluun.`; 2 000 merkkiä |
| Sisältöprofiilin snapshot | Valitse lukittu profiiliversio. Voi olla tyhjä keskeneräisessä tuotteessa. Oma tuonti liittää profiilin tähän automaattisesti. Mukana toimitetun profiilin valitseminen yksin ei käynnistä omaa tiedostogenerointia. | Profiilin IRI, versio ja SHA-256 auttavat erottamaan snapshotit. |

Profiilin, tuotteen metadatan tai toimitustapojen muuttaminen vanhentaa aiemman paikallisen paketin. Tuotteen **Tunniste** on automaattinen UUID.

## 6. Kolmen toimitustavan yhteiset kentät

Lisää **Rinnakkaiset toimitustavat** -kohdassa yksi kutakin: **Lisää JSON API -kuvaus**, **Lisää W3C VC -kuvaus**, **Lisää SD-JWT VC -kuvaus**. Numerointi riippuu lisäysjärjestyksestä. Taulukoissa kenttänimi on ilman toistuvaa etuliitettä, esimerkiksi `W3C VC 2: suojausprofiilin IRI` tarkoittaa alla olevaa **suojausprofiilin IRI** -kenttää.

Generointi tarvitsee täsmälleen kolme kuvausta, yhden kutakin tyyppiä. Näyttö sallii muitakin metadatakokeiluja, mutta generaattori hylkää ne.

| Kenttä | Täyttöohje | Ensikokeilun valinta |
| --- | --- | --- |
| ensisijainen | Valitse oletuksena esiteltävä toimitustapa. | W3C VC |
| saatavuus | Suunnitteilla / Kokeilupalvelu / Tuotannossa / Keskeytetty. Paikallisen generaattorin vaatimus on **Suunnitteilla** (`planned`) kaikille kolmelle. Valinta ei tarkista palvelua. | Suunnitteilla |
| ympäristö | Kuvattavan palvelun suunniteltu testi- tai tuotantoympäristö. Ei käynnistä ympäristöä. | Sandbox |
| tarjoaja | Organisaatio, joka tarjoaa tämän toimitustavan. | Tuotteen tarjoaja |
| operaattori | Organisaatio, joka operoisi rajapintaa/myöntäjäpalvelua. Voi olla sama kuin tarjoaja. | Tuotteen tarjoaja |
| lähdevastuu | Organisaatio, joka vastaa varsinaisen lähdetiedon laadusta ja ylläpidosta. Voi olla sama. | Tuotteen tarjoaja |
| suojausmekanismi | JSON API: `tls`. W3C VC: `dataIntegrity` tai `jose`. SD-JWT VC: `sdJwt`. Kuvaa suunniteltua suojausta, ei toteuta sitä. | `tls` / `dataIntegrity` / `sdJwt` |
| suojausprofiilin IRI | Valitun suojausprofiilin pysyvä tunniste. **Generointiin tarvittava W3C VC:lle ja SD-JWT VC:lle**. Synteettinen URN käy kokeilussa; se ei ole hyväksytty tuotantoprofiili. JSON API -kokeilussa voi jättää tyhjäksi. | `urn:synthetic:security:w3c:1`, `urn:synthetic:security:sdjwt:1` |
| ES256 / ES384 / EdDSA | Merkitse suunniteltuun profiiliin kuuluvat algoritmit. **SD-JWT tarvitsee vähintään yhden. W3C:n jose tarvitsee vähintään yhden**; dataIntegrity-kokeilussa ei ole samaa algoritmilistavaatimusta. JSON API:n tls ei vaadi näitä valintoja. Älä valitse kaikkia varmuuden vuoksi. | SD-JWT: ES256; W3C dataIntegrity: tyhjä |

Formaatti, protokolla ja tunniste näytetään automaattisesti. JSON API on `application/json` / HTTPS REST, W3C VC `application/vc+ld+json` ja SD-JWT VC `application/dc+sd-jwt`. Todistusmuodoissa OpenID4VCI-versiona näytetään 1.0. Näitä ei kirjoiteta erillisiin kenttiin. Kaikkien kolmen profiilisnapshot-viite päivittyy tuotteen valinnan mukana.

## 7. JSON API -kuvauksen kaikki omat kentät

Nämä kuvaavat tulevaa **tietosisällön** rajapintaa, eivät katalogin metatietovientiä. Planned-kokeilussa useimmat voi jättää tyhjiksi.

| Kenttä | Täyttöohje / tarve selaindemossa |
| --- | --- |
| palveluosoite | Varsinaisen lähdetieto-API:n suunniteltu pysyvä HTTPS-osoite. Voi jättää tyhjäksi generointikokeilussa. Jos havainnollistat osoitetta, käytä esimerkiksi `https://api.example.org/company`. |
| rajapintakuvauksen osoite | Tulevan API-dokumentaation osoite, esimerkiksi `https://api.example.org/openapi.json`. Valinnainen. Ei noudeta automaattisesti. |
| OpenAPI-artefakti | **Jätä Ei valittu.** Nykyinen selainpolku ei tuo tällaisia johdannaisartefakteja eikä validoi niiden viitteitä; valikko on yhteinen palvelinsovelluksen kanssa. Generointi hylkää annetun ulkoisen artefaktiviitteen. |
| JSON Schema -artefakti | **Jätä Ei valittu.** Paikallisesti generoitu schema tulee pakettiin, ei tähän palvelimen artefaktivalikkoon. |
| tunnistautuminen | `none` = ei tunnistautumista, `oauth2` = OAuth 2 -pääsynhallinta, `apiKey` = API-avain, `mtls` = molemminpuolinen TLS. Kuvaa suunnitelmaa; ei avaa kirjautumista. Esimerkin `oauth2` käy. |
| tarvittavat oikeudet (yksi rivillä) | Suunnitellut oikeuksien/scopejen nimet, esimerkiksi `company.read`. Tyhjä käy planned-generointiin. **Älä kirjoita käyttöoikeustokenia tai API-avainta.** |
| ajantasaisuus | Kerro tiedon päivitysrytmi tai tuoreus, esimerkiksi `Päivittäin; synteettinen suunnitelma.` Voi jättää tyhjäksi ensimmäisellä kierroksella. |

## 8. W3C VC:n ja SD-JWT VC:n yhteiset myöntäjätiedot

Nämä kentät näkyvät kummankin todistusmuodon omassa kuvauksessa. Planned-generointi ei tarvitse toimivaa myöntäjäpalvelua. Täytä suunniteltu työnjako vain siltä osin kuin se on tiedossa.

| Kenttä | Merkitys ja täyttöohje |
| --- | --- |
| myöntäjäorganisaatio | Organisaatio, joka tekisi myöntämispäätöksen ja vastaisi todistuksen myöntämisestä. Voi olla tarjoaja; planned-kokeilussa voi jäädä valitsematta. |
| myöntäjäpalvelun HTTPS-tunniste | OpenID4VCI-myöntäjän pysyvä tunniste, esimerkiksi `https://issuer.example.org`. Valinnainen tässä kokeilussa. Ei ole yksittäisen henkilön myöntämistapahtuman osoite. |
| pysyvä myöntämisen aloituslinkki | Ulkoisen myöntäjän pysyvä asiointilinkki, esimerkiksi `https://issuer.example.org/start/company`. Voi jättää tyhjäksi. Ei transaktiokohtaista Credential Offer -linkkiä, QR-koodia tai tokenia. |
| credential configuration -tunnisteet (yksi rivillä) | Myöntäjän määrittämät tuettujen todistuskonfiguraatioiden nimet. Voi jättää tyhjäksi. Jos sama myöntäjä tarjoaa molemmat muodot, käytä eri tunnisteita: esim. W3C: `company-w3c`, SD-JWT: `company-sdjwt`. Sama tunniste ei saa tarkoittaa molempia. |
| voimassaoloprofiili | Viittaus todistuksen voimassaolon sääntöihin. Ei yksittäisen todistuksen päättymisaika. Valinnainen planned-kokeilussa. |
| tilatietoprofiili | Viittaus mitätöinnin/tilatiedon toteutusprofiiliin. Ei henkilön tilatietue tai henkilökohtainen status-URL. Valinnainen. |
| edustamisen ehdot | Milloin henkilö voi toimia organisaation puolesta? Esim. `Myöntäjä tarkistaa edustamisoikeuden.` Valinnainen metatieto; demo ei tarkista valtuuksia. |
| tuki | Palvelun suunniteltu tukitieto tai ohjesivu. Voi jättää tyhjäksi. |
| maksu | Sanallinen hinnoittelutieto, esimerkiksi `Maksuton synteettinen kokeilu`. Ei maksutapahtumaa. Voi jättää tyhjäksi. |
| oikeudellinen luokka | `unassessed` = arvioimatta, `nonQualified` = ei kvalifioitu, `publicSectorAttestation` = julkisen sektorin todistusluokka, `QEAA` = kvalifioidun todistuksen väite. **Valitse ensikokeessa unassessed.** Selain ei vahvista mitään näistä luokista ja QEAA-valinta estää paketin generoinnin. |
| oikeudellinen näyttö | Perustelu/viittaus valitun luokan arvioinnille. Voi jättää tyhjäksi, kun luokka on unassessed. Pelkkä oma teksti ei vahvista oikeudellista asemaa. |
| kohde person | Rastita, jos suunniteltu sisältö koskee luonnollista henkilöä. Ei tarkoita sisäänkirjautunutta käyttäjää. |
| kohde legalPerson | Rastita, jos sisältö koskee oikeushenkilöä, kuten yritystä. Yritysesimerkissä valitse tämä; henkilösisältöön valitse tarkoituksen mukaisesti person. |

### Valinnaiset lompakkoprofiilit

Avaa **lompakkoprofiilit** ja valitse **Lisää lompakkoprofiili** vain, jos haluat kuvata suunniteltua tai erikseen todennettua yhteensopivuutta. Ensimmäiseen generointiin niitä ei tarvita.

| Kenttä | Täyttöohje |
| --- | --- |
| profiili | Lompakko-/yhteentoimivuusprofiilin tunniste tai nimi. Ei pelkkä yleinen väite ”EU-yhteensopiva”. |
| versio | Juuri kyseisen lompakkoprofiilin versio, ei tietotuotteen tai SHACLin versio. |
| tila | `planned` = suunnitteilla, `declared` = ilmoitettu, `tested` = erikseen testattu, `incompatible` = yhteensopimaton. Demokokeilussa käytä planned tai jätä koko profiili lisäämättä. |
| näyttö | Viittaus yhteensopivuustestin aineistoon/raporttiin. Valinnainen; älä merkitse tested ilman todellista näyttöä. Demo ei tarkista linkkiä. |
| testiaika (ISO 8601) | Erillisen oikean testin ajankohta, esim. `2026-10-20T12:00:00Z`. Jätä tyhjäksi suunnitellulle testille. Ei automaattinen tämän demon testitulos. |

## 9. W3C VC -kuvauksen omat kentät

| Kenttä | Täyttöohje / generoinnin vaatimus |
| --- | --- |
| VC-tyypit (yksi rivillä) | **Sisällytä VerifiableCredential.** Voit lisätä profiilin edellyttämän oman tyypin tunnisteen, esim. `urn:synthetic:company:Credential`. Ensikokeessa perustyyppi yksin riittää. |
| JSON-LD-kontekstit (yksi rivillä) | **Sisällytä https://www.w3.org/ns/credentials/v2.** Älä korvaa sitä omalla profiili-IRI:llä. Generaattori muodostaa pakettiin oman tuotekontekstin erikseen. Mielivaltaisia verkkokonteksteja ei noudeta; omaan kokeeseen ei tarvitse lisätä muita rivejä. |
| sisältöpolku | **Käytä /credentialSubject.** Selainversion generaattori edellyttää tätä sijaintia tietosisällölle. |

## 10. SD-JWT VC -kuvauksen omat kentät

| Kenttä | Täyttöohje / generoinnin vaatimus |
| --- | --- |
| vct | **Tarvitaan.** Todistustyypin pysyvä IRI-tunniste, ei tiedoston paikallinen polku. Kokeessa esimerkiksi `urn:synthetic:company:credential`. Tuotannossa myöntäjä järjestää standardinmukaisen Type Metadatan löydettävyyden; URN ei itsestään ole ladattava verkkodokumentti. |
| SD-JWT-profiilin versio | **Tarvitaan.** Nimeä käyttämäsi todistusprofiilin versio, esimerkiksi `synthetic-demo-1`. Tämä on eri asia kuin generaattorin lukittu IETF-standardiversio draft-ietf-oauth-sd-jwt-vc-19. |
| valikoiva paljastaminen | **Kaikki sisältökentät valikoivia** on helpoin ensikokeeseen. **Ei valikoivaa paljastamista** tekee sisällön aina näkyväksi. **Kenttäkohtainen** tarvitsee erillisen päätöksen jokaiselle generoidulle semanttiselle polulle tuotteen SD-JWT-mappingissa; ks. seuraava kohta. Tämä on kuvaus tulevasta käytännöstä, ei todellisten disclosurejen luonti. |
| haltijasidonta | Valitse profiilin suunnitelman mukaan **Pakollinen**, **Valinnainen** tai **Ei haltijasidontaa**. Ensikokeen Pakollinen käy. Demo ei toteuta tai testaa avainsidontaa. |
| aina näkyvät väitteet (yksi kenttäpolku rivillä) | Oletusarvot `/iss` ja `/vct` voi säilyttää. Omien sisältökenttien polkujen pitää vastata tarkastettua mappingia. Jos lisäät `/companyName` tähän, samaa kenttää ei voi merkitä valikoivaksi. Älä käytä satunnaisia tai vanhan profiilin kenttäpolkuja. |

SD-JWT-kuvaukseen ei tarvita JSON-LD-kontekstia. Sen semantiikka tulee erillisestä mappingista ja x-mtv-annotaatioista.

## 11. Versioitu kenttämapping: kaikki lisäkentät

Kunkin toimitustavan lopussa on mapping-editori. **Ensimmäisessä generointikokeessa sitä ei tarvitse täyttää käsin:** generaattori muodostaa paketin mappingit SHACLista ja hyväksytyistä kenttänimistä. Tuotteen editoriin aiemmin tallennetut mappingit eivät kuitenkaan päivity taustalla.

Jos valitset SD-JWT:lle **Kenttäkohtainen**-paljastamisen, editorin mappingeista on löydyttävä jokaiselle generoitavalle täydelle semanttiselle polulle eksplisiittinen paljastamispäätös. Pelkkä valikossa näkyvä oletusteksti ei korvaa puuttuvaa päätöstä. Jos päätös puuttuu, vaikka valikossa näkyy Valikoivasti, vaihda ensin Aina näkyvä ja sitten haluamasi Valikoivasti: näin valinta tallentuu eksplisiittisesti. Ensikierroksella yhteinen kaikkien kenttien käytäntö välttää tämän lisätyön.

| Kenttä | Täyttöohje |
| --- | --- |
| mappingin versio | Kyseisen toimitustavan editorimappingin versio, esim. `1.0.0`. Eri kenttä kuin generointikohdan Mappingin paikallinen versio. |
| juurimuodon IRI | Profiilin valittu juurimuoto, ei kyseisen ominaisuuden IRI. Sama juuri myös sisäkkäisillä kentillä. |
| semanttinen IRI-polku | Alkuperäiset ominaisuus-IRI:t juuresta kenttään, **yksi IRI rivillä**. Esim. osoiteominaisuus ja sen kaupunkiominaisuus kahdella rivillä. Ei näyttönimiä. |
| toimitusmuodon kenttäpolku | JSON Pointer -tyylinen polku, esim. JSON/SD-JWT `/companyName`, W3C `/credentialSubject/companyName`. Taulukon alkio: `/addresses/*/city`. |
| arvon rakenne | Literaali tai Olio alkuperäisen SHACLin mukaan. Älä muuta lähdemallin sisältösopimusta editorilla. |
| tietotyypin IRI | Näkyy literaalille. Kopioi SHACLin eksplisiittinen tyyppi, esim. `http://www.w3.org/2001/XMLSchema#string`. Ei lyhennettä `string`. |
| olion luokan IRI | Näkyy oliolle. Käytä profiilin määrittelemää luokka-IRI:tä. Sisäkkäinen kenttä tarvitsee myös oliovanhemman mappingin. |
| minCount | SHACLin alaraja kokonaislukuna. `0` = valinnainen, `1` = vähintään yksi. Ei omaa rinnakkaista sisältösääntöä. |
| maxCount (tyhjä = rajaton) | SHACLin yläraja; tyhjä tarkoittaa puuttuvaa ylärajaa. Generointiprofiilissa 1 on skalaari/olio, muu arvo tai puuttuva yläraja taulukko. |
| paljastaminen | Vain SD-JWT: **Valikoivasti** tai **Aina näkyvä**. Sovita yhteiseen käytäntöön ja aina näkyvien väitteiden listaan. Aina näkyvää lasta ei voi sijoittaa valikoivasti paljastettavan vanhemman alle. |

**Lisää kenttämapping** luo uuden editoririvin; **Poista kenttä** poistaa sen. Generaattori ei hyväksy käsin muutettuja tyyppejä tai määriä omaksi sisältömallikseen: muodostetun paketin auktoriteetti on lähde-SHACL. Muotokohtainen W3C-etuliite ja IETF:n taulukon `null`-polut muodostuvat pakettiin automaattisesti.

## 12. SHACL-tuonnin kaikki kentät ja valinnat

Nämä löytyvät tuotesivun kohdasta **Tuo SHACL-profiili ja muodosta paikallinen paketti**, myös tuotteen muokkauksen alapuolelta.

| Kenttä tai toiminto | Täyttöohje |
| --- | --- |
| SHACL Turtle -tiedosto | Valitse omalta koneelta Tietomallit-työkalusta ladattu UTF-8 `.ttl`-tiedosto. Osoitetta ei voi liittää tähän. Uusi päätiedoston valinta korvaa keskeneräisen tuontivalinnan; jo liitetty profiili säilyy, kunnes liität uuden. Tuonti ei korjaa virheellisiä tietotyyppejä tai semanttisia polkuja. |
| Paikalliset Turtle-riippuvuudet | Valitse paikalliset `.ttl`-tiedostot, jos tarvittava sisäkkäinen sh:node-muoto on toisessa aineistossa. Lisää ne ennen Liitä-painiketta. Pelkkä ulkoisen ominaisuuden IRI tai owl:imports ei tarkoita, että koko sanasto pitää liittää. |
| Lähdeprofiilin tunniste | Profiilin alkuperäinen absoluuttinen IRI, esim. `https://iri.suomi.fi/model/webcor/`. Täyttyy, jos tiedostosta löytyy yksiselitteinen ontologiatunniste; muuten kirjoita itse. Ei paikallinen tiedostonimi, juurimuodon IRI tai keksitty palveluosoite. |
| Lähdeprofiilin versio (jos tiedossa) | Alkuperäisen profiilin versio, esimerkiksi `0.0.2`. Voi jättää tyhjäksi, jos sitä ei ilmoiteta. Älä korvaa puuttuvaa versiota arvaamalla. |
| Liitä tuotu profiili tuotteeseen | Luo paikallisen lukitun snapshotin ja liittää sen tuotteeseen sekä toimitustapoihin. Odota liittämisen ilmoitusta ja Tallennettu-tilaa. |
| Käytä aiemmin tuotua profiilia | Valinnainen vaihtoehto uuden tiedoston lataamiselle. Valitse juuri oikea IRI/versio/tarkiste. Vaihto nollaa generoinnin esitysasetuksia ja jättää vanhan paketin vanhentuneena ladattavaksi. |
| Tyhjennä tuontivalinta | Tyhjentää keskeneräisen tiedostovalinnan. Ei poista jo liitettyjä profiileja tai kokeilun tuotteita. |
| Lataa muuttumaton lähde N | Lataa valitun lähdetiedoston alkuperäisen sisällön. SHA-256 auttaa tunnistamaan täsmälleen saman tiedoston. |

Tiedostoja enintään 10, yhteensä 256 KiB; jäsennettyjä kolmikoita enintään 10 000. Lähdeilmoituksesi ei varmista tiedostoa alustalta. Tiedoston onnistunut jäsennys ei vielä tarkoita tuettua generointia.

**Löydetyt luokkamuodot ja ominaisuudet** sekä **Nimiavaruudet ja riippuvuusviitteet** ovat tarkastelutietoja. Niissä ei muokata SHACLia. Ulkoisia viitteitä ei noudeta verkosta.

## 13. Generoinnin kaikki täytettävät kentät

| Kenttä | Täyttöohje / vaatimus |
| --- | --- |
| Generoinnin juurimuodon IRI | **Tarvitaan.** Valitse yksi tiedostossa oleva IRI-muotoinen sh:NodeShape, joka kuvaa halutun sisällön juurta. Esimerkkiprofiilissa `https://example.org/metatietovaranto/demo/ProductShape`. Ei ontologian yleisosoitetta tai luokka-IRI:tä. Tarkistuksen havainnot näkyvät tarkistuspainikkeen alla. |
| Valitse juurimuoto | Sama valinta pudotusvalikkona. Saat näkyviin painamalla Näytä tuodun profiilin luokkamuodot. Kenttä ja tekstisyöte ovat vaihtoehtoiset tavat antaa sama tieto. |
| Kenttänimi [semanttinen polku] | Ilmestyy onnistuneen ehdotuksen jälkeen. Tarkasta ehdotettu JSON-avain, esim. `companyName`. Jos muutat, käytä kirjaimella alkavaa ASCII-nimeä: kirjaimia, numeroita ja alaviivoja, enintään 100 merkkiä. Ei välilyöntejä tai varattuja nimiä kuten `name`, `id`, `type`, `issuer`, `vct`. Sisarusten nimet eivät saa törmätä; eri olioissa nimi voi toistua. Tarkista ehdotus uudelleen muutoksen jälkeen. |
| Mappingin paikallinen versio | **Tarvitaan.** Paketissa käytettävien mappingien versio muodossa `1.0.0`. Kasvata omia versioita esitysratkaisun muuttuessa. Tämä ei muuta SHACL-lähteen versiota tai tuotteen editorimappingeja. |
| Suunniteltu HTTPS-julkaisemisen perusosoite | **Tarvitaan.** Oma tuleva julkaisuperusta ilman tunnuksia, kyselyä tai fragmenttia, esim. `https://julkaisut.example.org`. Demo muodostaa sen alle `/id/technical-packages/...`-osoitteet. Se ei varaa osoitetta tai julkaise sinne. `jgmikael.github.io`-isäntää ei hyväksytä käyttäjäaineiston julkaisupaikaksi. |
| Synteettinen yhteisen sisällön JSON-esimerkki | **Tarvitaan.** Pelkkä yhteinen sisältö tarkastetuilla kenttänimillä, ei VC-kuorta, JWT:tä, `credentialSubject`-käärettä tai allekirjoitusta. Esim. `{"companyName":"Synteettinen Esimerkki Oy"}`. Oman profiilin sisäkkäiset oliot ja taulukot kirjoitetaan ehdotuksen mukaan. |
| Olen tarkastanut yhteiset kenttänimet ja hyväksyn paketin mapping-ehdotukset | **Kuittaus tarvitaan.** Vahvista luettuasi ehdotuksen. Nimen/juuren muuttaminen poistaa kuittauksen. Ei riippumattoman tarkastajan hyväksyntä. |
| Olen tarkastanut toimitustapojen vct-, suojaus-, algoritmi-, haltijasidonta- ja paljastamisvalinnat | **Kuittaus tarvitaan.** Varmista erityisesti kohdat 6, 9 ja 10. Tuotteen metadatan muuttaminen poistaa tämän kuittauksen. |
| Vahvistan JSON-esimerkin synteettiseksi | **Kuittaus tarvitaan.** Esimerkin muuttaminen poistaa kuittauksen. Älä käytä oikeita henkilö- tai rekisteritietoja. |

**Tarkista tuki ja muodosta mapping-ehdotus** on tehtävä onnistuneesti ennen generointia. Havainnot näkyvät heti painikkeen alla. Virheraportti kohdistuu näkyviin ja erottaa lähdeaineiston virheen, generaattorin tukirajoitteen, resurssirajan ja huomion. Se kokoaa turvallisesti todettavia riippumattomia havaintoja; se ei ole täydellinen SHACL-validointi. Ehdotuksen yhteydessä näkyvät tietotyyppi/luokka, määrä ja polku ovat vain luettavia johdoksia. Kokeilu ei korjaa lähteen SHACLia.

**Muodosta paikallinen tekninen paketti** aktivoituu, kun ehdotus ja kolme kuittausta ovat olemassa sekä valittu tuotu profiili vastaa tuotteen profiilia. Aktiivinen painike ei takaa, että kaikki tekniset asetukset tai esimerkin sisältö ovat kunnossa: puutteet tarkistetaan suorituksessa ja näytetään virheinä.

**Keskeytä generointi** lopettaa Worker-suorituksen; aikaraja on 15 s. Keskeytys tai epäonnistuminen ei korvaa vanhaa pakettia.

## 14. Tuloksen lukeminen ja lataaminen

| Näytettävä tieto tai toiminto | Mitä se tarkoittaa? |
| --- | --- |
| Ei validoitu tässä kokeilussa | Paikallisella tuotteella ei ole palvelimen riippumatonta SHACL-/hyväksyntätulosta. Ei katoa onnistuneen paikallisgeneroinnin jälkeen. |
| Paikallinen kokeilupaketti – ei julkaistu | Tiedostot on muodostettu selaimessa, ei julkaistu URL-osoitteisiin. |
| Paketti vastaa tallennettuja generointisyötteitä | Paketin sidonta vastaa nykyisiä lähteitä/asetuksia. Ei väite täydellisestä SHACL-validoinnista tai toimivasta myöntämispalvelusta. |
| Paketti vanhentunut – muodosta uudelleen | Lähde, juuri, nimet, metadata, esimerkki tai muu sidottu asetus muuttui. Vanhan paketin tiedostoja voi ladata, mutta uuteen toteutukseen muodosta uusi paketti. |
| Lataa koko paikallinen paketti JSONina | Yksi tiedosto artefakteineen. **Ei kokeilun palautustiedosto.** Palautukseen käytä Vie kokeilu JSONina. |
| Lataa context.jsonld | W3C VC:n tietotuotekohtainen JSON-LD-konteksti; peruskonteksti on erillinen. |
| Lataa content.schema.json | Yhteisen JSON-/SD-JWT-väitesisällön skeema ja semanttiset annotaatiot. |
| Lataa sd-jwt-type-metadata.json | Vct-tyypin ja väitepolkujen tekninen kuvaus. Ei SD-JWT-todistus. |
| Lataa semantic-mapping.json | Yhteinen semantiikka, SHACL-kytkennät ja muotokohtaiset kenttäpolut. |
| Lataa semantic-extension-profile.json | Metatietovarannon oman x-mtv-laajennuksen määrittely. Ei väite yleisestä lompakkotuesta. |
| Lataa issuer-metadata-binding.json | Ohjeellinen vct / vct#integrity-sidonta ulkoiselle myöntäjälle. Ei allekirjoitus tai luottamustodiste. |
| Lataa content-example.json / sd-jwt-claims-example.json | Synteettinen yhteinen sisältö; ei JWT tai disclosureja. |
| Lataa unsigned-vc-example.jsonld | Synteettinen, allekirjoittamaton W3C VC -rakenne-esimerkki, jota ei ole myönnetty. |
| Lataa example.nq | JSON-LD-prosessorin tuottama esimerkin RDF-esitys. |
| Lataa validation.json | Mitä tässä suorituksessa tarkistettiin ja mitä ei. Selaimessa täydellinen SHACL ja graafivertailu ovat not-run. |
| Lataa source-N.ttl | Paketissa käytetty alkuperäinen päätiedosto/riippuvuus. |
| Lataa manifest.json | Syötteet, versiot, lähteet ja lopullisten artefaktien tarkisteet. |
| Tarkastele paikallista artefaktia | Avaa sisällön luettavaksi tekstinä ilman latausta. |
| Suunniteltu osoite (ei julkaistu) | Mahdollisen tulevan julkaisemisen osoite. Demo ei ole tarkistanut sen saavutettavuutta. |
| SHA-256 / snapshot / UUID | SHA-256 on sisällön tarkiste, snapshot lukittu lähdeversio ja UUID paikallisen tietueen tunniste. Näitä ei tarvitse keksiä tai kirjoittaa käsin. Tiedoston ja snapshotin hashit ovat eri asioita. |
| Alkuperäinen lähtöesimerkki – ei tämän tuotteen validointitulos | Esittelyn mukana tullut aiempi paketti. Sen raportti koskee alkuperäistä lähtöesimerkkiä, ei omaa muutettua tuotettasi. |

## 15. Kun työnkulku pysähtyy

| Tilanne / havainto | Toimi näin |
| --- | --- |
| Generointikohdan asetuksia ei näy | Liitä ensin Turtle-profiili tuotteeseen. Pelkkä tiedoston valinta tai mukana toimitetun snapshotin valinta ei riitä tähän polkuun. |
| Muodosta-painike ei aktivoidu | Tee onnistunut mapping-ehdotus, kuittaa kolme ruutua ja varmista sama tuotu profiili tuotteella ja generoinnilla. Uudelleenavauksen jälkeen ehdotus pitää muodostaa uudelleen. |
| CARDINALITY_TERM | Määrärajoitteen RDF-termi tai tietotyyppi ei kelpaa. Lähteen sh:minCount/sh:maxCount tarvitsee XSD-kokonaislukuliteraalin, esimerkiksi `"0"^^xsd:int` tai `1`. Tavallinen `"1"`-merkkijono tai desimaalitietotyyppi ei kelpaa. |
| CARDINALITY_LEXICAL | Kokonaisluvun kirjoitusasu on virheellinen, esimerkiksi `"1.5"^^xsd:integer` tai eksponenttiesitys. Korjaa lähde/export; lomakkeen mapping ei muuta lähdettä. |
| CARDINALITY_VALUE | Arvo on negatiivinen tai ilmoitetun XSD-tietotyypin ulkopuolella. Esimerkiksi xsd:positiveInteger ei salli nollaa ja xsd:byte ei salli arvoa 128. |
| CARDINALITY_CONFLICT | Samalle ominaisuuspolulle kohdistuvien määrärajoitteiden yhteinen maxCount on yhteistä minCountia pienempi. Tarkista kaikki raportin lähderajoitteet. |
| CARDINALITY_LIMIT | Kelvollinen kokonaisluku ylittää generaattorin oman 10 000:n resurssirajan. Tämä ei itsessään tarkoita RDF-/SHACL-syntaksivirhettä. Arvoja 0 ja 1 tyypillä xsd:int tuetaan. |
| DATATYPE_TERM | sh:datatype-arvo on IRI:n sijaan esimerkiksi Literal. Virheellinen: `sh:datatype "http://www.w3.org/2001/XMLSchema#boolean"`. Odotettu: `sh:datatype <http://www.w3.org/2001/XMLSchema#boolean>`. Korjaa lähdeprofiili tai exportin tuottaminen ja tuo uusi Turtle-export. |
| SEMANTIC_TOP_PROPERTY | Useat rajoitteet käyttävät samaa owl:topObjectProperty-polkua. Generaattori ei voi päätellä niistä eri sisältöominaisuuksia. Tarkista kaikki nimet/tunnisteet raportista ja määrittele tarkoitetut semanttiset ominaisuudet lähdemallissa. Tämä on mapping-este, ei itsessään RDF-/SHACL-syntaksivirhe. |
| PROPERTY_CONSTRAINT_INTERSECTION | Huomio: saman polun yhteensopivat nimetyt literaalirajoitteet muodostavat yhden kentän. Määrärajoitteista käytetään leikkausta ja kaikki alkuperäiset rajoiteviitteet säilyvät. Ei erillisiä keksittyjä ominaisuuksia. |
| PROPERTY_CONSTRAINT_UNSUPPORTED | Saman polun rajoitteiden yhdistelmä ylittää tuen, esimerkiksi eri tyypit, nimetön moninkertainen rajoite tai moninkertaiset oliomuodot. Tämä ei yksin todista SHACLia virheelliseksi. |
| FIELD_LIMIT / DIAGNOSTIC_LIMIT | Esitarkistus on rajattu 200 kenttään ja 200 havaintoon. Raportin resurssieston jälkeen pakettia ei muodosteta; tarkista lähde ja aja uudelleen. |
| THREE_DISTRIBUTIONS | Tarvitaan yksi kutakin kolmesta toimitustavasta. Poista ylimääräinen saman tyypin kuvaus. |
| BROWSER_SERVICE_SCOPE | Aseta kaikille saatavuudeksi Suunnitteilla. |
| FORMAT_POLICY_REQUIRED / SDJWT_PROFILE_REQUIRED | Tarkista vct, nimetty SD-JWT-profiiliversio, W3C-sisältöpolku, suojausprofiilit ja tarvittavat algoritmit. |
| DISCLOSURE_REQUIRED | Kenttäkohtaiset päätökset puuttuvat. Täydennä ne oikein tai valitse kaikkien kenttien yhteinen käytäntö. |
| SDJWT_DISCLOSURE / DISCLOSURE_PATH_REVIEW | Aina näkyvien väitteiden lista tai vanhempi/lapsi-päätökset ovat ristiriidassa uuden mappingin kanssa. |
| RESERVED_NAME / NAME_COLLISION | Muuta ehdotuksen kenttänimi sallittuun ja yksilölliseen nimeen, tarkista ehdotus uudelleen ja kuittaa se. Älä muuta alkuperäistä IRI:tä. |
| TURTLE_SYNTAX | Varmista, että latasit oikean UTF-8 Turtle -exportin etkä verkkosivua. Tarkista ilmoitettu syntaksikohta. |
| UNRESOLVED_SHAPE | Liitä tarvittavan sh:node-muodon sisältävä paikallinen Turtle-riippuvuus ja tuo kokonaisuus uudelleen. |
| OBJECT_AMBIGUOUS / DATATYPE_UNSUPPORTED / SHACL_UNSUPPORTED | Nykyinen generaattori ei voi kuvata rakennetta luotettavasti. Älä keksi puuttuvaa tyyppiä tai poista rajoitetta huomaamatta. Tarkasta alkuperäinen malli Tietomallit-työkalussa tai käytä tuettua testiprofiilia. |
| EXAMPLE_SCHEMA | Korjaa JSON-esimerkki ehdotettujen kenttien, objektien, taulukoiden ja min/max-määrien mukaiseksi. |
| BROWSER_EXAMPLE_LEXICAL | Date/dateTime-arvon tarkka XSD-esimerkkitarkistus puuttuu selainversiosta. Älä muuta lähteen tyyppiä stringiksi vain virheen kiertämiseksi. |
| Kokoraja / aikaraja | Lähteille yhteensä 256 KiB, 10 000 kolmikkoa; enintään 8 tasoa / 200 kenttää. Esimerkki 100 kB, koko kokeilu 2 MiB. Suuri johdannaispaketti voi ylittää kokonaisrajan, vaikka lähde mahtuu. Aiempi kokeilu säilyy virheessä. |
| SOURCE_HASH / ARTIFACT_HASH / vioittunut tallenne | Älä korvaa toimivaa työtilaa vioittuneella tiedostolla. Ota raakatallenne talteen ja käytä aiempaa ehjää JSON-varmuuskopiota. |

Lomakkeen lisäkenttien täyttäminen ei korjaa lähdeprofiilin tietotyyppi- tai ominaisuuspolkumäärityksiä. Korjaa lähde ja tuo uusi Turtle-export. Demo ei muuta URI:n näköistä merkkijonoa automaattisesti IRI:ksi eikä keksi polkuja näyttönimistä.

**WE BUILD Certificate of Residence 0.0.2:** alkuperäinen export voidaan tuoda ja sen sisältöä tarkastella, mutta kaikki viisi juurta ylittävät nykyisen generointituen. Ensimmäiset esteet liittyvät epäselvään literaali-/oliorakenteeseen. Tämä ei tarkoita, että alkuperäinen Tietomallit-profiili olisi yleisesti virheellinen. [Juurikohtainen tukiraportti](browser-webcor-report.json).

Tekninen rajaus ja täsmälliset erot palvelinsovellukseen: [Selaimen SHACL-generointi](browser-shacl-generation.md). Tallennus- ja siirtoformaatti: [Oma kokeilu](own-experiment.md).
