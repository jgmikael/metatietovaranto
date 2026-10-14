# Metatietovarannon toteutussuunnitelma ja tekoälykoodauksen kehote

Versio 1.1 · 14.10.2026 · Toteutusehdotus Suomen julkishallinnon käyttöön

Version 1.1 täsmennys: tietotuotteen semanttinen perusta on Tietomallit-työkalun soveltamisprofiili. Katso sitova periaate luvusta 1.3 ja tarkennus `docs/semanttinen-periaate-1.md`. Toista suunnitteluolettamaa ei ole vielä käsitelty.

## 1 Tarkoitus ja käyttöohje

Toteuta tämän dokumentin perusteella ajettava Metatietovaranto: viranomaisten ylläpitämä, tietotuotteiden kuvauksia kokoava ja julkaiseva palvelu. Tietotuote tarkoittaa nimettyä ja hallittua tietokokonaisuutta, jolla on määritelty merkitys, rakenne, vastuut, käyttöehdot ja yksi tai useampi jakelutapa. Ensisijainen käyttötapa on viranomaislähteisiin perustuvien attribuuttitodistusten löytäminen ja käyttöönotto eIDAS-kehyksen digilompakoissa. Samaa sisältöä voidaan tarjota myös REST API -rajapinnasta JSON-muodossa.

Dokumentti on itsenäinen toimeksianto tekoälyä käyttävälle ohjelmistokehittäjälle. Sen voi antaa kokonaisuudessaan esimerkiksi GitHub-repositorioon toteuttavalle koodausagentille. Luvussa 18 on työn käynnistävä kehote. Luvuissa 4–8 määritellään toteutettava tietomalli ja validoinnit; luvut 9–17 määrittelevät toiminnallisuuden, teknisen toteutuksen ja hyväksymisen. Pelkkä käyttöliittymäluonnos ei täytä toimeksiantoa.

Tässä määritelty kansallinen soveltamisprofiili on suunnitteluehdotus. Kenttien nimet, pakollisuus, ohjelmistopino ja palvelutasot ovat tämän ratkaisun vaatimuksia, eivät DSSC:n, Gaia-X:n tai IDS:n sellaisinaan määräämä yhteinen skeema. Lähteistä johdetut periaatteet erotetaan paikallisista ratkaisuista luvussa 3. Tuotantokäyttö edellyttää nimettyjä vastuutahoja ja hyväksyttyjä tiedonluovutuksen sekä luottamuspalvelujen menettelyjä.

### 1.1 Ensimmäisen version lopputulos

Viranomainen voi kuvata tietotuotteen, liittää siihen semanttiset määritykset ja jakelutavat, lähettää kuvauksen tarkastettavaksi ja julkaista hyväksytyn version. Kehittäjä tai valtuutettu ohjelmistoagentti löytää tuotteen haulla, näkee sen käyttöedellytykset ja saa koneellisesti luettavan kuvauksen. Julkaistun kuvauksen jokainen versio on myöhemmin yksilöitävissä.

Palveluun tallennetaan metatietoja, skeemoja ja synteettisiä esimerkkejä. Varsinaiset henkilö- ja yrityskohtaiset todistukset, lähderekisterien tietueet, lompakoiden sisällöt, yksityiset avaimet ja käyttöoikeustokenit kuuluvat muihin järjestelmiin. Metatietovarannon omat käyttäjätilit ja auditointitiedot ovat erillisiä hallinnollisia tietoja.

### 1.2 Rajaus ja oletukset

Ensimmäinen versio toteuttaa keskitetyn metatietohakemiston ja hajautetut ylläpitovastuut. Viranomainen vastaa omista kuvauksistaan. Tietotuotteiden toimitus tapahtuu viranomaisen tai muun nimetyn palveluntarjoajan palveluista. Ratkaisu ei edellytä yhteistä keskitettyä henkilötietokantaa.

Metatietovaranto ei itse myönnä tuotannollisia QEAA-todistuksia, tee luovutuspäätöksiä eikä toteuta koko data-avaruuden sopimusneuvottelua. Se kuvaa näihin tarvittavat toimijat, ehdot, todistustyypit, palvelut ja tekniset liittymät. Ensimmäiseen versioon sisältyy paikallinen todistuspalvelun simulaattori vain demokäyttöön.

### 1.3 Tietomallit soveltamisprofiili sisällön ensisijaisena lähteenä

Jokaisen tietotuotteen semanttinen tietomalli perustuu Yhteentoimivuusalustan Tietomallit-työkalussa laadittuun soveltamisprofiiliin. Se tuodaan linkkinä tai alustalta ladattuna tiedostona. Profiili on SHACL-graafi, joka hyödyntää alustalla sijaitsevaa OWL-ydintietomallia tai ulkoisen nimiavaruuden OWL-sanastoa, tarvittaessa useita. Alkuperäiset tunnisteet ja riippuvuudet säilytetään. Metatietovaranto ei luo rinnakkaista käsin ylläpidettävää sisältömallia.

JSON-LD, RDF kuten RDF/XML ja Turtle ovat RDF/SHACL-aineiston esityksiä. OpenAPI ja JSON Schema ovat profiilista tuotettuja johdannaisia; ne eivät yksin korvaa SHACL-perustaa. JSON-exportin rooli ja skeemadialekti tunnistetaan sisällöstä. Pelkkä JSON-LD-konteksti ei ole soveltamisprofiili. Kaikkia exportteja ei vaadita jokaiselle tuotteelle.

Tietotuoteversio sitoutuu yksilöityyn profiiliversioon tai lukittuun snapshotiin. Linkin ja tiedoston tulee olla vaihtoehtoisia toimitustapoja; palvelu voi säilyttää linkistä noudetun kopion. Tietoelementtiluettelo johdetaan profiilista. Profiilin ja sitä käyttävän tuotteen metatiedot, katalogin vienti sekä todistuksen kuori ovat eri asioita. Täsmälliset kentät ja hyväksymisehdot ovat dokumentissa `docs/semanttinen-periaate-1.md`. Tämä periaate on ensisijainen suhteessa tämän suunnitelman yleisempiin muotoiluihin.

## 2 Käyttötapaukset ja käyttäjät

### 2.1 Viranomaisen ylläpitäjä

Ylläpitäjä luo tuotteen ohjatulla lomakkeella. Hän kuvaa esimerkiksi verovelkatietotuotteen sisällön, lähdejärjestelmän, tiedon tuoreuden, käsitteet ja tietokentät. Hän lisää REST-jakelun sekä suunnitellun lompakkotodistuksen profiilin. Palvelu näyttää puutteet kenttäkohtaisesti ennen tarkastukseen lähettämistä.

### 2.2 Semanttinen tarkastaja ja julkaisija

Tarkastaja arvioi käsitteiden, OWL-sanaston, SHACL-profiilin, JSON-skeeman ja jakelukohtaisten kenttäkartoitusten johdonmukaisuuden. Julkaisija tarkistaa vastuut, käyttöehdot, oikeusperustaviitteet ja luottamusväitteiden perustelut. Julkaisu ei merkitse viranomaisen tiedonluovutusoikeuden tai QTSP-aseman myöntämistä.

### 2.3 Kehittäjä ja tiedon hyödyntäjä

Kehittäjä etsii julkisen hankinnan kelpoisuustarkastukseen soveltuvia tietotuotteita. Hakutulos kertoo tarjoajan, sisällön, saatavuuden, jakelutavat, maantieteellisen soveltuvuuden ja käyttöedellytykset. Tuotesivu kertoo myös, mitä tuote ei todista. Esimerkiksi verovelan määrää kuvaavaa tuotetta ei automaattisesti tulkita hankintalainsäädännön mukaista poissulkemista ratkaisevaksi todistukseksi.

### 2.4 Ohjelmistoagentti

Agentti hakee metatietoja rajapinnasta ja valitsee semanttisten tunnisteiden perusteella sopivan tuotteen. Se saa tietää, mistä todistus tai API-palvelu löytyy ja mitä valtuuksia käyttö edellyttää. Tuotteen löytyminen ei anna agentille pääsyä henkilön tietoihin. Agentin tehtävävaltuutus, organisaation edustamisoikeus ja palvelun pääsyoikeus tarkistetaan erikseen toimituspalvelussa.

### 2.5 Hakemiston ylläpitäjä

Ylläpitäjä hyväksyy organisaatiot, hallitsee kansallista metatietoprofiilia ja koodistoja, seuraa vanhentuneita kuvauksia sekä käsittelee häiriöt. Hän ei saa korvata viranomaisen hyväksyntää muuttamalla julkaistua sisältöä huomaamatta.

## 3 Standardiperusta ja sen soveltaminen

| Lähde | Lähteestä käytettävä periaate | Tämän toteutuksen ratkaisu |
| --- | --- | --- |
| DSSC Blueprint 3.0 [S1] | Tietotuotteiden ja tarjonnan kuvaukset, löydettävyys, hallintamalli, osallistujat ja käytön ehdot kuuluvat data-avaruuteen. | Kuvausryhmät sisällölle, tarjoajille, politiikoille, laadulle ja ekosysteemin jäsenyyksille. |
| W3C DCAT 3 [S2] | Katalogi, aineisto, jakelu ja tietopalvelu kuvataan erillisinä resursseina. | DCAT-pohjainen ulkoinen vienti; sovelluksen sisäinen tietotuote kokoaa kuvauksen ja sen versiot. |
| SEMIC DCAT-AP 3.0.1 [S3] | Eurooppalainen soveltamisprofiili täsmentää katalogien yhteentoimivuutta. | Valittu viennin vertailuversio; validointi sen julkaistuilla SHACL-määrityksillä. Uudempi versio otetaan käyttöön erillisellä migraatiopäätöksellä. |
| Gaia-X Architecture 25.11 [S4] | Luottamuskehys erottaa toimijat, resurssit, palvelutarjonnan, politiikat ja vaatimustenmukaisuuden näytön. | Luottamusväite saa perustelun, arvioijan ja tarkistusajan. Gaia-X-sertifiointia ei oleteta. |
| IDSA Catalog Patterns [S5] | Kuvaukset ja käyttöehdot voidaan koota keskitettyyn tai federoituun hakemistoon; näkymä riippuu oikeuksista. | Ensimmäisessä versiossa push-julkaisu ja näkyvyysrajatut hakutulokset; myöhemmin harvestointi. |
| W3C ODRL 2.2 [S6] | Oikeudet, kiellot ja velvoitteet voidaan ilmaista koneellisesti. | Rajattu, versioitu politiikkaprofiili ja sen rinnalla ihmiselle luettava ehto. |
| W3C DQV [S7] | Laatua voidaan kuvata ulottuvuuksina, mittareina ja mittaustuloksina. | Erotetaan tavoitetaso, mitattu arvo ja mittauksen ajankohta. |
| eIDAS muutosasetus 2024/1183 [S8] | QEAA ja autenttisesta lähteestä vastaavan julkisen toimijan todistus ovat erotettavia oikeudellisia kategorioita. | Oikeudellinen todistusluokka ja tekninen formaatti ovat eri kenttiä. |
| Täytäntöönpanoasetus 2025/1569 [S9] | Attribuuttitodistusten toteutuksessa huomioidaan myös tarkentava sääntely. | Profiilissa on sovellettavien säädösten, standardien ja voimassaolon hallinnan viitteet. |
| W3C VCDM 2.0 [S10] ja OpenID4VCI 1.0 [S11] | Todistuksen tietomalli ja sen myöntämisen protokolla ovat eri asioita. | Semanttinen profiili ja formaattiadapteri erotetaan myöntämispalvelun kuvauksesta. |
| Data Act 2023/2854 artikla 33 [S12] | Yhteentoimivuuden kuvauksissa huomioidaan muun muassa rakenne, semantiikka, saatavuus ja rajoitukset. | Kentät aineiston kattavuudelle, rajoituksille, rakenteelle ja tekniselle saatavuudelle; soveltuvuus arvioidaan tapauskohtaisesti. |

Lähteet perustelevat suunnan. Täysi DSSC-, Gaia-X-, IDS-, DCAT-AP- tai eIDAS-vaatimustenmukaisuus voidaan ilmoittaa vasta kyseistä profiilia vastaan tehtyjen tarkistusten jälkeen. Katalogin REST API ei ole sellaisenaan Dataspace Protocol -rajapinta.

## 4 Käsitemalli ja tunnisteet

### 4.1 Tietomallin oliot

| Olio | Vastuu ja suhteet |
| --- | --- |
| Organization | Viranomainen tai muu tunnistettu organisaatio. Toimii tarjoajana, lähdevastuullisena, rekisterinpitäjänä, myöntäjänä tai operaattorina roolin mukaan. |
| SourceRegister | Nimetty lähderekisteri tai autenttinen lähde; vastuullinen organisaatio ja oikeusperustaviitteet. |
| DataProduct | Pysyvä tuoteidentiteetti, omistava organisaatio ja viite nykyiseen julkaistuun versioon. |
| ProductVersion | Julkaisun sisältösnapshot. Sisältää vähintään yhden lähdeviitteen ja yhden semanttisen profiilin. |
| SemanticProfile | Versioitu sisältösopimus: käsitteet, luokat, tietoelementit, validoinnit ja skeema-artefaktit. |
| Distribution | Tuoteversion konkreettinen esitystapa tai toimituskanava. Viittaa yhteen semanttiseen profiiliin ja yhteen tai useampaan tietopalveluun. |
| DataService | Rajapinnan tai todistuksen myöntämispalvelun tekninen kuvaus sekä operaattori ja ympäristö. |
| AttestationProfile | Todistustyypin oikeudelliset ja tekniset vaatimukset. Käytetään lompakkojakelussa; ei ole yksittäinen myönnetty todistus. |
| PolicySet | Versioidut näkyvyys-, pääsy- ja käyttöehdot. Soveltamisala on tuote tai yksittäinen jakelu. |
| TrustEvidence | Todiste väitteen perustasta ja tarkistuksesta. Ei korvaa ulkoista luottamusankkuria. |
| Artifact | SHACL, JSON Schema, konteksti, OWL-viite, OpenAPI tai muu määrittely; immutable-versio ja tarkiste. |
| Review ja AuditEvent | Hyväksyntä sekä hallinnollinen tapahtuma. Sidotaan sisältöversioon ja sen tarkisteeseen. |
| DataspaceMembership | Tuotteen tai organisaation suhde data-avaruuteen, sääntökirjaan ja mahdolliseen jäsenyysnäyttöön. |

DataProductilla on 0..n julkaistua ProductVersionia ja korkeintaan yksi aktiivinen työkopio. Julkaistulla ProductVersionilla on 1..n Distributionia, 1..n SemanticProfilea ja 1..n SourceRegister-viitettä. REST-jakelulla on DataService. Lompakkojakelulla on lisäksi AttestationProfile ja myöntämispalvelu. Sama profiili voidaan jakaa usean tuotteen kesken, mutta viittaus kohdistuu aina lukittuun versioon.

Distribution voi antaa semanttisen profiilin osajoukon. Tällöin `fieldMappings` luettelee jaellut elementit ja pois jätetyt elementit. Julkaisu estetään, jos jakelun pakollinen elementti jää ilman merkitystä tai kohdekenttää. Kaksi jakelua ei saa väittää olevansa sisällöllisesti identtinen, jos merkitys, ajallinen pätevyys tai tietojen tarkkuus eroaa.

### 4.2 Tunniste- ja versiointisäännöt

Sisäiset avaimet ovat UUID-tunnisteita. Ulkoiset tunnisteet ovat pysyviä HTTPS-URI-tunnisteita: `{PUBLIC_BASE_URL}/id/products/{uuid}`, ja version URI on `{productUri}/versions/{semver}`. Älä käytä henkilötunnusta, Y-tunnusta tai käyttäjän antamaa nimeä tuotteen teknisenä avaimena. Organisaatioiden tunnisteet tallennetaan erillisinä `(scheme, value)`-pareina.

Tuotteen identiteetti, metatietoprofiilin versio, julkaisuversio, semanttisen profiilin versio, lähteen sanastoversio ja rajapinnan versio ovat eri tietoja. Tuoteversiot noudattavat semanttista versiointia. Rikkova merkitys- tai rakennemuutos nostaa major-versiota, yhteensopiva lisäys minor-versiota ja korjaus patch-versiota. Julkaistua snapshotia ei muuteta. Sen voimassaolo, keskeytys tai korvaaminen kirjataan erilliseksi elinkaaritapahtumaksi.

URI palauttaa selaimelle HTML-kuvauksen ja `Accept`-otsakkeen mukaan JSON-LD- tai Turtle-kuvauksen. Käytä sisältöneuvottelussa `Vary: Accept`-otsaketta ja eri esitysten välimuistiavaimia. JSON API:n resurssit ovat lisäksi erillisessä `/api/v1`-avaruudessa. Arkistoidun julkisen version URI säilyy. Tuotteen peruuttaminen luettelosta ei peruuta jo myönnettyjä todistuksia.

## 5 Metatietosanasto ja pakollisuus

P = pakollinen julkaistaessa, E = ehdollinen ja V = valinnainen. Luonnos saa olla keskeneräinen. Ehdollisuus tarkistetaan palvelimella. Tyhjä merkkijono tai tyhjä taulukko ei täytä pakollisuutta. URI on absoluuttinen tunniste; URL tarkoittaa noudettavaa resurssia. Ajankohdat ovat RFC 3339 UTC -aikoja, päivämäärät ISO 8601 -päiviä ja kestot ISO 8601 -kestoja. Merkkijonojen enimmäispituudet, lukuarvojen rajat ja taulukoiden enimmäiskoot määritellään JSON Schemassa.

### 5.1 Yhteiset tietotyypit

`LocalizedText` on kielikoodin ja tekstin sanakirja. Nimi ja kuvaus vaaditaan suomeksi; ruotsin- ja englanninkieliset vastineet ovat suositeltuja. `Ref` on `{id, version?}`. `LegalReference` sisältää säädöksen URI:n tai virallisen URL:n, säännösviitteen, selityksen ja tarkistusajan. Jos pysyvää säädös-URI:a ei ole, käytä yksilöityä virallista lähdeviitettä. `VersionedResource` sisältää `{uri, version, sha256?, mediaType?}`. `Assessment` sisältää tilan, perustelun, arvioijan ja ajan.

Seuraavien taulukoiden pistepolut ovat sisäisen JSON-profiilin polkuja. Ne eivät ole olemassa olevien standardien termitunnisteita. Ydinolioiden täsmällinen JSON Schema on tuotettava näiden sääntöjen perusteella. `additionalProperties: false` koskee ydinolioita; nimetty `extensions`-olio sallii vain URI-tunnisteiset ja skeemaan viittaavat laajennukset.

### 5.2 Identiteetti ja vastuut

| Polku | Tyyppi ja määrä | Vaatimus ja merkitys |
| --- | --- | --- |
| metadataProfile | VersionedResource 1 | P Metatietoprofiilin tunniste ja versio. |
| id | URI 1 | P Palvelimen antama tuotteen pysyvä tunniste. |
| version | semver 1 | P Tuoteversion numero. |
| title ja description | LocalizedText 1 kumpikin | P Tuotteen nimi ja ymmärrettävä sisältökuvaus. |
| purpose | LocalizedText 1 | P Mihin tuote on tarkoitettu. |
| limitations | LocalizedText 1 | P Mitä sisältö ei kata tai todista; tarvittaessa nimenomainen ei tunnettuja lisärajoituksia. |
| themes ja keywords | URI[] ja LocalizedText[] | P Vähintään yksi teema; V hakusanat. |
| subjectTypes | enum[] 1..n | P naturalPerson, legalPerson, legalArrangement, asset tai other. |
| providerOrganizationId | UUID 1 | P Julkaisusta ja tarjonnasta vastaava organisaatio. |
| responsibleUnit ja productOwner | teksti ja rooliyhteys 1 | P Ylläpitoyksikkö ja vastuuroolin yhteystieto; suosi ryhmäosoitetta. |
| steward ja supportContact | rooliyhteys 1 kumpikin | P Sisällön ylläpito ja käyttötuki. |
| controllerOrganizationIds | UUID[] 0..n | E Vaaditaan henkilötietoja sisältävälle tuotteelle. |
| processorOrganizations | rooliviite[] 0..n | V Käsittelijät ja tehtävien rajaus. |
| sourceRegisterIds | UUID[] 1..n | P Lähteet ja vastuulliset organisaatiot. |
| sourceRelations | olio[] 1..n | P Lähde, rooli, auktoritatiivisuusväite, perustelu ja tarkistus. |
| landingPage ja documentation | URL 0..1 ja URL[] | V Lisäohjeet; tuotesivu muodostuu automaattisesti. |

Organisaatiotietue sisältää vähintään `id`, `legalName`, `identifiers`, `country`, `roles`, `verificationStatus`, `verificationEvidence` ja `verifiedAt`. Todellinen organisaatio hyväksytään ylläpitäjän prosessissa; demo-organisaatio merkitään synteettiseksi. Lähdetietue sisältää `id`, `name`, `responsibleOrganizationId`, `legalReferences`, `authenticSourceAssessment`, `coverage` ja `documentationUrl`.

### 5.3 Semantiikka ja rakenne

| Polku | Tyyppi ja määrä | Vaatimus ja merkitys |
| --- | --- | --- |
| semanticProfiles | Ref[] 1..n | P Lukitut sisältöprofiilit. |
| profile.id ja profile.version | URI ja semver | P Profiilin identiteetti ja versio. |
| profile.vocabularies | VersionedResource[] 1..n | P Käytetyt sanastot kuten EU Core tai EBWV; täsmälliset versiot. |
| profile.conceptSchemes | VersionedResource[] | V SKOS-käsitejärjestelmät ja terminologiset viitteet. |
| profile.subjectClassUri | URI 1 | P Tiedon kohteen luokka; OWL-sanaston olemassa oleva termi. |
| profile.elements | DataElement[] 1..n | P Lähdeprofiilista johdettu tietoelementtinäkymä; ei erillinen käsin ylläpidettävä malli. |
| profile.shaclArtifactId | UUID 1 | P Sisällön RDF-validointiprofiili. |
| profile.jsonSchemaArtifactId | UUID 0..1 | E JSON-jakelun validointia varten. Johdettu samasta lähdeprofiilista; lähdeskeeman ilmoittama draft/dialekti säilytetään. |
| profile.jsonLdContextArtifactId | UUID 0..1 | E Vaaditaan JSON-LD-jakelussa. |
| profile.mappingArtifactIds | UUID[] | E Vaaditaan, jos jakelut tai lähderakenne poikkeavat sisältöprofiilista. |
| profile.exampleArtifactIds | UUID[] 1..n | P Vähintään yksi synteettinen validi sisältöesimerkki. |
| profile.conformanceTargets | VersionedResource[] | V Sääntökirjat, standardit ja hyväksytyt soveltamisprofiilit. |

Jokainen `DataElement` sisältää pakolliset kentät `id` (profiilin sisäinen pysyvä avain), `name`, `description`, `semanticPropertyUri`, `datatype`, `minCount`, `maxCount` ja `personalDataCategory`. Valinnaiset tai ehdolliset kentät ovat `conceptUri`, `objectClassUri`, `codeList` version kanssa, `unitUri`, `pattern`, `minimum`, `maximum`, `format`, `sourceField`, `derivationRuleRef`, `valueMeaning`, `temporalMeaning`, `sensitivity`, `disclosureGroup` ja `exampleValue`. `maxCount: null` tarkoittaa rajatonta. Olioarvoisella elementillä `objectClassUri` on pakollinen. Rahasummassa ilmaistaan valuutta erillisellä elementillä tai kiinteänä profiilitietona.

Boolean-kentän nimi ei yksin määritä totuusarvon merkitystä. Esimerkiksi `debtBalance=true` tarvitsee kuvauksen siitä, tarkoittaako se velan olemassaoloa, nollarajaa vai muuta sääntöä. Päivämäärän merkitys erottaa havaintohetken, antamispäivän, jakson alun ja todistuksen voimassaolon.

Palvelu ei keksi puuttuvia EU Core- tai EBWV-termejä. Jos sopivaa termiä ei ole, käytä erillistä paikallista ehdotusnimiavaruutta ja merkitse laajennus tarkastettavaksi. Varsinaisten sanastojen julkaisut pysyvät niiden ylläpitäjien vastuulla.

### 5.4 Oikeudet ja data-avaruuden ehdot

| Polku | Tyyppi ja määrä | Vaatimus ja merkitys |
| --- | --- | --- |
| policySetId | Ref 1 | P Tuotteen käyttöehtojen versio. |
| policy.metadataVisibility | enum 1 | P public, authenticated tai restricted. |
| policy.metadataAudience | organisaatio- tai rooliviite[] | E restricted-näkyvyyden sallittu yleisö. |
| policy.dataAccessCategory | enum 1 | P open, conditional tai restricted; erillään metatiedon näkyvyydestä. |
| policy.personalData ja specialCategoryData | boolean 1 kumpikin | P Henkilötietojen ja erityisten henkilötietoryhmien sisältyminen. |
| policy.processingLegalBases | LegalReference[] | E Vaaditaan henkilötietoja käsittelevän toimituspalvelun kuvaukselle. |
| policy.disclosureLegalBases | LegalReference[] 1..n | P Tiedon luovutuksen tai julkaisun perusteen viitteet ja selitys. |
| policy.purposes | URI[] 1..n | P Sallitut käyttötarkoitukset paikallisesta versioidusta koodistosta. |
| policy.eligibleConsumers | sääntö[] 1..n | P Sallitut vastaanottajaryhmät ja todentamistapa. |
| policy.subjectRequest ja consent | olio 1 kumpikin | P Erottele henkilön pyyntö, lompakon hyväksyntä ja mahdollinen GDPR-suostumus. |
| policy.mandateRequirements | olio 1 | P Edustaminen tai agenttikäyttö: required, typeUri, scope, verificationServiceRef. |
| policy.termsUrl ja termsVersion | URL ja teksti | P Ihmiselle luettavat ehdot ja versio. |
| policy.licenseUri | URI 0..1 | E Avoimessa datassa vaaditaan; ei korvaa henkilötietojen käsittelyperustetta. |
| policy.retention | olio 1 | P Vastaanottajan säilytysehto ja sen oikeudellinen peruste tai notSpecified perusteluineen. |
| policy.onwardSharing | enum 1 | P allowed, conditional, prohibited tai notSpecified; lisäehtojen viite. |
| policy.prohibitions ja obligations | sääntö[] | P Saa olla tyhjä vain perustellusti; esim. edelleenluovutus ja käyttöloki. |
| policy.odrlArtifactId | UUID 0..1 | E Vaaditaan automaattisesti tulkittaviksi ilmoitetuille käyttöehdoille. |
| policy.enforcement | olio 1 | P Valvova toimija, palvelu, päätöslogiikan viite ja valvonnan rajat. |
| policy.geographicRestrictions | URI[] | V Sijainti- tai lainkäyttörajoitukset ja soveltamisperuste. |
| policy.pricing | olio 1 | P free, paid, statutoryFee tai unknown; maksulliselle hinnasto, valuutta ja laskentaperuste. |
| dataspaceMemberships | jäsenyysolio[] | V Data-avaruuden tunniste, sääntökirjaversio, hallinnoija, jäsenyysnäyttö ja voimassaolo. |

Suostumus, valtuutus, sopimus ja lakisääteinen tiedonluovutus eivät ole toistensa synonyymejä. Käyttäjän pyyntö saada todistus ei itsessään ratkaise kolmannen osapuolen oikeutta käsitellä sen sisältöä. GDPR:n tarkastusoikeutta ei koodata yleiseksi oikeudeksi saada QEAA-todistus tai luovuttaa viranomaisaineistoja rajattomasti.

`PolicySet` jakaa säännöt kolmeen osaan: metatiedon näkyvyys, tiedon saamisen edellytykset ja saadun tiedon käyttöehdot. Viranomaisen toimivaltaa tai lakisääteistä käyttörajoitusta ei korvata kaupallisella lisenssillä. ODRL kuvaa ehtoja; ehtojen olemassaolo ei osoita, että kaikki velvoitteet voidaan teknisesti valvoa vastaanottajan ympäristössä.

### 5.5 Laatu ja elinkaari

| Polku | Tyyppi ja määrä | Vaatimus ja merkitys |
| --- | --- | --- |
| coverage.spatial ja jurisdiction | URI[] | P Soveltamisalue ja oikeudellinen konteksti. |
| coverage.temporal | jakso tai dynaamisen kattavuuden kuvaus | P Ajallinen kattavuus. |
| coverage.population ja exclusions | LocalizedText | P Kohdejoukko ja pois rajatut tilanteet. |
| quality.updateFrequency | koodi ja selitys | P Lähdetiedon päivitysrytmi. |
| quality.maxSourceLag | duration 0..1 | E Vaaditaan, jos tuoreudelle luvataan enimmäisviive. |
| quality.freshnessDescription | LocalizedText | P Miten tiedon ikä määrittyy; ei sama asia kuin todistuksen voimassaolo. |
| quality.metrics | mittari[] | V Mittari, ulottuvuus, yksikkö, tavoite, havainto, mittausaika, menetelmä ja näytön viite. |
| quality.knownIssues ja correctionProcess | teksti[] ja URL | P Puutelista saa olla tyhjä; korjausprosessi aina pakollinen. |
| provenance.lineage | lähde- ja muunnosvaihe[] | P Tiedon alkuperä, muunnokset ja johdetut arvot kuvauksina. |
| lifecycle.status | enum | P draft, inReview, approved, published, deprecated, withdrawn tai archived. |
| lifecycle.createdAt ja modifiedAt | datetime | P Palvelimen hallitsemat ajat. |
| lifecycle.reviewDueAt | datetime | P Seuraava sisällön tarkistus. |
| lifecycle.issuedAt ja effectiveFrom | datetime | E Julkaisussa vaaditaan. |
| lifecycle.sunsetAt ja replacementId | datetime ja URI | E Lopetettavalle tuotteelle lopetusaika ja seuraaja tai perusteltu puuttuminen. |
| metadataProvenance | olio | P Kuvauksen laatijaorganisaatio, lähde, tarkiste ja mahdollinen harvestointiaika. |

Laatumittari ei saa sisältää keksittyä mittaustulosta. Jos vain tavoite on tiedossa, havainto ja mittausaika jätetään pois ja mittarin tila on `targetOnly`. Metatiedon vanheneminen näkyy hakutuloksessa, mutta ei automaattisesti peruuta lähdepalvelua.

## 6 Jakelujen ja palvelujen metatiedot

| Polku | Tyyppi ja määrä | Vaatimus ja merkitys |
| --- | --- | --- |
| distribution.id ja title | URI ja LocalizedText | P Jakelun tunniste ja nimi. |
| distribution.channel | enum | P walletAttestation tai restApi. Jatkolaajennus voi lisätä tiedosto- ja tapahtumajakelut. |
| distribution.semanticProfile | Ref | P Sisällön version viite. |
| distribution.fieldMappings | mapping[] | P Profiilielementin id, lähdepolku, kohdepolku ja mahdollinen muunnosviite. |
| distribution.mediaTypes | merkkijono[] 1..n | P Esitysmuodot IANA-mediatyyppeinä. |
| distribution.serviceIds | UUID[] 1..n | P Toimituksesta vastaavat palvelut. |
| distribution.policyOverride | Ref 0..1 | V Tuotteen ehdoista poikkeavat jakeluehdot; eivät saa hiljaisesti lieventää lain rajoituksia. |
| distribution.availability | enum | P planned, sandbox, production tai suspended. |
| service.operatorOrganizationId | UUID | P Tekninen operaattori. |
| service.endpointUrl ja documentationUrl | URL | P Palveluosoite ja dokumentaatio, myös demoarvo selvästi merkittynä. |
| service.environment | enum | P sandbox tai production. |
| service.protocol ja protocolVersion | teksti | P Nimetty protokolla ja lukittu versio. |
| service.authentication | olio | P Menetelmät, vaaditut tunnistetiedot, scopes ja metatieto-URL:t; ei salaisuuksia. |
| service.authorization | olio | P Päätöksentekijä, pääsyehdon viite ja valtuutuksen todentamistapa. |
| service.serviceLevels | olio | P Tuki, ylläpitoikkuna sekä saatavuus- ja vasteaikatavoitteet tai perusteltu unknown. |
| service.rateLimits | olio | V Kiintiöt, aikayksikkö ja ylitystilanteen käsittely. |
| service.regions ja processingLocations | URI[] | V Käsittely- ja palvelualueet. |
| service.health | olio | V Tarkistusaika, saavutettavuustulos ja testimenetelmä. |
| service.openApiArtifactId | UUID | E REST-jakelun OpenAPI-kuvaus pakollinen. |
| service.errorModel | VersionedResource | P Virherakenne ja asiakasta ohjaavat virhekoodit. |

REST-jakelussa kuvataan lisäksi resurssien tai operaatioiden tarkoitus, kyselyparametrien skeema, sivutus, tuetut kenttärajaukset, tunnistejärjestelmät ja aikaleimojen merkitys. Henkilötunnisteita ei sisällytetä metatieto-URL:iin eikä lokiteta esimerkkipyyntöinä. Metatietovarannon API ja kuvattu viranomaisen data-API ovat erillisiä palveluja.

Suunniteltu jakelu voidaan julkaista vain, jos se on näkyvästi `planned`, mukana on vastuuhenkilö ja tavoitepäivä, eikä hakutulos esitä sitä käytettävissä olevana tuotantopalveluna. Vähintään yhden jakelun tulee olla sandbox- tai production-tilassa, jotta tuote saa käyttöliittymän `usableNow`-merkinnän.

## 7 Lompakkotodistuksen profiili ja luottamus

### 7.1 Todistusluokka ja myöntäjät

`legalCategory` saa arvon `QEAA`, `PublicSectorAuthenticSourceEAA`, `EAA` tai `Unassessed`. QEAA edellyttää sovellettavien vaatimusten mukaista hyväksyttyä luottamuspalvelua ja myöntäjää. Autenttisesta lähteestä vastaavan julkisen toimijan tai sen puolesta annettu todistus kuvataan omana luokkanaan. Luokan valinta ei seuraa automaattisesti siitä, että tarjoaja on viranomainen tai sisältö on W3C VC -muodossa. [S8–S9]

`intendedLegalCategory` ilmaisee tavoitteen, jos luokka ei ole vielä todennettu. Käyttöliittymä näyttää tällöin esimerkiksi ”QEAA-tavoite — luottamusasemaa ei vahvistettu”. Automaattinen haku `verifiedLegalCategory=QEAA` palauttaa vain voimassa olevan näytön perusteella vahvistetut osumat.

### 7.2 Profiilin kentät

| Kenttä | Vaatimus |
| --- | --- |
| id, version, title, semanticProfile | P Profiilin identiteetti ja sisällön versio. |
| legalCategory, intendedLegalCategory | P Todettu luokka; V tavoiteltu luokka. |
| schemeUri ja schemeVersion | E Vaaditaan, jos todistus kuuluu nimettyyn attestaatioskeemaan. |
| applicableSpecifications | P Säädös-, standardi-, ARF- ja kansallisten profiiliversioiden viitteet sekä tarkistuspäivä. |
| issuerOrganizationId ja sourceProviderOrganizationId | P Myöntäjä ja lähdetiedon vastuullinen toimittaja; voivat erota. |
| authenticSourceVerification | P Mitkä attribuutit tarkistetaan, mistä lähteestä ja minkä palvelun kautta. |
| qualificationEvidenceIds | E Vahvistetulle QEAA- tai julkisen toimijan erityisluokalle luottamusnäyttö. |
| supportedRepresentations | P Formaattikohtaiset adapterit ja metatiedot. |
| issuanceServiceId | P Kuvattu myöntämispalvelu. |
| subjectIdentification ja holderBinding | P Kohteen yksilöintitapa ja haltijasidonnan vaatimus tai perusteltu soveltumattomuus. |
| validityPolicy | P Voimassaolon määräytyminen, enimmäiskesto ja uusiutuminen. |
| statusPolicy | P Voimassaolon tai peruutuksen tarkistusmenetelmä, ohjeen URL ja yksityisyysominaisuudet. |
| selectiveDisclosure | P supported, unsupported tai representationDependent; formaattikohtainen tarkennus. |
| presentationRequirements | P Vastaanottajan tunnistamisen, tietojen minimoinnin ja käytön periaatteiden viitteet. |
| revocationTriggers ja incidentContact | P Peruutuksen syyt ja häiriöyhteys. |
| assuranceAssessment | P assessed, unassessed tai expired, arvioija, ajankohta ja perustelu. |

`supportedRepresentations` kuvaa esimerkiksi W3C VC JSON-LD-, SD-JWT VC- tai mdoc-esityksen, mutta toteutus ei oleta niiden olevan kaikissa lompakoissa keskenään vaihdettavia. Adapterissa ovat `format`, `formatVersion`, `schemaArtifactId`, `semanticMappingArtifactId`, `credentialTypeIdentifiers`, `cryptographicSuiteReferences`, `walletProfileReferences` ja `interoperabilityEvidence`. W3C VCDM on semanttisen demoprofiilin lähtökohta; tuotannon sallittu formaatti määräytyy käytettävän eIDAS- ja lompakkoprofiilin mukaan. [S10]

OpenID4VCI-palvelun kuvauksessa `credentialIssuer` yksilöi issuer-metadataa tarjoavan tahon ja `credentialConfigurationIds` sen tukemat nimetyt konfiguraatiot. Lisää valtuutuspalvelimen metatieto-URL ja dokumentaatioviite. Älä rakenna tuotannon myöntämisprotokollaa itse ensimmäiseen versioon. [S11]

### 7.3 Luottamusnäyttö

`TrustEvidence` sisältää `id`, `claimType`, `subjectOrganizationId`, `serviceIdentifier`, `evidenceUri`, `evidenceType`, `trustFrameworkUri`, `assessedBy`, `checkedAt`, `validUntil`, `result`, `method`, `environment` ja `limitations`. `result` on verified, rejected, expired tai unverified. Tallenna tarkistetun väitteen kohde: myöntäjän yksi palvelu ei tee kaikista saman organisaation palveluista hyväksyttyjä.

Ensimmäisessä versiossa virallinen näyttö voidaan kirjata tarkastajan arvioimana; näytä menetelmä `manualReview`. Luottamuslistan automaattinen kryptografinen tarkistus on erillinen jatkokehitystehtävä. Demo käyttää vain `unverified`-näyttöä, eikä näytä virallisen QEAA-palvelun hyväksyntämerkkiä. Erillinen synteettinen testifixture saa todentaa validointisäännöt suljetussa testissä.

Vahvistettu luottamusmerkintä lasketaan dynaamisesti voimassa olevasta näytöstä. Vanhentunut näyttö poistaa vahvistetun merkinnän ilman julkaistun snapshotin muuttamista. Hakutuloksen mukana palautetaan aina arvioinnin ajankohta.

## 8 Skeemat ja semanttinen yhteentoimivuus

### 8.1 Kaksi eri skeemakerrosta

Metatietoprofiilin JSON Schema ja SHACL validoivat tietotuotteen kuvausta. Tuotteen sisältöprofiilin JSON Schema ja SHACL validoivat puolestaan luovutettavaa tietosisältöä. Näitä ei yhdistetä yhdeksi skeemaksi. Todistuksen kuori, kuten myöntäjä ja voimassaolo, on vielä oma rakenteensa suhteessa credentialSubject-sisältöön.

Sisältöketju on SKOS-käsitteet → OWL-sanasto → SHACL-soveltamisprofiili → JSON-esitys ja JSON-LD-konteksti → todistuksen formaattiadapteri. Tämä kuvaa hallittuja riippuvuuksia; SHACL ei yksin tuota täydellistä JSON Schemaa, eikä JSON-LD-konteksti validoi tietojen oikeellisuutta. Muunnoksissa tarvitaan eksplisiittisiä kartoituksia ja esimerkkien testejä.

Tietomallit-soveltamisprofiili on tämän ketjun ensisijainen sisältösopimus. Metatietovaranto lukee SHACL-graafin ja sen OWL-viitteet linkistä tai tiedostosta sekä liittää samaan lähdeversioon saatavilla olevat JSON Schema- ja OpenAPI-johdannaiset. Sisältöprofiilin omaa skeemadialektia ei korvata katalogin metatietoskeeman dialektilla. Täysi SHACL-graafi säilytetään, vaikka käyttöliittymä näyttäisi siitä vain osan.

### 8.2 DCAT-vienti

| Sisäinen tieto | Viennin termi tai ratkaisu |
| --- | --- |
| Tietotuotteen sisältöversio | dcat:Dataset; tuotteen pysyvä URI yhdistää versiot. |
| Jakelu ja palvelu | dcat:Distribution ja dcat:DataService; distribution → dcat:accessService → palvelu. |
| Nimi, kuvaus ja tarjoaja | dct:title, dct:description ja dct:publisher. |
| Teema ja asiasana | dcat:theme ja dcat:keyword. |
| Versionumero ja edeltävä versio | dcat:version ja dcat:previousVersion. |
| Formaatti ja rajapinta | dcat:mediaType, dcat:endpointURL ja dcat:endpointDescription oikeilla resurssitasoilla. |
| Oikeudet ja lisenssi | dct:accessRights, dct:rights ja dct:license soveltamisalan mukaan. |
| Soveltamisprofiili | dct:conformsTo; tarkka profiili-URI ja versio. |
| Lähde ja alkuperä | dct:source ja tarvittaessa PROV-O-laajennus. |
| Laatu ja käyttöpolitiikka | DQV- ja ODRL-viitteet erillisinä resursseina. |
| Todistusluokka, lompakkokonfiguraatio ja valtuusvaatimukset | Paikalliset mtr:-laajennukset; ei keksittyjä dcat:-termejä. |

Käytä DCAT-AP-viennissä sen edellyttämiä kontrolloituja sanastoja ja luokkia. Sisäisen profiilin yksinkertaiset enum-arvot kartoitetaan versionhallituissa taulukoissa ulkoisiin URI-arvoihin. `mappingCoverage` kertoo kenttäkohtaisesti direct, transformed, extension tai notExported perusteluineen. Älä nimeä puutteellista vientiä DCAT-AP-vaatimustenmukaiseksi.

Alkuvaiheen nimiavaruus on konfiguroitava `https://metadata.example.org/vocab/`. Se on demon placeholder, ei kansallisesti hyväksytty julkaisuosoite. Tuotannossa nimiavaruuden ylläpito ja URI:en pysyvyys ratkaistaan ennen käyttöönottoa.

### 8.3 Artefaktit

Artefakti sisältää `id`, `kind`, `version`, `mediaType`, `sha256`, `storageKey` tai sallitun ulkoisen URL:n, `sourceUri`, `license`, `createdAt`, `validationStatus` ja `dependencies`. Julkaisussa käytetyt skeemat ja kontekstit lukitaan tarkisteella. Etäviitteitä ei noudeta julkaisuvalidoinnissa vapaasti internetistä; sallitut riippuvuudet tuodaan etukäteen hallittuun välimuistiin. JSON-LD-kontekstien ja SHACL-riippuvuuksien muutokset eivät saa muuttaa vanhan julkaisun tulkintaa.

Toteuta JSON Schema-, RDF-jäsennys-, SHACL- ja esimerkkien validointi. Yhteensopivuustarkistus tuottaa raportin, joka kertoo muun muassa puuttuvat kartoitukset, ristiriitaiset kardinaliteetit ja poikkeavat tietotyypit. Ohjelma ei väitä ratkaisevansa ontologioiden täydellistä loogista ekvivalenssia.

## 9 Ylläpitoprosessi ja valtuudet

### 9.1 Tilasiirtymät

Normaali ketju on draft → inReview → approved → published → deprecated → archived. Tarkastaja voi palauttaa inReview-version draft-tilaan kommentin kanssa. Published-versio voidaan myös siirtää withdrawn-tilaan, jos sen käyttäminen tai kuvaus on virheellinen. Jokainen siirtymä on palvelimen tarkistama komento.

Uusi työkopio voi syntyä published-version rinnalle. Sen muokkaus ei muuta näkyvää julkaisua. Julkaisu tapahtuu tietokantatransaktiossa, joka tallentaa snapshotin, hyväksyntäviitteet, auditointitapahtuman ja outbox-tapahtuman. Tuotteen nykyversioviite vaihtuu vasta onnistuneessa julkaisussa. Palautus aiempaan sisältöön tehdään uutena julkaisuna.

### 9.2 Roolit

| Rooli | Oikeus |
| --- | --- |
| Anonymous | Julkisten, julkaistujen kuvausten haku ja vienti. |
| AuthenticatedReader | Oman organisaation tai erikseen sallitun yleisön kuvaukset. |
| ProductEditor | Oman organisaation luonnosten ja artefaktien ylläpito. |
| SemanticReviewer | Profiilien ja kartoitusten tarkastus valtuutetussa organisaatiossa. |
| Publisher | Sisällön hyväksyntä ja julkaisu omassa organisaatiossa. |
| RegistryAdmin | Organisaatioiden hyväksyntä, profiilin ja koodistojen ylläpito, käyttökatkon hallinta. |
| Auditor | Valtuutetun laajuuden tapahtuma- ja hyväksyntäloki. |
| ServiceAccount | OAuth-scopeihin ja organisaatioon sidottu koneellinen toimija. |

Kirjoittaja ei saa hyväksyä omaa muutostaan. Ensimmäisessä versiossa vaaditaan eri käyttäjän antama hyväksyntä sekä semanttisen tarkastuksen tulos; sama tarkastaja voi toimia julkaisijana, jos organisaation politiikka sen sallii. Julkaisuhyväksyntä sidotaan sisältötarkisteeseen. Hyväksynnän jälkeinen muutos palauttaa version draft-tilaan ja mitätöi hyväksynnän.

Organisaatioraja tarkistetaan palvelimella jokaiselle oliolle, liitteelle, viennille ja hakutulokselle. RegistryAdmin ei saa muokata toisen organisaation hyväksyntöjä. Hätäkeskeytys kirjataan perusteluineen ja ilmoitetaan vastuulliselle organisaatiolle järjestelmän sisäisenä tehtävänä.

### 9.3 Julkaisun estävät säännöt

1. Kaikki P-kentät ja toteutuneet E-ehdot täyttyvät; viittaukset kohdistuvat olemassa oleviin lukittuihin versioihin.
2. Tarjoaja ja lähdevastuut on hyväksytty, ja tietotuotteella on nimetty ylläpitovastuu.
3. Jokaisella jakelulla on sisältöprofiili, käyttöehdot, saatavuustila ja tekninen palvelukuvaus.
4. Esimerkit läpäisevät sisältöskeemat; JSON-LD-esimerkki laajenee odotettuihin termitunnisteisiin ja läpäisee SHACL-tarkistuksen.
5. Luottamusluokan näyttö on riittävä. Puutteellinen QEAA-näyttö sallii vain Unassessed-luokan ja erillisen tavoitteen.
6. Henkilötietotuotteella on rekisterinpitäjä, käsittely- ja luovutusperusteen kuvaus sekä pääsyehdot. Palvelu tarkistaa täydellisyyden; oikeudellisen soveltuvuuden hyväksyy nimetty ihminen.
7. Artefaktit ja esimerkit eivät sisällä salaisuuksia tai aitoja henkilötietoja; ylläpitäjä vahvistaa esimerkkien synteettisyyden.
8. Sisällöllä on voimassa oleva toisen käyttäjän hyväksyntä ja semanttisen tarkastuksen raportti.

## 10 Käyttöliittymä

Toteuta suomenkielinen responsiivinen käyttöliittymä. Koodipohja tukee fi-, sv- ja en-kielisiä tuotetekstejä ja käyttöliittymän käännöstiedostoja. Tavoittele WCAG 2.2 AA -tasoa: näppäimistökäyttö, näkyvä kohdistus, otsikkohierarkia, virheiden yhteenveto ja ohjelmalliset kenttäotsikot.

Julkinen haku sisältää vapaan tekstin, teeman, tarjoajan, kohteen tyypin, semanttisen termin, jakelutavan, maantieteellisen alueen, saatavuustilan ja todennetun todistusluokan suodattimet. Hakutulos näyttää myös metatiedon tarkistusajan. Luottamusmerkinnöissä käytetään tekstiselitettä värin lisäksi.

Tuotesivun ensisijaiset osat ovat sisältö ja käyttötarkoitus, tietoelementit, tarjoaja ja lähteet, käyttöönoton ehdot, jakelutavat sekä laatu ja voimassaolo. Tekniset skeemat, JSON-LD, Turtle ja versiovertailu ovat avattavissa. Lompakkopainike ”Myöntämispalvelun ohjeet” avaa dokumentoidun palvelun; se ei väitä myöntävänsä todistusta suoraan katalogista.

Ylläpitonäkymässä on omat tuotteet, keskeneräiset tarkistukset, palautteet, versiovertailu ja tarkistusajan ylittäneet kuvaukset. Muokkauslomake on jaettu samoihin tietoryhmiin kuin luvut 5–7. Kenttien pakollisuus päivittyy valintojen mukaan. Automaattitallennus koskee vain luonnosta ja käyttää optimistista lukitusta.

Vertailunäkymässä voi verrata enintään neljää tuotetta samojen metatietoryhmien perusteella. Formaatti- tai luottamusluokka ei saa peittää sisällöllisiä eroja.

## 11 Rajapintasopimus

Toteuta OpenAPI 3.1 -sopimus ja JSON Schema 2020-12 -määritykset. Rajapinta käyttää JSONia, erilliset vientipolut RDF-esityksiä. Aikaleimat ja käyttöoikeudet ratkaistaan palvelimella. Asiakas ei saa asettaa auditointikenttiä, hyväksyntää, todettua luottamusasemaa tai omistavaa organisaatiota vapaasti.

| Operaatio | Tarkoitus ja keskeinen vastaus |
| --- | --- |
| GET /api/v1/products | Haku; items, nextCursor, appliedFilters. Vain käyttöoikeuden sallimat osumat. |
| GET /api/v1/products/{id} | Nykyinen julkaistu kuvaus ja erilliset ajantasaiset tila-arviot. |
| GET /api/v1/products/{id}/versions/{version} | Immutable-sisältöversio ja tarkiste. |
| GET /api/v1/products/{id}/versions | Sallitut versiot ja elinkaaritapahtumat. |
| POST /api/v1/products | Luo tuotteen ja ensimmäisen työkopion; 201 ja Location. |
| POST /api/v1/products/{id}/drafts | Luo seuraavan version työkopion nykyisestä julkaisusta. |
| GET ja PUT /api/v1/drafts/{draftId} | Lue tai korvaa työkopio; PUT vaatii If-Match-otsakkeen. |
| POST /api/v1/drafts/{draftId}/validate | Palauttaa virheet, varoitukset, säännön id:n ja JSON Pointer -polun. |
| POST /api/v1/drafts/{draftId}/submit | Lähetä tarkastukseen; 409 jos tila tai tarkiste on muuttunut. |
| POST /api/v1/drafts/{draftId}/reviews | Hyväksy tai palauta; payload sisältää tarkisteen ja kommentin. |
| POST /api/v1/drafts/{draftId}/publish | Julkaise hyväksytty tarkiste; idempotentti samalla avaimella. |
| POST /api/v1/products/{id}/lifecycle-events | deprecated, withdrawn tai archived; syy pakollinen. |
| GET /api/v1/organizations ja /semantic-profiles | Valintalistat ja sallitut kuvaukset. |
| POST /api/v1/artifacts | Lataa sallittu skeema tai synteettinen esimerkki; tarkiste ja validointitila. |
| GET /api/v1/artifacts/{id} | Lataa vain sellainen artefakti, johon lukijalla on oikeus. |
| GET /api/v1/catalog/export | Sivutettu DCAT-AP JSON-LD tai Turtle; samat näkyvyysrajat kuin haussa. |
| POST /api/v1/import-jobs | Validoi kuvaukset ensin dryRun-tilassa; MVP tukee omaa JSON-profiilia. |
| GET /api/v1/import-jobs/{id} | Tilat ja tietuekohtaiset virheet; julkaiseminen vaatii tavallisen hyväksynnän. |
| GET /api/v1/audit-events | Auditor-roolin rajattu tapahtumalista. |
| GET /health/live ja /health/ready | Prosessin ja riippuvuuksien tila; ei sisäisiä salaisuuksia. |

Hakufiltterit ovat `q`, `theme`, `providerId`, `subjectType`, `semanticUri`, `channel`, `availability`, `verifiedLegalCategory`, `jurisdiction`, `modifiedSince`, `cursor` ja `limit`. Oletusraja 20, enimmäisraja 100. Käytä vakaata avainsivutusta `(modifiedAt,id)` ja läpinäkymätöntä allekirjoitettua kursoria. Väärä kursori palauttaa 400. Enum-virhe ei saa muuttua hiljaiseksi suodattimen ohittamiseksi.

Virheet noudattavat RFC 9457 -rakennetta: `type`, `title`, `status`, `detail`, `instance`, `traceId`, `errors[]`. Kenttävirhe sisältää `path`, `ruleId`, `message` ja `severity`. Käytä 401 tunnistamattomalle, 403 kielletylle toiminnolle, 404 ei-näkyvälle resurssille, 409 tilaristiriidalle, 412 vanhalle ETagille, 422 skeemavirheelle ja 429 kuormitusrajoitukselle. If-Match puuttuu → 428.

Kirjoitukset käyttävät `Idempotency-Key`-otsaketta tuotteen luomisessa ja julkaisussa. Sama avain ja sama sisältö palauttavat alkuperäisen tuloksen 24 tunnin ajan. Sama avain eri sisällöllä palauttaa 409. Julkisia vastauksia voi välimuistittaa; tunnistetut tai rajoitetut vastaukset eivät päädy yhteiseen välimuistiin.

## 12 Arkkitehtuuri ja tekninen toteutus

### 12.1 Valittu toteutus

Rakenna TypeScript React -käyttöliittymä ja Python FastAPI -palvelin modulaarisena monoliittina. Tallenna tiedot PostgreSQL-tietokantaan. Käytä SQLAlchemyä ja Alembic-migraatioita, Pydanticia API-malleihin, jsonschema-kirjastoa JSON-validointiin sekä RDFLib- ja pySHACL-kirjastoja RDF- ja SHACL-käsittelyyn. OIDC-kirjautumista varten paikallisessa ympäristössä on Keycloak. Valitse toteutushetkellä tuetut vakaat versiot ja lukitse ne lock-tiedostoihin sekä konttiversioihin.

Tämä pino on ehdotus koodausagentin valinnanvaran rajaamiseksi. Jos olemassa oleva repositorio käyttää toista ylläpidettyä pinoa, säilytä se ja dokumentoi vastaavat komponentit ADR-päätöksessä. Toiminnallisia vaatimuksia ei poisteta pinon vaihtuessa.

Palvelimen moduulit ovat catalog, organizations, semantics, policies, attestations, workflow, artifacts, search, exports ja audit. Julkaisusäännöt ovat domain-palvelussa, jota käyttöliittymä ja REST-kutsut käyttävät samoin. Erillinen worker suorittaa raskaat validoinnit; sama koodipohja, PostgreSQL-jobijono ja outbox riittävät ensimmäisessä versiossa. Ei pakollista Kafkaa, graafitietokantaa tai vektorihakua.

Artefaktit tallennetaan paikallisessa demossa erilliseen pysyvään volumeen; tuotannossa vaihdettavaan objektivarastoon. Tietokanta säilyttää metatiedot ja tarkisteet. PostgreSQL:n tekstihaku ja indeksoidut URI- sekä enum-kentät riittävät ensimmäisen version hakuun. Semanttinen haku tarkoittaa täsmällisten termitunnisteiden ja hyväksyttyjen kartoitusten hakua; se ei edellytä kielimallin päättelyä.

### 12.2 Tietokanta

Vähimmäistaulut: organizations, organization_memberships, source_registers, products, product_drafts, product_versions, semantic_profiles, distributions, data_services, attestation_profiles, policy_sets, trust_evidence, artifacts, artifact_dependencies, reviews, lifecycle_events, audit_events, import_jobs, background_jobs, outbox_events ja idempotency_keys.

Käytä relaatiotauluja omistajuuksille, tunnisteille, versioille, oikeuksille ja viittauksille. Sisältösnapshotin JSONB-esitys on sallittu, mutta sen viitteet validoidaan julkaisussa ja indeksoitavat kentät erotetaan. Tietokannassa ovat uniikkiusrajoitteet `(product_id, version)` ja aktiiviselle työkopiolle. Julkaistuihin sisältöriveihin ei tarjota UPDATE-rajapintaa; sovelluksen käyttörooli ei saa muuttaa niitä normaalissa kirjoituspolussa.

AuditEvent sisältää actorId:n, organisaation, toiminnon, kohteen, edeltävän ja uuden sisältötarkisteen, ajan, perustelun ja traceId:n. Tapahtumaan ei kopioida henkilötietoesimerkkejä tai tokeneita. Auditointi on append-only normaalille sovellusroolille. Tuotannollinen väärentämiseltä suojaaminen ja riippumaton säilytys toteutetaan erillisellä lokiratkaisulla.

### 12.3 Paikallinen käynnistys

Repositorion juuresta komento `docker compose up --build` käynnistää käyttöliittymän, API:n, workerin, PostgreSQL:n ja paikallisen OIDC-palvelun. Terveystarkistukset ohjaavat käynnistysjärjestystä. Migraatiot ja idempotentti demosiemennys suoritetaan hallitusti. README kertoo osoitteet, demokäyttäjät, roolit, testikomennot ja datan nollauksen erillisen komennon. Tavallinen käynnistys ei saa tuhota tietokannan volumea.

Kirjautuminen toimii oikealla paikallisella OIDC-ketjulla. Demo-oikopolut ovat sallittuja vain eksplisiittisellä DEMO_MODE-asetuksella. Käynnistys epäonnistuu tuotantotilassa, jos demoasetukset tai oletussalaisuudet ovat käytössä.

## 13 Tietoturva ja tiedonhallinta

OIDC-tunnistautuminen ja palvelimen valvomat organisaatiosidonnaiset oikeudet ovat pakollisia. Tarkista tokenin allekirjoitus, issuer, audience ja aikarajat; nouda avaimet vain konfiguroidulta tunnistuspalvelulta. Selain käyttää turvallista palvelinistuntoa tai dokumentoitua BFF-mallia, HttpOnly-evästeitä ja CSRF-suojausta. Älä tallenna pitkäikäisiä käyttöoikeustokeneita selaimen localStorageen.

Salaisuudet tulevat ympäristöstä tai salaisuuksien hallinnasta. CORS on sallittujen alkuperien lista. Lisää pyyntöjen koko- ja nopeusrajat, tiedostotyyppirajat ja parametrisoidut tietokantakyselyt. Skeema- ja RDF-validoinnilla on aika-, muisti-, syvyys- ja kolmoisraja. Tuotteen tekstit, Markdown ja ulkoinen HTML käsitellään epäluotettavana syötteenä ja puhdistetaan ennen näyttöä.

Ulkoisten URL:ien automaattinen nouto on SSRF-riski. MVP:ssa URL on viite, jota palvelin ei automaattisesti nouda. Erillinen sallittujen lähteiden noutotoiminto estää yksityiset osoiteavaruudet, localhostin, pilven metatietopalvelut, DNS-uudelleensidonnan ja hallitsemattomat uudelleenohjaukset. JSON-LD-dokumenttilataaja käyttää vain sallittuja lukittuja konteksteja. XML/RDF-jäsentäjiltä estetään ulkoiset entiteetit.

Rajoitetun tuotteen olemassaolo ei saa vuotaa hakumäärissä, suodatinvaihtoehdoissa, viennissä, artefaktin URL:ssa tai versiohistoriassa. Cache-avaimet sisältävät näkyvyyskontekstin. Julkisen tuotteen sisäiset yhteyshenkilöt, tarkastajakommentit ja luottamusnäytön mahdollisesti rajoitetut liitteet eivät kuulu julkiseen vientiin.

Määrittele konfiguroitavat säilytysajat käyttäjätiedoille, luonnoksille, auditointitiedoille ja jobilokeille. Tuotannon arvot hyväksyy rekisterinpitäjä; demo ei esitä niitä lakisääteisinä aikoina. Varmuuskopioi tietokanta ja artefaktit samaan palautuspisteeseen. Dokumentoi palautusharjoitus, version tarkisteiden tarkistus ja lokien käyttöoikeudet.

Agentin lukema metatieto on dataa. Jos tuleva avustava käyttöliittymä käyttää kielimallia, kuvaukseen sisältyvä teksti ei saa muuttaa agentin järjestelmäohjeita tai käynnistää työkalukutsuja. Generatiivinen tekoäly ei ole MVP:n ajonaikainen riippuvuus.

## 14 Esimerkkiaineisto

### 14.1 Kolme demotuotetta

1. **Yrityksen perustiedot**: synteettinen rekisteriviranomainen, oikeushenkilö, yritystunnisteet ja nimi; REST ja lompakkoprofiili. Tuotteen selitys kertoo, ettei perustieto yksin kuvaa kaikkia edustamisoikeuksia.
2. **Verovelkatiedot**: synteettinen veroviranomainen, tiedon kohteen tunniste, velan olemassaolo, määrä, valuutta ja havaintopäivä; rajoitetun tiedon pääsyehdot, molemmat jakelutavat.
3. **Edustamisoikeus**: synteettinen rekisteriviranomainen, päämies, edustaja, toiminnan laajuus, yksin tai yhdessä toimiminen ja voimassaolo; lompakkoprofiili ja valtuuden tarkistuspalvelun viite.

Tuotteet ovat mallintamisesimerkkejä. Älä väitä niitä PRH:n, Verohallinnon tai DVV:n oikeiksi rajapinnoiksi. Organisaatioiden nimissä näkyy ”Demo”. Käytä `.example`-verkkotunnuksia. Älä käytä oikeita tai oikealta näyttäviä henkilötunnuksia. Demossa henkilö yksilöidään `urn:example:person:001`-tunnisteella.

Lisää myös yksi luonnos, yksi vain organisaatiolle näkyvä julkaisu, yksi vanhentunut luottamusnäyttö ja yksi poistuva versio. Näillä osoitetaan näkyvyys, hyväksyntä ja elinkaari.

### 14.2 Havainnollistava kuvauskatkelma

Seuraava on julkaistavan tietotuotteen tiivistetty katkelma, ei koko skeeman mukainen dokumentti. Tekoälykoodaajan on tuotettava täydet validit fixturet ja niiden kaikki viitatut oliot. Paikalliset termit ovat demon termejä, eivät väitettyjä EBWV-termejä.

```json
{
  "metadataProfile": {"uri": "https://metadata.example.org/profiles/product", "version": "1.0.0"},
  "id": "https://metadata.example.org/id/products/4d9059f8-bc73-43ae-b2a5-9835ec8a35cf",
  "version": "1.0.0",
  "title": {"fi": "Verovelkatiedot Demo"},
  "subjectTypes": ["naturalPerson", "legalPerson"],
  "semanticProfiles": [{"id": "https://metadata.example.org/profiles/tax-debt", "version": "1.0.0"}],
  "policySetId": {"id": "https://metadata.example.org/policies/tax-debt", "version": "1.0.0"},
  "distributions": [
    {
      "id": "https://metadata.example.org/distributions/tax-debt-rest",
      "channel": "restApi",
      "availability": "sandbox",
      "mediaTypes": ["application/json"]
    },
    {
      "id": "https://metadata.example.org/distributions/tax-debt-wallet",
      "channel": "walletAttestation",
      "availability": "planned",
      "mediaTypes": ["application/ld+json"]
    }
  ],
  "attestationProfile": {
    "legalCategory": "Unassessed",
    "intendedLegalCategory": "QEAA",
    "assuranceAssessment": {"status": "unassessed", "reason": "Synteettinen demopalvelu"}
  }
}
```

Sisällön synteettinen JSON-esimerkki voi sisältää `subjectId`, `hasTaxDebt`, `amount`, `currency` ja `observedOn`. Näiden merkitykset, tietotyypit ja tietolähde määritellään profiilissa. Tuotantoesimerkkiä varten valitaan todelliset hyväksytyt semanttiset termit erillisen kartoituksen kautta.

### 14.3 Esimerkkien todentaminen

Kehittäjän on voitava näyttää selaimessa yritystietotuote, ladata sen profiili, hakea sitä semanttisella URI:lla ja vertailla REST- sekä todistusjakelujen kenttiä. Paikallinen simulaattori palauttaa synteettisen JSON-sisällön ja todistuksen havainnollistavan kuoren. Simulaattorin vastauksessa on `demo: true`; sitä ei esitetä kryptografisesti varmennettuna tai kelpuutettuna todistuksena. Testiavaimella tehty allekirjoitus on sallittu vain erikseen nimetyssä demo- tai testiprofiilissa.

## 15 Testit ja hyväksymiskriteerit

Kriittiset testit ovat osa toteutusta. Hyväksyminen perustuu ajettuihin tuloksiin, ei kuvakaappauksiin tai tekijän ilmoitukseen.

| Tunnus | Hyväksymiskriteeri ja todennus |
| --- | --- |
| AC01 | Puhdas checkout käynnistyy dokumentoidulla Compose-komennolla; readiness onnistuu ja demotuotteet näkyvät. |
| AC02 | Editor luo ja muokkaa oman organisaation luonnosta; toisen organisaation olion muuttaminen estyy myös suoralla API-kutsulla. |
| AC03 | Luonnos ja restricted-tuote eivät näy anonyymille haussa, faseteissa, versioissa, artefakteissa tai viennissä. |
| AC04 | Puuttuva luovutusperuste, rikkinäinen viite tai REST-jakelun puuttuva OpenAPI tuottaa kenttäkohtaisen julkaisua estävän virheen. |
| AC05 | Kirjoittaja ei hyväksy omaa muutostaan. Hyväksytyn sisällön muutos mitätöi hyväksynnän. |
| AC06 | Kaksi samanaikaista muokkausta ei hukkaa tietoja: vanha If-Match palauttaa 412; puuttuva 428. |
| AC07 | Julkaistu versio säilyy muuttumattomana uuden työkopion ja julkaisun jälkeen; hash on sama. |
| AC08 | QEAA ilman riittävää näyttöä ei saa verified-luokkaa. Vanhentunut näyttö poistuu vahvistetun luokan hausta. |
| AC09 | JSON-esimerkki läpäisee JSON Scheman; JSON-LD laajenee odotettuihin URI:hin ja läpäisee SHACL-profiilin. Virheellinen tietotyyppi hylätään. |
| AC10 | JSON-LD- ja Turtle-viennit jäsentyvät ja tuottavat saman RDF-graafin. DCAT-AP-testiraportti ja mahdolliset laajennuspoikkeamat tallentuvat. |
| AC11 | Sama tuotteen URI palvelee HTML:n, JSON-LD:n ja Turtlen oikein ilman välimuistimuotojen sekoittumista. |
| AC12 | Tuote löytyy semanticUri-suodattimella; planned-jakelu erottuu käytettävästä sandbox- tai production-jakelusta. |
| AC13 | Importin dryRun ei muuta tietoja. Tuonti ei julkaise sisältöä hyväksynnän ohi. Duplikaatit raportoidaan tunnisteittain. |
| AC14 | Julkaisuvirhe ei jätä puolikasta snapshotia tai nykyversioviitettä. Idempotentti uusintapyyntö ei luo toista versiota. |
| AC15 | URL-nouto, haitallinen konteksti, suuri RDF-graafi ja skriptiteksti eivät aiheuta sisäverkkoyhteyttä, rajatonta prosessointia tai XSS:ää. |
| AC16 | Auditointi näyttää julkaisijan, hyväksynnän, sisältötarkisteen ja perustelun; tokenit eivät näy lokeissa. |
| AC17 | Näppäimistöllä voi hakea, avata tuotteen ja korjata lomakkeen virheet; automaattinen saavutettavuustesti ei löydä kriittisiä virheitä. |
| AC18 | Varmuuskopiosta palautettu tietokanta ja artefaktit säilyttävät julkaistujen versioiden tarkisteet. |

Toteuta domain-yksikkötestit julkaisusäännöille, API-integraatiotestit PostgreSQL:llä, skeema- ja RDF-testit sekä Playwright-testit pääpoluille. Sisällytä kielteiset käyttöoikeustestit, jotta UI:n piilotus ei riitä suojaukseksi.

Suorituskykytavoite ensimmäiselle versiolle on 10 000 julkaistua tuotetta, 100 organisaatiota ja 20 samanaikaista lukijaa. Vertailuympäristössä 4 vCPU ja 8 GiB muistia API-haun p95 on alle 1 sekunti valmiiksi käynnistyneessä palvelussa; raskaita vienti- ja validointitöitä ei lasketa samaan mittariin. Raportoi datamäärä, kuorma, välimuistin tila ja mittaustulos. Tämä on suunnittelutavoite, ei osoitus valmiin järjestelmän suorituskyvystä.

## 16 Toteutusvaiheet ja GitHub-toimitus

### 16.1 Vaiheistus

**Vaihe A — sopimukset ja tietomalli.** Tuota metatietoprofiilin JSON Schema, OpenAPI, tietokantamigraatiot, sanastot ja täydet fixturet. Lisää ADR-päätökset tunnisteista, versioinnista, luottamusluokista ja näkyvyydestä. Hyväksyntä: skeematestit ja viitteiden eheyden tarkistus.

**Vaihe B — ylläpito ja julkaisu.** Toteuta OIDC, organisaatiorajat, luonnokset, tarkastus, julkaisu, auditointi ja käyttöliittymän lomakkeet. Hyväksyntä: AC02–AC08 ja AC14–AC16.

**Vaihe C — löydettävyys ja semanttiset kuvaukset.** Toteuta haku, tuotesivu, artefaktit, JSON-LD ja Turtle, sisältöneuvottelu sekä validointiraportit. Hyväksyntä: AC03 ja AC09–AC13.

**Vaihe D — ajettava toimitus.** Viimeistele Compose, CI, demopolut, saavutettavuus, palautusharjoitus ja kuormitusmittaus. Kaikki hyväksymiskriteerit on raportoitu. Ulkoiset tuotantointegraatiot kuvataan dokumentoiduiksi adapterirajoiksi.

### 16.2 Repositorion vähimmäissisältö

| Polku | Sisältö |
| --- | --- |
| README.md | Tarkoitus, rajaus, käynnistys, demopolku, testit ja ympäristöasetukset. |
| apps/web ja apps/api | Käyttöliittymä ja palvelin moduuleineen. |
| apps/worker | Taustatyön käynnistys saman palvelinkoodin pohjalta. |
| schemas/metadata ja schemas/content | Metatieto- ja demotuotteiden sisältöskeemat erikseen. |
| semantics | Metatietoprofiilin konteksti, SHACL ja vientikartoitukset. |
| fixtures | Synteettiset organisaatiot, tuotteet, politiikat ja esimerkit. |
| migrations | Versionhallittu tietokantarakenne. |
| tests | Yksikkö-, integraatio-, semantiikka- ja selainkokeet. |
| docs | Arkkitehtuuri, kenttäsanasto, uhkamalli, käyttöohje ja ADR-päätökset. |
| docker-compose.yml ja .env.example | Toistettava paikallisympäristö; ei tuotantosalaisuuksia. |
| .github/workflows | Linttaus, testit, skeemavalidointi ja konttien build. |
| SECURITY.md ja LICENSE | Haavoittuvuuksien käsittely ja valittu lisenssi. |

CI epäonnistuu, jos kriittinen testi, migraatiotarkistus, skeemavalidointi tai tuotantobuild epäonnistuu. Lukitse riippuvuudet ja dokumentoi päivityskäytäntö. Valmiissa toimituksessa ei saa olla ydintoimintoja korvaavia TODO-kommentteja tai pysyvästi muistiin tallentavaa tietokantaa.

## 17 Hallinta ja jatkokehitys

### 17.1 Vastuut ennen tuotantokäyttöä

Kansallinen palveluomistaja vastaa palvelun tarkoituksesta, rahoituksesta ja metatietoprofiilin muutosten hyväksymisestä. Tekninen operaattori vastaa käytettävyydestä, tietoturvasta ja palautumisesta. Viranomaiset vastaavat omien tuotteidensa sisällöstä ja oikeudellisista viitteistä. Semanttinen koordinaatio vastaa yhteisten käsitteiden, sanastojen ja profiilien muutosten käsittelystä yhdessä tietoalueiden asiantuntijoiden kanssa.

Tuotantopäätöksessä nimetään metatietopalvelun henkilötietojen rekisterinpitäjä, organisaatioiden hyväksyjä, pysyvien URI-tunnisteiden ylläpitäjä sekä luottamusasemaa koskevan näytön arvioija. Nämä ovat konfiguroitavia vastuita; ohjelmisto ei oleta minkään tietyn viraston saaneen tehtävää.

Metatietoprofiilin muutoksessa julkaistaan uusi skeema, muutosloki, migraatio-ohje ja siirtymäaika. Viranomaisen vanhaa julkaisua ei kirjoiteta automaattisesti uuteen merkitykseen. Katalogi säilyttää alkuperäisen profiiliversion ja voi näyttää siitä tuotetun uuden esityksen vain muunnoksen alkuperän kanssa.

### 17.2 MVP:n jälkeiset laajennukset

Prioriteetti 1: hyväksyttyjen viranomaiskatalogien harvestointi, poistojen välitys, ristiriitojen käsittely ja allekirjoitettujen metatietokuvausten tarkistus. Harvestointi säilyttää lähteen tunnisteen ja version eikä julkaise tuontia hyväksynnän ohi.

Prioriteetti 2: Dataspace Protocol -katalogiadapteri ja tarvittaessa DCP-tunnistus. Protokollayhteensopivuus testataan oikeaa vertaispalvelua vastaan; oma REST-vienti ei riitä.

Prioriteetti 3: tuotannollisten lompakko- ja QEAA-palvelujen integraatiot, luottamuslistan tarkistus sekä todistuskehyksen ajantasaisten profiilien käyttöönotto. Nämä eivät tee Metatietovarannosta itsestään hyväksyttyä luottamuspalvelua.

Prioriteetti 4: politiikkapäätöspalvelu ja tehtävävaltuuksien tarkistusadapteri. Metatiedon ehto, yksittäinen pääsypäätös ja luovutustapahtuman auditointi säilyvät eri vastuualueina.

Prioriteetti 5: sääntökirjojen ja palvelukokonaisuuksien kuvaukset esimerkiksi julkisen hankinnan tai elämäntapahtuman orkestrointiin. Agentti voi yhdistää löydetyt palvelut prosessiksi vain hyväksyttyjen valtuuksien ja sääntöjen puitteissa.

## 18 Tekoälykoodaajalle annettava käynnistyskehote

Kopioi seuraava ohje ja liitä mukaan tämä koko suunnitteludokumentti. Kehote ei tarvitse aikaisempia keskusteluja.

> Toimi kokeneena ohjelmistoarkkitehtina ja toteuttajana. Rakenna liitteenä olevan Metatietovarannon toteutussuunnitelman mukainen ajettava sovellus Git-repositorioon. Toteuta ensimmäisen version kaikki pakolliset toiminnot, skeemat, metatietoryhmät ja hyväksymiskriteerit. Käytä dokumentin ehdottamaa pinoa, ellei olemassa oleva repositorio perustellusti edellytä muuta.
>
> Aloita lukemalla repositoryn ohjeet ja kirjaa toteutussuunnitelma sekä vaatimusten jäljitettävyystaulukko. Toteuta ensin kokonainen polku organisaation kirjautumisesta tuotteen luonnokseen, tarkastukseen, julkaisuun ja julkiseen hakuun. Lisää tämän jälkeen semanttiset artefaktit, lompakkoprofiilit, politiikat, versiointi ja viennit. Älä pysähdy pelkkään suunnitelmaan tai käyttöliittymämalliin.
>
> Erottele tuotteen sisältö, metatietokuvaus, jakelu, myöntäjä ja luottamusnäyttö. Älä merkitse demoa QEAA-vaatimustenmukaiseksi. Älä keksi olemassa olevien sanastojen termitunnisteita. Jos oikeaa termiä tai ulkoista integraatiota ei voi varmistaa, käytä näkyvästi nimettyä paikallista demomääritystä ja dokumentoitua adapterirajaa. MVP:n katalogitoiminnot on silti toteutettava toimivina.
>
> Lisää pysyvä tietokanta, migraatiot, kolme synteettistä demotuotetta, paikallinen OIDC, Docker Compose, CI sekä domain-, API-, semantiikka- ja selaintestit. Dokumentoi asennus yhdestä puhtaasta checkoutista ja aja testit. Korjaa havaitut viat. Tuotannon ulkoisia tunnuksia tai salaisuuksia ei tarvita demoon.
>
> Toimita lähdekoodi, OpenAPI, JSON Schemat, SHACL, JSON-LD-konteksti, DCAT-kartoitukset, README, arkkitehtuuripäätökset ja testiraportti. Raportoi hyväksymiskriteereittäin toteutus ja ajettu todennus sekä jäljelle jäävät ulkoiset riippuvuudet. Älä esitä ajamatonta testiä onnistuneena. Älä julkaise ulkoiseen tuotantoympäristöön tai lisää aitoja rekisteritietoja ilman erillistä toimeksiantoa.

## 19 Lähteet ja tarkistusrajat

Lähteet tarkistettu 14.10.2026. Lähdeversiot ovat tässä suunnitelmassa valittuja vertailuversioita, eivät väite siitä, että ne olisivat jokaisen organisaation uusimmat hyväksytyt profiilit. Toteutusvaiheessa kirjataan uusi standardien ja sääntelyn tarkistuspäivä. Euroopan unionin viralliset säädöstekstit ja sovellettavat täytäntöönpanosäännöt ovat oikeudellisen tulkinnan ensisijaiset lähteet.

- **S1 DSSC Blueprint 3.0.** Erityisesti Data, Services and Offerings Descriptions; Publication and Discovery; Access and Usage Policies Enforcement; Identity and Attestation Management. https://blueprint.dssc.eu/
- **S2 W3C DCAT 3.** W3C Recommendation 22.8.2024. https://www.w3.org/TR/vocab-dcat-3/
- **S3 SEMIC DCAT-AP 3.0.1.** Eurooppalaisen katalogiviennin vertailuprofiili. https://semiceu.github.io/DCAT-AP/releases/3.0.1/
- **S4 Gaia-X Architecture Document 25.11.** Trust Framework architecture. https://docs.gaia-x.eu/technical-committee/architecture-document/25.11/trust_framework_architecture/
- **S5 IDSA Knowledge Base.** Catalog Patterns. Elävä dokumentaatio; käytetty 14.10.2026. https://kb.internationaldataspaces.org/external/ram/Pattern/Catalogs/
- **S6 W3C ODRL Information Model 2.2.** https://www.w3.org/TR/odrl-model/
- **S7 W3C Data Quality Vocabulary.** https://www.w3.org/TR/vocab-dqv/
- **S8 Asetus EU 2024/1183.** eIDAS-kehyksen muutos; erityisesti attribuuttitodistuksia koskevat artiklat 45d–45f ja liitteet V–VII. https://eur-lex.europa.eu/eli/reg/2024/1183/oj
- **S9 Komission täytäntöönpanoasetus EU 2025/1569.** Attribuuttitodistuksia koskevat soveltamissäännöt. https://eur-lex.europa.eu/eli/reg_impl/2025/1569/oj
- **S10 W3C Verifiable Credentials Data Model 2.0.** https://www.w3.org/TR/vc-data-model-2.0/
- **S11 OpenID for Verifiable Credential Issuance 1.0.** https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html
- **S12 Asetus EU 2023/2854.** Data Act, artikla 33. https://eur-lex.europa.eu/eli/reg/2023/2854/oj

Tämä dokumentti määrittelee toteutuksen ja vaatimusten tarkistukset. Se ei korvaa valvontaviranomaisen ratkaisua, QTSP-vaatimustenmukaisuuden arviointia, organisaation tiedonluovutuspäätöstä tai tuotannon tietoturva-arviointia.

