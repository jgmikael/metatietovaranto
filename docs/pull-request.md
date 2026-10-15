Vaihe 2D lisää oikean offline SHACL Core -validoinnin synteettiselle esimerkkisisällölle. Uusi julkaisu tarvitsee lukitun profiilin rakenne-/riippuvuustarkistuksen, esimerkin läpäisseen SHACL-raportin ja aiemman erillisen ihmishyväksynnän. Vanhoja 2C-julkaisuja ei muuteta tai poisteta.

- pySHACL: profiilin meta-SHACL, tietotyypit, kardinaliteetit, sisäkkäiset muodot ja koodistot. Tyhjä, kohdistamaton tai kokonaan deaktivoitu profiili ei anna väärää onnistumista.
- Turtle/RDFXML/paikalliskontekstinen JSON-LD, yksi synteettinen esimerkkigraafi. Esimerkin alkuperäiset UTF-8-tavut ja vahvistus synteettisyydestä; tiedoston/tekstin syöttö käyttöliittymässä.
- Palvelimen raportti kertoo säännön, JSON Pointerin, RDF-polun, kohteen ja muodon. Raportti sitoo esimerkin/profiilin tarkisteet sekä moottori-/käytäntöversion. Asiakas ei voi asettaa raporttia.
- Esimerkki ja raportti kuuluvat sisältötarkisteeseen, hyväksyntään ja muuttumattomaan julkaisuun. Muutos mitätöi hyväksynnän; virheellinen esimerkki säilyy korjattavana luonnoksena.
- Resurssirajattu, verkoton validointiprosessi. SPARQL/JS/AF/mukautetut komponentit, tuntemattomat SHACL-predikaatit, etäkontekstit ja XML DTD/ENTITY torjutaan. Nimetyt JSON-LD-graafit hylätään, jotta sisältöä ei katoa huomaamatta.
- Ei skeemamuutosta: käytetään 2C:n JSONB-sisältöjä. Head pysyy 0004_publication. Ei taustatäydennyksiä vanhoihin riveihin tai julkaistuihin snapshotteihin.
- Nykyinen OIDC, CSRF, organisaatio-oikeudet, ETag, idempotenssi, Codespacesin Private-portti 8000 ja automaattinen selainavaus säilyvät.

Todennus: 55 API-/PostgreSQL-/migraatiotestiä ja 7 oikean Chromiumin/Keycloakin selaintestiä läpäissyt (62 eri testiä). TypeScript/Vite, pilven Docker-build, Compose-readiness, restartin tietojen säilyminen ja Alembic check läpäisevät. Kolmen aidon vanhan 2C-julkaisun sisältö/tarkiste/API/vienti säilyi. Tarkat ajot ja rajoitukset STATUS.md:ssä. Testit kattavat myös raskaan regex-rajoitteen pysäyttämisen CPU-rajaan, muuttumattomat aiemmat julkaisut, raportin väärentämiskiellon, RDF-esitykset ja raakasisällön tarkisteet. Selainpolku käyttää kahta oikeaa Keycloak-käyttäjää: virheellinen esimerkki → korjaus → hyväksyntä → julkaisu → anonyymi haku.

Rajaus: ei SHACL-SPARQL/JS/AF-tukea tai OWL-päättelyä, JSON Schema/OpenAPI-kattavuuskartoitusta, DCAT-AP-vaatimustenmukaisuutta, VC-kuoren/allekirjoituksen tarkistusta tai ulkoisia myöntäjä-/lompakkointegraatioita. SHACL-tulos ei todista Tietomallit-alkuperää tai myöntämisoikeutta. Oikea Codespaces/Windows/etä-CI ja elävän Tietomallit-palvelun tuonti raportoidaan ajamattomina.

Kokeile ennen yhdistämistä: https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2d-shacl . Portti 8000 Private. README sisältää tiedostojen latauksen, tuonnin, synteettisyysvahvistuksen ja vero → yritys -hyväksyntäpolun. Älä yhdistä mainiin automaattisesti.
