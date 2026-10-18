# Ohjeet koodausagenteille

## Rajaus

Lue `ROADMAP.md`, `STATUS.md` ja `metatietovaranto_suunnittelu.md`. Suunnitelma kuvaa tavoitearkkitehtuurin. Nykyinen toimitus kattaa ROADMAPin vaiheet 1, 2A, 2B, 2C, 2D, 2E, 2F, 2G ja 2H (luonnokset, riippumaton hyväksyntä, lukitut profiili-/julkaisusnapshotit, VC-metatiedot ja auditointi). Lue myös docs/phase-2c.md, docs/phase-2e.md, docs/phase-2f.md ja docs/phase-2g.md. Vaihe 2D tarkistaa synteettisen esimerkkisisällön offline SHACL Corella. Älä lisää SPARQL/JS/AF-laajennuksia, laajempaa elinkaarta tai ulkoisia integraatioita ilman erillistä toimeksiantoa. Älä yhdistä main-haaraan automaattisesti.

## Sitova semanttinen suunnitteluperiaate

Lue `docs/semanttinen-periaate-1.md` ennen tietotuotteen sisällön, soveltamisprofiilien, skeematuonnin tai julkaisuversioiden suunnittelua. Sisältö perustuu Tietomallit-työkalun SHACL-soveltamisprofiiliin, joka annetaan linkkinä tai alustalta ladattuna tiedostona. OWL voi sijaita alustalla tai ulkoisessa nimiavaruudessa. JSON Schema/OpenAPI ovat johdannaisia; tietoelementtien käsin ylläpidettävä rinnakkaismalli ei ole tavoiteratkaisu. Nykyiset dataElements ovat väliaikaista demoa eivätkä vahvistettu profiilikytkentä. Periaatteen kirjaaminen ei vielä tilaa toteutusta.

## Sitova VC toimitusperiaate

Lue `docs/vc-periaate-2.md`. Ensisijainen toimitusmuoto on W3C VC. Tuotesivu tarjoaa pysyvän myöntäjän HTTPS-asiointilinkin **Pyydä todistus lompakkoon**. Myöntäjä vastaa henkilön/yrityksen tunnistamisesta, edustamisoikeudesta, lähdetiedosta, myöntämisestä, VC:n suojaamisesta ja lompakkoprotokollasta. Katalogi ei säilytä henkilökohtaisia tarjouksia tai tokeneita. Katalogin Keycloak-istunto ei ole myöntäjän pääsyoikeus. EUDIW-/EBW-yhteensopivuus kuvataan ja todennetaan erikseen. Tämä suunnittelupäätös ei vielä tilaa myöntämispalvelun tai lompakkointegraation toteutusta.

## Työskentelyn käytännöt

Käytä nykyistä checkoutia: pilvitehtävät ovat jo eristettyjä. Älä luo worktreea ilman käyttäjän pyyntöä. Säilytä käyttäjän muutokset. Testattavat henkilö-/yrityssisällöt ovat synteettisiä. fixtures/tietomallit-hakemisto sisältää myös alkuperäisiä julkisia mallikuvauksia, joiden alkuperä ja tarkiste on lukittu. Älä lisää salaisuuksia, aitoja rekisteritietoja tai väitteitä QEAA-/DCAT-AP-vaatimustenmukaisuudesta.

## Käynnistys ja todennus

Täsmälliset komennot ovat READMEssä. Sovellus käyttää aina PostgreSQL:ää, myös API-testeissä. Testit käyttävät erillistä `catalog_test`-kantaa; älä aja tyhjentäviä testejä `catalog`-kantaan. Aja muutoksen mukaan `uv sync --locked`, `npm ci --prefix apps/web`, `npm run build --prefix apps/web` ja API-, migraatio- ja osoitteenmuodostustestit. Älä aja samaa tyhjentävää testikantaa käyttäviä pytest-ajoja rinnakkain. Käyttöliittymämuutoksissa aja myös `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q` käynnistettyä demoa vasten. Raportoi ajamattomat ja ohitetut testit erikseen. Päivitä STATUS toteutuksen muuttuessa.

Kirjoitus-API vaatii palvelinistunnon ja CSRF-tarkistuksen. Luonnoksen muokkaus tarvitsee editor-jäsenyyden pysyvään omistajaorganisaatioon; tarkastus reviewer/publisher- ja julkaisu publisher-roolin. Älä anna kirjoittajan hyväksyä omaa sisältöään. Säilytä ETag/If-Match ja idempotenssi. Julkinen haku ja vienti käyttävät vain muuttumattomia julkaisuja. Älä lisää testejä tai demoa varten autentikoinnin ohitusreittiä. Käytä selaintesteissä oikeaa Keycloak-kirjautumista. Säilytä `DEMO_MODE=true`-käynnistysvaatimus ja Compose-porttien sidonta loopbackiin. Älä poista PostgreSQL-volumea tavallisen käynnistyksen yhteydessä.

## Migraatiot

Muuta skeemaa uusilla Alembic-revisioilla; älä muokkaa jo toimitettuja revisioita. Älä käytä sovelluksessa create_all-kutsua tai stamp-komentoa tuntemattoman skeeman hyväksymiseen. Säilytä legacy-päivityksen tietojen ja tunnisteiden säilymistestit. Älä yhdistä organisaatioita pelkän nimen perusteella. Tavallinen startup ei saa palauttaa vanhan kannan fixtureitä.

## Kirjautuminen

Lue docs/authentication.md. Keycloakin tunnukset ovat synteettisiä demotunnuksia, eivät tuotantosalaisuuksia. Älä lokita koodeja, tokeneita, evästeitä tai salasanoja. Säilytä --no-access-log deployatussa Uvicornissa. Älä myönnä oikeuksia organisaation nimen tai käyttäjän lähettämän organisaatiotiedon perusteella. Älä muuta vanhoja jäsenyyksiä fixtureiden perusteella uudelleenkäynnistyksissä.



## SHACL ja synteettiset esimerkit

Lue README:n vaiheen 2D rajaus. Älä muuta 2C:n muuttumattomia julkaisuja tai snapshotteja taustapäivityksellä. Raportti on palvelimen tuottama ja sidottu profiiliin, esimerkkiin, moottoriin ja käytäntöön; älä hyväksy raporttia asiakkaalta. Esimerkin muokkaus mitätöi hyväksynnän. Säilytä prosessin CPU-/muisti-/aikarajat ja verkkoyhteyksien esto, älä suorita profiilin koodia tai nouda riippuvuuksia validoinnissa. Lisää tests/test_semantic_validation.py API-/migraatiotestien ajoon. Vain synteettistä esimerkkisisältöä, ei henkilötietoja tai allekirjoitettuja VC-todistuksia.

## Rinnakkaiset toimitustavat

Distributions on uusien kuvausten auktoritatiivinen toimitusmalli, issuance säilyy vanhojen tietojen yhteensopivuutena. JSON API, W3C VC ja SD-JWT VC jakavat saman profiilisnapshotin; älä pakota SD-JWT:hen JSON-LD-kontekstia tai väitä sen olevan W3C VC -kuori. Säilytä versioidut sisäkkäiset mappingit ja erota metadata, SHACL-esimerkki ja kryptografinen tarkistus. Tuotteen metatietovienti ei ole lähdetietopalvelu. Älä lisää tokeneita tai Credential Offer -tietoja. Uusi fixture lisätään vain kerran tunnettuun demo-organisaatioon, ei vanhojen tietojen nollauksena. Aja myös tests/test_derived_validation.py ja tests/test_distributions.py.

## Synteettinen JSON → RDF -esikatselu

Vaiheen 2F muunnoslaboratorio on tallentamaton ja vain omistajaorganisaation editorille. Säilytä CSRF ja If-Match myös esikatselussa. Älä tee onnistumisväitettä kartoittamattomille, häviöllisille tai tukemattomille rakenteille. RDF-graafivertailu ei ole kryptografinen tarkistus tai VC-kuoren/JSON-LD-laajennuksen validointi. Prosessi on verkoton ja resurssirajattu. Älä muuta vanhoja julkaisuja tai fixtureitä raportin lisäämiseksi. Aja tests/test_conversion.py ja olemassa olevat selaintestit.

## Julkaisuversioiden elinkaari

2G sallii published → deprecated/withdrawn ja deprecated → withdrawn, vain omistajan publisherille. Säilytä erillinen lifecycle-ETag, idempotenssi, append-only-tapahtuma ja audit/outbox samassa transaktiossa. Älä muokkaa alkuperäistä ProductVersion-sisältöä tai julkaisuoutboxia. Versio-API ja version vienti säilyttävät snapshotin; ajantasainen tila löytyy erillisestä julkisesta resurssista ja vastausotsakkeista. Withdrawn-uusimman tilalle ei nosteta aiempaa versiota. Estä palvelutoiminnot myös historiallisessa versiossa ja tilatiedon puuttuessa. Aja tests/test_lifecycle.py sekä täytetyn 0004-kannan migraatiotesti ja selainpolut.

## SHACL-pohjaiset tekniset paketit

Lue docs/phase-2h.md. Paketilla ei muokata lähdeprofiilia tai OWLia. Säilytä generaattorin yksilöidyt estot, yhteiset hyväksytyt esitysvalinnat, erillinen IETF Type Metadata ja paikallinen lukittu JSON-LD-lataaja. Älä väitä upstream-testifixtureä aidoksi muuttamattomaksi Tietomallit-exportiksi. Aja tests/test_technical_packages.py sekä oikean JSON-LD-prosessorin RDF/SHACL-tarkistukset. Paketin generointi on editorin kirjoitus ja mitätöi hyväksynnän. Julkisia artefakteja palvellaan vain muuttumattomista julkaisuista, myös withdrawn-tilassa; luonnoksista ei synny julkista kontekstia. Paikallisen HTTP-demon ja Codespacesin Private-HTTPS-portin rajat ilmoitetaan erikseen.

WE BUILD -aineistokoe: lue docs/webcor-acceptance.md. Säilytä fixtures/tietomallit/webcor-0.0.2/original.ttl tavuntarkasti. Erillisen testiprojektion lisättyä xsd:string-rajoitetta ei saa väittää alkuperäiseksi eikä alkuperäisen profiilin generointia valmiiksi. Täysi testi on edelleen tests/test_technical_packages.py; kohdennettu ajo -k webcor sisältää 8 tapausta.
