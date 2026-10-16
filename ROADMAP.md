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

## Vaiheen 2 myöhemmät osat — erillinen toimeksianto

JSON Schema-/OpenAPI-johdannaisten validointi ja kattavuuskartoitukset, laajemmat SHACL-profiilit, DCAT-AP-vientien vaatimustenmukaisuus, retired/withdrawn/deprecated/archived-elinkaaret, useat rinnakkaiset VC-jakelut ja niiden valinta, jäsenyyksien hallintakäyttöliittymä, tuotannon IdP, kielituen laajennukset ja kuormitusvaatimukset. Vaiheen 2D offline Core -tarkistus ja erillinen ihmistarkastus eivät korvaa näitä tai VC-kuoren/suojauksen tarkistusta.

## Vaihe 3 — ulkoiset integraatiot

Erillinen myöntäjäsimulaattori, oikeat OpenID4VCI/lompakko-, QEAA- ja data-avaruuspalvelut, linkkien saavutettavuuden ja luottamuksen todennus sekä nimetyt EUDIW-/EBW-yhteentoimivuuskokeet. Katalogi ei toteuta Credential Endpointia tai tallenna henkilökohtaisia myöntämisistuntoja.

Seuraavaan vaiheeseen siirrytään vain erillisellä toimeksiannolla. Työhaaroja ei yhdistetä automaattisesti main-haaraan.
