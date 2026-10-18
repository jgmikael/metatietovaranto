# Toteutuksen vaiheistus

`metatietovaranto_suunnittelu.md` on tavoitearkkitehtuuri. Käyttäjän tehtävän 1 rajaus korvaa luvun 18 vaatimuksen koko ratkaisun toimittamisesta kerralla. Alla olevat vaiheet eivät ole suunnitteludokumentin A–D-vaiheistus.

## Vaihe 1 — paikallinen toimiva demo

- React/TypeScript-käyttöliittymä ja FastAPI-palvelin.
- Tietotuotteen lisäys, luku, muokkaus ja poisto.
- Tekstihaku, teema- ja tarjoajarajaus, sivutus ja tuotesivu.
- PostgreSQL ja pysyvä Compose-volume; kolmen synteettisen tuotteen kertaluonteinen siemennys.
- Tuote- ja katalogivienti JSONina ja JSON-LD:nä.
- Palvelimen validointi, API-/PostgreSQL-testit, RDF-jäsentämistestit ja selaintestit.
- Suomenkielinen responsiivinen demo, näkyvä demomerkintä ja dokumentoitu käynnistys.

## Vaihe 2A — migraatiot ja tarjoajaorganisaatiot

Tämä tehtävä on tilattu erikseen nykyisen main-haaran pohjalta.

- Alembic: ensimmäinen migraatio kuvaa alkuperäisen skeeman ja ottaa tarkistetun vaiheen 1 kannan käyttöön ilman tiedonmenetystä.
- Toinen migraatio lisää Organization-mallin ja pakollisen tuote–tarjoajaorganisaatio-vierasavaimen. Samannimisiä vanhoja tarjoajia ei yhdistetä nimen perusteella.
- Organisaation UUID, virallinen nimi, maa, tunnistejärjestelmä/tunniste-parit ja synteettisyys; luku-API ja yksinkertainen näkymä.
- Tuotteen ylläpidossa organisaatiovalinta; tarjoajanimi säilyy haussa, tuotesivulla ja vienneissä.
- Migraatiot ennen readiness-tilaa samalla käynnistyspolulla Composessa ja Codespacesissa; fixtureitä ei palauteta vanhaan kantaan.
- Vanhan muokatun kannan, tyhjän kannan ja toistuvien migraatioiden PostgreSQL-testit sekä aiempien selainpolkujen säilyttäminen.
- Codespacesin automaattinen selainavaus ja Private-portti säilyvät.

## Vaihe 2B — kirjautuminen ja organisaatiokohtainen ylläpito

- Keycloak OIDC authorization code + PKCE; ei demokäyttäjän identiteetin oikopolkua.
- Opaque palvelinistunto PostgreSQL:ssä, HttpOnly/SameSite-eväste, HTTPS:ssä Secure ja kirjoituspyyntöjen CSRF-tarkistus.
- Eksplisiittiset organisaatiojäsenyydet ja editor/reader-roolit. Muokkaaja ylläpitää vain omien organisaatioidensa tuotteita; palvelin tarkistaa myös vaihdettavan tarjoajan.
- Vaiheen 2B toimituksessa metatiedot näkyivät anonyymisti; vaihe 2C rajaa julkiset haut, sivut ja viennit julkaistuihin snapshotteihin.
- Kolme synteettistä demokäyttäjää (kaksi eri organisaation muokkaajaa, yksi lukija) ja oikean OIDC-ketjun selaintestit.
- Yksi selainportti 8000: rajattu saman alkuperän kirjautumisproxy Keycloakille. Codespacesin Private-portti ja automaattinen selainavaus säilyvät.
- Migraatio 0003_auth lisää istunnot, OIDC-tilat ja jäsenyydet; aiempia migraatioita tai tuotetietoja ei kirjoiteta uudelleen.

## Vaihe 2C — luonnokset, hyväksyntä ja lukitut julkaisut

Tilattu käyttäjän toimeksiannolla PR:ien 5 ja 6 yhdistämisen jälkeen. Toteutus perustuu mainin commitiin `0dd6555`.

- Omistajaorganisaation yksityinen työkopio, draft → inReview → approved → published; perusteltu palautus tarkastuksesta.
- Eri käyttäjän hyväksyntä sidottuna sisältötarkisteeseen ja revisioon. Kaikki kirjoittajat huomioidaan; muokkaus mitätöi hyväksynnän.
- Optimistinen If-Match-lukitus, PostgreSQL-rivilukitus, luonnin/julkaisun idempotenssi.
- Muuttumaton semver-julkaisu, version URI, vanhojen versioiden vienti ja julkinen haku vain julkaisuista.
- Julkaisu, hyväksyntäviite, audit ja outbox samassa transaktiossa. Tietokantatriggerit estävät historian muuttamisen.
- PR 5: Tietomallit SHACL-profiili linkillä TAI tiedostona, alkuperäiset IRI:t/graafi ja lukitut riippuvuudet, johdetut tietoelementit, esitysten graafiekvivalenssi. Alkuperä tarkastetaan ihmisen arviona, ei automaattisena alustatodistuksena.
- PR 6: W3C VC ensisijaisena suunniteltuna/käytettävänä jakeluna, versioon ja profiiliin sidotut metatiedot, pysyvä myöntäjän HTTPS-linkki ja nimetyn lompakkoprofiilin näyttö. Ei myöntämistä katalogissa.
- Migraatio 0004 säilyttää vanhat tiedot luonnoksina; mitään ei julkaista automaattisesti. Kaksi nykyistä synteettistä editoria toimivat ristikkäin toisen organisaation tarkastajana/julkaisijana.
- Codespacesin Private-portti 8000, automaattinen selainavaus ja vanhojen tietojen säilyminen jatkuvat.

## Vaihe 2D — offline SHACL Core ja synteettinen esimerkkisisältö

Jatko käyttäjän hyväksymän PR #7:n (2C) jälkeen, pohjana main `61ca4ed`.

- Profiilin ja lukittujen riippuvuuksien SHACL Core -rakennetarkistus pySHACL-moottorilla sekä esimerkkisisällön oikea SHACL-validointi.
- Turtle/RDFXML/paikalliskontekstinen JSON-LD, yksi synteettinen esimerkkigraafi, eksplisiittinen synteettisyysvahvistus.
- Tietotyypit, kardinaliteetit, sisäkkäiset muodot ja koodistorajoitteet; tyhjä/kohdistamaton/deaktivoitu kohde ei anna väärää onnistumista.
- Palvelimen tuottama raportti: säännöt, JSON Pointer, RDF-polut, kohteet, profiili-/esimerkkitarkisteet ja moottori-/käytäntöversio. Raportti ja esimerkki sidotaan hyväksyntään ja muuttumattomaan julkaisuun.
- Uusi julkaisu tarvitsee läpäisseen ja ajantasaisen raportin. Vanhoja julkaisuja ei kirjoiteta uudelleen tai poisteta. Virheellisen esimerkin voi tallentaa korjattavaksi luonnokseksi.
- Verkoton ja resurssirajattu prosessi. SPARQL/JS/AF/mukautetut komponentit ja tuntemattomat SHACL-predikaatit hylätään; ei hiljaista ohittamista.
- Selainlomake tiedoston/tekstin syöttöön ja raportin näyttö. Tietokannan nykyinen JSONB-sisältö riittää, ei uutta migraatiota.
- Codespacesin Private-portti 8000, automaattinen selainavaus ja nykyiset demotunnukset säilyvät.

## Vaihe 2E — rinnakkaiset toimitustavat ja mappingit

Käyttäjän täsmentämä rajaus, pohjana main `5611be2` (2D / PR #8).

- Tyypitetty distributions-kokoelma: tarjoajan JSON API, W3C VCDM 2.0 JSON-LD VC ja IETF SD-JWT VC; W3C VC oletuksena ensisijainen. Formaatti, protokolla ja suojaus erotetaan.
- Jokaisella oma saatavuus, ympäristö, vastuut ja tekninen kuvaus. Kaikki lukitaan saman tuoteversion samaan SHACL-snapshotiin.
- Versioidut semanttiset kenttämappingit, myös sisäkkäiset oliot, tietotyypit ja moniarvoisuus. SD-JWT VC käyttää erillistä mappingia ilman pakotettua JSON-LD-kontekstia. Metadata-/mapping-raportti sidotaan hyväksyntään.
- Rakenteiset muokkausnäkymät ja muotokohtaiset tuotesivutoiminnot; planned/suspended ei saa aktiivista palvelutoimintoa. Sama OpenID4VCI-palvelu voi kuvata kaksi erillistä konfiguraatiota.
- Neljäs synteettinen planned-esimerkki kertaluonteisesti tunnettuun demo-organisaatioon. Vanhat julkaisut/snapshotit/issuance-luku säilyvät; uusi kokoelma julkaistaan tavallisella hyväksyntäprosessilla.
- Aiemmin aloitettu JSON Schema/OpenAPI -johdannaisten ja synteettisten JSON-esimerkkien tarkistus säilyy erillisenä rajattuna lisätarkistuksena. Suoran kenttävertailun rajaus ei rajoita toimitustapamappingien sisäkkäistä metadataa.
- Ei lähdesisällön palvelua, todistusten muodostusta/allekirjoitusta, JWT:n tarkistusta tai lompakkointegraatiota. Ratkaisu ja integraation hyväksymiskriteerit: docs/phase-2e.md.

## Vaihe 2F — hallittu synteettisen JSON-sisällön RDF-esikatselu

Jatko käyttäjän yhdistämän PR #9:n jälkeen, pohjana main `feca7b8`. Rajaus: docs/phase-2f.md.

- Editorin yksityinen, tallentamaton esikatselu luonnoksen nykyisillä toimitustapamappingeilla ja yhteisellä lukitulla profiililla. Istunto, organisaatioraja, CSRF ja If-Match.
- JSON API:n synteettinen sisältö, W3C:n sisältöpolun olio ja SD-JWT:n erillinen synteettinen väiteolio. Ei kuorta, JWT:n purkamista tai lompakkointegraatiota.
- Yksiselitteinen juuriluokka, sisäkkäiset oliot ja moniarvoiset kentät, eksplisiittiset XSD-literaalit. Kartoittamattomat, häviävät ja tukemattomat kohdat hylätään.
- Lukitun JSON API -skeeman tarkistus, hallittu muunnos, 2D:n offline SHACL ja RDF-graafien isomorfinen vertailu erillisinä. Sidonta luonnoksen, profiilin, mappingien ja syötteiden tarkisteisiin.
- Selainkokeilu valmiilla synteettisellä sisällöllä. Ei fixtureiden tai aiempien julkaisujen muutosta, uutta relaatiomigraatiota tai uusia julkaisuehtoja.
- Varsinaiset lähde-/todistuspalvelut, kuoriskeemat, kontekstin laajennus, SD-JWT-profiilin purku ja kryptografia jäävät vaiheeseen 3.

## Vaihe 2G — julkaisuversioiden deprecated-/withdrawn-elinkaari

Tilattu käyttäjän hyväksymän ehdotuksen mukaisesti; pohjana main `79dc9d1` (PR #10 / 2F). Sopimus: docs/phase-2g.md.

- Julkaisijan perustellut tilamuutokset: published → deprecated/withdrawn ja deprecated → withdrawn. Erillinen version elinkaari-ETag, CSRF, omistajaorganisaation oikeus ja idempotenssi.
- Korvaava versio valitaan saman tuotteen myöhemmistä julkaisuista; ristiriitaiset tai käytöstä poistetut kohteet hylätään.
- Uusi migraatio 0005: muuttumattomat elinkaaritapahtumat ja erillinen outbox; auditointi samassa transaktiossa. Julkaistuja sisältöjä, profiileja, hyväksyntöjä ja luonnoksia ei kirjoiteta uudelleen.
- Deprecated näkyy oletushaussa varoituksella; withdrawn jätetään oletushaun/katalogiviennin ulkopuolelle, mutta pysyvä sivu ja historia säilyvät. Ei automaattista paluuta vanhempaan versioon.
- Ajantasainen elinkaari lukuesityksissä ja erillisenä resurssina. Alkuperäiset versio-API:t/tarkisteet säilyvät. Tuotesivu estää withdrawn-version palvelutoiminnot myös historiallisessa versiossa; puuttuva tilatieto estää toiminnot.
- Migraatio-, oikeus-, rinnakkaisuus-, rollback-, triggeri-, vienti- ja selaintestit. Codespacesin Private-portti/openBrowser ja vanhat tiedot säilyvät.
- Ei archived/retired-tilaa, ajastettua lopetusta, ulkoisten oikeuksien peruuttamista tai todistusten revokaatiota. Nämä eivät seuraa katalogin withdrawn-merkinnästä.

## Vaihe 2H — SHACL-pohjaiset tekniset kuvauspaketit

Käyttäjän toimeksianto, pohjana main `ac002ad` (PR #11). Tämä korvaa aiemman DCAT-AP-vientiehdotuksen vaiheelle 2H. Sopimus ja täsmällinen tuettu profiili: [docs/phase-2h.md](docs/phase-2h.md).

- Eksplisiittinen juurimuoto, deterministiset tekniset nimet, tarkastettavat yhteiset esitysvalinnat ja kaikkien kolmen toimitustavan mappingit; SHACL-tyyppejä/kardinaliteetteja ei muuteta rinnakkaismalliksi.
- JSON-LD 1.1 scoped -konteksti erillään VCDM 2.0 -peruskontekstista, yhteinen JSON Schema, SD-JWT VC draft-19 Type Metadata, erilliset mappingit ja synteettiset allekirjoittamattomat esimerkit.
- Oikea PyLD-prosessointi, lukittu paikallinen lataaja, RDF-graafivertailu ja offline SHACL. Ei JWT:tä, disclosureja, allekirjoitusta tai myöntämistä.
- Versioitu, tarkistesidottu deterministinen paketti luonnoksessa/julkaisussa, normaali riippumaton hyväksyntä, pysyvät koneluettavat artefaktipolut; vanhojen julkaisujen ja withdrawn-artefaktien säilyminen. Ei uutta relaatiomigraatiota.
- Useat sanastoviitteet sijainteineen ja riippuvuusaineistot käyttöliittymään. Ei mielivaltaisia verkkonoutoja.
- Aidon aineiston koe täydennetty käyttäjän toimittamalla WE BUILD Certificate of Residence 0.0.2 -exportilla: alkuperäiset tavut/provenienssi/tarkiste, koko profiilin hallittu esto sekä erillinen rajattu JSON-LD/RDF/SHACL-koe. [Tulos ja tarkat rajoitteet](docs/webcor-acceptance.md). Literaalityyppien ja SKOS-riippuvuuden puute estävät koko profiilin generoinnin; sitä ei väitetä tuetuksi. DCAT-AP ja generointiprofiilin laajentaminen jäävät myöhemmiksi.

## 2H:n jatko — attribuuttikohtainen semantiikka

Erillinen tarkastettava jatkohaara 2H:n päällä: [sopimus ja lähdeversiot](docs/attribute-semantics.md). Generaattori 1.1.0 tuottaa alkuperäisen ominaisuus-IRI:n ja SHACL-rajoitteen käyttöyhteyden yhteiseen mappingiin, JSON Scheman x-term/x-mtv-shacl-annotaatioihin ja Type Metadatan x-mtv-semantic-annotaatioihin. Nimetön PropertyShape säilyy nimettömänä ja yksilöidään snapshotin, juurimuodon ja rajoitepolun avulla. Sisäkkäiset taulukot käyttävät IETF Claim Pathin null-askelia.

Versioitu oma laajennusprofiili, schema-/mapping-löydettävyys ja standardin base64-SRI-ketju julkaistaan artefakteina. Esimerkkikuluttaja lukee semantiikkaa ilman väitearvoja tai allekirjoituksen tarkistusta. Valinnaiset attribuutti-/järjestelykatalogivastaavuudet edellyttävät lähdettä, versiota, todistusaineiston tarkistetta ja normaalia hyväksyntää. TS11 1.0.1 ja molemmat viralliset tietomallit on lukittu muuttamattomina; pyydettyjen ETSI-versioiden ja EU-asetuksen ajantasaisen tekstin tarkistus on avoin 403-eston vuoksi. Koneellinen puuteraportti ei ole vaatimustenmukaisuusväite.

Main-pohja tuotu PR #13:n työhaaraan (main `9258fff`, merge `339824e`). [Uusi normatiivisen lähdetarkistuksen yritys](docs/pr13-normative-review.md): ETSI/EUR-Lex edelleen HTTP 403; TS11-lukot uudelleen varmennettu virallisesta Gitistä. Alkutekstivertailu ja EU-muutosten ajantasaisuus vaativat vielä lähdeaineistot.

Jäljellä: normatiivisten lähteiden tarkistus ja mahdolliset täsmennykset sen perusteella sekä erikseen tilattavat katalogirekisteröinti- ja ulkoisen myöntäjän integraatiot. Osittainen esitys ei osoita piilotetun attribuutin puuttumista alkuperäisestä todistuksesta.

## Vaiheen 2 myöhemmät osat — erillinen toimeksianto

Laajemmat JSON Schema/OpenAPI-kattavuuskartoitukset ja muunnoksen laajentaminen IRI-identiteetteihin, RDF-listoihin ja monijuurisiin profiileihin, laajemmat SHACL-profiilit, DCAT-AP-vientien vaatimustenmukaisuus, retired/archived-elinkaaret ja ajastettu lopetus, jäsenyyksien hallintakäyttöliittymä, tuotannon IdP, kielituen laajennukset ja kuormitusvaatimukset. Vaiheen 2D offline Core -tarkistus ja erillinen ihmistarkastus eivät korvaa näitä tai VC-kuoren/suojauksen tarkistusta.

## Vaihe 3 — ulkoiset integraatiot

Saman synteettisen sisällön JSON-haku sekä W3C VC- ja SD-JWT VC -myöntäminen yhteiseen profiiliin perustuen; yksi lähde-API/sovitin riittää. Erillinen myöntäjäsimulaattori, oikeat OpenID4VCI/lompakko-, QEAA- ja data-avaruuspalvelut, linkkien saavutettavuuden ja luottamuksen todennus sekä nimetyt EUDIW-/EBW-yhteentoimivuuskokeet. Katalogi ei toteuta Credential Endpointia tai tallenna henkilökohtaisia myöntämisistuntoja.

Seuraavaan vaiheeseen siirrytään vain erillisellä toimeksiannolla. Työhaaroja ei yhdistetä automaattisesti main-haaraan.
