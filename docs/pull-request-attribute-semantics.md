## Ongelma ja tulos

SD-JWT VC:n väitepolku ei yksin kerro alkuperäistä semanttista ominaisuutta tai sen SHACL-käyttöyhteyttä. Jatko johtaa attribuuttiviittaukset samasta lukitusta SHACL-lähteestä JSON Schemaan (`x-term`/`x-mtv-shacl`), Type Metadataan (`x-mtv-semantic`) ja yhteiseen mappingiin. Sisäkkäinen rooli, nimetön PropertyShape, ulkoinen nimiavaruus, lähdeversio ja snapshotin tarkiste säilyvät. Ei uutta käsin ylläpidettävää sisältömallia.

**Base: main `9258fff`** (PR #12 yhdistetty), joka sisältyy työhaaraan. Ei automaattista yhdistämistä.

## Toteutus ja yhteensopivuus

- Oma semanttinen laajennusprofiili **1.0.0** määrittelee x-kentät sekä schema-/mapping-löydettävyyden. Ne eivät ole IETF:n schema/schema_uri-standardikenttiä. IETF SD-JWT VC pysyy **draft-19**:ssä, generaattori **1.1.1**:ssä.
- Type Metadata, annotoitu skeema, mapping ja laajennusprofiili julkaistaan muuttumattomista tuoteversioista oikeilla mediatyypeillä. Standardin base64-SRI-ketju ja myöntäjän vct#integrity-ohje eivät toteuta allekirjoittamista tai myöntäjän luottamuksen todentamista. Withdrawn säilyttää julkaistut artefaktit.
- Nimetön PropertyShape säilyy nimettömänä: snapshot, rootShapeUri ja constraintPath yksilöivät käyttökohdan. Claim Path käyttää sisäkkäisten taulukoiden kohdalla nullia, ei sisäistä /*-merkintää.
- Valinnaiset attribuutti-/järjestelykatalogivastaavuudet ovat tyypitettyjä ja alkuperätiedollisia. Muutos mitätöi hyväksynnän ja paketin. Vanhan asiakkaan pois jättämä uusi kenttä säilyttää aiemmat viitteet.
- Esimerkkikuluttaja `examples/semantic_consumer.py` selvittää yhden claimin semantiikan ilman väitearvoja tai JSON Schemaa. Se ei ole SD-JWT-verifioija eikä tulkitse paljastamatta jäänyttä attribuuttia alkuperäisestä todistuksesta puuttuvaksi.

## ETSI-/EU-lähdetarkistus — päätös 19.10.2026

Relevantit kohdat käyttäjän toimittamista **ETSI TS 119 472-1 V1.2.1**, **ETSI TS 119 478 V1.1.1** ja **EU 2025/1569:n EN-konsolidoinnista 11.8.2026 / 001.001** on luettu. PDF-kopiot, TS11 1.0.1:n viralliset Git-lähteet ja tarkisteet ovat lukittuja. Myös konsolidoidun tekstin asiakirjatietosivu ja käyttäjän copy-pastena toimittama alkuperäisen asetuksen muutos-/oikaisuluettelo on kirjattu alkuperätietoineen.

| Havainto | Vaikutus / raja |
| --- | --- |
| ETSI 472-1 konteksti, schema, Type Metadata; ETSI 478 semanticDataSpecification ja schemaDistribution | Oma x-mtv-profiili säilyy omana laajennuksena. Tekniikan kuvaus ei ole täysi ETSI-profiili tai DIP-palvelu. |
| ETSI 472-1 viittaa SD-JWT VC draft-13:een | Paikallinen draft-19 säilyy eksplisiittisenä valintana. Ero raportoidaan; ei yhteensopivuusväitettä. |
| EU art.7/8:n tietovaatimukset ja M1:n 3(2)/liite IV | Attribuutti, järjestely ja yksittäinen tekninen schema erotetaan. Myöntäjä-/rekisteröinti-/tarkistuspalvelun puuttuvia tietoja ei päätellä formaatista. Liite IV:n mukautukset jäävät ulkoisen integraation vaatimuksiksi. |
| Oikaisu 32025R1569R(01), kielimerkintä PL | Oikaisu on tunnistettu. Koko PL-tekstiä ei saatu (403); tätä EN-metatietotehtävää ei nimetä PL-version arvioinniksi. |
| EU 2026/1735: seitsemän luettelon muutosta 11.8.2026 alkaen | Toimitetun konsolidoinnin rajaus ja aiempi myöntäjän/ulkoisen tarkistuspalvelun työnjako säilyvät. Ei havaittua metatietokoodin korjaustarvetta. |
| EU 2026/1735: 9(4) ja uusi 9(2a) luettelon mukaan **1.1.2027** alkaen | Erotettu nykyisestä konsolidoinnista. Täysi tuleva sanamuoto on luettava ennen ulkoisen tarkistuspalvelun toteutusta; sitä ei ole saatu tai toteutettu tässä. |
| EN-konsolidoinnin art.11 | 6–9 artikloja sovelletaan **19.8.2026** alkaen; konsolidointipäivä ei ole kaikkien kohtien soveltamispäivä. |

**Lähdevertailu on valmis tämän englanninkielisen metatietotehtävän rajauksessa, ilmoitetuin rajoituksin.** Siitä ei jää tähän rajattuun PR:ään tunnistettua yhdistämisestettä. Raportin `status=partial` ja `conformanceClaim=false` säilyvät. Aiempi yleinen luettelon puuttumishavainto korvautuu täsmällisillä PL-oikaisun ja tulevan 9 artiklan tekstin lukemattomuutta kuvaavilla havainnoilla. Tämä ei väitä noita tekstejä tarkistetuiksi.

**Riippumatonta EUR-Lex-verkkovertausta ei saatu:** sekä EUR-Lex että EU Publications/Cellar palauttivat 403. Muutosluettelo on käyttäjätoimituksen käsin rakenteistettu jäljennös, ei virallinen JSON-export. Ei kattavaa kaikkien kieliversioiden/kaikkien säädösmuutosten sanamuodon arviointia tai oikeudellista/ETSI-/EUDIW-vaatimustenmukaisuusväitettä.

[Kohtakohtainen lähdevertailu ja täsmälliset rajat](https://github.com/jgmikael/metatietovaranto/blob/feat/phase-2h-attribute-semantics/docs/pr13-source-comparison.md). Lähdepinnit vaikuttavat vain uuteen generointiin. Vanhoja julkaisuja, raportteja tai profiilisnapshotteja ei kirjoiteta uudelleen; uudet paketit kulkevat normaalin luonnos-/hyväksymis-/julkaisuprosessin kautta.

## Konkreettinen ketju

Synteettinen SHACL ProductShape → hyväksytty /companyName-mapping → JSON-LD-konteksti, annotoitu JSON Schema ja SD-JWT Type Metadata → oikean PyLD:n RDF, odotettu graafi ja lähde-SHACL → toisen käyttäjän hyväksymä muuttumaton julkaisu → 12 julkista artefaktia → esimerkkikuluttajan ominaisuus-IRI, PropertyShape ja lähdesnapshot.

Aito WE BUILD 0.0.2 -export säilyy tavuntarkasti. Koko profiilin puuttuvat literaalityypit ja ratkaisematon SKOS-importti estävät valmiin paketin. Erillinen nimetty paikallinen testiprojektio on testattu; sen lisättyä tyyppiä ei väitetä alkuperäiseksi.

## Tässä viimeistelyssä todella suoritetut tarkistukset

- Koko README/CI:n 13 tiedoston API-/PostgreSQL-/migraatiosarja: **209 passed, 4 warnings in 355.05s (0:05:55)**. Ei epäonnistuneita tai ohitettuja. Oikeudet/CSRF, hyväksynnän mitätöityminen, julkaisuimmutabiliteetti, JSON-LD/RDF/SHACL, attribuuttiannotaatiot, tarkisteketju sekä vanhan/tyhjän kannan ja toistuvien migraatioiden kokeet mukana. Testit käyttivät vain erillistä catalog_test-kantaa.
- Oikea Chromium + Keycloak uudelleen rakennettua ja käynnistettyä Docker-sovellusta vasten: **13 passed, 1 warning in 115.88s (0:01:55)**. Tallennus/uudelleenavaaminen, organisaatiorajat, riippumaton hyväksyntä, julkaisu ja julkiset artefaktit läpäisivät. **222 eri pytest-testiä** yhteensä; varoitukset ovat Starlette/httpx- ja RDFLib-deprekaatioita.
- Uuden lähderegressiotestin lopullinen kohdennettu ajo: **1 passed, 1 warning in 0.21s**. Tarkistaa luettelon tarkisteen, alkuperän, PL-rajauksen, seitsemän nykyistä ja kaksi tulevaa muutosriviä, 19.8.2026 soveltamispäivän sekä niiden päätymisen generoituun raporttiin. Sama testitapaus kuuluu 209 testiin, eikä sitä lasketa lisätestiksi kokonaismäärään.
- `npm run build --prefix apps/web`: läpäisi (Vite 1,59 s). `bash scripts/cloud-build.sh` läpäisi TLS-varmennuksen säilyttäen; viimeinen image **sha256:6c7b957f54486509745c2369ffed1a0b923eb01689dcc41241665047ffa80177**. `docker compose up -d --no-build --wait`: app, db ja Keycloak healthy. Käynnissä olevan sovelluksen sources.json- ja muutosluettelotiedoston SHA:t vastaavat checkoutia.
- Ennen selaintestien uusia synteettisiä julkaisuja **13 catalog-kannan metatietotaulun kaikki rivit ja Alembic-head 0005_lifecycle säilyivät tarkalleen ennallaan uudelleenkäynnistyksessä**. Ei uutta relaatiomigraatiota tai fixtureiden palautusta; live-kantaa ei tyhjennetty.
- Julkinen HTTP-yhteensopivuuskoe selaintestien jälkeen: **88 julkaisuversiota luettavissa**, **8 vanhan generaattorin pakettia / 78 artefaktia** alkuperäisillä tavuilla ja SHA-arvoilla. Versioiden technicalPackage-sisällöt vastasivat tallennettuja muuttumattomia sisältöjä.
- Uuden paketin toimintakoe: kaikki **12 julkaistua artefaktia** palautuivat oikeilla mediatyypeillä ja tarkisteilla. Julkinen catalogue-coverage.json sisälsi täsmälleen uudet lähdepinnit ja rajatun päätöksen. Oikea `examples/semantic_consumer.py` palautti companyName-väitteen alkuperäisen ominaisuus-IRI:n, PropertyShapen ja lähdesnapshotin ilman väitearvoja tai JWT:n kryptografista tarkistusta.
- Main **9258fff** sisältyy työhaaraan; PR #13:n GitHub-mergeviitteen ensimmäinen vanhempi oli sama main, joten base on teknisesti vahvistettu. `git diff --check` läpäisi. Ei automaattista yhdistämistä.


## Ajamattomat ja ulkoiselle integraatiolle jäävät

GitHub Actionsin etätulos ja PR:n kuvauskenttä eivät ole luettavissa/päivitettävissä tämän ympäristön API-yhteydellä (Forbidden). Käyttäjä tarkistaa GitHubin vihreät tarkistukset ja yhdistettävyyden. Valmis kuvausteksti on tässä tiedostossa manuaalista kuvauskentän päivitystä varten.

Ei Windows Docker Desktop -koetta, uuden Codespacen luontia/automaattisen selainavauksen/Private-portin ajonaikaista tarkistusta, tuotanto-HTTPS:ää tai kuorma-/tietoturva-auditointia. Tavallista `docker compose up --build` -reittiä ei ajettu tässä pilviympäristössä; käytetty pilvirakennus säilyttää TLS-varmennuksen.

PL-oikaisun ja koko muutossäädöksen/tulevan 9 artiklan sanamuotojen luku jää raportoiduksi lähderajaksi. Ulkoiselle myöntäjälle jäävät tunnistaminen, asiointivaltuudet, lähdetiedon käyttö/tarkistus, myöntämispäätös, todistuksen vct-löydettävyys, allekirjoittaminen, suojaus-/luottamusprofiili ja lompakkotoimitus. Ei EU-katalogirekisteröintiä tai täyttä katalogipalvelua.
