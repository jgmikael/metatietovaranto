# PR #13: toimitettujen ETSI-/EU-alkutekstien vertailu

18.10.2026 (Europe/Helsinki). Käyttäjä toimitti kolme PDF:ää: ETSI TS 119 472-1 V1.2.1 (2026-02), ETSI TS 119 478 V1.1.1 (2026-01) ja EU 2025/1569:n konsolidoinnin 11.8.2026 / 001.001. PDF:ien etusivut, jäljempänä yksilöidyt kohdat ja EU-tekstin muutosmerkit luettiin paikallisesti. Alkuperäiset tavut on tallennettu `fixtures/catalog-standards/originals/`; tiedostokohtainen koko, SHA-256, käyttäjätoimitus ja tarkastetut kohdat on lukittu `sources.json`-tiedostoon.

Kyse on käyttäjän toimittamien kopioiden sisältövertailusta, ei riippumattomasta verkkopalveluun vertailusta tai kaikenkattavasta ETSI-/EU-vaatimustenmukaisuusarviosta. Normatiiviset lauseet ovat analysoitavaa lähdeaineistoa, eivät sovelluksen laajentamista tai allekirjoituspalvelun rakentamista tilaavia ohjeita.

## Lähdetarkistuksen päätös 19.10.2026

Käyttäjä toimitti lisäksi alkuperäisen asetuksen **32025R1569** Relationship between documents -osion copy-pastena. Sen kymmenen riviä on kirjattu lähteineen tiedostoon `fixtures/catalog-standards/eur-lex-basic-act-relationships-2026-10-19.json`. Kyse on **käyttäjätoimituksen käsin rakenteistetusta jäljennöksestä**, ei virallisesta JSON-exportista tai riippumattomasta verkkonoudosta. Tyhjät solut ovat null ja päivät ISO-muodossa. Tiedoston SHA-256 ja koko ovat sources.json-tiedoston `basicActRelationshipEvidence`-osiossa.

| Lähteestä havaittu | Vaikutus tähän PR:ään | Tarkistuksen raja / myöhempi työ |
| --- | --- | --- |
| Corrected by **32025R1569R(01)**, kommentti **PL** | Oikaisu on nyt tunnistettu ja kielirajaus kirjattu; vertailun sisältölähde on toimitettu EN-teksti | Oikaisun koko tekstiä ei saatu (403). Sen sanamuotoa tai vaikutuksia PL-versioon ei väitetä arvioiduksi. Oikaisuja ei enää oleteta puuttuviksi. |
| EU 2026/1735: 3(2), 4(1)/4(3)/4(4), liitteet I/II/IV, From **11.8.2026** | Seitsemän riviä täsmäävät toimitetun konsolidoinnin muutosten rajaukseen. 3(2):n ja liite IV:n vaikutus myöntäjään/tarkistuspalveluun on kuvattu edellä. Ei muutostarvetta attribuuttiannotaatioiden tietomalliin. | Ei myöntäjän tai autenttisen lähteen verifiointia tässä PR:ssä. Liitteiden I/II kaikkien myöntäjä-/turvallisuusvaatimusten vaatimustenmukaisuusarviota ei tehty. |
| EU 2026/1735: 9(4) Replacement, 9(2a) Addition, From **1.1.2027** | Kaksi tulevaa muutosta erotetaan nykyisestä 11.8.2026 konsolidoinnista. PR ei toteuta 9 artiklan tarkistuspalvelua eikä päättele tulevaa palautussanomaa otsikkotiedosta. | Myöhemmän integraation on luettava täysi muutossäädös ja tuleva sanamuoto ennen 1.1.2027 soveltuvan tarkistuspalvelun toteutusta. Täyttä muutossäädöstä ei saatu (403). |
| Toimitetun EN-konsolidoinnin **11 artikla** | 6–9 artikloja sovelletaan **19.8.2026** alkaen; 11.8.2026 konsolidointipäivää ei käytetä kaikkien säännösten soveltamispäivänä | Tarkistuspäivänä 19.10.2026 tämä soveltamispäivä on jo ohitettu. Tulevia 1.1.2027 muutoksia ei silti sisällytetä nykyiseen kuvaukseen. |

**Artikla 4 ja liitteet I/II:** nykyisestä EN-konsolidoinnista luettiin myös M1-merkityt revokaatiokohdat, myöntäjä-/turvallisuusmääritysten rajaus ja liitteen II viittaus EU 2024/2979:n liitteeseen II. Revokaatio, kryptografia, lompakon tunnistus ja myöntäjän toimintaperiaatteet pysyvät ulkoisella palvelulla. Katalogin withdrawn/deprecated ei toteuta todistuksen revokaatiota. Tätä raja-arviota ei esitetä koko viitattujen standardien tai turvallisuusprofiilin auditointina.

**Päätös:** PR #13:n **englanninkielisiä metatietoja, semanttisia annotaatioita ja teknisiä kuvauspaketteja koskeva lähdevertailu on valmis ilmoitetuin rajauksin** (`reviewClosure.status=completed-with-disclosed-limitations`). Toimitetun luettelon perusteella ei tunnistettu tähän metatietomuutokseen tarvittavaa sovelluskoodin korjausta. Aiempi yleinen `EU_CORRIGENDUM_STATUS_UNVERIFIED` poistuu uusien pakettien raportista: luettelo on nyt saatu. Sen tilalla näkyvät täsmälliset `EU_POLISH_CORRIGENDUM_TEXT_NOT_REVIEWED` ja `EU_FUTURE_ARTICLE9_TEXT_NOT_REVIEWED`, joiden `blocksMetadataMerge=false` koskee vain tätä rajattua PR:ää. Tämä ei ole puolankielisen oikaisun tai tulevan säädöstekstin hyväksyntä.

Mainin sisältävällä haaralla tehtävien teknisten tarkistusten läpäistyä lähdevertailusta ei jää tämän rajatun PR:n yhdistämisesteeksi tunnistettua asiaa. Täysi ETSI-/EU-yhteensopivuus ei ole tämän PR:n hyväksymiskriteeri eikä sitä väitetä. ETSI draft-13 / paikallinen draft-19 -ero, ulkoisen myöntäjän vct-löydettävyys/integrity, katalogirekisteröinti ja autenttisen lähteen integraatio säilyvät näkyvinä puutteina.

**Todentamisen rajat:** EUR-Lexin ja EU Publications/Cellar-palvelun haut antoivat 403:n myös tässä tarkistuksessa; koneellinen noutoloki on `fixtures/catalog-standards/review-attempt-2026-10-19.json`. Ei riippumatonta verkkovertailua, kaikkien kieliversioiden tai kaikkien muutosten sanamuodon tarkistusta, allekirjoittamista tai vaatimustenmukaisuusarviota. `currentAsOfReviewDate=null` säilyy yleisen oikeudellisen ajantasaisuuden kohdalla; rajattu valmistumispäätös on erillisessä `reviewClosure`-osiossa. Käyttäjältä ei pyydetä samaa asiakirjasivua uudelleen.

Lähdepinnit ovat deterministisen paketin syöte. Generaattori **1.1.1**, IETF **draft-19** ja oma semanttinen laajennus **1.0.0** säilyvät; lähdeaineiston muutos tuottaa uudelle generoinnille eri pakettitunnisteen. Vanhojen julkaisujen raportteja tai profiilisnapshotteja ei kirjoiteta uudelleen. Uusi generointi kulkee normaalin luonnoksen, riippumattoman hyväksynnän ja version kautta.

## Viimeistelyn tekninen todennus 19.10.2026

- Koko README/CI:n 13 tiedoston API-/PostgreSQL-/migraatiosarja: **209 passed, 4 warnings in 355.05s (0:05:55)**. Ei epäonnistuneita tai ohitettuja. Oikeudet/CSRF, hyväksynnän mitätöityminen, julkaisuimmutabiliteetti, JSON-LD/RDF/SHACL, attribuuttiannotaatiot, tarkisteketju sekä vanhan/tyhjän kannan ja toistuvien migraatioiden kokeet mukana. Testit käyttivät vain erillistä catalog_test-kantaa.
- Oikea Chromium + Keycloak uudelleen rakennettua ja käynnistettyä Docker-sovellusta vasten: **13 passed, 1 warning in 115.88s (0:01:55)**. Tallennus/uudelleenavaaminen, organisaatiorajat, riippumaton hyväksyntä, julkaisu ja julkiset artefaktit läpäisivät. **222 eri pytest-testiä** yhteensä; varoitukset ovat Starlette/httpx- ja RDFLib-deprekaatioita.
- Uuden lähderegressiotestin lopullinen kohdennettu ajo: **1 passed, 1 warning in 0.21s**. Tarkistaa luettelon tarkisteen, alkuperän, PL-rajauksen, seitsemän nykyistä ja kaksi tulevaa muutosriviä, 19.8.2026 soveltamispäivän sekä niiden päätymisen generoituun raporttiin. Sama testitapaus kuuluu 209 testiin, eikä sitä lasketa lisätestiksi kokonaismäärään.
- `npm run build --prefix apps/web`: läpäisi (Vite 1,59 s). `bash scripts/cloud-build.sh` läpäisi TLS-varmennuksen säilyttäen; viimeinen image **sha256:6c7b957f54486509745c2369ffed1a0b923eb01689dcc41241665047ffa80177**. `docker compose up -d --no-build --wait`: app, db ja Keycloak healthy. Käynnissä olevan sovelluksen sources.json- ja muutosluettelotiedoston SHA:t vastaavat checkoutia.
- Ennen selaintestien uusia synteettisiä julkaisuja **13 catalog-kannan metatietotaulun kaikki rivit ja Alembic-head 0005_lifecycle säilyivät tarkalleen ennallaan uudelleenkäynnistyksessä**. Ei uutta relaatiomigraatiota tai fixtureiden palautusta; live-kantaa ei tyhjennetty.
- Julkinen HTTP-yhteensopivuuskoe selaintestien jälkeen: **88 julkaisuversiota luettavissa**, **8 vanhan generaattorin pakettia / 78 artefaktia** alkuperäisillä tavuilla ja SHA-arvoilla. Versioiden technicalPackage-sisällöt vastasivat tallennettuja muuttumattomia sisältöjä.
- Uuden paketin toimintakoe: kaikki **12 julkaistua artefaktia** palautuivat oikeilla mediatyypeillä ja tarkisteilla. Julkinen catalogue-coverage.json sisälsi täsmälleen uudet lähdepinnit ja rajatun päätöksen. Oikea `examples/semantic_consumer.py` palautti companyName-väitteen alkuperäisen ominaisuus-IRI:n, PropertyShapen ja lähdesnapshotin ilman väitearvoja tai JWT:n kryptografista tarkistusta.
- Main **9258fff** sisältyy työhaaraan; PR #13:n GitHub-mergeviitteen ensimmäinen vanhempi oli sama main, joten base on teknisesti vahvistettu. `git diff --check` läpäisi. Ei automaattista yhdistämistä.

**Ajamattomat:** riippumaton EUR-Lex-verkkovertaus, PL-oikaisun ja tulevan muutossäädöksen koko sanamuotojen luku, Windows Docker Desktop, uuden Codespacen luonti/openBrowser/Private-portin ajonaikainen tila, tuotanto-HTTPS ja GitHub Actionsin etätulos. Ei allekirjoitusta, lompakkotestiä, katalogirekisteröintiä tai täydellistä vaatimustenmukaisuusarviota. Aiemmat tarkistusajot alempana ovat historiaa, eivät lisäajoja tämän päälle.

## ETSI TS 119 472-1 V1.2.1

| Kohta / PDF:n painettu sivu | Lähteessä tarkistettu vaatimus | Metatietovarannon kuvaus ja raja |
| --- | --- | --- |
| 4.2.1.3-01…03, s.15–16 | URL-nimisten komponenttien konteksti kuvaa URL-/alias-vastaavuudet; sijoittelu riippuu toteutusmuodosta | SHACL-IRI:t ja JSON-kenttänimet säilyvät mappingissa. W3C saa oikean JSON-LD-kontekstin; SD-JWT:hen ei pakoteta W3C-kuorta tai JSON-LD @contextia. |
| 4.2.1.4-01…04, s.16 | Schema tarkistaa sisällön/rakenteen; skeemaviitteessä tyyppi ja URI | JSON Schema on tekninen johdannainen, SHACL alkuperäinen semanttinen rajoite. Oma x-mtv-schema on eksplisiittisesti paikallinen viiteprofiili, ei standardin schema/schema_uri-kenttä. |
| 5.1 ja 5.2.1.1, s.27; 2.1 viite [3], s.9 | ETSI:n SD-JWT-toteutus viittaa **draft-ietf-oauth-sd-jwt-vc-13**:een | Sovelluksen aiemmin lukittu **draft-19** säilyy. Ero raportoidaan, ei oleteta samaa standardiprofiilia eikä vaihdeta formaattia taustalla. Koko ETSI-profiilin yhteensopivuudesta ei tehdä väitettä. |
| EAA-5.2.1.2-01…03, s.27–28 | vct liittyy Type Metadataan ja osoittaa siihen; myönnetyssä SD-JWT VC:ssä vct#integrity | Generaattori julkaisee Type Metadatan ja myöntäjälle tarkoitetun vct/vct#integrity-ohjeen. Synteettinen URN-vct ja erillinen metadata-URL eivät yksin osoita ETSI:n vaatiman osoittamisen toteutumista. Ulkoinen myöntäjä järjestää oikean löydettävyyden, lisää väitteet todistukseen ja allekirjoittaa sen. |
| 5.2.1.3, s.28 | SD-JWT-kontekstin tietoa voidaan sisällyttää Type Metadataan | x-mtv-semantic mahdollistaa attribuuttikohtaisen semantiikan löytämisen; se on oma dokumentoitu laajennus. Lähde ei standardoi juuri tätä avainta eikä osoita lompakoiden tulkitsevan sitä. |
| 5.2.1.4, s.28 | Informatiivinen viite katalogeihin/Rulebook-kuvauksiin | Erillinen JSON Schema ja semanttinen mapping ovat löydettävissä paikallisilla x-mtv-viitteillä ja tarkisteilla. Pelkkä tämä kohta ei tuo aiemman IETF-luonnoksen schema/schema_uri-kenttiä draft-19:ään. |
| 7.2.1.1 ja 7.2.1.2-01…04, s.44 | W3C VCDM 2.0 type-taulukko ja @context URI-taulukko, mukana VCDM-peruskonteksti | Generoidussa allekirjoittamattomassa esimerkissä peruskonteksti ja tuotekonteksti ovat erilliset. Ei suojattujen perustermien uudelleenmäärittelyä; oikea PyLD ja lähde-SHACL tarkistetaan erikseen. ETSI:n omia uusia EAA-termejä ei keksitä katalogiin. |
| 7.2.1.3-01…04, s.44–45 | credentialSchema on valinnainen; jos käytössä, taulukko id/type-viitteitä. Nimet JsonSchemaCredential, CddlSchemaCredential ja ShaclSchemaCredential | Katalogin johdannaispaketti tarjoaa skeemat, mutta ei lisää myönnettyyn todistukseen schema- tai QEAA-väitteitä. Ulkoinen myöntäjä valitsee hyväksytyn skeema-/suojausprofiilin. SHACL ei tarkista allekirjoitettua JWT:tä. |

Valittu IETF draft-19, oma semanttinen laajennus 1.0.0 ja ETSI V1.2.1 ovat erillisiä lukkoja. Puuteraportti säilyttää `ETSI_SD_JWT_PROFILE_VERSION_DIFFERENCE`- ja `EXTERNAL_ISSUER_PROFILE_NOT_VERIFIED`-havainnot. Ne eivät ole väitteitä, että toimitustapa olisi QEAA tai että kaikki ETSI-vaatimukset olisi toteutettu.

## ETSI TS 119 478 V1.1.1

| Kohta | Tarkistettu sisältö | Paikallinen vastaavuus ja puute |
| --- | --- | --- |
| 3.1, s.12–13: semantic data specifications / semantic repository | Semantiikka ja sen tekniset esitykset ovat eri asioita; esityksinä voi olla RDF-/XML-/JSON-skeemoja | OWL-IRI, SHACL-snapshot, tekninen schema ja mapping säilyvät eri artefakteina. Eri IRI:jä ei korvata vastaavuuksilla automaattisesti. |
| 5.2.1 ja 5.2.2, s.17–19 | Discover-palvelun search ja sen suodattimet; mediaType-skeemaesitykset | Katalogin tuotemetatietojen haku ei ole tämän DIP-rajapinnan toteutus. Ei I1-yhteensopivuusväitettä tai täydellistä attribuuttikatalogia. |
| REQ-DIP-5.2.3-03-01/-02, s.20 | attributeIdentifier on URI ja sisältää nimiavaruuden, paikallisen tunnisteen ja version | Alkuperäinen OWL-ominaisuus-IRI ei automaattisesti ole katalogin antama versioitu attribuuttitunniste. Ulkoinen viite vaatii hyväksytyn vastaavuuden ja alkuperän. |
| REQ-DIP-5.2.3-08, s.20 | semanticDataSpecification-URI viittaa media-agnostiseen semanttiseen määrittelyyn | Profiili-IRI ja lukittu SHACL ovat semanttinen lähde; JSON-kentän nimi ja JSON Schema eivät yksin korvaa niitä. |
| REQ-DIP-5.2.3-09/-10, s.21 | schemaDistribution sisältää accessURL- ja mediaType-kentät | Paikallisilla artefakteilla on URL ja oikea mediatyyppi, mutta katalogi ei esitä niitä valmiina standardin DIP-vastauksena. Lähteen esimerkki application/json-schema ei muuta palvelumme JSON Schema -artefaktin application/schema+json-mediatyyppiä. |
| 5.3, s.21 alkaen | retrieve löytää jäsenvaltion tietopalveluja attribuutin tunnisteella | Ei toteuteta tässä. Omistajaorganisaatio tai myöntäjän aloituslinkki ei ole automaattisesti kansallinen attribuutin todentamispiste. |

TS11 1.0.1:n oma viite V0.0.7:ään säilytetään sen alkuperäisenä tietona. Lopullisen V1.1.1:n sisältövertailu perustuu nyt toimitettuun PDF:ään, ei luonnoksen nimeämiseen uudelleen.

## EU 2025/1569, toimitettu konsolidointi 11.8.2026

Etusivu luettelee muutossäädöksen **EU 2026/1735, 15.7.2026, EUVL 22.7.2026**. Konsolidoitu teksti on etusivunsa mukaan dokumentointiväline; autenttiset säädöstekstit julkaistaan EUVL:ssä. Tässä ei väitetä erillisen muutossäädöksen autenttista alkuperäistekstiä saaduksi. Artiklat 7 ja 8 näkyvät toimitetussa tekstissä B-perustekstin merkeillä. M1-merkittyjä muutoksia näkyy muualla, mm. 3(2):ssa ja liitteissä.

| Kohta / painettu PDF-sivu | Tietovaatimus | Paikallinen kuvaus / puuttuva tieto |
| --- | --- | --- |
| 7(5)(a)–(b), s.6 | Pyytäjän tunnistus ja tarvittaessa oikeudellinen/hallinnollinen authentic source -perusta | Organisaatiometatiedot ovat lähtötietoa, eivät todistus oikeusperustasta tai rekisteröintikelpoisuudesta. Virallinen hakija/oikeusperusta puuttuu. |
| 7(5)(c)–(e), s.6 | Uusi vai olemassa oleva attribuutti; katalogin yksikäsitteinen namespace, paikallinen tunniste ja attribuutin versio | Valinnainen catalogueReferences ja hyväksytty vastaavuus; ei automaattista samastusta OWL-ominaisuuteen. Tuote-/snapshot-versio ei korvaa attribuutin katalogiversiota. |
| 7(5)(f)–(h), s.6 | Semanttinen kuvaus, tietotyyppi ja kansallinen todentamispiste/aloituskuvaus | SHACL/mapping antavat sisältösemantiikan vain tuetun profiilin rajoissa. Todentamispistettä ei päätellä tarjoajasta eikä myöntäjän lompakkolinkistä. |
| 7(6), s.6 | Rekisteröintipyynnön allekirjoitus/sinetöinti määritellyllä tasolla | Ei toteuteta; tavallinen katalogin kirjautuminen tai hyväksyntä ei ole tällainen allekirjoitus. |
| 7(8) ja 7(10), s.7 | Komission sinetöimä, maksuton, ilman ennakkotunnistamista saavutettava kone-/ihmisluettava hakukatalogi; Komission attribuuttitunniste | Paikallinen demo/Private Codespaces ei ole tämä palvelu. Paikallinen UUID tai tuote-IRI ei ole Komission antama attribuuttitunniste. |
| 8(3)(a)–(d), s.7 | Järjestelyn nimi, omistaja/yhteystiedot, tila/versio ja sääntöviitteet | Tuotteen kuvaus ja valinnainen scheme-viite ovat osittaisia lähtötietoja. Järjestelyä ei luoda tuotteen tai teknisen scheman synonyymiksi. |
| 8(3)(e)–(f), s.8 | Formaatit sekä attribuuttien namespaces/tunnisteet/semantiikka/tietotyypit tai attribuuttikatalogiviitteet | Distributions ja mappingit kuvaavat formaatit ja semanttisen perustan; muodosta ei päätellä rekisteröityä järjestelyä tai attribuuttitunnistetta. |
| 8(3)(g)–(i), s.8 | Luottamus/governance/revokaatio, tarjoaja-/lähdevaatimukset, ilmoitettu oikeudellinen todistusluokka | Ulkoisen hyväksytyn järjestelyn ja myöntäjän vastuulla. Formaatista ei päätellä QEAA-/PuB-EAA-asemaa. |
| 8(4), 8(6), 8(8), s.8–9 | Yksikäsitteiset attribuutit, allekirjoitettu/sinetöity pyyntö, Komission sinetöimä julkinen katalogi ja Komission järjestelytunniste | Ei katalogirekisteröintiä, allekirjoituspalvelua tai täyttä EU-katalogia tässä tehtävässä. |
| M1: 3(2), s.4 | Rekisteröidyn järjestelyn mukainen myöntäjä noudattaa sen vaatimuksia ja vaatimustenmukaisuusarviointia | Ulkoisen myöntäjän työnjako säilyy; metatietopaketin valmis-tila ei ole tämän arvioinnin hyväksyntä. |
| M1: liite IV, s.16 | ETSI 119 478 V1.1.1:n yksilöidyt kohdat **mukautuksineen**, mm. attributeValue/fragmentValue-palautusvaatimukset | Myöhemmän autenttisen lähdeintegraation pitää huomioida säädöksen mukautukset, ei vain toteuttaa ETSI-perustekstiä sellaisenaan. Tässä ei toteuteta autenttisen lähteen verifiointia. |

## Asiakirjatietosivu vastaanotettu 19.10.2026

Käyttäjän `Document Information.pdf` (15 kuvaa sisältävää sivua, 5 816 112 tavua) on luettu paikallisella OCR:llä ja sivu 1 tarkastettu kuvana. Alkuperäinen kopio on `fixtures/catalog-standards/originals/eur-lex-document-information-2026-10-19.pdf`, SHA-256 `18b574d05a9a15b6aabfdeded5aab829056bbd8653fd6eb50395305e9df34bb5`. Alkuperä, havainnot ja rajat ovat koneellisesti `sources.json`-tiedoston `documentInformationEvidence`-osiossa. OCR ei muuta alkuperäisiä tavuja eikä ole itsenäinen verkkovarmistus.

- **Sivu 1:** otsikko *Consolidated text*, ELI `http://data.europa.eu/eli/reg_impl/2025/1569/2026-08-11`. Aikajanassa näkyvät 30.7.2025 ja 11.8.2026; sen viimeisin näytetty konsolidointi on 11.8.2026 ja jana päättyy Today-merkkiin. Päivämäärät Date of document / Date of effect ovat 11.8.2026.
- **Sivu 1:** Relationship between documents sisältää vain `Consolidation: basic act: 32025R1569`. Tämä on **konsolidoidun tekstin**, ei alkuperäisen asetuksen asiakirjatietosivu. Siksi Amended by / Corrected by -otsikoita ei näy tässä osiossa.
- **Sivu 2:** tekstin versio 001.001 ja Amended by -viite EU 2026/1735 ovat yhtäpitäviä aiemman tekstikopion kanssa. Myöhemmillä sivuilla on säädösteksti liitteineen, ei erillistä oikaisurekisteriä.

**Tämän aiemman PDF-vaiheen johtopäätös (korvattu yllä olevalla copy-pasten arviolla):** viimeisin liitteen aikajanassa esitetty versio on nyt tarkistettu. Sivulta ei voi vahvistaa alkuperäisen asetuksen kaikkia muutos-/oikaisusuhteita tai myöhempien oikaisujen puuttumista. `latestDisplayedVersionConfirmed=true`, mutta `currentAsOfReviewDate=null` säilyy. Aiempi yleinen `EU_AMENDMENT_CURRENTNESS_UNVERIFIED` rajataan tarkemmaksi `EU_CORRIGENDUM_STATUS_UNVERIFIED`-havainnoksi. Tätä ei nimetä koko lähdetarkistuksen valmistumiseksi.

**Historiallinen ohje ennen copy-pasten saamista; tätä ei enää tarvitse tehdä:** valitse liitteen ensimmäisen sivun **Access initial legal act** -linkki tai avaa [alkuperäisen asetuksen asiakirjatiedot](https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=CELEX:32025R1569). Tarkista, että tunniste on **32025R1569**, ei **02025R1569-20260811**. Avaa **Relationship between documents** ja tallenna siinä näkyvät muutos-/oikaisusuhteet. Pelkkä otsikon puuttuminen konsolidoidun tekstin sivulta ei osoita, ettei oikaisuja ole. Mahdolliset uudet viitteet on luettava ennen lopullista ajantasaisuuspäätelmää. Riippumaton verkkohaku ei ole tässä ympäristössä onnistunut.

## Aiemman asiakirjatietoliitteen tarkistukset 19.10.2026 (ennen copy-pastea)

- `pytest tests/test_technical_packages.py tests/test_attribute_semantics.py -q`: **61 passed, 1 warning in 55.00s**. Ei epäonnistuneita tai ohitettuja. Mukana oikea paikallinen JSON-LD/RDF/SHACL, attribuuttien yhdenmukaisuus, pakettien tarkisteketju sekä uusi asiakirjatietokopion pinnaus ja generoituun raporttiin päätyvä täsmällinen näyttöraja. Varoitus koskee Starlette/httpx-deprekaatiota.
- `git fetch origin main`: main on edelleen **9258fff** ja sisältyy työhaaraan. Työhaara vastasi etähaaraa ennen tätä lisäystä; ei muiden muutosten ylikirjoitusta. `git diff --check` läpäisi.
- Tämä täydennys muuttaa lähdepinnit, raportin syötteet, testit ja dokumentaation. Sovelluskoodia, käyttöliittymää, tietokantaskeemaa tai käynnistysasetuksia ei muutettu. Ei uutta migraatiota. Muuttumattomia julkaisuja tai demokantaa ei päivitetty.
- Koko API-/migraatiosarjaa, selaintestejä, web-buildia, Docker-buildia tai toimintakokeilua ei toistettu tässä liitetäydennyksessä. Alla oleva **207 API-/migraatiotestin ja 13 selaintestin** läpäisy sekä build-/säilymiskokeet ovat edellisen toteutusmuutoksen tuloksia, eivät uusia ajoja. Uusi 61 testin ajo menee osittain niiden kanssa päällekkäin, joten lukuja ei lasketa yhteen.
- Avoin sisältötarkistus: alkuperäisen asetuksen muutos-/oikaisusuhteet ja mahdolliset niistä löytyvät uudet tekstit. GitHub API palauttaa edelleen **Forbidden**; PR:n kuvaus ja etätarkistusten tila eivät päivity tai varmistu tämän ympäristön kautta. Kuvausteksti on repositoriossa `docs/pull-request-attribute-semantics.md`. Ei automaattista yhdistämistä.

## Aiemman toteutuskorjauksen todennus (18.10.2026)

Generaattori `technical-package/1.1.1` lukee puuteraportin normatiiviset havainnot lukituista lähdepinneistä. Vanha yleinen `NORMATIVE_SOURCES_UNVERIFIED` korvautuu tässä aineistossa täsmällisillä havainnoilla `EU_CORRIGENDUM_STATUS_UNVERIFIED`, `ETSI_SD_JWT_PROFILE_VERSION_DIFFERENCE` ja `EXTERNAL_ISSUER_PROFILE_NOT_VERIFIED`. Tiedossa olevien lähdetekstien vastaanottoa ei enää esitetä puuttuvana, eikä myöhempien muutosten ajantasaisuutta tai täyttä ETSI-yhteensopivuutta esitetä vahvistettuna. Katalogirekisteröinnin ja autenttisen lähteen verifioinnin puutteet säilyvät.

Lähdepinnit ja generaattoriversio kuuluvat uuden paketin deterministisiin syötteisiin. Vanhojen julkaisujen paketteja/raportteja tai profiilisnapshotteja ei kirjoiteta uudelleen. Uusi generointi kulkee normaalin luonnoksen, hyväksynnän ja version kautta. IETF draft-19, semanttinen laajennus 1.0.0, suojausvalinnat ja nykyiset myöntäjälinkit säilyvät.

- Mainin 9258fff sisältävän korjatun toteutuksen koko 13 tiedoston API-/PostgreSQL-/migraatiosarja: **207 passed, 4 warnings in 357.80s (0:05:57)**. Ei epäonnistuneita tai ohitettuja. Mukana aiemmat 205 testiä sekä kaksi uutta lähdekopioiden pinnaus-/tarkiste- ja puuteraporttitestiä.
- Kohdennettu paketti-/attribuuttisarja: **60 passed, 1 warning in 51.17s**; nämä sisältyvät täyteen 207 testin ajoon.
- Oikea Chromium + Keycloak, korjattua Docker-sovellusta vasten: **13 passed, 1 warning in 116.18s (0:01:56)**. Tallennus/uudelleenavaaminen, eri käyttäjän hyväksyntä, julkaisu, julkiset artefaktit ja semantiikan lukija säilyivät.
- **220 eri pytest-testiä** yhteensä. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia.
- Web-build läpäisi. Docker-image rakennettiin varmennukset säilyttävällä scripts/cloud-build.sh-reitillä; `docker compose up -d --no-build --wait` käynnisti app/db/Keycloakin healthy-tilaan. Tavallista `docker compose up --build` -reittiä tai Windows Docker Desktopia ei ajettu tässä täydennyksessä.
- **13 oikean catalog-kannan metatietotaulua säilyi tarkalleen ennallaan uudelleenkäynnistyksen yli** ennen uusia synteettisiä selainjulkaisuja. Ei uutta relaatiomigraatiota; aiemmat migraatiot tarkistettiin erillisessä catalog_test-kannassa. Demokantaa ei tyhjennetty.
- Julkinen HTTP-yhteensopivuuskoe: **83 julkaisuversiota luettavissa**, **8 vanhan generaattorin pakettia / 78 artefaktia** tavuntarkasti alkuperäisillä SHA-arvoilla. Uusi lähdetarkistus ei kirjoittanut vanhojen julkaisujen raportteja uudelleen.
- `git diff --check` läpäisi. PR #13:n GitHub-mergeviite vahvisti basen mainiksi 9258fff; käyttäjä vahvisti saman. Main-haaraa ei muutettu eikä PR:ää yhdistetty.
- Ajamattomat: asiakirjatietosivun jälkeiset mahdolliset lisäsäädösten tarkistukset, Windows, uuden Codespacen luonti/Private-portin ajonaikainen tila, tuotanto-HTTPS ja GitHub Actionsin etätulos. Ei allekirjoittamista, lompakkoa, EU-katalogirekisteröintiä tai koko ETSI-profiilin vaatimustenmukaisuusarviota.

