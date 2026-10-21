# SHACL-määrärajoitteet ja lähdeprofiilin diagnostiikka (21.10.2026)

Pohja main `c0e3a2e` (Pagesin kenttäohjeet yhdistetty), haara `fix/browser-shacl-diagnostics`. Selain-/palvelinlukijan yhteinen määrärajoitesopimus tukee XSD:n kokonaislukuperhettä, myös xsd:int-arvoja 0/1. Täsmällinen BigInt-/merkkijonovertailu ennen rajattua Number/int-muunnosta. Eri koodit termille/tyypille, leksikaalille, arvoavaruudelle, ristiriidalle ja 10 000:n resurssirajalle. Turtle-lähteen leksikaali säilytetään palvelingeneraattorissa per-parser-sinkillä, ei prosessinlaajuisella normalisointimuutoksella tai alkuperäisen snapshotin muokkauksella.

Selaimen bounded read-only-esitarkistus kokoaa riippumattomia havaintoja ennen mapping-ehdotusta. DATATYPE_TERM näyttää muodon/ominaisuusrajoitteen, predikaatin, RDF-termin/arvon, odotetun IRI:n ja korjausesimerkin. SEMANTIC_TOP_PROPERTY kertoo mapping-esteestä ja luettelee kaikki lähderajoitteet/nimet; sama polku ei automaattisesti tarkoita virheellistä SHACL-syntaksia. Saman tavallisen polun nimetyt yhteensopivat literaalirajoitteet käsitellään yhtenä kenttänä ja määrien leikkauksena, säilyttäen kaikki alkuperäiset rajoiteviitteet. Muu yhdistelmä saa dokumentoidun tukirajoitteen. Ei korjattua lähdekopiota, keksittyjä ominaisuuksia tai viittä eri JSON-kenttää epäselvästä semantiikasta.

Raportti luokittelee lähdevirheet, generaattorin tukirajoitteet, resurssirajat ja huomiot. Virhe kohdistuu tarkistuspainikkeen alle; aiempi ehdotus tyhjennetään uusintatarkistuksessa. Ei täydellistä SHACL-validointia: raportti enintään 200 kenttää / 200 havaintoa, syvyys 8, ei verkkoriippuvuuksien noutoa, Worker 15 s ja nykyiset tiedosto-/kolmikkorajat säilyvät. Nimetön PropertyShape näkyy paikallisena kohtana, ei URI:na. Lähde-/exportkorjaukset jäävät ylläpitäjälle.

Alkuperäinen käyttäjän toimittama **Verovelkatiedot (1).ttl** löytyi ja on tavuntarkkana testifixturena provenansseineen: **70 390 tavua / 1 015 kolmikkoa**, SHA-256 `576c4e7dbded346df0da2626eaac0b556ace059d36d6c8b2316416aced5969aa`. Ei riippumatonta verkkovarmennusta tai tuntemattoman version väittämistä. Juurena `https://iri.suomi.fi/model/verovelka/Debtor` muuttamaton aineisto tuottaa **38 DATATYPE_TERM**, **2 SEMANTIC_TOP_PROPERTY**, **2 PROPERTY_CONSTRAINT_UNSUPPORTED**, ei CARDINALITY-havaintoja. Debtorin topObjectProperty-havainto sisältää kaikki viisi alkuperäistä rajoitetta ja niiden nimet. Paketti estyy edelleen. Fixture ei kuulu julkaistavaan Pages-katalogiin.

Generaattoriversiot palvelin **1.1.2**, selain **1.0.1**; yhteinen contract regeneroitu. Vanhojen paikallisten pakettien sidonta vanhenee version mukana ilman niiden tai lähteiden poistamista. Vanhoja julkisia versioita ei muuteta. Ei skeemamigraatiota tai oikeus-/hyväksyntämuutosta. Ohjeet READMEssä, docs/browser-shacl-generation.md:ssä ja yhteisen kenttäohjeen vianmäärityksessä.

Huomio: xsd:int-luvun hyväksyntä lukijassa ei tarkoita SHACL-metavalidoinnin läpäisyä. Nykyinen pySHACL vaatii parametriin xsd:integer-tietotyypin ja palvelimen riippumaton validointi säilyy. RDF/XML-/JSON-LD-palvelinlähteiden aiempaa leksikaalista normalisointia ei muuteta; parity on testattu samoilla Turtle-lähteillä. Palvelin palauttaa edelleen ensimmäisen eston, selain voi koota monta. Nämä erot on dokumentoitu.

## Tämän muutoksen todennus ja toimitus

- **99 staattista testiä läpäisi** (`.venv/bin/pytest tests_static -q`), joista 37 uutta lukija-/parity-/diagnostiikkatapausta. Mukana alkuperäinen muuttamaton export, termi-/leksikaali-/arvo-/ristiriita-/resurssiluokat, hyvin suuret luvut/etunollat, alkuperäisen sisällön/hashien säilyminen, viisi topObjectProperty-rajoitetta, nimetön PropertyShape, samaan polkuun kohdistuva kelvollinen leikkaus, Unicode-IRI:en järjestys, virheellisen paketin esto sekä oikean JSON-LD-prosessorin RDF/SHACL-koe. Kaikki vanhat staattiset testit mukana. Ei API-/tunnistus-/ulkoverkkopyyntöjä tai selainvirheitä.
- Viimeisen kohdistus-/vierityskorjauksen jälkeen **8 kohdennettua selaintestiä läpäisi**: lähderaportin näkyvyys navigaation alapuolella, syntaksi-/koko-/keskeytys-/aikarajapolku ja koko kenttäohjesarja. Alkuperäisellä exportilla tehty visuaalinen HTTP-koe varmisti fokusoidun raportin alun näkyvän 112 px:n kohdalla (ylänavigaation alapuolella).
- **209 API-/profiili-/migraatiotestiä läpäisi** (`.venv/bin/pytest tests --ignore=tests/test_browser.py -q`) lopullisella palvelinlukijalla. Erillinen testikanta; ei kahta tyhjentävää sarjaa rinnakkain. Vain nykyisten rdflib/Starlette-riippuvuuksien deprekaatiovaroituksia.
- **13 palvelinselaintestiä läpäisi** (`BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`), oikea Keycloak-kirjautuminen sekä ylläpito/hyväksyntä/julkaisu ja elinkaari mukana. Ensimmäinen ajo aikakatkaisi yhdessä elinkaaritestin withdrawn-hakutuloksen odotuksessa. Sama testi läpäisi erillisen uusinnan (1/1) ja koko sarja uusinnan (13/13) ilman tämän polun tai testin muuttamista. Ensimmäisen aikakatkaisun syytä ei yksilöity; ei toistuvaa estettä viimeisissä ajoissa.
- **Tavallinen web-build, Pages-build ja Docker-build läpäisivät.** Komennot `npm run build --prefix apps/web`, `UV_CACHE_DIR=/workspace/.cache/uv bash scripts/build-pages.sh` (myös 3 ohjekääntäjän testiä) ja `DOCKER_CONFIG=/workspace/.cache/docker bash scripts/cloud-build.sh`. Viimeinen Docker-image käynnistettiin `docker compose up -d --no-build --wait` -komennolla. Kaikkien 13 live-katalogitaulun sisältöhashit ja Alembic-head säilyivät ennen/jälkeen uudelleenkäynnistyksen. Dockerin käyttämätöntä build-välimuistia vapautettiin levytilan vuoksi; tietokantavolumeja ei poistettu.
- **124 vanhaa julkaisuversiota**, **10 vanhaa generaattoripakettia** ja **102 vanhaa artefaktia** luettiin erillisessä HTTP-yhteensopivuuskokeessa, artefaktien alkuperäiset tavut/tarkisteet varmennettu.
- Jaettu contract vastaa palvelinvakioita. `node apps/web/scripts/build-help.mjs --check` ja `git diff --check` läpäisivät.
- **Ajamattomat:** Firefox/Safari, oikea NVDA/VoiceOver, fyysinen puhelin, Windows Docker Desktop ja Codespacesin oma käynnistys. Julkista deployta tai GitHub Actionsin tulosta ei tarkistettu tästä haarasta; PR-haara ei julkaise.


Toteutuscommit `a4cdcf3`, haara `fix/browser-shacl-diagnostics` pushattu. Valmis PR-kuvaus docs/pull-request-shacl-diagnostics.md. `gh pr create --base main --head fix/browser-shacl-diagnostics --title "Korjaa SHACL-määrärajoitteet ja lähdeprofiilin diagnostiikka" --body-file docs/pull-request-shacl-diagnostics.md` estyi GitHub GraphQL API:n **Forbidden**-vastaukseen. PR:ää ei luotu tässä ympäristössä. Luontilinkki https://github.com/jgmikael/metatietovaranto/pull/new/fix/browser-shacl-diagnostics (base main, compare fix/browser-shacl-diagnostics). Kopioi valmis kuvaus PR:n kuvauskenttään. Ei main-yhdistämistä tai Pages-deployta.

---

# Pagesin käyttöliittymän ohjeet (20.10.2026)

Pohja ajantasainen main `8398c02` (käyttöohje-PR #17 yhdistetty), haara `feat/pages-inline-help`. Sama **docs/pages-kayttoohje.md** toimii nyt käyttöliittymän kokonaisohjeena ja lyhyiden kenttäselitteiden lähteenä. Buildin kenttärekisterissä on **104 yhteistä kenttä-/käsiteavainta ja 19 pysyvää osiota**. Navigaatiossa Käyttöohje, sisällysluettelo, suorat/reloadia kestävät `#ohje/<tunniste>`-linkit ja Markdown-lataus. Kentän Ohje on natiivi avaus-/sulkupainike (type=button, aria-expanded/controls), ja kenttä viittaa selitteeseen aria-describedby-attribuutilla. Lue lisää vie oikeaan osioon. Paluu palauttaa kohdistuksen ja vierityksen; myös keskeneräinen Turtle-tuonti, mapping-ehdotus ja kuittaukset säilyvät ohjevierailun ajan.

Kattavuus: julkinen haku, paikalliset organisaatiot ja tuotteen perustiedot, JSON API / W3C VC / SD-JWT VC, myöntäjä-/lompakkoasetukset, mappingit, SHACL-tuonti ja generointi, tallennus/tuonti/vienti/palautus sekä keskeiset johdetut tulokset. Kattavuustestissä käytiin läpi myös olio- ja lompakkokenttien ehdolliset haarat. Nykyisiä Pagesin muokattavia kenttiä ei tunnistettu jääneen ohjeistamatta. Omistajaorganisaation oikeudet selitetään käsitteenä; Pagesiin ei keksitä omistajan vaihtokenttää. Palvelinsovelluksen omat ylläpitolomakkeet säilyvät ilman uutta Pages-ohjenäkymää.

Markdown jäsennetään buildissa unified/remark-parse/remark-gfm-kirjastoilla rajattuun rakenteeseen. Selaimessa ei suoriteta koodia, renderöidä raakaa HTML:ää tai haeta ohjetta ulkopuolelta. Markdown, Turtle-esimerkki ja raportti sisältyvät buildiin. Kenttätekstejä ei kopioida Reactiin. Ohjekääntäjä tarkistaa rekisterin lähderivit/otsikot. Ohjeiden ylläpito: **docs/pages-help-maintenance.md**. Molempien buildien ja kehityskäynnistyksen esivaihe generoi ohjeen. Dockerin web-stage huomioi ohjeen lähdetiedostot. Ei migraatiota tai muutosta olemassa oleviin julkaisuihin, käyttöoikeuksiin tai paikallisen kokeilun tallennusformaattiin.

## Tämän muutoksen todennus

- Ohjekääntäjän `npm run test:help --prefix apps/web`: **3 läpäisi** (otsikko-/kenttäkytkennät, puutteiden/duplikaattien hylkäys, HTML/linkkien turvallisuus ja koodiesimerkin käsittely tekstinä).
- `npm run build --prefix apps/web` sekä `UV_CACHE_DIR=/workspace/.cache/uv bash scripts/build-pages.sh`: **läpäisivät**. Pages-build ajaa myös ohjekääntäjän testit. `node apps/web/scripts/build-help.mjs --check` ja `git diff --check`: läpäisivät.
- `.venv/bin/pytest tests_static -q`: **62 läpäisi** lopullisesta buildista `/metatietovaranto/`-alipolussa. Kuusi uutta ohjekoetta: avaus/sulku/näppäimistö ilman lomakelähetystä, suorat linkit/reload/Markdown-rakenteet/lataukset, ehdollisten kenttien kattavuus, keskeneräinen tiedostotuonti ja muokkaus, mapping/kuittaukset/fokus/vieritys sekä julkisen tuotesivun paluu ja Chromium-kosketustapahtuma kapeassa näkymässä. Kaikki ulkoiset/API-/tunnistuspyynnöt estetty; ei yrityksiä niihin tai JavaScript-/konsolivirheitä. Nykyiset vienti-/palautus-, Worker-parity-, JSON-LD/RDF- ja generointikokeet mukana.
- Palvelinregressiot: **193 läpäisi** (`test_api`, `test_auth`, `test_publication`, `test_public_url`, `test_semantic_validation`, `test_derived_validation`, `test_distributions`, `test_conversion`, `test_lifecycle`, `test_technical_packages`, `test_attribute_semantics`) ja tämän jälkeen **16 läpäisi** (`test_migrations`, `test_profiles`). Yhteensä **209** erilliseen testikantaan; tyhjentäviä testisarjoja ei ajettu rinnakkain samaan kantaan.
- Lopullinen Docker-image rakennettu `DOCKER_CONFIG=/workspace/.cache/docker bash scripts/cloud-build.sh` -komennolla (ympäristön välityspalvelin/CA huomioitu); `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait` käynnisti terveen sovelluksen. Kaikkien 13 katalogitaulun sisältöhashit ja Alembic-head verrattu ennen/jälkeen: **muuttumattomat**. PostgreSQL-volumeja ei poistettu. Levytilan loppuminen korjattiin poistamalla käyttämätön Docker-build-välimuisti, minkä jälkeen lopulliset buildit ja testit ajettiin uudelleen.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **13 läpäisi** lopullista imagea vasten, oikea Keycloak-kirjautuminen mukana. Sarjoissa vain nykyisten Starlette/rdflib-riippuvuuksien deprekaatiovaroituksia.
- Erillinen HTTP-yhteensopivuuskoe: **108 vanhaa julkaisuversiota luettavissa**, **8 vanhaa generaattoripakettia** ja **78 artefaktin** alkuperäiset tavut/tarkisteet varmennettu. Hakunäkymä/avoin selite ja ohjeosio tarkastettu lisäksi kuvakaappauksista Chromiumissa.


Rajat: ei NVDA-/VoiceOver-koetta tai fyysistä puhelinta, Firefoxia/Safaria, Windows Docker Desktopia tai Codespaces-ympäristön omaa käynnistystä tällä kierroksella. Ohjelmalliset saavutettavuus-, näppäimistö- ja kosketuskokeet ajetaan Chromiumissa. GitHub Actionsin tai julkisen Pages-deployn tulosta ei ole tarkistettu; PR-haara ei julkaise. Julkista URLia ei väitetä tässä muutoksessa päivitettynä toimivaksi.

## Toimitus

Toteutuscommit `7bf7363`, haara `feat/pages-inline-help` pushattu. Valmis PR-kuvaus **docs/pull-request-pages-help.md**. `gh pr create --base main --head feat/pages-inline-help --title "Pages: käyttöohje ja kenttäkohtaiset ohjeet" --body-file docs/pull-request-pages-help.md` estyi GitHub GraphQL API:n **Forbidden**-vastaukseen. PR:ää ei siksi luotu tässä ympäristössä eikä sille ilmoiteta keksittyä numeroa. Luontilinkki: https://github.com/jgmikael/metatietovaranto/pull/new/feat/pages-inline-help (base main, compare feat/pages-inline-help). Kopioi valmiin kuvauksen sisältö PR:n kuvauskenttään. Ei main-yhdistämistä tai Pages-julkaisua.

---

# Public Pages -demon kenttäkohtainen käyttöohje (20.10.2026)

Pohja main `0f26969`, paikallinen SHACL-generointi yhdistetty. Uusi dokumentti **docs/pages-kayttoohje.md** kuvaa Aloita oma kokeilu -työnkulun vaihe vaiheelta: valmiin esimerkin ensikokeilu, oma organisaatio/tuote, kaikki perustieto-/toimitustapa-/myöntäjä-/lompakko-/mapping-kentät, SHACL-tuonti, esitysvalinnat ja kuittaukset, tulokset/lataukset, palautus ja virhetilanteet. Generointiin tarvittavat ja valinnaiset tiedot erotellaan; ei kehoteta keksimään toimivaa myöntäjäpalvelua, QEAA-näyttöä tai lompakkotukea. Kenttänimet vastaavat nykyistä käyttöliittymää. Linkit READMEssä ja nykyisissä kokeilu-/generaattoriohjeissa. Ei sovelluskoodin tai tietokannan muutoksia.

Tarkistettu lähdekoodista 49 toimitustapa-/mapping-kenttäselitettä, 10 generointikenttää, 5 kokeilun/organisaation kirjaimellista labelia ja 7 perustietokentän nimeä sekä dokumenttien suhteelliset tiedostolinkit. `git diff --check` läpäisi. `bash scripts/build-pages.sh` läpäisi.

Ohjeen ensikokeilun arvot ajettiin oikealla Chromiumilla staattisessa `/metatietovaranto/`-alipolussa: synteettinen Turtle → juurimuoto ja ehdotus → `1.0.0`, `https://julkaisut.example.org`, `{"companyName":"Synteettinen Esimerkki Oy"}` ja kolme kuittausta → **13 artefaktia**, context.jsonld-lataus ja työtilan reload läpäisivät. Kaikki ulkoiset/kirjoituspyynnöt oli estetty; ei yrityksiä niihin tai JS-/konsolivirheitä. Preview pysäytettiin. Julkista sivustoa ei tarkistettu tässä ohjepäivityksessä.

Koko API-/migraatio-/palvelinselaintestisarjaa tai 56 testin staattista regressiosarjaa ei toistettu pelkän dokumentaatiomuutoksen vuoksi. Edellisen toteutuksen tulokset ovat alla historiallisina raportteina. Dokumentti ei lisää kenttäkohtaisia tooltippejä sovellukseen vaan antaa yhden luettavan, esimerkeillä täydennetyn täyttöohjeen.

Toimitus: commit `4f3ce80`, haara `docs/pages-workflow-guide` pushattu. PR:n avaaminen komennolla `gh pr create --base main --head docs/pages-workflow-guide --body-file docs/pull-request-pages-guide.md` estyi GitHub GraphQL API:n Forbidden-vastaukseen. Ohje on jo luettavissa haarassa. Valmis PR-kuvaus docs/pull-request-pages-guide.md ja luontilinkki https://github.com/jgmikael/metatietovaranto/pull/new/docs/pages-workflow-guide. Ei main-mergeä.

---

# Pagesin paikallinen SHACL-tuonti ja generointi (19.10.2026)

Pohja main `f1f4de6` (PR #15 / Oma kokeilu yhdistetty), uusi haara `feat/pages-browser-shacl`. Main tarkistettu uudelleen ennen toimitusta ja ennallaan. Toteutettu UTF-8 Turtle -tuonti ja paikalliset riippuvuudet, muodot/ominaisuudet/nimiavaruudet/importit, juuren valinta, tarkastettavat deterministiset nimet ja esitysvalinnat sekä rajattu planned-toimitustapojen tekninen kuvauspaketti Web Workerissa.

N3.js 2.13.12, Ajv 8.20.0 ja jsonld.js 9.0.0, npm-lock. Yhteiset palvelimesta johdetut määritykset ja standardilähteiden hashit, palvelinreferenssi technical-package/1.1.1, selain browser-technical-package/1.0.0. [Täsmällinen tuki, erot ja käyttö](docs/browser-shacl-generation.md). Käyttäjän lähteitä ei noudeta/siirretä verkkoon. Ei kirjautumista, APIa, tietokantaa, hyväksyntää, todistusta tai oikeaa julkaisua selainpolussa. Varsinainen palvelinsovellus ja sen snapshotit/prosessit säilyvät.

Paketti sisältää kontekstin, scheman, Type Metadatan ja attribuuttisemantiikan, yhteiset/muotokohtaiset mappingit, x-mtv-laajennuksen, vct#integrity-kuvauksen, synteettiset allekirjoittamattomat esimerkit/RDF:n, muuttumattomat lähteet ja manifestin tarkisteketjuineen. Turtle-jäsennys, generointituki, JSON Schema ja lukittu JSON-LD-prosessointi erotetaan; täydellinen SHACL ja selaimen graafivertailu **not-run**. Paketti on paikallinen, URLit vain suunniteltuja. Metadatan tai lähteen/asetusten/generaattorisopimuksen muutos vanhentaa paketin. Vanha paketti säilyy ladattavana, tuotteen mappingeja ei ylikirjoiteta generoinnissa.

Oma kokeilu -v1:n valinnaiset localProfiles/generation-laajennukset säilyttävät vanhojen tallenteiden luettavuuden. Alkuperäiset lähteet ja tavuhashit palautuvat JSONista, snapshotin hash on erillinen. Tuonti/uudelleenavaus tarkistavat hashit Workerissa ennen hyväksymistä; epäonnistuminen ei korvaa tallennetta. 2 MiB kokonaisraja ja aiemmat välilehti-/kiintiö-/atomisen palautuksen suojat säilyvät. Tiedostoille 256 KiB / 10 tiedostoa, 10 000 jäsennettyä kolmikkoa (raja jo quadien muodostuksessa), puulle 8 tasoa / 200 kenttää, esimerkille 100 kB / 20 tasoa / 2000 arvoa, Workerille 15 s + terminate-keskeytys.

## Todella suoritetut tarkistukset

- `bash scripts/build-pages.sh` sekä lopullinen `npm run build:pages --prefix apps/web`: läpäisivät. Normaali `npm run build --prefix apps/web`: läpäisi; normaali pääbundle ei sisällä paikallista generointinäkymää tai worker-kutsua.
- `pytest tests_static -q`: **56 passed in 120.75s**, ei ohituksia tai JS-/konsolivirheitä. Oikea staattinen `/metatietovaranto/`-HTTP-palvelin, API/auth/identity/ulkoiset ja kirjoituspyynnöt kielletty. Koko aiempi julkinen/kokeilutoiminnallisuus sekä uudet tuonti/generointi/lataus/reload/vienti/palautus/vanheneminen/hashihylkäykset/rajat/keskeytys/aikaraja.
- Selaimen oikea koottu Worker vastaa nykyisen palvelingeneraattorin mapping-rivejä, kontekstia, annotoitua schemaa ja SD-JWT claims-kuvauksia sisäkkäisessä vertailuaineistossa. Determinismi, kaksi eri city-roolia, monikieliset näyttönimet, nimettömät PropertyShapet, kansalliset/ulkoiset IRI:t, taulukkojen null-polut ja SRI-eheysketju/muutoshavainto läpäisivät.
- Erillinen **PyLD**, lukittu dokumenttilataaja, käsin laadittu odotettu RDF, selaimen jsonld.js:n RDF sekä offline-lähde-SHACL läpäisivät. Testiajon SHACL ei ole selaimen tuottama raportti.
- Juurikohtainen 429 kolmikon / viiden juuren raportti: docs/browser-webcor-report.json (ensimmäinen estävä havainto per juuri). Aito muuttamaton WE BUILD Certificate of Residence 0.0.2 jäsentyi alkuperäisellä SHA-256:lla `2ad4331272558bb541b7804f194a74e261d8313985554015ccc4e23785286133`. Kokonaiset juuret ylittävät tuen: erityisesti puuttuvat eksplisiittiset literaalityypit ja tukemattomat rajoitteet. Erikseen merkitty family-name-test-projektio toimii. Ei alkuperäisen muokkausta tai koko profiilin tukiväitettä; riippumatonta verkkovarmennusta ei väitetä.
- README:n koko 13 tiedoston API-/PostgreSQL-/migraatiosarja: **209 passed, 4 warnings in 405.87s**. catalog_test erillisenä: oikeudet/CSRF, hyväksyntä/julkaisu, vanha/tyhjä kanta ja toistuvat migraatiot, SHACL-/muunnos-/paketti-/attribuuttikokeet.
- `bash scripts/cloud-build.sh` ja `docker compose up -d --no-build --wait`: läpäisivät, kaikki palvelut healthy. 13 catalog-taulun rivien/tavujen ja Alembic headin ennen/jälkeen vertailu muuttumaton. Ei volumen poistoa. Ei uutta migraatiota.
- Uudelleenrakennettu normaali sovellus, oikea Chromium/Keycloak: **13 passed, 1 warning in 134.78s**. Tallennus/uudelleenavaaminen, oikeudet, hyväksyntä/julkaisu, elinkaari ja artefaktit. **278 eri pytest-testiä** yhteensä. Varoitukset Starlette/httpx ja RDFLib. Selaintestit jättävät omat synteettiset julkaisut historiaan; alkuperäisiä fixturetuotteita ei muutettu.
- HTTP-lisäkoe: **103 julkaisuversiota, 8 vanhaa pakettia, 78 artefaktin tavutarkistusta** läpäisi. Paikallinen dokumentoitu preview, oikea käyttöliittymän tuonti/generointi, desktop-näkymä ja 390 px leveys ilman JS-virheitä. Preview pysäytettiin; se ei ole julkinen julkaisu. Viimeisen tekstitarkennuksen jälkeen molemmat web-buildit ja kohdennettu tuonti/generointi/reload/JSON-palautustesti läpäisivät (1 passed in 7.70s). Palvellun buildin Worker-polun löytämisen testiapurin tarkennus varmennettiin erikseen parity- ja aidon exportin kokeilla (2 passed in 4.04s). `git diff --check` läpäisi.

## Rajat ja ajamattomat tarkistukset

Ei natiivia Windows-/Firefox-/Safari-ajoa. Worker-aikaraja testattiin deterministisellä pysäytetyllä testityöntekijällä; käyttöjärjestelmän muistikiintiötä ei ole. Ei oikeaa uutta Pages-deployta/julkista HTTP-tarkistusta tai GitHubin etä-CI-tuloksen varmistusta tässä tehtävässä. Suunniteltuja osoitteita ei noudettu tai väitetty saavutettaviksi. Ei ulkoista myöntäjä-/lompakkopalvelua, rekisteröintiä tai vaatimustenmukaisuusväitettä. Selainversion suljetut muodot, date/dateTime-arvojen tarkka XSD-leksikaalinen esimerkkivalidointi ja palvelimen täydellinen SHACL/julkaisuprosessi jäävät palvelinsovellukseen. Katso docs/browser-shacl-generation.md ja valmis PR-kuvaus docs/pull-request-browser-generation.md.

## Toimitus

Toteutuscommit `8d1f5ca`, haara `feat/pages-browser-shacl` pushattu GitHubiin. `gh pr create --base main --head feat/pages-browser-shacl --title 'Pages: paikallinen SHACL-tuonti ja tekninen generointi' --body-file docs/pull-request-browser-generation.md` estyi: `POST https://api.github.com/graphql: Forbidden`; myös REST-luku palautti Forbidden. PR:ää ei siis saatu avattua automaattisesti. Valmis kuvaus docs/pull-request-browser-generation.md, luontilinkki https://github.com/jgmikael/metatietovaranto/pull/new/feat/pages-browser-shacl (base main). Ei main-mergeä tai julkista deployta.

---

# Oma kokeilu: PR:n CI-korjaus (19.10.2026)

Käyttäjä on luonut PR:n haarasta `feat/pages-local-experiment`. Sen Pages-CI:ssä JSON-tuonnin testi ehti lukea vanhan tuotteen nimen. Syy toistettiin deterministisesti: korvausoperaatio ei vaihtanut edellistä `Tallennettu`-tilaa keskeneräiseksi ennen asynkronista kirjoitusta. Kyse ei osoittanut tuonnin jälkeistä palautumista alkuperäiseen aineistoon.

Korvaus näyttää nyt heti `Tallennetaan…`; myöskään edeltävä automaattitallennus ei saa ilmoittaa kesken olevaa korvausta valmiiksi. Kaksi uutta selaintestiä jonottaa tuonnin/resetin oikean varatun Web Lockin taakse, tarkistaa vanhan tallenteen ja keskeneräisen tilan, vapauttaa lukon sekä tarkistaa korvatut tiedot ja reloadin. **Ennen korjausta molemmat epäonnistuivat** (2 failed in 14.65s).

Korjauksen jälkeen `bash scripts/build-pages.sh`, `.venv/bin/pytest tests_static -q` (**30 passed in 63.99s**, ei ohituksia tai konsolivirheitä) ja `npm run build --prefix apps/web` läpäisivät. Mukana alkuperäinen epäonnistunut tuonti-/palautustesti sekä uudet lukitus-/reload-kokeet. `git diff --check` läpäisi. API-/tietokanta-/palvelinsovelluksen selaintestejä ei ajettu uudelleen tämän vain Pagesin korvaustilan korjauksen vuoksi; edellisen toteutuscommitin 24 API- ja 13 palvelinselaintestiä on raportoitu alla. GitHubin uutta etä-CI-tulosta ei ole varmennettu tässä ympäristössä. Korjaus toimitetaan samaan PR-haaraan, ei main-mergeä.

---

# Pagesin Oma kokeilu (19.10.2026)

Työhaara `feat/pages-local-experiment` perustuu ajantasaiseen mainiin `edb4348` (PR #14 yhdistetty). Main tarkistettiin uudelleen ennen toimitusta; uusia päähaaran muutoksia ei ollut. Alla olevat aiempien vaiheiden raportit ovat historiallisia.

Toteutettu selaimessa toimiva paikallinen metadatan ylläpito: tuotteet ja organisaatiot, kolme toimitustapaa, mukana toimitetun profiilin valinta, alkuperäisten artefaktien tarkastelu. Yhteiset tietotyypit, peruslomake sekä toimitustapa- ja pakettikomponentit; tavallinen palvelinbuild ei avaa kokeilutilaa. Julkinen katalogi säilyy muuttumattomana. Ei uusia taustapalveluja, riippuvuuksia, migraatioita tai muutoksia varsinaisen sovelluksen snapshotteihin/julkaisuihin.

Versioitu localStorage, 500 ms automaattitallennus, onnistumisen takaisinluku, Web Locks ja edellisen tallenteen vertailu. Virhe-/kiintiö-/tuntematon versio- ja välilehtitilanteet säilyttävät aineiston. Koko työtilan JSON-siirtoformaatti 1, enintään 2 MiB, tiukka sallittujen kenttien ja viittausten tarkistus ennen vahvistettua korvaamista. Uusi demojulkaisu ei siemennä tallennetta uudelleen; puuttuvat tarkisteviitteet ilmoitetaan.

Paikalliset tuotteet aina **Ei validoitu tässä kokeilussa**. Alkuperäisen paketin raportit näytetään vain erillisessä lähtöesimerkissä, eivät nykyisen tuotteen tuloksina. Myöntämis-/lähdetietotoiminnot estetty myös production-tilaisessa tuodussa metadatassa. Ei generointia, SHACL-validointia, hyväksyntää tai allekirjoittamista. [Käyttö ja siirtoformaatti](docs/own-experiment.md).

## Tämän muutoksen todella ajetut tarkistukset

- `bash scripts/build-pages.sh`: läpäisi, tietokannaton Pages-build sekä TypeScript/Vite-build.
- `.venv/bin/pytest tests_static -q`: **28 passed in 70.32s**, ei ohituksia. Oikea staattinen HTTP-palvelin `/metatietovaranto/`-alipolussa, backend-/auth-/identity-/ulkoiset ja kirjoituspyynnöt kielletty. Kattaa aiemman julkisen esittelyn ja paikallisen ylläpidon, reloadin, viennin/tuonnin/peruutuksen, 8 virheellistä tuontitapausta, kiintiö-/käyttöestot, viallisen/oudon tallenneversion, oikean kahden välilehden Web Locks -kilpailun, puuttuvat profiili-/pakettiviitteet uuden demoversion jälkeen sekä validoimattoman tilan. Ei JavaScript- tai konsolivirheitä. Yksi väliajo paljasti lukituskokeen ajoitusoletuksen: korjattu odottamaan todellista jonojärjestystä; lopullinen täysi ajo läpäisi.
- `.venv/bin/pytest tests/test_api.py tests/test_auth.py tests/test_publication.py tests/test_public_url.py -q`: **24 passed, 3 warnings in 25.16s**, erillinen catalog_test-PostgreSQL. Perustoiminnot, oikeudet/CSRF ja riippumaton julkaisu säilyivät.
- `npm run build --prefix apps/web`: läpäisi. Normaali palvelinsovellus rakennettiin myös Docker-kuvaksi `bash scripts/cloud-build.sh` ja käynnistettiin `docker compose up -d --no-build --wait` (DOCKER_CONFIG ympäristön välimuistihakemistossa). Kaikki palvelut healthy.
- Tietokannan 13 taulun rivien tavutarkisteet ja Alembic head vertailtiin ennen/jälkeen uudelleenkäynnistyksen: kaikki ennallaan. Ei volumen poistoa. Erillinen vanhojen julkaisujen lukukoe: **97 versiota**, **8 vanhan generaattorin pakettia**, **78 artefaktin tavutarkistusta** läpäisi.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **13 passed, 1 warning in 132.38s**, oikea Chromium/Keycloak uudelleenrakennettua palvelinta vasten. Tallennus/uudelleenavaaminen, oikeudet, hyväksyntä, julkaisu, elinkaari, tekniset paketit ja julkiset artefaktit läpäisivät. Selaintestit jättävät omat synteettiset muuttumattomat julkaisut historiaan; alkuperäisiä fixturetuotteita ei muutettu. Nykyisessä tehtävässä **65 eri pytest-testiä**, ei ohituksia. Varoitukset Starlette/httpx ja RDFLib.
- Erillinen dokumentoitu preview `python -m scripts.preview_pages --port 4173`: HTTP 200, oikea selaimen aloitus/tallennus, desktop- ja 390 px mobiilikuvakaappaus tarkastettu; ei vaakavieritystä. Preview pysäytettiin. `git diff --check` läpäisi.

## Rajat ja ajamattomat tarkistukset

Ei toistettu koko taustapalvelimen 209 testin SHACL-/muunnos-/migraatiosarjaa: taustapalvelimen tai tietokantaskeeman toteutus ei muutu. Tyhjän/vanhan kannan migraatioajoja ei tässä tehtävässä ajettu; olemassa olevan kannan startup/säilyminen tarkistettiin yllä. Ei natiivia Windows-, Firefox-, Safari- tai oikean yksityisen selausprofiilin ajoa. Tallennuksen estyminen ja kiintiövirheet testattiin selaimen Storage-operaatioiden virheinjektiolla; fyysistä kiintiötä ei täytetty. Selain voi hävittää paikallistietoja eikä tallentamaton muistidata ole kaatumiskestävä: JSON-varmuuskopio on käyttäjän palautuskeino.

Käyttäjä vahvisti aiemman julkisen Pages-julkaisun onnistuneen. Tämän haaran kokeilutilaa ei julkaistu tai HTTP-varmennettu julkisessa osoitteessa eikä mainiin yhdistetty. Yhdistämisen jälkeen nykyinen Public Pages demo -workflow julkaisee mainin; tarkista deploy ja Verify published HTTP responses. GitHubin etä-CI-tulos varmistetaan erikseen.

## Toimitustila

Toteutuscommit `fead6c7`, haara `feat/pages-local-experiment` pushattu GitHubiin. `gh pr create --base main --head feat/pages-local-experiment --title 'Pages: selaimessa toimiva Oma kokeilu' --body-file docs/pull-request-own-experiment.md` estyi: `Post https://api.github.com/graphql: Forbidden`. PR:ää ei siis saatu luotua automaattisesti. Valmis kuvaus on docs/pull-request-own-experiment.md; luontilinkki https://github.com/jgmikael/metatietovaranto/pull/new/feat/pages-local-experiment (base main). Ei main-mergeä tai julkista deployta.

---

# GitHub Pages -esittelydemo (19.10.2026)

PR #13 on yhdistetty mainiin **6b48536**. Uusi työhaara `feat/github-pages-demo` perustuu siihen. Samalle React-sovellukselle on toteutettu erillinen Pages-build, yhteiset tyypit ja vain lukua tukeva tietolähdekerros. Neljä versionhallituista synteettisistä fixtureistä koottua tuotetta, kolme organisaatiota, yksi yhteisen SHACL-perustan ja kolmen planned-toimitustavan paketti. Ei tietokantavientiä, käyttäjäaineistoa, tunnuksia, istuntoja tai auditointitietueita. Ei kirjoitus-, hyväksyntä-, myöntämis- tai palvelinpuolen validointitoimintoja Pagesissa.

Nykyinen generaattori tuottaa kontekstin, scheman, Type Metadatan, mappingit, attribuuttiannotaatiot, synteettiset allekirjoittamattomat esimerkit ja raportit lopullisesta konfiguroidusta julkaisuosoitteesta. Rakentaja normalisoi vain uuden synteettisen build-snapshotin ajokohtaiset metatiedot; varsinaisen sovelluksen snapshotteja ja julkaisuja ei kirjoiteta uudelleen. JSON-LD-vienti jaettiin samaksi tietokannattomaksi apumoduuliksi. Generaattorin valinnainen snapshot_url säilyttää palvelimen nykyiset oletukset.

Tavoite **https://jgmikael.github.io/metatietovaranto/** ei ole tässä tehtävässä julkaistu tai HTTP-varmistettu. Vain main saa deployata. PR ja muut workflow_dispatch-haarat rakentavat/testaavat ilman julkaisua. GitHub API:n Pages-/repoasetusten luku palautti Forbidden; näkyvyyttä, Pages-tilaa tai tilauksen tukea ei voitu varmistaa. Käyttäjän on valittava Settings → Pages → GitHub Actions ja ajettava Public Pages demo mainista yhdistämisen jälkeen. Näkyvyyttä/maksullisia asetuksia ei muutettu eikä uutta repositoriota luotu.

## Todella suoritetut tarkistukset

- Staattisen demon `pytest tests_static -q`: **7 passed in 6.14s**, ei ohituksia tai JavaScript-/konsolivirheitä. Tavallinen HTTP-palvelin /metatietovaranto/-alipolussa; kaikki backend-/ulkoiset selainpyynnöt estetty. Lista, haku, teema/tarjoaja, mobiilileveys, suora tuoteversiolinkki/reload, organisaatio, SHACL-tarkastelu, lataukset ja semanttinen kuluttaja läpäisivät. Luonnoshash ei avaa ylläpitoa. Determinismi, eri julkaisuosoitteen vaikutus tarkisteeseen, täydellinen SRI-ketju ja julkaisutiedostojen/credentialien allowlist tarkistettiin. Offline-data-buildissa socket-yhteydet ja SQLAlchemy-enginen luonti estettiin.
- Varsinaisen sovelluksen koko 13 tiedoston API-/PostgreSQL-/migraatiosarja: **209 passed, 4 warnings in 357.73s (0:05:57)**. Erillinen catalog_test-kanta; oikeudet, CSRF, riippumaton hyväksyntä, muuttumattomat julkaisut, vanha/tyhjä kanta, toistuvat migraatiot ja nykyiset JSON-LD/RDF/SHACL-/attribuuttikokeet läpäisivät.
- Oikea Chromium + Keycloak normaalia uudelleenrakennettua Docker-sovellusta vasten: **13 passed, 1 warning in 113.07s (0:01:53)**. Tallennus/uudelleenavaaminen, hyväksyntä/julkaisu, oikeudet ja artefaktit säilyivät. **229 eri pytest-testiä** yhteensä. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia.
- Molemmat web-buildit (`build` ja `build:pages`) läpäisivät. Pagesin lopullinen aineisto ja assets eivät sisällä demotunnuksia tai localhost-palveluosoitteita. Normaali dist ja staattinen dist-pages ovat erilliset.
- Dokumentoitu `python -m scripts.preview_pages --port 4173` ajettiin: HTML ja demo/catalog.json palauttivat HTTP 200:n ja neljä tuotetta renderöityi oikeassa selaimessa. Näkymä tarkastettiin myös kuvakaappauksesta. Tilapäinen preview pysäytettiin kokeen jälkeen. Julkista GitHub Pages -osoitetta ei testattu tai väitetä toimivaksi.
- Docker rakennettiin TLS-varmennukset säilyttävällä scripts/cloud-build.sh-reitillä ja käynnistettiin `docker compose up -d --no-build --wait` -komennolla. App/db/Keycloak healthy; viimeinen image **sha256:850c997f379d84a94bb0793851602373a249da79ea6ce36428160b34ecb07697**. Ennen uusia selaintestijulkaisuja **13 catalog-kannan metatietotaulua ja Alembic-head 0005_lifecycle säilyivät tarkalleen ennallaan restartissa**. Ei uutta migraatiota eikä live-kannan nollausta.
- Yhteensopivuuden HTTP-koe: **92 julkaisuversiota luettavissa**, **8 vanhan generaattorin pakettia / 78 artefaktia** alkuperäisinä tavuina ja SHA-arvoina. Versio-API:n pakettisisällöt vastasivat tallennettuja snapshotteja.
- GitHub Pages -workflow jäsennettiin YAMLina ja main/ei-PR-deployehto tarkistettiin. Varsinaista Actions-ajoa/deployta ei voitu tehdä PR-haarasta. `git diff --check` läpäisi. Uusin origin/main on edelleen 6b48536 ja sisältyy haaraan.
- Ensimmäisessä determinismikokeessa löytynyt checkedAt-aikaleima poistettiin uuden staattisen aineiston ajokohtaisista tiedoista; lopullinen seitsemän testin sarja läpäisi. Palvelimen raportteja tai vanhoja julkaisuja ei muutettu.


## Toimitus

Toteutuscommit **581b3db** on työnnetty haaraan `feat/github-pages-demo`. `gh pr create --base main --head feat/github-pages-demo --title ... --body-file docs/pull-request-pages-demo.md` yritettiin, mutta GitHub GraphQL API palautti **Forbidden**. **PR:ää ei saatu avattua automaattisesti.** Käyttäjä voi avata sen GitHubin tarjoamasta linkistä https://github.com/jgmikael/metatietovaranto/pull/new/feat/github-pages-demo ja liittää valmiin docs/pull-request-pages-demo.md-kuvauksen. Mainia ei yhdistetty eikä Pages-deployta tehty. Tämä toimitusmerkintä ei muuta testattua sovelluskoodia tai aineistoa.

## Ajamattomat / julkaisuun jäävät

Varsinainen GitHub Pages -deployment, julkisen tavoiteosoitteen ja CDN-otsakkeiden HTTP-koe, GitHub Actionsin etätulos, Windows Docker Desktop/PowerShell ja uuden Codespacen luonti/openBrowser/Private-portin ajonaikainen koe. Paikallinen staattinen alipolku ja nykyinen palvelinsovellus testattiin alla kuvatuilla ajoilla. Ei ulkoista myöntäjää, allekirjoitusta tai lompakkotestiä. GitHub Pages ei takaa .schema.json-tiedostolle application/schema+json-otsaketta; manifestissa mediatyyppi säilyy ja varsinaisen palvelimen otsakkeet säilyvät.

[Toteutus, aineisto, komennot ja käyttöönotto](docs/github-pages-demo.md). [Valmis PR-kuvaus yhdistämisen jälkeisine tehtävineen](docs/pull-request-pages-demo.md). Ei automaattista main-mergeä tai PR-haaran julkista deployta.

---

Alla on aiempien vaiheiden historia. PR #13 on nyt yhdistetty mainiin; sen vanhat PR-tilat eivät kuvaa tämän tehtävän haaraa.

# PR #13 — lähdevertailun päätös (19.10.2026)

Alkuperäisen asetuksen Relationship between documents -copy-paste on nyt arvioitu ja lukittu käyttäjätoimituksen käsin rakenteistettuna jäljennöksenä lähdeaineistoon. **PR #13:n EN-metatietoja ja teknisiä kuvauspaketteja koskeva lähdevertailu on päätetty ilmoitetuin rajauksin.** Ei havaittua tarvetta sovelluskoodin, attribuuttimallin tai relaatiomigraatioiden muutokseen. Main **9258fff** sisältyy työhaaraan; ei yhdistämistä.

- Oikaisu **32025R1569R(01)** on luettelossa kielimerkinnällä **PL**. Koko tekstiä ei saatu, eikä sen sisältöä tai PL-version vaatimustenmukaisuutta väitetä arvioiduksi. EN-lähde säilyy.
- **EU 2026/1735**: seitsemän luettelon 11.8.2026 muutosta kohdistuu 3(2):een, 4 artiklaan ja liitteisiin I/II/IV. Myöntäjän, revokaation ja ulkoisen tarkistuspalvelun vastuut säilyvät erillisinä. Katalogin withdrawn ei peru myönnettyjä todistuksia.
- **9(4) ja uusi 9(2a), 1.1.2027**: tulevat muutokset erotetaan nykyisestä konsolidoinnista. Koko sanamuoto jää tarkistettavaksi ennen autenttisen lähteen integraatiota; sitä ei päätellä pelkistä muutosotsikoista.
- EN-konsolidoinnin 11 artiklan mukaan 6–9 artikloja sovelletaan **19.8.2026** alkaen. Konsolidoinnin 11.8.2026 päivää ei käytetä kaikkien säännösten soveltamispäivänä.

Generaattori **1.1.1**, oma laajennus **1.0.0** ja IETF **draft-19** säilyvät. Lähdepinnit ja uuden paketin raportti tarkentuvat: yleinen luettelon puuttumishavainto korvataan tunnistetun PL-oikaisun ja tulevan 9 artiklan lukemattomien tekstien havainnoilla. Niitä ei esitetä luettuina tai tämän rajatun metatieto-PR:n yhdistämisesteinä. `status=partial`, `conformanceClaim=false`; ETSI:n draft-13-ero ja ulkoisen myöntäjän velvoitteet pysyvät raportissa. Vanhoja julkaisuja, hyväksyntöjä, profiilisnapshotteja tai raportteja ei kirjoiteta uudelleen. [Päätös, vastaavuudet ja lähderajat](docs/pr13-source-comparison.md).

Riippumaton EUR-Lex- ja EU Publications/Cellar-haku estyi edelleen 403:een. Ei kaikenkattavaa säädös-/kieliversio-/ETSI-vaatimustenmukaisuusarviota. PL-oikaisun ja koko tulevan muutossäädöksen sanamuotojen lukua ei väitetä tehdyksi. `currentAsOfReviewDate=null` säilyy yleisen ajantasaisuuden kohdalla; rajattu päätös on `reviewClosure`-osiossa.

## Tässä viimeistelyssä suoritetut tarkistukset

- Koko README/CI:n 13 tiedoston API-/PostgreSQL-/migraatiosarja: **209 passed, 4 warnings in 355.05s (0:05:55)**. Ei epäonnistuneita tai ohitettuja. Oikeudet/CSRF, hyväksynnän mitätöityminen, julkaisuimmutabiliteetti, JSON-LD/RDF/SHACL, attribuuttiannotaatiot, tarkisteketju sekä vanhan/tyhjän kannan ja toistuvien migraatioiden kokeet mukana. Testit käyttivät vain erillistä catalog_test-kantaa.
- Oikea Chromium + Keycloak uudelleen rakennettua ja käynnistettyä Docker-sovellusta vasten: **13 passed, 1 warning in 115.88s (0:01:55)**. Tallennus/uudelleenavaaminen, organisaatiorajat, riippumaton hyväksyntä, julkaisu ja julkiset artefaktit läpäisivät. **222 eri pytest-testiä** yhteensä; varoitukset ovat Starlette/httpx- ja RDFLib-deprekaatioita.
- Uuden lähderegressiotestin lopullinen kohdennettu ajo: **1 passed, 1 warning in 0.21s**. Tarkistaa luettelon tarkisteen, alkuperän, PL-rajauksen, seitsemän nykyistä ja kaksi tulevaa muutosriviä, 19.8.2026 soveltamispäivän sekä niiden päätymisen generoituun raporttiin. Sama testitapaus kuuluu 209 testiin, eikä sitä lasketa lisätestiksi kokonaismäärään.
- `npm run build --prefix apps/web`: läpäisi (Vite 1,59 s). `bash scripts/cloud-build.sh` läpäisi TLS-varmennuksen säilyttäen; viimeinen image **sha256:6c7b957f54486509745c2369ffed1a0b923eb01689dcc41241665047ffa80177**. `docker compose up -d --no-build --wait`: app, db ja Keycloak healthy. Käynnissä olevan sovelluksen sources.json- ja muutosluettelotiedoston SHA:t vastaavat checkoutia.
- Ennen selaintestien uusia synteettisiä julkaisuja **13 catalog-kannan metatietotaulun kaikki rivit ja Alembic-head 0005_lifecycle säilyivät tarkalleen ennallaan uudelleenkäynnistyksessä**. Ei uutta relaatiomigraatiota tai fixtureiden palautusta; live-kantaa ei tyhjennetty.
- Julkinen HTTP-yhteensopivuuskoe selaintestien jälkeen: **88 julkaisuversiota luettavissa**, **8 vanhan generaattorin pakettia / 78 artefaktia** alkuperäisillä tavuilla ja SHA-arvoilla. Versioiden technicalPackage-sisällöt vastasivat tallennettuja muuttumattomia sisältöjä.
- Uuden paketin toimintakoe: kaikki **12 julkaistua artefaktia** palautuivat oikeilla mediatyypeillä ja tarkisteilla. Julkinen catalogue-coverage.json sisälsi täsmälleen uudet lähdepinnit ja rajatun päätöksen. Oikea `examples/semantic_consumer.py` palautti companyName-väitteen alkuperäisen ominaisuus-IRI:n, PropertyShapen ja lähdesnapshotin ilman väitearvoja tai JWT:n kryptografista tarkistusta.
- Main **9258fff** sisältyy työhaaraan; PR #13:n GitHub-mergeviitteen ensimmäinen vanhempi oli sama main, joten base on teknisesti vahvistettu. `git diff --check` läpäisi. Ei automaattista yhdistämistä.


## Ajamattomat tai rajauksen ulkopuolella

Riippumaton EUR-Lex-verkkovertaus, PL-oikaisun ja tulevan 9 artiklan koko tekstit eivät olleet saatavilla (403). Windows Docker Desktopia, uuden Codespacen luontia/openBrowseria/Private-portin ajonaikaista tilaa, tuotanto-HTTPS:ää ja GitHub Actionsin etätulosta ei varmistettu. Tavallista docker compose up --build -reittiä ei ajettu tässä täydennyksessä; pilvirakennus ja Compose-käynnistys ajettiin yllä kuvatuilla komennoilla. Ei myöntämistä, allekirjoitusta, lompakkotestiä tai täydellistä ETSI-/EU-vaatimustenmukaisuusarviota.

## Toimitus ja käyttäjän seuraava askel

Lähdevertailun viimeistelycommit **bc85164** on työnnetty PR #13:n nykyiseen haaraan. `gh pr edit 13 --body-file docs/pull-request-attribute-semantics.md` palautti myös viimeistelyn jälkeen **Forbidden**, joten GitHubin ylin kuvaus ei päivittynyt automaattisesti. Tämä toimitusmerkintä on erillinen dokumentaatiotäydennys; sovellusta tai lähdepinnejä ei muuteta sen vuoksi. Muutokset ovat olemassa olevassa PR #13:ssa. Uutta PR:ää tai base-vaihtoa ei tarvita. GitHubin API on palauttanut Forbidden; valmis PR-kuvaus on `docs/pull-request-attribute-semantics.md`, eikä kuvauskentän päivitystä väitetä onnistuneeksi. GitHub Actionsin lopullinen etätulos on tarkistettava käyttöliittymässä. Yhdistäminen jää käyttäjälle, kun rajaus on arvioitu ja GitHubin tarkistukset ovat vihreät. Main-haaraa ei muuteta.

---

Alla on tarkistushistoria ennen viimeisen copy-paste-aineiston saamista. Sen avoin asiakirjasivu-/oikaisuluettelopyyntö on korvattu yllä olevalla rajatulla päätöksellä.

# PR #13 — asiakirjatietoliitteen tarkistus (19.10.2026)

Käyttäjän `Document Information.pdf` on vastaanotettu, luettu paikallisella OCR:llä ja sen tietosivu tarkastettu kuvana. Alkuperäinen kopio, koko ja SHA-256 on lukittu lähdeaineistoon. Aikajanassa viimeisin esitetty konsolidointi on **11.8.2026**, ja muutosviite **EU 2026/1735** vastaa aiempaa tekstikopiota.

Liite näyttää **konsolidoidun tekstin** tiedot (02025R1569-20260811). Relationship between documents sisältää vain linkin alkuperäiseen asetukseen 32025R1569; sen muutos-/oikaisurekisteri ei ole esillä. Nyt vahvistettu viimeisin näytetty versio erotetaan todentamattomasta oikaisujen puuttumisesta. Generoidun raportin havainto tarkentuu `EU_CORRIGENDUM_STATUS_UNVERIFIED`-koodiksi. ETSI draft-13/draft-19 -ero ja ulkoisen myöntäjän vastuut säilyvät. [Täsmälliset havainnot ja jäljellä oleva tarkistus](docs/pr13-source-comparison.md).

**Jäljellä ennen lopullista yhdistämissuositusta:** alkuperäisen asetuksen asiakirjatietosivun muutos-/oikaisusuhteet. Avaus liitteen sivun 1 **Access initial legal act** -linkistä tai suoraan CELEX:32025R1569-sivulta. Ei tarvetta toimittaa samoja ETSI-/konsolidointitekstejä uudelleen.

## Asiakirjatietoliitteen täydennyksen tarkistukset 19.10.2026

- `pytest tests/test_technical_packages.py tests/test_attribute_semantics.py -q`: **61 passed, 1 warning in 55.00s**. Ei epäonnistuneita tai ohitettuja. Mukana oikea paikallinen JSON-LD/RDF/SHACL, attribuuttien yhdenmukaisuus, pakettien tarkisteketju sekä uusi asiakirjatietokopion pinnaus ja generoituun raporttiin päätyvä täsmällinen näyttöraja. Varoitus koskee Starlette/httpx-deprekaatiota.
- `git fetch origin main`: main on edelleen **9258fff** ja sisältyy työhaaraan. Työhaara vastasi etähaaraa ennen tätä lisäystä; ei muiden muutosten ylikirjoitusta. `git diff --check` läpäisi.
- Tämä täydennys muuttaa lähdepinnit, raportin syötteet, testit ja dokumentaation. Sovelluskoodia, käyttöliittymää, tietokantaskeemaa tai käynnistysasetuksia ei muutettu. Ei uutta migraatiota. Muuttumattomia julkaisuja tai demokantaa ei päivitetty.
- Koko API-/migraatiosarjaa, selaintestejä, web-buildia, Docker-buildia tai toimintakokeilua ei toistettu tässä liitetäydennyksessä. Alla oleva **207 API-/migraatiotestin ja 13 selaintestin** läpäisy sekä build-/säilymiskokeet ovat edellisen toteutusmuutoksen tuloksia, eivät uusia ajoja. Uusi 61 testin ajo menee osittain niiden kanssa päällekkäin, joten lukuja ei lasketa yhteen.
- Avoin sisältötarkistus: alkuperäisen asetuksen muutos-/oikaisusuhteet ja mahdolliset niistä löytyvät uudet tekstit. GitHub API palauttaa edelleen **Forbidden**; PR:n kuvaus ja etätarkistusten tila eivät päivity tai varmistu tämän ympäristön kautta. Kuvausteksti on repositoriossa `docs/pull-request-attribute-semantics.md`. Ei automaattista yhdistämistä.

---

Alla on edellisen sisältövertailun tarkistushistoria. Sen asiakirjatietosivun puuttumista koskeva yleinen tila on tarkentunut yllä.

# PR #13 — toimitettujen alkutekstien vertailu (18.10.2026)

Käyttäjältä saatu kolme pyydettyä PDF:ää: ETSI TS 119 472-1 V1.2.1 (2026-02), ETSI TS 119 478 V1.1.1 (2026-01) ja EU 2025/1569:n konsolidointi 11.8.2026 / 001.001. Etusivut, yksilöidyt kohdat/artiklat ja EU-tekstin muutosmerkit luettu paikallisesti. Alkuperäiset kopiot ja SHA-256:t lukittu fixtures/catalog-standards/originals/ ja sources.json. Ei väitettä riippumattomasta verkkovertauksesta tai koko ETSI-/EU-vaatimustenmukaisuudesta. [Uusi lähdevertailu ja kohdan 4 asiakirjatietosivun ohje](docs/pr13-source-comparison.md).

Generaattori 1.1.1 korjaa puuteraportin: luettuja tekstejä ei enää merkitä kokonaan puuttuviksi. Raportti erottaa vielä avoimen EU-muutosten ajantasaisuuden, ETSI:n SD-JWT draft-13 -viitteen ja sovelluksen draft-19:n eron sekä ulkoisen myöntäjän vct-löydettävyyden/integrityn ja profiilin todentamisen. ETSI 478:n attributeIdentifier/semanticDataSpecification/schemaDistribution-vaatimukset sekä EU art.7/8:n tietovaatimukset ja ulkoiset vastuut on lisätty koneelliseen peitto-/puuteraporttiin. IETF-profiilia tai semanttista laajennusta ei vaihdeta automaattisesti; suojaus/myöntäminen jää ulkoiselle palvelulle. Vanhoja muuttumattomia julkaisuja tai snapshotteja ei kirjoiteta uudelleen.

**Jäljellä:** konsolidoinnin etusivu luettelee EU 2026/1735:n, mutta mahdolliset 11.8.2026 jälkeiset muutokset/oikaisut ja uusin versio pitää vielä varmistaa EUR-Lexin Document information / Asiakirjan tiedot -sivulta. Artiklat 7/8 ovat annetussa tekstissä B-merkittyjä. Myöhemmässä integraatiossa on huomioitava M1:n liite IV:n mukautukset ETSI 119 478:aan. Ei vielä lopullista yhdistämissuositusta.

## Todella ajettu korjatulle toteutukselle

- Mainin 9258fff sisältävän korjatun toteutuksen koko 13 tiedoston API-/PostgreSQL-/migraatiosarja: **207 passed, 4 warnings in 357.80s (0:05:57)**. Ei epäonnistuneita tai ohitettuja. Mukana aiemmat 205 testiä sekä kaksi uutta lähdekopioiden pinnaus-/tarkiste- ja puuteraporttitestiä.
- Kohdennettu paketti-/attribuuttisarja: **60 passed, 1 warning in 51.17s**; nämä sisältyvät täyteen 207 testin ajoon.
- Oikea Chromium + Keycloak, korjattua Docker-sovellusta vasten: **13 passed, 1 warning in 116.18s (0:01:56)**. Tallennus/uudelleenavaaminen, eri käyttäjän hyväksyntä, julkaisu, julkiset artefaktit ja semantiikan lukija säilyivät.
- **220 eri pytest-testiä** yhteensä. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia.
- Web-build läpäisi. Docker-image rakennettiin varmennukset säilyttävällä scripts/cloud-build.sh-reitillä; `docker compose up -d --no-build --wait` käynnisti app/db/Keycloakin healthy-tilaan. Tavallista `docker compose up --build` -reittiä tai Windows Docker Desktopia ei ajettu tässä täydennyksessä.
- **13 oikean catalog-kannan metatietotaulua säilyi tarkalleen ennallaan uudelleenkäynnistyksen yli** ennen uusia synteettisiä selainjulkaisuja. Ei uutta relaatiomigraatiota; aiemmat migraatiot tarkistettiin erillisessä catalog_test-kannassa. Demokantaa ei tyhjennetty.
- Julkinen HTTP-yhteensopivuuskoe: **83 julkaisuversiota luettavissa**, **8 vanhan generaattorin pakettia / 78 artefaktia** tavuntarkasti alkuperäisillä SHA-arvoilla. Uusi lähdetarkistus ei kirjoittanut vanhojen julkaisujen raportteja uudelleen.
- `git diff --check` läpäisi. PR #13:n GitHub-mergeviite vahvisti basen mainiksi 9258fff; käyttäjä vahvisti saman. Main-haaraa ei muutettu eikä PR:ää yhdistetty.
- Ajamattomat: asiakirjatietosivun jälkeiset mahdolliset lisäsäädösten tarkistukset, Windows, uuden Codespacen luonti/Private-portin ajonaikainen tila, tuotanto-HTTPS ja GitHub Actionsin etätulos. Ei allekirjoittamista, lompakkoa, EU-katalogirekisteröintiä tai koko ETSI-profiilin vaatimustenmukaisuusarviota.


## PR ja toimitus

Main 9258fff sisältyy työhaaraan. Käyttäjä vahvisti PR #13:n baseksi mainin; GitHubin refs/pull/13/merge-viitteen ensimmäinen vanhempi 9258fff varmisti tämän myös teknisesti. Basea ei tarvitse vaihtaa uudelleen. Sovelluksen UI tai relaatiomigraatiot eivät muutu; generaattorin lähdepinnit ja puuteraportti muuttuvat, joten Docker-image rakennettiin ja käynnistettiin uudelleen. Normaalin restartin tiedonsäilyminen tarkistettiin ennen uusia synteettisiä selaintestijulkaisuja.

Toteutuscommit **e79b453** (generaattori 1.1.1) on työnnetty PR #13:n nykyiseen haaraan. `gh pr edit 13 --body-file docs/pull-request-attribute-semantics.md` yritti päivittää kuvauksen mutta estyi **Forbidden**-vastaukseen: GitHubin kuvauskenttä ei siis päivittynyt automaattisesti. Ajantasainen valmis kuvausteksti on repositoriossa, ja haara-/tiedostomuutokset näkyvät olemassa olevassa PR:ssä. PR #13:n base on main, joten sitä ei tarvitse vaihtaa uudelleen. Main 9258fff säilyi ennallaan, yhdistämistä ei tehty. PR jää avoimeksi asiakirjatietosivun loppuvarmistusta varten.

---

Alla ovat aiempien tarkistusyritysten historiatiedot. Niiden kaikkien kolmen alkutekstin puuttumista ja vanhaa PR-basea koskevat tilat on korvattu yllä olevilla havainnoilla.

# PR #13 — main-pohjan tarkistus ja estynyt normatiivinen vertailu (18.10.2026)

PR #12 on yhdistetty mainiin `9258fffb4633c90240eddba1c09b6b135c3fb057`. Main on tuotu PR #13:n työhaaraan `feat/phase-2h-attribute-semantics` merge-commitissa `339824ece0127f13cc17494efc13ef7d0c030ba0`. Main-haaraa ei muutettu eikä PR #13:a yhdistetty. Main-pohjan päivitys ei muuttanut sovelluskoodia. Päivitettiin tarkistuksen loki, dokumentaatio ja vanhat pohjahaara-/export-tilaviittaukset.

**Normatiivinen tarkistus ei ole valmis:** molempien ETSI-PDF:ien ja EU 2025/1569:n alkuperäistekstin noudot palauttivat edelleen HTTP 403:n. Myös viralliset EU:n CELEX- ja data.europa.eu-vaihtoehdot palauttivat 403:n. Alkutekstien tarkisteita, voimassa olevia muutoksia tai vaatimustenmukaisuutta ei väitetä tarkistetuiksi. TS11:n 1.0.1 kolme lähdetiedostoa verrattiin uudelleen virallisen Git-commitin täsmällisiin tavuihin/lukittuihin SHA-arvoihin; upstream HEAD `ee91a294c833af5188726fd8c302c641212192aa` on ennallaan. TS11:n V0.0.7-luonnosviite ei korvaa ETSI V1.1.1:tä.

[Tarkistusyrityksen täsmällinen raportti ja tarvittavat lähdetiedostot](docs/pr13-normative-review.md); koneellinen loki fixtures/catalog-standards/review-attempt-2026-10-18.json. Alkuperäisiä sources.json-lukkoja tai generaattorin syötteitä ei muutettu, vanhoja paketteja ei generoitu uudelleen. Ilman alkutekstejä ei tehty arvauksiin perustuvia sovelluskoodin muutoksia.

## Tässä main-päivityksessä todella ajettu

- Koko README/CI:n 13 tiedoston API-/PostgreSQL-/migraatiosarja: **205 passed, 4 warnings in 344.76s (0:05:44)**. Ei epäonnistuneita tai ohitettuja. Mukana oikeudet/CSRF, hyväksynnän mitätöinti, muuttumattomat julkaisut, tyhjä/vanha kanta ja toistuvat migraatiot, todellinen JSON-LD/RDF/SHACL, uusi WE BUILD -aineistokoe, attribuuttiannotaatiot sekä tarkisteketju.
- Oikea Chromium + Keycloak -selainajo käynnistettyä demoa vasten: **13 passed, 1 warning in 114.18s (0:01:54)**. Mukana tallennus/uudelleenavaaminen, riippumaton hyväksyntä/julkaisu, julkiset artefaktit ja semantiikan lukija. Vain erillinen API-sarja käyttää tyhjennettävää catalog_test-kantaa; live-katalogia ei nollattu.
- Yhteensä **218 eri pytest-testiä**. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia.
- `npm run build --prefix apps/web`: läpäisi (Vite 1,13 s). Käynnissä olevan Docker-sovelluksen **20 API-/lukijalähdetiedoston** SHA-256:t vastaavat checkoutia, ja **3 web-build-tiedoston** SHA-256:t vastaavat tuoretta paikallista buildia. Selainajo testasi näin nykyisiä sovellustavuja, ei aiempaa erilaista versiota.
- `git merge-base --is-ancestor origin/main HEAD`: läpäisi mainin 9258fff sisältävällä työhaaralla. `git diff --check` ja tarkistuslokin JSON-jäsennys läpäisivät.
- Ei uutta tietokantamigraatiota tai sovelluskoodimuutosta. Docker-imagea/compose-käynnistystä ei rakennettu uudelleen tässä dokumentaatio-/pohjapäivityksessä; päällä olevien palveluiden vastaavuus varmistettiin yllä. Windows Docker Desktopia, uuden Codespacen luontia/Private-portin tilaa, tuotanto-HTTPS:ää tai GitHub Actionsin etätulosta ei ajettu tässä ympäristössä.
- **Ajamattomat sisältötarkistukset:** pyydettyjen ETSI-alkutekstien kohta-/kenttävertailu, EU-asetuksen ajantasaisen konsolidoidun tekstin ja myöhempien muutosten/oikaisujen vertailu sekä niiden perusteella mahdollisesti tarvittavat koodikorjaukset. Näitä ei korvaa yllä oleva tekninen läpäisy.


## Jäljellä ja toimitus

- ETSI TS 119 472-1 V1.2.1 ja TS 119 478 V1.1.1 -PDF:t, EU 2025/1569:n ajantasainen konsolidoitu teksti tai alkuperäinen ja muutossäädökset sekä EUR-Lexin muutos-/oikaisutiedot tarvitaan sisältövertailun jatkamiseen. Ei vielä yhdistämissuositusta.
- GitHubin refs/pull/13/merge-viitteen base-vanhempi oli 8bc37dc (vanha 2H-haara). Base-vaihto mainiksi yritettiin REST PATCH /pulls/13 -pyynnöllä; **Forbidden**. Käyttöliittymässä on varmistettava **PR #13 → Edit → base: main**. Paikallinen main-pohja ja PR:n kohdehaara eivät ole sama asetus.
- Main-integrointi **339824e** ja tarkistusraportti **b9f2d68** on työnnetty nykyiseen PR #13:n haaraan. REST PATCH /pulls/13 -pyynnöllä yritettiin päivittää sekä `base: main` että valmis kuvausteksti: **Forbidden**. GitHubin base- tai kuvauskenttää ei siis ole päivitetty tämän työympäristön kautta; base pitää tarkistaa/vaihtaa ja ajantasainen docs/pull-request-attribute-semantics.md kopioida haluttaessa kuvauskenttään käsin. Koodi-/dokumentaatiomuutokset näkyvät olemassa olevassa PR:ssä. Main-haara säilyi commitissa 9258fff. Normatiivinen lähdevertailu odottaa yllä lueteltuja tiedostoja, eikä PR:ää yhdistetty.

---

Alla ovat aiempien vaiheiden ja tarkistusten historiatiedot. Niiden vanhat main-/PR-pohjat ja puuttuvan exportin tilat eivät korvaa yllä olevaa nykytilaa.

# 2H:n aineistokokeen täydennys — WE BUILD 0.0.2 (18.10.2026)

Käyttäjä toimitti alkuperäisen Turtle-exportin, profiilin <https://iri.suomi.fi/model/webcor/> ja version 0.0.2. Tiedosto on lukittu muuttamattomana `fixtures/tietomallit/webcor-0.0.2/original.ttl`: **29 811 tavua**, **429 kolmikkoa**, SHA-256 **2ad4331272558bb541b7804f194a74e261d8313985554015ccc4e23785286133**. Tiedoston profiili-/versiotiedot täsmäävät ilmoitukseen. Alkuperä on käyttäjän ilmoittama alustalta ladattu tiedosto; riippumatonta verkkovertausta ei väitetä tehdyksi (403). Provenienssi, raportti ja erillisen testiprojektion muutosluettelo/tarkiste tallennettu.

Koko profiili **ei ole generaattorin tukema valmis paketti**: 24 literaaliominaisuudelta puuttuu sh:datatype ja SKOS owl:imports on unresolved. Viisi juurta tuottavat hallitun eston; API säilyttää alkuperäiset tavut/luonnoksen ja estää tarkastukseen lähettämisen. Tietotyyppejä, kardinaliteetteja tai OWL-riippuvuuksia ei päätellä tai haeta verkosta.

Erillinen paikallinen synteettinen Person/familyName-projektio lisää xsd:stringin eksplisiittisenä testioletuksena, ei alkuperäisen profiilin määrityksenä. Sillä on eri profiili-identiteetti/testiversio; minCountia/maxCountia ei keksitä. Oikea PyLD + lukittu lataaja tuottaa käsin kirjoitetun odotteen kanssa isomorfisen RDF-graafin. Se tarkistetaan projektion sekä alkuperäisen SHACLin kanssa offline yhdellä Person-fokussolmulla; puuttuvia ulkoisia riippuvuuksia tai puuttuvia tyyppirajoitteita ei väitetä tarkistetuiksi. [Täsmällinen koeraportti](docs/webcor-acceptance.md).

## Todella ajettu tässä täydennyksessä

- Kohdennettu realistisen aineiston koe: **8 passed, 34 deselected, 1 warning in 5.45s**. Rajatut vanhat testit kuuluvat täyteen ajoon.
- Perus-2H:n koko README/CI:n 12 tiedoston API-/PostgreSQL-/migraatiosarja: **189 passed, 4 warnings in 318.14s (0:05:18)**. Ei epäonnistuneita tai ohitettuja. Sisältää kaikki aiemmat 181 testiä ja 8 uutta aineistotapausta; oikeudet, hyväksyntä, muuttumattomat julkaisut ja vanhan/tyhjän kannan migraatiot säilyivät. Kohdennettu ajo ei ole lisätestimäärä tämän päälle.
- Ensimmäisessä kohdennetussa ajossa testin oletus claims-listan järjestyksestä korjattiin: molempien standardipolkujen sisältyminen tarkistetaan järjestyksestä riippumatta. Lopullinen rajattu koe läpäisee.
- Sovelluskoodia, skeemaa, UI:ta tai käynnistysasetuksia ei muutettu. Web-buildia, Docker-imagea, selaintestejä tai demokannan restartia ei ajettu uudelleen tässä testi-/dokumentaatiotäydennyksessä. Aiemmat tulokset ovat alla historiassa; niitä ei lasketa uusiksi ajoiksi. catalog-kantaa ei tyhjennetty, API-testit käyttävät catalog_test-kantaa.
- Windowsin, uuden Codespacen ja GitHub Actionsin etätulosta ei varmistettu tässä ympäristössä. Ei allekirjoittamista tai lompakkotestausta.

## Yhteensopivuus jatkohaaraan

Perus-2H:n commit 8bc37dc tuotu attribuuttisemantiikan haaraan (PR #13). Myös paikallisen testiprojektion annotaatioissa ominaisuus-IRI erotetaan PropertyShapesta ja profiiliviite säilyy paikallisen testin viitteenä; sitä ei nimetä alkuperäiseksi webcor 0.0.2:ksi. Jatkohaaran paketti-/attribuuttisemantiikan sarja: **58 passed, 1 warning in 50.08s**. Ei epäonnistuneita tai ohitettuja. Mukana kaikki 42 pakettitestiä (myös 8 uutta aidon aineiston tapausta) sekä 16 attribuuttisemantiikan testiä; uusi testi varmistaa paikallisen projektion lähde-identiteetin ja alkuperäisen ominaisuus-/PropertyShape-IRI:n eron. Tämä ei ole uusi täysi API-/migraatioajo tässä jatkohaarassa, eikä päällekkäisiä testejä lasketa uutena kokonaismääränä.

## PR-tilanne

GitHubin git-viitteistä tarkistettiin käyttäjän avaamat **PR #12** (perus-2H) ja **PR #13** (attribuuttisemantiikka). Tämä koe täydentää PR #12:n aiemmin avoimen aineistovaatimuksen toimeksiannon sallimalla tavalla: koko aineiston raja raportoidaan ja erillinen rajattu tapaus testataan. Se ei väitä koko WE BUILD 0.0.2:n generointia tuetuksi. PR #12:n vaadittujen GitHub-tarkistusten ja katselmoinnin on edelleen läpäistävä. PR #13:n ETSI-/EU-alkutekstitarkistus jää avoimeksi.

Toteutuscommit **9420d05** on työnnetty haaraan `feat/phase-2h-technical-packages`; olemassa oleva [PR #12](https://github.com/jgmikael/metatietovaranto/pull/12) saa nämä muutokset automaattisesti. PR:n kuvausta yritettiin päivittää sekä `gh pr edit 12 --body-file docs/pull-request.md` -komennolla (GraphQL) että REST PATCH /pulls/12 -pyynnöllä: molemmat estyivät **Forbidden**-vastaukseen. **Kuvaustekstiä ei ole päivitetty GitHubissa**: kopioi ajantasainen docs/pull-request.md olemassa olevan PR:n ensimmäisen kuvauksen Edit-kenttään. Main-haaraa ei muutettu. Pohjamuutos on yhdistetty ja työnnetty myös jatkohaaraan/PR #13 commitissa **96454b9**, ja sen 58 kohdennettua testiä läpäisivät. PR #13:n kuvausta yritettiin päivittää `gh pr edit 13 --body-file docs/pull-request-attribute-semantics.md` -komennolla: **Forbidden**. Myös sen ajantasainen kuvaus pitää kopioida tiedostosta PR:n kuvauskenttään käsin. Aineistokoe ei sulje jatkon normatiivisten alkutekstien tarkistuspuutetta.

---

Seuraavat ovat aiempien 2H-toimitusten historiatietoja ennen yllä olevaa aineistotäydennystä. Niiden aiempi puuttuvan exportin tila on korvattu yllä olevalla tuloksella. Jatko-PR:n ETSI-/EU-alkutekstitarkistus säilyy avoimena.

# Vaiheen 2H jatko — attribuuttien semanttiset viittaukset (18.10.2026)

Erillinen työhaara `feat/phase-2h-attribute-semantics`, pohja `feat/phase-2h-technical-packages` (`ace80e3`). Uudelleen tarkistettu origin/main on `ac002ad` (2G); 2H ei vielä sisälly päähaaraan. Tämä jatko on tarkastettava erillisenä PR:nä 2H-haaraa vasten ja siirrettävä main-pohjaiseksi vasta pohjan yhdistämisen jälkeen. Aiemman tehtävän historiatiedot ovat alempana.

Toteutus: generaattori 1.1.0 johtaa lähde-SHACLista yhteiset attribuuttiviittaukset mappingiin, JSON Scheman x-term/x-mtv-shacl-kenttiin ja SD-JWT VC draft-19 Type Metadatan x-mtv-semantic-kenttiin. Viite erottaa alkuperäisen ominaisuus-IRI:n PropertyShapesta, säilyttää koko sisäkkäisen käyttöyhteyden sekä lähdeprofiilin version/snapshotin tarkisteen. Nimettömälle lähdesolmulle ei keksitä URI:a. IETF-väitepolut käyttävät taulukoille null-askelia. Oma versioitu laajennusprofiili määrittelee annotaatiot ja schema-/mapping-löydettävyyden.

Paketissa on 12 julkista muuttumatonta artefaktia. SRI-tarkisteketju sitoo laajennusprofiilin, mappingin, skeeman ja Type Metadatan; issuer-metadata-binding.json ohjeistaa ulkoisen myöntäjän vct/vct#integrity-käytön. Esimerkkikuluttaja hakee yhden väitepolun semantiikan ilman väitearvoja tai JSON Schemaa. Se ei ole SD-JWT-/allekirjoitusverifioija. Valinnaiset attribuutti- ja järjestelykatalogiviitteet säilyttävät vastaavuusväitteen alkuperän ja kulkevat normaalissa hyväksynnässä. Vanhan asiakkaan puuttuva uusi kenttä ei poista jo tallennettuja viitteitä. Ei uutta relaatiomigraatiota, allekirjoittamista, katalogirekisteröintiä tai lompakkointegraatiota.

Sopimus, vastaavuustaulukko, lähdeversiot ja kokeiluohje: [docs/attribute-semantics.md](docs/attribute-semantics.md).

## Tässä jatkotehtävässä todella ajettu

- Koko README/CI:n 13 tiedoston API-/PostgreSQL-/migraatiosarja: **196 passed, 4 warnings in 317.51s (0:05:17)**. Ei epäonnistuneita tai ohitettuja. Mukana vanhojen kantojen päivitykset, tyhjä kanta/toistuvat migraatiot, käyttöoikeudet, hyväksynnän mitätöinti, muuttumattomat julkaisut, oikea PyLD + lukittu lataaja + RDF-graafivertailu + lähde-SHACL, sisäkkäiset taulukot/roolit, nimetön PropertyShape, ulkoinen nimiavaruus, ristiriitaisten annotaatioiden hylkäys ja SRI-ketjun muutosten havaitseminen.
- Kohdennettu paketti-/attribuuttisemantiikan ajo: **49 passed** (sisältyy edellä olevaan 196 testiin). Näistä 15 on uuden jatkon testejä.
- Oikea Chromium ja Keycloak, lopullista Docker-imagea vasten: **13 passed, 1 warning in 106.27s (0:01:46)**. Aiempien polkujen lisäksi katalogiviitteen syöttö → tallennus → uudelleenavaaminen → paketin generointi → toisen käyttäjän hyväksyntä/julkaisu → julkisten kuvausten tarkisteketju ja yhden claimin semantiikka. Ensimmäinen selainajo löysi uuden JSON-kentän nimilappuongelman; eksplisiittinen label/id-yhteys korjattiin ja koko selainajo uusittiin onnistuneesti.
- **209 eri pytest-testiä**, ei ohituksia. Deprekaatiovaroitukset ovat Starlette/httpx- ja RDFLib-varoituksia.
- `npm run build --prefix apps/web` läpäisi (TypeScript/Vite). Docker-image rakennettiin varmennukset säilyttävällä `scripts/cloud-build.sh`-reitillä ja käynnistettiin `docker compose up -d --no-build --wait`: app/db/Keycloak healthy. Tavallista `docker compose up --build` -rakennusreittiä ei ajettu uudelleen tässä jatkossa; pilviympäristön aiemmin todettu build-DNS-rajaus edellytti proxy-/CA-asetukset säilyttävää apureittiä.
- Olemassa olevan catalog-kannan uudelleenkäynnistys: **13 metatietotaulun kaikki rivit täsmälleen ennallaan**, mukana 71 tuotetta, 71 luonnosta, 36 profiilisnapshotia ja 64 julkaisua ennen selaintestien uusia synteettisiä julkaisuja. `alembic current`: **0005_lifecycle (head)**. Ei uutta skeemamigraatiota; toimitetut revisiot ennallaan. Tyhjentävät API-testit käyttivät vain erillistä catalog_test-kantaa.
- Julkisten vanhojen tietojen erillinen HTTP-toimintakoe: **73 julkaisuversiota luettavissa**, mukaan lukien kaikki testien jättämät historiat. **6 vanhan 1.0.0-generaattorin pakettia / 54 artefaktia** haettiin ja alkuperäiset tavut/tarkisteet säilyivät.
- Dockerissa ajettu `examples/semantic_consumer.py` luki oikean julkisen Type Metadatan ja palautti `["companyName"]`-polulle alkuperäisen ominaisuus-IRI:n, NameShape-kytkennän ja lähdesnapshotin/version/SHA:n. Kaikki **12 uuden paketin artefaktia** haettiin julkisista HTTP-reiteistä ja niiden tavut, mediatyypit ja SHA:t tarkistettiin. Tämä on kuvausten toimintakoe, ei SD-JWT:n kryptografinen verifiointi.
- `git diff --check` läpäisi. `.devcontainer`/Private-portin määrityksiä, Composea tai Alembic-revisioita ei muutettu.


## Avoimet / ajamattomat tarkistukset

Virallinen TS11 1.0.1 (2026-01-30), commit `ee91a294c833af5188726fd8c302c641212192aa`, ja sen kaksi JSON-tietomallia on tallennettu muuttamattomina SHA-256-tarkisteineen. TS11 viittaa itse 119 478:n V0.0.7-luonnokseen: sitä ei esitetä pyydetyn V1.1.1:n vahvistuksena.

Pyydettyjen ETSI TS 119 472-1 V1.2.1- ja TS 119 478 V1.1.1 -alkutekstien sekä EU 2025/1569:n artiklojen 7/8 ajantasaisen tekstin ja myöhempien muutosten varmistaminen estyi **HTTP 403** -verkkovastaukseen. Vastaavuustaulukko ja koneellinen catalogue-coverage.json erottavat vahvistamattomat kohdat. Ajantasaista oikeudellista tai ETSI-/EU-vaatimustenmukaisuusväitettä ei tehdä. Myös pohja-2H:n aito muuttamaton Tietomallit-exportin hyväksymiskoe säilyy avoimena. Näiden vuoksi toimitus on tarkastettava luonnos; en suosittele yhdistämistä ennen lähdetarkistusten täydentämistä.

Windows Docker Desktopia, uuden Codespacen todellista luontia/selainavausta/Private-porttia, julkista tuotanto-HTTPS-palvelua ja GitHub Actionsin etäajoa ei ajettu. Compose, `.devcontainer` ja aiemmat Alembic-revisiot säilyvät ennallaan. Ei kuorma-/tietoturva-auditointia tai ulkoisen myöntäjän kryptografisia integraatiotestejä. Piilotettu väite osittaisessa esityksessä ei tarkoita puuttuvaa attribuuttia alkuperäisessä todistuksessa.

## Toimitus

Toteutuscommit **86f90ae** on työnnetty GitHubiin haaraan `feat/phase-2h-attribute-semantics`. Draft-PR:n avaaminen yritettiin sekä `gh pr create` -komennolla (GraphQL) että REST POST /repos/jgmikael/metatietovaranto/pulls -pyynnöllä. Molemmat estyivät **Forbidden**-vastaukseen. **PR:ää ei ole luotu.** Native git push onnistui; uusia tunnuksia tai kiertotapaa ei käytetty.

[Avaa erillinen draft-PR käsin](https://github.com/jgmikael/metatietovaranto/compare/feat/phase-2h-technical-packages...feat/phase-2h-attribute-semantics?expand=1), base `feat/phase-2h-technical-packages`, compare `feat/phase-2h-attribute-semantics`. Valmis kuvaus: [docs/pull-request-attribute-semantics.md](docs/pull-request-attribute-semantics.md). [Kokeile haaran Codespacessa](https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2h-attribute-semantics); käynnistyksen tarkat ohjeet ovat READMEssä. Main on edelleen `ac002ad`. Ei automaattista yhdistämistä.

---

# Vaihe 2H — SHACL-pohjaiset tekniset kuvauspaketit (17.10.2026)

Pohja main `ac002ad` (PR #11), työhaara `feat/phase-2h-technical-packages`. Toteutus ja täsmällinen rajaus: [docs/phase-2h.md](docs/phase-2h.md). Tämä tehtävä korvaa aiemman DCAT-AP-ehdotuksen vaiheelle 2H.

Toteutettu lukitusta SHACL-snapshotista yhteiset tarkastettavat esitysvalinnat/mappingit, JSON-LD 1.1 -konteksti, yhteinen JSON Schema, SD-JWT VC draft-19 Type Metadata, erilliset mappingit sekä synteettiset allekirjoittamattomat esimerkit. Paketti ja tarkisteet kulkevat luonnoksen, riippumattoman hyväksynnän ja muuttumattoman julkaisun mukana. Muutos mitätöi hyväksynnän; keskeneräinen/vanhentunut paketti ei kelpaa julkaistavaksi. Julkiset artefaktit ovat sisältöosoitteisia ja saatavilla myös withdrawn-julkaisuille. Vanhoihin julkaisuihin/profiileihin/fixtureihin ei luotu paketteja taustalla. Useat sanastoviitteet ja riippuvuusaineistot lisättiin tuontikäyttöliittymään. Ei uutta relaatiomigraatiota tai ulkoisia myöntäjäintegraatioita.

## Lopullisesta toteutuksesta todella ajettu

- Koko API-/PostgreSQL-/migraatiosarja (README/CI:n 12 tiedostoa): **181 passed, 4 warnings in 298.49s (0:04:58)**. Ei epäonnistuneita tai ohitettuja. Mukana tyhjä/legacy-kanta, toistuvat migraatiot/startup, oikeudet, CSRF, ETag/idempotenssi, SHACL/johdannaiset, hyväksyntä, immutable-julkaisut ja elinkaari.
- Uuden pakettimoduulin erillinen korjauksen jälkeinen ajo: **34 passed**; nämä sisältyvät yllä olevan täyden ajon 181 testiin. Mukana determinismi, kymmenen literaalityyppiä, sisäkkäisyys/moniarvoisuus, varatut/törmäävät nimet, alkuperäiset IRI:t, useat sanastot/lukitut riippuvuudet, Type Metadata, luku-/kirjoitusoikeudet, nykyinen tarjoaja, hyväksynnän mitätöinti ja julkiset artefaktit.
- Oikea Chromium + Keycloak, lopullista Docker-toteutusta vasten: **13 passed, 1 warning in 99.15s (0:01:39)**. Mukana aiemmat 12 selainpolkua ja uusi 2H:n editori → mapping-ehdotus → generointi → tallennus/reload → eri käyttäjän hyväksyntä → julkaisu → artefakti sekä mapping-taulukon mobiilileveys.
- **194 eri pytest-testiä** yhteensä; erillistä 34 testin ajoa ei lasketa uudelleen. Starlette/httpx- ja RDFLib-varoitukset eivät ole ohituksia.
- `uv sync --locked`, `npm ci --prefix apps/web` ja `npm run build --prefix apps/web`: läpäisivät. PyLD 2.0.4 ja transitiiviset riippuvuudet lukittu uv.lockiin.
- `bash scripts/cloud-build.sh` ja `docker compose up -d --no-build --wait`: läpäisivät; TLS-tarkistuksia ei poistettu. Käynnissä olevan imagen **34 lähde-/migraatio-/web-build-/standardiaineisto-/lock-tiedoston** SHA:t vastasivat checkoutia.
- Myös `docker compose up --build -d --wait` todella yritettiin tässä tehtävässä: **epäonnistui build-kontin DNS-virheeseen** (`Temporary failure in name resolution`, pip/uv). Tätä ei ilmoiteta läpäisseeksi. Pilviskripti käyttää ympäristön olemassa olevaa proxy-/CA-reittiä; sama lähde rakentui sillä ja käynnistyi.
- Käytössä olevan `catalog`-kannan 13 metatietotaulun kokonaissisältötarkisteet säilyivät lopullisen imagen restartin yli (ennen viimeistä selainajoa): 66 tuotetta/luonnosta, 59 muuttumatonta julkaisua, 34 profiilisnapshotia, 3 organisaatiota ja 5 jäsenyyttä. Kaikkien **59 julkaisun** sisältötarkiste ja version API vastasivat alkuperäistä; myös yksi varhainen 2C-versio ilman versionUriä. **45 julkista artefaktia** tarkistettiin. Varsinaista demokantaa ei tyhjennetty, auth-istuntoja ei kopioitu.
- Alembic head edelleen `0005_lifecycle`; `alembic check`: **No new upgrade operations detected**. Ei uutta skeemamigraatiota. Startup/tyhjä/vanha kanta testattu; fixturet eivät palaudu tavallisessa restartissa.
- Erillinen julkaistun paketin toimintakoe: yhdeksän artefaktia haettiin oikeista julkisista reiteistä, tavut/tarkisteet tarkistettiin. HTTP:llä haettu konteksti käsiteltiin PyLD:llä **lukitulla paikallisella lataajalla**, RDF vastasi käsin kirjoitettua odotettua graafia ja läpäisi julkaisun alkuperäisen SHACL-snapshotin. Lähteen manifestin SHA vastasi julkaistun paketin viitettä. Tämäkin käytti synteettistä aineistoa.
- Aiemman koko ajon löytämä nykyisen tarjoajan oikeustarkistuksen virhe korjattiin; yllä olevat lopulliset API-tulokset sisältävät regressiotestin. Ensimmäisen uuden selainajon valitsinvirhe korjattiin; lopullinen 13 testin ajo läpäisi.

## Ajamattomat / varmistamatta jääneet

Aidosta muuttamattomasta Tietomallit-exportista ei voitu tehdä hyväksymiskoetta (HTTP 403); virallisen työkalun migraatiotestifixture ja erillinen suppea projektio testattiin, eikä niitä nimetä aidoksi exportiksi. Windows Docker Desktopia, oikean uuden Codespacen luontia/automaattista selainavausta/Private-portin ajonaikaista tilaa, ulkoisen pysyvän HTTPS-palvelun noutoa tai GitHub Actions -ajoa ei voitu varmistaa tässä ympäristössä. `.devcontainer`, Compose-portit ja toimitetut Alembic-revisiot säilyvät muuttumattomina. Kuorma-/tietoturva-auditointia tai ulkoisen myöntäjän/allekirjoituksen/lompakon integraatiotestejä ei ajettu; ne eivät ole tämän paikallisen generointivaiheen toteutusväitteitä.

## Avoin hyväksymiskriteeri

**En suosittele yhdistämistä vielä:** käyttäjän vaatima aidon julkisen muuttamattoman Tietomallit-exportin testi puuttuu noutoeston vuoksi. `fixtures/tietomallit/provenance.json` kertoo virallisen työkalurepositorion testiaineiston alkuperän/tarkisteen ja sen testimuokkaukset. Koko aineiston rajoitteet raportoidaan; erillinen projektio ei muuta alkuperäistä eikä osoita koko profiilin tukea. Tarkastettava PR-kuvaus on [docs/pull-request.md](docs/pull-request.md). Automaattista yhdistämistä ei tehdä.

Toteutuscommit `21a04c9` on työnnetty GitHubiin haaraan `feat/phase-2h-technical-packages`. PR:n avaaminen yritettiin sekä `gh pr create --draft --body-file docs/pull-request.md` (GraphQL) että REST `POST /repos/jgmikael/metatietovaranto/pulls` -pyynnöllä. Molemmat estyivät ympäristön **Forbidden**-vastaukseen. **PR:ää ei ole luotu.** Native git push onnistui; uutta tokenia tai oikeuksien kiertotapaa ei käytetty.

[Avaa tarkastettava PR käsin](https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2h-technical-packages?expand=1), base `main`, compare `feat/phase-2h-technical-packages`; valmis kuvaus on `docs/pull-request.md`. Avaa luonnoksena avoimen aidon exportin hyväksymiskokeen vuoksi. [Kokeile haaran Codespacessa](https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2h-technical-packages); täsmällinen kokeilupolku README:n alussa. Main säilyi commitissa `ac002ad`; automaattista yhdistämistä ei tehty.

---

# 2G:n PR-esitarkistus käyttäjän pyynnöstä — 17.10.2026

Käyttäjä pyysi PR:n avaamista ja ennen yhdistämissuositusta automaattiset tarkistukset sekä lyhyen toimintakokeilun ilman omaa demotestaustaan. Tarkistettu haara `feat/phase-2g-lifecycle`, lähtö-HEAD `d0a5232`, sovellustoteutus `1146932`. Main `79dc9d1` on ennallaan ja sisältyy haaraan. Tässä esitarkistuksessa ei muutettu sovelluskoodia, migraatiota tai testejä; päivitettiin tulokset ja valmis PR-kuvaus.

## Tässä esitarkistuksessa uudelleen ajettu

- Koko nykyinen API-/PostgreSQL-/migraatiotestisarja (README/CI:n 11 tiedostoa): **147 läpäissyttä**, 0 epäonnistunutta/ohitettua, 283,74 s. Mukana käyttöoikeudet, omistaja vs tarjoaja, CSRF, lukitus/idempotenssi, SHACL/johdannaisten/mappingien validointi, erillinen hyväksyntä/julkaisu, elinkaari, rollback, triggerit ja vanhojen kantojen migraatiot.
- `npm run build --prefix apps/web`: TypeScript + Vite läpäisi.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **12 läpäissyttä**, 0 epäonnistunutta/ohitettua, 84,55 s; oikea Chromium ja Keycloak OIDC.
- Yhteensä **159 eri pytest-testiä**, lisäksi alla kuvatut erilliset kokeet. Testikantaa tyhjentäviä ajoja ei ajettu samanaikaisesti. Starlette/httpx- ja RDFLib-varoitukset eivät ole ohituksia.
- Käynnissä olevan imagen API-/migraatiotiedostojen ja web-buildin **26 tiedoston SHA-256:t vastasivat checkoutia**. Näin selainajo kohdistui tarkistettuun toteutukseen. Docker-imagea ei rakennettu tässä uudelleen, koska sovelluskoodi ei muuttunut.
- Alembic current: `0005_lifecycle (head)`; Alembic check: `No new upgrade operations detected.` `git diff --check` läpäisi.

## Lyhyt toimintakokeilu

Ajettiin erillinen Playwright-kokeilu oikealla kirjautumisella (väliaikainen ajoskripti `/tmp/phase2g-pr-smoke.py`; ei uutta sovellusreittiä tai tunnistautumisen ohitusta):

1. `vero` loi uuden synteettisen kolmen toimitustavan tuotteen, muokkasi nimeä, tallensi ja latasi sivun uudelleen. Nimi, suurempi revisio ja muuttunut sisältötarkiste palasivat palvelimelta.
2. Kohdistamaton synteettinen RDF-esimerkki tallennettiin ja avattiin uudelleen. Se säilyi korjattavana luonnoksena; tarkastukseen lähetys palautti **422**.
3. Esimerkki korjattiin. Editorilta estettiin elinkaarimuutos (**404**) eikä hänelle näytetty oman sisällön hyväksyntää. Eri OIDC-käyttäjä `yritys` ei voinut muokata luonnosta, mutta hyväksyi ja julkaisi sen; julkaisu avattiin uudelleen ja SHACL-/mapping-raportit olivat conforms.
4. Publisher tallensi deprecated- ja withdrawn-tapahtumat. Sivun uudelleenlataus jokaisen jälkeen palautti oikean tilan. Historia sisälsi kaksi tapahtumaa; withdrawn jäi pois oletushausta ja löytyi erillisellä rajauksella. Alkuperäinen julkaisu pysyi täsmälleen samana.

Kokeilu läpäisi ilman selaimen JavaScript-virheitä. Sen synteettinen tuote `8e05bddd-cf4f-4baf-a3a6-e176a13e4921` jää demokantaan withdrawn-tilassa; alkuperäisiä tuotteita ei muokattu tai poistettu. Jäsenten rooleja ei muutettu.

## Migraatio olemassa olevan demoaineiston kopiolla

Ajettiin väliaikainen `/tmp/phase2g-pr-upgrade-copy.py` vasta API- ja selainajojen päätyttyä. Se loi Alembicilla **0004_publication-skeeman erilliseen catalog_test-kantaan**, kopioi siihen oikean demokannan 11 yhteistä metatietotaulua ja ajoi **0004 → 0005**, migraation toiston ja oikean sovelluksen startupin. Ei downgradea tai stampia. Alkuperäistä catalog-kantaa luettiin ainoastaan. Istuntoja, OAuth-tiloja, autentikoitujen pyyntöjen välimuisteja tai 2G:n uusia elinkaaritauluja ei kopioitu tähän 0004-skeemaan.

- Säilyneet kopioidut määrät: **37 tuotetta/luonnosta**, **30 julkaisua/tarkastusta/julkaisuoutboxia**, 22 profiilisnapshotia, 3 organisaatiota, 5 jäsenyyttä, 1 semanttinen profiili, 197 audit-tapahtumaa ja 4 alustusmerkintää.
- Jokaisen kopioidun rivin koko sisällön SHA-256 ja tunnisteet säilyivät samoina kopioinnin, migraation, toiston ja startupin jälkeen. Uudet elinkaaritaulut alkoivat tyhjinä.
- Kaikki **30 versiota** olivat luettavissa; mukana yksi aito vanha snapshot ilman versionUri-kenttää. Julkinen haku ja readiness toimivat.
- Alkuperäisen catalog-kannan samat taulut olivat muuttumattomia koko migraatiokokeen ajan. Erillinen testikopio siivottiin lopuksi; alkuperäiseen kantaan tai sen volyymeihin ei tehty palautusta tai nollausta.
- Lisäksi oikeasta käynnissä olevasta demosta luettiin kaikki 30 versiota ja elinkaariresurssia: alkuperäinen sisältö vastasi tallennettua SHA-256:ta ja versio-API palautti täsmälleen tallennetun sisällön. Haku vastasi 200 myös vanhan versionUri-kentättömän julkaisun kanssa.

## Ajamattomat ja yhdistämisarvio

- Windows/Docker Desktop, oikea Codespace/Private-portin pääsynvalvonta/automaattinen selainavaus ja GitHub Actionsin etätulos jäivät tässäkin varmistamatta. Käyttäjän omaa demotestausta ei ole oletettu tehdyksi.
- Aiemman 2G-toteutusajon tavallisen Compose-buildin DNS-epäonnistumista ei uusittu eikä esitetä tässä läpäisseeksi. Nykyinen toimiva image on rakennettu aiemmin pilven proxy-/CA-wrapperilla; nyt varmistettiin sen vastaavuus sovelluskoodiin sekä uudelleen ajettu web-build ja toiminta.
- Ei kuormitus-, tuotantoturvallisuus- tai saavutettavuusauditointia eikä ulkoisen lähde-/issuer-/wallet-palvelun testiä. Nämä eivät kuulu 2G:n toimitukseen.
- Paikallisissa automaattisissa tarkistuksissa ja toimintakokeiluissa **ei havaittu uutta avointa toiminnallista yhdistämisestettä**. Yhdistämissuositus on ehdollinen: PR on saatava avattua ja sen pakollisten CI-tarkistusten läpäistävä. GitHubin etä-CI:tä tai mergeability-tilaa ei ole varmennettu. Käyttäjän omaa demotestausta ei edellytetä tämän paikallisen arvion tueksi.

## PR:n avaaminen — edelleen estynyt

PR-tilan luku `gh pr view feat/phase-2g-lifecycle --repo jgmikael/metatietovaranto --json ...` ja tuoreella kuvauksella tehty `gh pr create --base main --head feat/phase-2g-lifecycle --title ... --body-file docs/pull-request.md` palauttivat `Post https://api.github.com/graphql: Forbidden`. REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2g-pr-reviewed.json` palautti myös Forbidden-vastauksen.

**PR:ää ei pystytty avaamaan tai sen etätilaa vahvistamaan.** Gitin fetch toimii ja päivitetty kuvaus/raportti toimitetaan samaan haaraan. Valmis kuvaus on [docs/pull-request.md](docs/pull-request.md). PR:n selaimen avauslinkki: https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2g-lifecycle . Muutoksia ei yhdistetty mainiin eikä automaattista yhdistämistä asetettu.

---

# Aikaisempi 2G-toimitus ja sen ajot

# Vaihe 2G — julkaisuversioiden elinkaari

Tarkistettu 17.10.2026. Pohjana main `79dc9d1`, käyttäjän PR #10:llä yhdistämä 2F. Työhaara `feat/phase-2g-lifecycle`. Toteutus vastaa käyttäjän hyväksymää 2G-ehdotusta: deprecated/withdrawn, muuttumaton tapahtumahistoria, käyttöoikeudet, auditointi, haku, tuotesivut ja vientien tilatieto. Täsmällinen sopimus: [docs/phase-2g.md](docs/phase-2g.md). Ei vaihetta 3 eikä automaattista yhdistämistä mainiin.

## Toteutettu

- Versiokohtainen published → deprecated/withdrawn ja deprecated → withdrawn. Withdrawn on lopullinen tälle versiolle; sisältö palautetaan uutena normaalisti hyväksyttynä julkaisuna. Tapahtumaton julkaisu on published ilman vanhojen rivien täydentämistä.
- Omistajaorganisaation publisher, oikea istunto, CSRF, erillinen elinkaari-ETag/If-Match ja 24 h idempotenssi. Editor/reviewer/reader tai pelkkä tarjoajaorganisaation publisher ei saa oikeutta. Julkinen perustelu vaaditaan; käyttäjän subject ei sisälly julkiseen elinkaarihistoriaan, vaan suojattuun auditointiin.
- Korvaava versio on saman tuotteen myöhempi julkaisu, joka ei ole withdrawn kirjaushetkellä. Itseviitteet, takautuvat ketjut, toisen tuotteen/luonnoksen viitteet ja käytöstä poistetut kohteet estetään. Mahdollinen myöhempi kohteen tilamuutos ei kirjoita aiempaa tapahtumaa uudelleen.
- Uusi Alembic `0005_lifecycle`: lifecycle_events ja lifecycle_outbox_events, vierasavaimet/rajoitteet ja append-only-triggerit. Aiemmat revisiot säilyvät. Tuoterivilukitus sarjoittaa elinkaarikomennot ja julkaisemisen. Tapahtuma, audit, oma outbox ja idempotenssivastaus samassa transaktiossa. Vanha julkaisuoutbox säilyy.
- GET `/api/v1/products/{id}/versions/{version}/lifecycle` ja POST `/api/v1/products/{id}/lifecycle-events`. Luonnosta, hyväksyntää, ProductVersion-sisältöä, profiilisnapshotia tai niiden tarkisteita ei muuteta.
- Oletushaku näyttää uusimmat published/deprecated-versiot. Withdrawn-uusimman tilalle ei nosteta vanhempaa versiota. lifecycleStatus=current/published/deprecated/withdrawn/all vaikuttaa ennen sivutusta/lukumääriä. Katalogiviennin includeWithdrawn=true mahdollistaa poistuneiden havaitsemisen.
- Nykyversion lukuesitys/vienti saa erillisen lifecycle-tiedon tapahtuman jälkeen. contentHash koskee edelleen alkuperäistä sisältöä. Versio-API, version URI ja export?version=... säilyttävät alkuperäisen snapshotin/ETagin; ajantasainen tila ilmoitetaan X-Product-Lifecycle-Status- ja Link: describedby -otsakkeilla sekä erillisenä resurssina. JSON-LD:n elinkaaritieto on erillinen paikallinen demo-resurssi.
- Selain: varoitus, historia, julkaisijan lomake, korvaavan version valinta ja hakurajaus. Withdrawn-version palvelutoiminnot estetään myös historiallisessa versiossa ja vanhassa issuance-näkymässä. Tilatiedon hakuvika estää palvelutoiminnot. Metatietojen ja profiilien lataus säilyy. Ulkoisten palvelujen oikeuksia tai myönnettyjä todistuksia ei peruta katalogimerkinnällä.
- Varhainen 2C-snapshot voi olla ilman versionUri-kenttää. Lukuesitys johtaa silloin version URI:n alkuperäisestä tuote-URI:sta ja version tunnuksesta; puuttuvan tuote-URI:n tapauksessa nykyisestä perusosoitteesta ja UUID:stä. Vanhan snapshotin tavallinen JSON/JSON-LD-sisältö ja tarkiste säilyvät. Tästä lisättiin regressiotesti.
- README, ROADMAP, AGENTS, tavoitearkkitehtuurin rajaus, arkkitehtuuri/verkkodemo, PR-kuvaus ja CI:n testilista päivitetty. .devcontainer, Private-portin ohje, openBrowser, fixtures, OIDC ja sisältöhyväksynnän säännöt säilyvät.

## Tässä tehtävässä todella ajettu

- Nykyinen pilviympäristö tarkistettiin cloud-environment-onboarding:setup-taidon avulla; PostgreSQL ja Keycloak käynnistettiin olemassa olevilla volyymeilla. Uusia ympäristöasetuksia, tunnuksia tai riippuvuuksia ei tarvittu eikä ympäristömäärityksiä tallennettu uudelleen. `UV_CACHE_DIR=/workspace/.cache/uv uv sync --locked` onnistui.
- `npm run build --prefix apps/web`: TypeScript/Vite-tuotantobuild läpäisi. `./scripts/cloud-build.sh`: lopullinen Docker-build läpäisi nykyisellä proxy-/CA-reitillä ja TLS-tarkistuksilla. `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app/db/keycloak healthy.
- **Suoraa Compose-buildia yritettiin:** `DOCKER_CONFIG=/workspace/.cache/docker docker compose up --build -d --wait` epäonnistui pipin uv-asennuksessa build-kontin DNS-virheeseen (`Temporary failure in name resolution`). Tämä ei ole läpäissyt tarkistus. Käynnistys ja lopulliset selaintestit tehtiin toimivalla cloud-build.sh-imagella ja --no-build-komennolla. Windowsin toimintaa ei päätellä pilven DNS-virheestä tai wrapper-buildin onnistumisesta.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_derived_validation.py tests/test_distributions.py tests/test_conversion.py tests/test_lifecycle.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: lopullinen ajo **147 läpäissyttä**, 0 epäonnistunutta/ohitettua, 284,71 s. Vain yksi tyhjentävää catalog_test-kantaa käyttävä ajo kerrallaan.
- Aiemmat 130 API-testiä säilyivät. Lisäksi 16 elinkaaritestiä ja yksi täytetyn 0004-kannan migraatiotesti. Todennettu käyttöoikeudet ja omistaja vs tarjoaja, CSRF, erillinen ETag, idempotenssi ja rinnakkaiset pyynnöt, siirtymät/korvaava versio, rollback, DB-triggerit, audit/outbox, haku/sivutus/URI:t/viennit, restart ja vanha versionUri-kentätön snapshot.
- Tyhjän kannan, vaiheiden 1/2A/2B kantojen ja toistuvien migraatioiden säilymistestit läpäisivät. Uusi testi täyttää toimitetun 0004-skeeman julkaisuineen, tarkastuksineen, profiileineen, luonnoksineen, audit-/outbox-riveineen, oikeuksineen ja tuntemattomine JSON-kenttineen; vanhat rivit pysyvät samoina 0005:n, toiston ja oikean app-startupin jälkeen.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: lopullista imagea vasten **12 läpäissyttä**, 0 epäonnistunutta/ohitettua, 81,39 s. Oikea Chromium ja Keycloak, aiemmat kymmenen polkua sekä uusi deprecated → withdrawn → hakurajaus/pysyvä versiosivu ja vanhan issuance-palvelulinkin esto tilan puuttuessa/withdrawn-tilassa.
- Kolmen muodon aktiivisten linkkien renderöinti ja tilatiedon hakuvika tarkistettiin selaimen muistissa korvatuilla API-vastauksilla. Olemattomia aktiivisia palveluita ei tallennettu demokatalogiin eikä ulkoisia linkkejä avattu. Varsinaiset tilamuutokset tehtiin oikean API:n ja publisher-istunnon kautta. Katalogiin jäävät palvelukuvaukset ovat planned.
- Yhteensä **159 erilaista testiä** läpäisi. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia. Ei kuormitus-/latenssitavoitteen mittausta.
- Alembic current: `0005_lifecycle (head)`. Alembic check: `No new upgrade operations detected.` Aiemmat 0001–0004-migraatiot ja .devcontainer säilyivät diffittä.
- Imagen ensimmäinen 0004 → 0005 -käynnistys säilytti kaikkien tarkistettujen vanhojen katalogirivien määrät ja koko sisällön SHA-256:t; elinkaaritaulut alkoivat tyhjinä. Myös korjatun imagen päivitys ja lopullinen tavallinen app-restart säilyttivät kaikki tarkistetut rivit.
- Lopullisessa restartissa ennallaan: 32 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 1 semanttinen profiili / 20 snapshotia, 25 julkaisua/tarkastusta/julkaisuoutboxia, 164 audit-tapahtumaa, 4 alustusmerkintää ja 4 elinkaaritapahtumaa/elinkaarioutboxia. Selainajojen omat synteettiset julkaisut ja elinkaarihistoriat jäävät muuttumattomaan historiaan. Volyymeja, alkuperäisiä tuotteita tai käyttäjän muutoksia ei nollattu.
- Kaikkien nykyisten 25 julkaisuversion sisältö vastaa alkuperäistä SHA-256:ta ja versio-API palauttaa täsmälleen tallennetun snapshotin. Näihin kuuluu aito aiemman 2C-toimituksen versio ilman versionUri-kenttää. Julkinen haku toimii sen kanssa.
- Codespacesin yhdistetty Compose tarkistettu synteettisellä CODESPACE_NAME-arvolla: HTTPS /identity samalla portilla 8000, workspace service:app-verkossa, openBrowser ennallaan. `git diff --check` läpäisi.

Ensimmäinen laaja ajo läpäisi 146 API-testiä, mutta ensimmäisessä selainajossa kolme testiä epäonnistui julkisen haun 500-virheeseen: elinkaariluku oletti versionUri-kentän myös kaikkein varhaisimmassa 2C-snapshotissa. Varsinaista vanhaa dataa ei korjattu, poistettu tai siemennetty uudelleen. Lukuyhteensopivuus korjattiin, lisättiin regressiotesti ja ajettiin yllä olevat lopulliset 147 + 12 testiä onnistuneesti. Epäonnistunut suora Compose-build on erillinen yllä raportoitu pilven DNS-rajoite.

## Ajamattomat ja rajat

- Windows/Docker Desktop, oikea GitHub Codespace/Private-portin pääsynvalvonta/automaattinen selainvälilehti ja GitHub Actions -etäajo jäivät ajamatta. Staattinen määritystarkistus ei todenna niitä. Tavallinen Compose-build tässä pilvessä epäonnistui kuten yllä, joten sitä ei esitetä onnistuneena.
- Ei archived/retired-tilaa, lopetusajastusta, tuotannon roolihallintaa tai elinkaaren erillistä kahden henkilön hyväksyntäprosessia. Publisherin perusteltu operatiivinen komento ei muuta sisältöhyväksyntää.
- Ei ulkoista outbox-kuluttajaa, lähde-/issuer-/wallet-integraatiota, ulkoisen käyttöoikeuden perumista tai todistuksen revokaatiota. Jo avoin vanha välilehti ei ole tarjoajan pääsynvalvonta; sivun lataus hakee tuoreen tilan.
- Ei DCAT-AP-, QEAA-, EUDIW-/EBW-, tuotantoturvallisuus-, kuormitus- tai saavutettavuusvaatimustenmukaisuusväitettä. Alkuperäinen muuttumaton metatieto voi sisältää palveluosoitteita myös withdrawn-tilassa; ajantasainen erillinen elinkaari on tarkistettava ennen niiden käyttöä.

## Toimitus

Haara `feat/phase-2g-lifecycle` on pushattu GitHubiin (toteutuscommit `1146932`). Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2g-lifecycle --title ... --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Myös REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2g-pr.json` palautti Forbidden-vastauksen. Git-push onnistui, mutta GitHub API -avaus estyi. Valmis kuvaus: docs/pull-request.md. Avaa PR selaimessa: https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2g-lifecycle . Main-haaraan ei yhdistetty muutoksia.

Kokeilu ennen yhdistämistä: https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2g-lifecycle . Portti 8000 Private. `vero` / `demo-vero` muokkaa/lähettää tarkastukseen, `yritys` / `demo-yritys` hyväksyy ja julkaisee. Julkaisun tuotesivun Version elinkaari -lomakkeella yritys voi merkitä version deprecated/withdrawn. Tarkka polku ja API-sopimus READMEssä.

---

# Aikaisemmat toimitukset (historia, eivät tämän ajon tuloksia)

# Vaihe 2F — hallittu synteettisen JSON-sisällön RDF-esikatselu

Tarkistettu 16.10.2026. Käyttäjä yhdisti 2E:n PR #9:llä; pohjana main `feca7b8`. Työhaara `feat/phase-2f-json-rdf`. ROADMAP ei nimennyt seuraavaa osatehtävää, joten ennen toteutusta rajattiin hallittu JSON → RDF -muunnos paikalliseksi valmisteluksi. Suunnitelma ja täsmällinen muunnossopimus: [docs/phase-2f.md](docs/phase-2f.md). Vaiheeseen 3 ei siirrytty. Main-haaraan ei yhdistetä automaattisesti.

## Toteutettu

- Editorin yksityinen muunnoslaboratorio luonnossivulla ja POST `/api/v1/drafts/{draftId}/conversion-preview`. Oikea istunto, omistajaorganisaation editor-jäsenyys, CSRF ja If-Match. Kokeilu ei muuta luonnosta, hyväksyntää, auditointisisältöä tai julkaisuja eikä tallenna syötteitä/raporttia.
- Tallennetun luonnoksen toimitustapamappingit ja yhteinen lukittu SHACL-snapshot. JSON API -sisältöolio, W3C:n sisältöpolun mukainen olio ja SD-JWT:n erillinen synteettinen väiteolio. Ei JWT:n purkamista tai kokonaisen todistuksen käsittelyä.
- Yksi juuriluokka, eksplisiittiset IRI-ominaisuuspolut, sisäkkäiset oliot ja vanhempaansa kohdistuvat taulukkoalkiot. Eksplisiittiset XSD-literaalit; decimal tarkkana merkkijonona. Anonyymit RDF-solmut eivät keksi liiketoimintatunnisteita. Null, ylimääräinen kenttä, ristiriitainen mapping, häviävä toistuva literaali tai tukematon rakenne estää onnistumisen.
- JSON API:n liitettyjen alkuperäisen dialektin JSON Schema/OpenAPI -skeemojen rakenne-/sisältötarkistus, hallittu muunnos ja 2D:n SHACL Core erillisinä tuloksina. Vähintään kahden onnistuneen esimerkin RDF-graafien isomorfinen vertailu. Samuus koskee järjestyksettömiä RDF-ominaisuuksia, ei OWL-ekvivalenssia tai yleistä literaalien arvonormalisointia.
- Raportin sidonta luonnoksen revisioon/tarkisteeseen, profiilin UUID/SHA-256:een ja mappingien versioihin/tarkisteisiin sekä syötteiden tarkisteisiin. Raporttia ei hyväksytä asiakkaan asettamaksi julkaisutodisteeksi. Nykyiset 2D/2E-julkaisuehdot säilyvät.
- Verkoton aliprosessi: CPU 5 s, muisti 512 MiB, seinäkello 15 s. 1–3 esimerkkiä, UTF-8 100 kB per sisältö / 200 kB yhteensä, JSON syvyys 20 / solmut 5 000, RDF 2 000 kolmikkoa. Myös raskaan SHACL-regexin oikea prosessirajan testi.
- Selainlomake, synteettisyysvahvistus, valmiin neljännen demon täyttö, eri/virheellisten sisältöjen näyttö, RDF-teksti ja tarkisteet. Muutos tyhjentää vanhan tuloksen ja vahvistuksen. Sivun lataus tyhjentää kokeilun.
- README, ROADMAP, AGENTS, arkkitehtuuri, verkkodemo, 2E-jatkorajaus ja tavoitearkkitehtuurin täsmennys päivitetty. CI:n API-testilistaan lisätty muunnostestit.
- Ei relaatiomigraatiota tai fixtures-muutosta. .devcontainer ja aiemmat migraatiot säilyvät ennallaan. Private-portin ohje ja automaattinen openBrowser säilyvät.

## Tässä tehtävässä todella ajettu

- `UV_CACHE_DIR=/workspace/.cache/uv uv sync --locked`: lukittu asennus onnistui; uusia riippuvuuksia ei lisätty.
- `npm run build --prefix apps/web`: lopullinen TypeScript/Vite-build läpäisi. `./scripts/cloud-build.sh`: lopullinen Docker-build läpäisi pilven proxy-/CA-reitillä. `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app/db/keycloak healthy nykyisillä volyymeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_derived_validation.py tests/test_distributions.py tests/test_conversion.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **127 läpäissyttä**, 0 epäonnistunutta/ohitettua, 266,48 s. Tässä kokoelmassa muunnostestejä oli 37. Aiemmat 90 API-/auth-/julkaisu-/semantiikka-/migraatiotestiä säilyivät.
- Viimeisen aikaleimarajauksen ja kolmen uuden reunatapauksen jälkeen `.venv/bin/pytest tests/test_conversion.py -q`: **40 läpäissyttä**, 0 epäonnistunutta/ohitettua, 52,72 s. Tämä on lopullisen muunnostoteutuksen koko testitiedosto. Laajaa kokoelmaa ja kohdistettua uusinta-ajoa ei ajettu samanaikaisesti samaan catalog_test-kantaan.
- API-puolella yhteensä **130 erilaista testiä** (90 aiempaa + 40 uutta), ei 167. Testattu saman/eri sisällön vertailu, sisäkkäisten taulukko-olioiden korrelaatio, järjestys, eksplisiittiset tyypit ja tarkka decimal, aikaleimarajat, null/puuttuvat/ylimääräiset kentät, häviävät toistot, väärät juuret/mappingit, JSON Schema vs SHACL-koodisto, disclosure-/todistusmateriaalin kielto, resurssiraja, oikeudet/CSRF/If-Match, vanha julkaisu ja esikatselun tallentamattomuus.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: lopullista Docker-imagea vasten **10 läpäissyttä**, 0 epäonnistunutta/ohitettua, 71,38 s. Oikea Chromium/Keycloak; aiemmat yhdeksän polkua ja uusi kolme samaa sisältöä → eri sisältö → null-hylkäys → luonnos ennallaan → uudelleenlataus tyhjentää kokeilun.
- Yhteensä **140 erilaista testiä** läpäisi. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia. Ei suorituskyky-/kuormitusmittaus.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.` Tyhjän ja vanhan muokatun kannan sekä toistuvien migraatioiden säilymistestit läpäisivät osana laajaa ajoa.
- Katalogirivien määrät ja koko sisältö tarkistettiin ennen/jälkeen imagen päivityksen ja tavallisen restartin SHA-256:lla. Viimeisessä tarkistuksessa ennallaan: 24 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 16 profiilisnapshotia, 17 julkaisua/tarkastusta/outboxia ja 116 audit-tapahtumaa. Selainajojen omat synteettiset julkaisut jäävät muuttumattomaan historiaan. Tuotteita, oikeuksia tai volyymeja ei nollattu.
- Kaikkien nykyisten 17 julkaisuversion sisältö vastaa tallennettua SHA-256:ta ja version API palauttaa täsmälleen saman JSON-sisällön. Vanhoja julkaisuja ei kirjoitettu uudelleen.
- Codespacesin yhdistetty Compose tarkistettu synteettisellä CODESPACE_NAME-arvolla: Keycloak saman HTTPS-portin 8000 /identity-polussa, workspace service:app-verkossa ja openBrowser. Migrations- ja .devcontainer-diff tyhjä. `git diff --check` läpäisi.

Kehityksessä korjattiin kaksi uuden testiaineiston ongelmaa (SHACL-koodistorajoitteen sijoitus ja julkaisun jälkeen vanhentunut ETag). Kohdistettu korjausajo läpäisi. Viimeisen buildin ensimmäinen yritys epäonnistui ENOSPC-levytilaan. Poistettiin vain käyttämätöntä Dockerin build-välimuistia ja irrallisia imageja, jolloin vapautui noin 6,6 Gt; tietokantavolyymeihin ei koskettu. Tämän jälkeen lopullinen web-/Docker-build, käynnistys, säilyvyystarkistus ja selaintestit läpäisivät.

## Ajamattomat ja rajat

- Windows/Docker Desktop, tavallinen `docker compose up --build` ilman pilven build-wrapperia, oikea GitHub Codespace/Private-portin pääsynvalvonta/automaattinen välilehti ja GitHub Actions -etäajo jäivät ajamatta. Staattinen määritystarkistus ei todista näitä.
- Ei elävän Tietomallit-palvelun hakua, oikeaa lähde-APIa tai issuer-/wallet-integraatiota. Ei VC-kuoren rakennetarkistusta, JSON-LD-kontekstin laajennusta, SD-JWT-profiilin purkua/disclosurejen todennusta, kryptografiaa tai luottamus-/haltijasidontatarkistusta.
- Ei monijuurisia/rekursiivisia profiileja, RDF-listojen järjestystä, IRI-viitearvoja, kielitunnisteita tai liiketoimintaidentiteettien yhdistämistä. Ne saavat hylkäyksen/arvioimatta-tuloksen. Tuetut tyypit ja tarkkuusrajat on dokumentoitu phase-2f.md:ssä.
- Ei QEAA-, DCAT-AP-, EUDIW-/EBW-, tuotantoturvallisuus-, kuormitus- tai saavutettavuusvaatimustenmukaisuuden väitettä. Synteettisyys perustuu käyttäjän vahvistukseen. Kokeilun läpäisy ei ole julkaisuun tallennettu hyväksymisraportti.

## Toimitus

Haara `feat/phase-2f-json-rdf` on pushattu GitHubiin (toteutuscommit `812d402`). Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2f-json-rdf --title ... --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Myös REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2f-pr.json` palautti Forbidden-vastauksen. Git-push onnistui; GitHub API -avaus estyi. Valmis kuvaus: docs/pull-request.md. Avaa PR selaimessa: https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2f-json-rdf . Main-haaraan ei yhdistetty muutoksia.

Kokeilu ennen yhdistämistä: https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2f-json-rdf → portti 8000 Private → `vero` / `demo-vero` → Omat luonnokset → Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo) → JSON → RDF -muunnoskokeilu.

---

# Aikaisemmat toimitukset (historia, eivät tämän ajon tuloksia)

# Vaihe 2E — rinnakkaiset toimitustavat ja versioidut mappingit

Pohjana yhdistetty main `5611be2` (PR #8 / 2D). Työhaara `feat/phase-2e-derived-validation`. Käyttäjän täsmennetty 2E-suunnitelma esitettiin ensin ja toteutettiin sen jälkeen. Main-haaraan ei yhdistetä automaattisesti. Alla olevat 2D/2C-toimitusten tulokset ovat historiaa.

## Muutos aiempaan suunnitelmaan ja toteutus

- Aiempi 2E-suunnitelma keskittyi JSON Schema/OpenAPI -johdannaisten tarkistuksiin. Käyttäjän täsmennyksen jälkeen pääkohteeksi tuli yksi tietotuote ja kolme tyypitettyä rinnakkaista toimitustapaa: JSON API, W3C VCDM 2.0 JSON-LD VC ja IETF SD-JWT VC. Johdannaistarkistus säilyi erillisenä, rajattuna lisätarkistuksena.
- Distributions erottaa formaatin, protokollan, suojausprofiilin, saatavuuden, ympäristön, vastuuorganisaatiot ja yhteisen profiiliviitteen. W3C VC on oletuksena ensisijainen, kun se on mukana; eksplisiittinen primaryDistributionId tuetaan API:ssa ja käyttöliittymässä.
- JSON API sisältää palvelun ja kuvauksen osoitteet, OpenAPI-/JSON Schema -artefaktiviitteet, tyypitetyn tunnistautumistavan, oikeudet ja ajantasaisuuden. Todistusjakeluilla ovat issuer/aloituslinkki, OpenID4VCI 1.0, erilliset configuration-tunnisteet, suojaus/voimassaolo/status-profiilit, kohdeluokat/edustaminen, maksu, tuki, oikeudellinen luokka ja lompakkonäyttö.
- W3C VC:llä ovat VCDM 2.0, tyypit, kontekstit ja sisältöpolku. SD-JWT VC:llä ovat vct, profiiliversio, erillinen väitemapping sekä paljastamis- ja haltijasidontakäytännöt. SD-JWT:hen ei vaadita JSON-LD-kontekstia eikä sitä esitetä W3C VC:n samana kuorena.
- Sama myöntäjäpalvelu voi tarjota molempia todistusmuotoja erillisillä konfiguraatioilla ja käyttää samaa lähde-APIa/sovitinta. Katalogi kuvaa ja ohjaa; sen metatietovienti ei ole lähdesisällön jakelurajapinta. Uusia lähdeintegraatioita, allekirjoituksia tai lompakkoprotokollaa ei toteutettu.
- Kaikki toimitustavat sidotaan julkaistun tuoteversion samaan SHACL-snapshotiin. DistributionBindings sisältää tuotteen version, yhteisen snapshotin UUID/SHA-256:n ja mappingin version. Muuttunutta mappingia ei julkaista saman toimitustapa-ID:n vanhalla mapping-versiolla eikä versionumeroa alenneta.
- Metadata-/mapping-tarkistus vertaa alkuperäisiä IRI-polkuja, sisäkkäisiä olioita, literaalien tietotyyppejä, luokkia ja min/maxCountia. Moniarvoisuus kuvataan /*-poluilla ja lapset oliovanhemman alle. Puuttuvat/ristiriitaiset/epäselvät mappingit, väärät skeemaviitteet tai JSON API:n skeemasta puuttuvat polut estävät uuden julkaisun.
- 2D:n erillinen SHACL-esimerkki ja hyväksyntä säilyvät. DistributionValidation ja rajattu DerivedValidation kuuluvat sisältötarkisteeseen, erilliseen hyväksyntään ja muuttumattomaan versioon. Metadata, semanttinen esimerkki ja kryptografinen tarkistus erotetaan näkyvästi.
- JSON Schema tukee alkuperäisiä draft 4/6/7/2019-09/2020-12-dialekteja, OpenAPI 3.0.x/3.1.x-versioita. Rajattu suora kenttävertailu ei väitä mallien ekvivalenssia eikä korvaa toimitustapojen sisäkkäistä metadataa. JSON-esimerkit ovat synteettisiä. Viitteitä ei noudeta ulkoisista lähteistä, prosessit ovat resurssirajattuja ja verkottomia.
- Rakenteiset muokkauslomakkeet ja erilliset tuotesivutoiminnot. Planned/suspended ei saa aktiivista palvelutoimintoa. Muotokohtaiset toimintotekstit ovat Käytä JSON-rajapintaa / Tutustu rajapintakuvaukseen / Pyydä W3C VC lompakkoon / Pyydä SD-JWT VC lompakkoon.
- Neljäs synteettinen esimerkki, jossa kaikki kolme ovat planned, lisätään kerran tunnettuun synteettiseen tuote–organisaatio-pariin. UUID-kollisiota, käyttäjän muokkauksia tai poistettua esimerkkiä ei palauteta alkuperäisiksi. Muita organisaatioita ei yhdistetä tai oikeuteta nimen perusteella.
- Vanha issuance-luku ja vanhojen luonnosten kirjoitus säilyvät. Uuden kokoelman hiljainen pudottaminen vanhaan malliin estetään. Jo julkaistuja versioita ja snapshotteja ei kirjoiteta uudelleen. Ei uutta relaatiomigraatiota; head on edelleen 0004_publication.
- ROADMAP, AGENTS, README, verkkodemon/arkkitehtuurin ohjeet, tavoitearkkitehtuuri ja VC-periaate päivitetty. Täsmällinen ratkaisu ja integraatiovaiheen hyväksymiskriteerit: docs/phase-2e.md. Codespacesin määrityksiin ei tehty muutoksia; portti 8000 / openBrowser / Private-ohje säilyvät.

## Tässä tehtävässä todella ajettu

- Lukittu uv-asennus: jsonschema 4.26.0, openapi-spec-validator 0.7.2 ja openapi-schema-validator 0.6.3 sekä niiden riippuvuudet. `UV_CACHE_DIR=/workspace/.cache/uv uv sync --locked` onnistui.
- `npm run build --prefix apps/web`: TypeScript ja Vite-tuotantobuild onnistuivat. `./scripts/cloud-build.sh` rakensi Docker-imagen pilven proxy-/CA-reitillä TLS-tarkistuksia säilyttäen. `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app/db/keycloak healthy samoilla voluumeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_derived_validation.py tests/test_distributions.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **90 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**, lopullinen ajo 211,99 s. Yksi tyhjentävää catalog_test-kantaa käyttävä pytest-ajo kerrallaan.
- Aiemmat 55 API-/auth-/SHACL-/migraatio-/osoitetestiä säilyivät. Lisäksi 18 johdannais- ja 17 toimitustapatestiä: alkuperäiset skeemadialektit, local-ref/OpenAPI/nullable, puuttuvat ja ristiriitaiset kentät, koodistot/taulukot, token-/salaisuusparametrien kielto, kolme muotoa, sama profiili, erilliset konfiguraatiot, sisäkkäiset mappingit, uusi mapping-versio, vanhat muuttumattomat versiot sekä fixtureiden muokkauksen/poiston säilyminen.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **9 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**, lopullinen ajo 55,50 s. Oikea Chromium ja Keycloak: aiemmat seitsemän polkua, JSON-johdannaisen tiedostotuonti/virhe/korjaus/hyväksyntä/julkaisu sekä kolmen toimitustavan muokkaus, eri käyttäjän hyväksyntä, planned-julkaisu ja anonyymi näyttö.
- Aktiivisten muotokohtaisten linkkien renderöinti tarkistettiin selaimessa korvatulla API-vastauksella. Tätä vastausta ei tallennettu katalogiin eikä palvelulinkkejä avattu. Aktiivisen metadatan oikeat backend-ehdot tarkistettiin erillisessä catalog_test-kannassa. Katalogiin jäävät selaintestijulkaisut ovat synteettisiä ja palvelukuvaukset planned-tilassa.
- Yhteensä **99 eri testiä** läpäisi. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia. Kyse on oikeellisuustesteistä, ei latenssi-/kuormitustavoitteen todennuksesta. Selainodotus sallii usean erillisen rajatun validointiprosessin vaatiman ajan.
- Olemassa olevasta demokannasta tarkistettiin neljä aitoa ennen 2E:tä julkaistua versiota. Niiden koko sisältö vastaa alkuperäistä SHA-256:ta ja versio-API palauttaa saman sisällön/UUID:n/version/tarkisteen. Vanhoja julkaisuja ei muutettu.
- Vanhojen vaiheiden 1/2A/2B kantojen migraatio-, alkuperäisten rivien säilymis- ja toistuvien käynnistysten testit läpäisivät. Käyttäjän nyt erikseen tilaama neljäs fixture on lisäys, ei alkuperäisten tuotteiden nollaus.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.` Migrations- ja .devcontainer-diff on tyhjä.
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: Keycloak samalla HTTPS-portin 8000 osoitteella, workspace service:app-verkossa ja openBrowser ennallaan.
- `git diff --check` läpäisi. Tavallinen app-restart ja Compose-readiness läpäisivät. Ennen/jälkeen kaikkien tarkistettujen katalogirivien sisältö/tarkiste säilyi: 18 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 12 profiilisnapshotia, 11 julkaisua/tarkastusta/outboxia ja 80 audit-tapahtumaa. Testien omat synteettiset julkaisut ja keskeneräiset kehitysluonnokset jäivät historiaan; alkuperäisiä tuotteita tai volumeita ei poistettu.

Kehitysajoissa korjattiin vanhimmasta demokannasta puuttuvien maa-/organisaatiotunnisteiden vaikutus uuden fixturen lisäämiseen. Luotettava tunnistus käyttää tunnettua UUID-paria ja synteettisyyttä. Tässä kehitysympäristössä poistettiin kerran vain uuden, epäonnistuneen alustuskokeen oma phase-2e-distribution-demo-merkintä, kun ensin varmistettiin ettei neljättä tuotetta ollut luotu. Tuotteita, julkaisuja tai volumeita ei poistettu. Lisäksi selainkokeen viiden sekunnin odotus oli liian lyhyt usealle peräkkäiselle rajatulle validoinnille; odotus korjattiin ja käyttöliittymä näyttää käsittelyn olevan kesken. Lopulliset yllä raportoidut ajot läpäisivät.

## Ajamattomat ja jatkovaiheen rajat

- Windows/Docker Desktop, tavallinen `docker compose up --build` ilman pilven build-wrapperia, oikea GitHub Codespace/Private-portin pääsynvalvonta/automaattinen selainvälilehti ja GitHub Actions -etäajo jäivät ajamatta. Staattinen määritystarkistus ei todista näitä.
- Ei elävän Tietomallit-palvelun hakua, lähde-APIa, oikeaa issuer-palvelua, todistusten muodostusta/allekirjoitusta, JWT:n tai haltijasidonnan kryptografista tarkistusta, OpenID4VCI/lompakkotoimitusta tai EUDIW-/EBW-yhteentoimivuuskoetta.
- Tässä ei muunneta JSON-/purettuja VC-sisältöjä RDF:ksi eikä anneta JWT-merkkijonoa SHACL-moottorille. Hallittu muunnos ja saman sisällön vertailu kaikissa kolmessa muodossa ovat integraatiovaiheen hyväksymiskriteeri, eivät ajettu ominaisuus.
- Mapping-profiili tukee yksiselitteisiä sisäkkäisiä sh:node/sh:class-polkuja, ei rekursiivisia tai mielivaltaisia SHACL-polkulausekkeita. Johdannaisten suora JSON-kenttävertailu on tätä suppeampi ja näkyvästi erillinen. Rajauksen ulkopuolinen kohta estää hyväksynnän; sitä ei hyväksytä hiljaisesti.
- Ei QEAA-, DCAT-AP-, tuotantoturvallisuus-, kuormitus- tai saavutettavuusvaatimustenmukaisuuden väitettä. Synteettisyys on käyttäjän vahvistus, ei automaattinen henkilötietotunnistin. Palvelun saatavuus on kuvattu metadata, ei saavutettavuus-/luottamusmittaus.

## Toimitus

Haara `feat/phase-2e-derived-validation` on pushattu GitHubiin. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2e-derived-validation --title ... --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Myös REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2e-pr.json` palautti Forbidden-vastauksen. Git-push onnistui; GitHub API -avaus estyi. Valmis kuvaus on docs/pull-request.md. PR:n voi avata selaimessa: https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2e-derived-validation . Main-haaraan ei yhdistetty muutoksia.

---

# Aikaisemmat toimitukset (historia, eivät tämän ajon tuloksia)

# Vaihe 2D — offline SHACL Core ja synteettinen esimerkkisisältö

Tarkistettu 15.10.2026. Pohjana main `61ca4ed` (PR #7, vaihe 2C, yhdistetty käyttäjän hyväksynnällä). Työhaara `feat/phase-2d-shacl`. PR:ien 5 ja 6 semanttinen ja VC-toimituksen periaate säilyvät sitovina. Mainiin ei yhdistetä automaattisesti.

## Toteutettu

- pySHACL 0.31: profiilin ja lukittujen riippuvuuksien meta-SHACL-rakennetarkistus sekä synteettisen RDF-esimerkin oikea SHACL Core -validointi. Tietotyypit, kardinaliteetit, sisäkkäiset muodot ja koodistorajoitteet tarkistuvat alkuperäisestä graafista, eivät litistetystä tietoelementtilistasta.
- Yksi esimerkkigraafi (voi sisältää monta tietuetta), Turtle/RDFXML/paikalliskontekstinen JSON-LD. Pakollinen synthetic:true-ilmoitus, 100 kB/2 000 kolmikkoa. Käyttöliittymän tiedostotuonti ja tekstikenttä sekä erillinen synteettisyyden vahvistus.
- Kohdistumaton/tyhjä esimerkki tai deaktivoitu aloitusmuoto ei tuota väärää onnistumista. Aloitusmuotojen kohdistus tarkistetaan; varsinaiset rajoitteet tarkistetaan koko graafista. Ei OWL-päättelyä.
- Palvelimen semanticValidation: tulos, sääntö-IRI, JSON Pointer, RDF-polku, kohde/muoto, profiili-/esimerkkitarkiste, esitysmuoto, moottoriversio ja validointikäytäntö. Asiakas ei voi asettaa raporttia. Näyttö rajattu 100 havaintoon, mikä ei muuta epäonnistumista onnistumiseksi.
- Esimerkki ja raportti sisältyvät luonnoksen/julkaisun sisältötarkisteeseen. Muutos mitätöi hyväksynnän; uusi julkaisu vaatii ajantasaisen läpäisseen raportin ja aiemman erillisen ihmishyväksynnän. Virheellisen esimerkin voi tallentaa korjattavaksi luonnokseksi. Validate-esikatselu on muuttamaton: uuden raportin tallennus tehdään editorin luonnostallennuksessa.
- Resurssirajattu validointiprosessi: CPU 5 s, muisti 512 MiB, seinäkello 15 s, syvyys 20, verkkoyhteyksien esto. SPARQL/JS/AF/mukautetut komponentit ja tuntemattomat SHACL-predikaatit estävät hyväksynnän. Ulkoisia konteksteja, DTD/ENTITYjä tai riippuvuuksia ei noudeta.
- Alkuperäisen UTF-8-sisällön alun/lopun tyhjää tilaa ei enää normalisoida uusissa tuonneissa; tavutarkiste vastaa tallennettua alkuperäistä tekstiä. Nimetyt JSON-LD-graafit hylätään eksplisiittisesti sen sijaan, että oletusgraafin ulkopuolisia rajoitteita/sisältöä katoaisi.
- Ei uutta migraatiota: 2C:n JSONB-sisällöt riittävät. Head on 0004_publication. Vanhoihin julkaistuihin sisältöihin, profiilisnapshotteihin tai luonnoksiin ei tehdä automaattisia täydennyksiä. Vanhat julkaisut säilyvät; seuraava julkaisu tarvitsee esimerkin ja tallentamalla muodostuvan raportin.
- Nykyinen OIDC, CSRF, organisaatiorajat, If-Match, idempotenssi ja erillinen hyväksyntä säilyvät. Codespacesin määrityksiin ei tehty muutoksia: portti 8000, openBrowser ja service:app-verkko ennallaan; ohje edellyttää Private-tilaa. Ei ulkoisia issuer/wallet-yhteyksiä.
- README, ROADMAP, AGENTS, verkkodemon ja arkkitehtuurin ohjeet sekä CI-testilista päivitetty. Uusi synteettinen fixture fixtures/semantic-example-demo.ttl.

## Tässä tehtävässä todella ajettu

- `uv add` ja `UV_CACHE_DIR=/workspace/.cache/uv uv sync --locked`: runtime-riippuvuudet ja lukitus onnistuivat. `npm run build --prefix apps/web`: TypeScript ja Vite-tuotantobuild onnistuivat.
- `./scripts/cloud-build.sh` rakensi Docker-imagen pilven proxy-/CA-reitillä TLS-tarkistuksia säilyttäen; `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait` käynnisti app/db/keycloak-palvelut healthy-tilaan olemassa olevilla voluumeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **55 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Sisältää aiemmat 39 testiä ja 16 uutta SHACL-testiä. Vanhojen kantojen, muokattujen metatietojen/UUID:iden ja jäsenyyksien säilymistestit läpäisivät.
- Uudet testit: puuttuva kenttä, väärä tietotyyppi, liikaa arvoja, kohdistamaton esimerkki, kolme RDF-esitystä, väärä profiilirakenne, estetty SPARQL/tuntematon rajoite, sisäkkäinen riippuvuus ja koodisto, etäkonteksti/DTD/ENTITY, synteettisyysvahvistus, raportin väärentämiskielto ja sidonta, muuttumaton vanha julkaisu, vanhan raportittoman luonnoksen uudelleentallennus, deaktivoitu muoto, raskaan regexin resurssiraja, UTF-8-tavujen säilyminen ja nimetyn graafin hylkäys.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **7 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Oikea Chromium ja Keycloak; aiemmat CRUD/mobiili/organisaatiot/reader/eristys/session vanheneminen sekä virheellinen esimerkki → korjaus tiedostosta → raportti → toisen käyttäjän hyväksyntä → julkaisu → anonyymi haku. Ei kirjautumisen ohitusreittiä.
- Yhteensä **62 eri testiä** läpäisi. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia. Resurssirajan testin lisätarkistus läpäisi erikseen: VALIDATION_RESOURCE_LIMIT ja palvelimen readiness säilyivät, testikutsu kesti 6,12 s. Tämä ei ole lisätesti kokonaismäärään.
- Olemassa olevasta oikeasta demokannasta tarkistettiin kolme aitoa 2C-julkaisua: sisältö vastaa alkuperäistä SHA-256:ta, version API palauttaa saman snapshotin eikä vanhaan JSON-LD-vientiin ilmesty puuttuvia 2D-kenttiä. Tietoja tai volumeita ei nollattu.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.` Sekä migrations- että .devcontainer-diff on tyhjä.
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: Keycloak samalla portilla 8000, workspace service:app-verkossa ja openBrowser ennallaan.
- `git diff --check`: ei whitespace-virheitä. Tavallinen app-restart ja Compose-readiness läpäisivät. Ennen/jälkeen samat rivit ja tarkisteet: 8 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 5 profiilisnapshotia, 4 julkaisua/tarkastusta/outboxia ja 33 audit-tapahtumaa. Selaintestien synteettiset julkaisut jäävät muuttumattomaan historiaan; epäonnistuneen kehitysajon keskeneräinen synteettinen luonnos säilytettiin.

Selaintestin ensimmäinen uusi tiedostopolku paljasti tekstikentän label-kohdistuksen ongelman. Kentälle lisättiin eksplisiittinen label/htmlFor/id. Lopullinen seitsemän selaintestin ajo läpäisi korjauksen jälkeen.

## Ajamattomat ja rajat

- Oikea GitHub Codespace, GitHubin Private-portin pääsynvalvonta ja automaattinen selainvälilehti, Windows/Docker Desktop, tavallinen `docker compose up --build` ilman pilven build-wrapperia sekä GitHub Actions -etäajo jäivät ajamatta. Asetusten staattinen tarkistus ei todista näitä.
- Elävän Tietomallit-palvelun linkkituontia ei ajettu. Oikea paikallinen tiedostotuonti sekä nykyinen hallitulla verkkovastauksella tehtävä linkkitesti ajettiin. Molemmat fixturet ovat synteettisiä eivätkä oikea Tietomallit-export tai rekisteriote.
- SHACL-tulos ei todista lähdeprofiilin alkuperää, oikeudellista asemaa tai myöntämisoikeutta. Se ei tarkista VC-kuorta, allekirjoitusta, myönnettyä todistusta tai lompakkoyhteentoimivuutta. Ei vaihetta 3.
- Vain offline Core, ei SPARQL/JS/AF- tai mukautettujen komponenttien tukea. Nimettyjä JSON-LD-graafeja ei tueta. JSON Schema/OpenAPI-johdannaisten validointi ja kattavuuskartoitus sekä DCAT-AP-vaatimustenmukaisuus jäävät jatkoon.
- Synteettisyys on käyttäjän vahvistus, ei automaattinen henkilötieto-/salaisuustunnistin. Ei kuormitus-, tuotantoturvallisuus- tai saavutettavuusauditointia.

## Toimitus

Haara `feat/phase-2d-shacl` on pushattu GitHubiin. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2d-shacl --title ... --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`, ja REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2d-pr.json` palautti saman Forbidden-esteen. Git-push onnistuu, GitHub API -pääsy on estynyt. Valmis kuvaus on docs/pull-request.md. Avaa PR selaimessa: https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2d-shacl . Main-haaraan ei yhdistetty muutoksia.

---

# Aikaisemmat toimitukset (historia, eivät tämän ajon tuloksia)

# Vaihe 2C — yksityiset luonnokset ja muuttumattomat julkaisut

Tarkistettu 14.10.2026. Pohjana main `0dd6555`, joka sisältää PR:t 5 ja 6. Työhaara `feat/phase-2c-publication`. Mainiin ei yhdistetä automaattisesti. Alla olevat aiempien toimitusten PR-esteet/testimäärät ovat historiaa.

## Toteutettu ja suunnittelumuutosten vaikutus

- Luonnos → tarkastus → erillinen hyväksyntä → julkaisu. Muokkaus mitätöi hyväksynnän, kaikki luonnoksen kirjoittajat estetään sen hyväksynnästä. Julkaisija voi olla sama kuin erillinen tarkastaja.
- Pysyvä omistajaorganisaatio erotetaan tarjoajasta. Editor muokkaa, reviewer/publisher tarkastaa, publisher julkaisee. Omat luonnokset vaatii jäsenyyden; julkinen haku, URI:t ja viennit palauttavat vain julkaisuja. Anonyymi tyhjä haku uuden kannan alussa on tarkoituksellinen muutos.
- ETag/If-Match, PostgreSQL-rivilukko, luonnin/julkaisun 24 h idempotenssi. Julkaisu, profiiliviite, audit ja outbox samassa transaktiossa. Tietokantatriggerit estävät snapshot-/tarkastus-/tapahtumahistorian UPDATE/DELETE-operaatiot.
- Semver-julkaisut, pysyvä version URI, vanhan version JSON-/JSON-LD-vienti ja uuden työkopion luonti aiemman julkaisun rinnalle. Vanhaa sisältöä ei muokata eikä julkaistua tuotetta poisteta.
- PR 5: SHACL-profiilin tuonti linkillä TAI tiedostolla, lukitut alkuperäiset artefaktit, IRI:t, OWL-viitteet, riippuvuudet ja johdannaisdialektit. Tietoelementit johdetaan profiilista. Vanha dataElements säilyy keskeneräisenä legacy-demotietona. Kolmen RDF-esityksen graafiekvivalenssi tarkistetaan erikseen tavutarkisteista.
- Rakenne-/riippuvuustarkistukset ja lähdeilmoituksen eksplisiittinen ihmistarkastus. Ei automaattista Tietomallit-alkuperän todistusta, ei SHACL-instanssivalidointipalvelua. Parserilla on tiedosto-, kolmikko-, CPU-, muisti- ja aikarajat. Etäkontekstien/DTD:n jäsennys estetään.
- PR 6: W3C VC ensisijaisena toimitusmuotona, oletuksena näkyvästi planned. VC-/issuer-/wallet-metatiedot lukitaan tuoteversioon ja profiilisnapshotiin. Vain käytettävä palvelu saa pysyvän HTTPS-asiointilinkin, ei henkilökohtaisia tarjouksia/tokeneita. Esimerkkidomain tai planned/suspended ei saa toimivaa painiketta. Ei issuer/wallet-integraatiota tai QEAA-vahvistusta.
- Uusi 0004_publication säilyttää vanhat tuoterivit, UUID:t, muokkausajat ja kaikki metatiedot yksityisissä luonnoksissa; vanhoja migraatioita ei muuteta. Kolme alkuperäistä tuotetta siemennetään vain uuteen kantaan. Ei automaattista julkaisua tai tietojen nollausta.
- Keycloakin samoja käyttäjiä käytetään ristikkäiseen tarkastukseen: yritys julkaisee verotuotteita, vero yritystuotteita. Uudet jäsenyydet lisätään kerran tunnettuun synteettiseen organisaatioon; vanhaa realmiä tai oikeuksia ei korvata. Kolmannelle organisaatiolle ei keksitä oikeuksia.
- Codespacesin määritykset säilyvät muuttumattomina: portti 8000, openBrowser ja sovelluksen verkon jakaminen. README ja verkkodemon ohje edellyttävät Private-näkyvyyttä. README, ROADMAP, AGENTS, arkkitehtuuri ja tunnistusohje päivitetty; ratkaisun yksityiskohdat docs/phase-2c.md.

## Tässä tehtävässä todella ajettu

- Lukittu uv-riippuvuuksien asennus onnistui; RDFLib siirrettiin runtime-riippuvuudeksi. TypeScript-tarkistus ja Vite-tuotantobuild `npm run build --prefix apps/web` onnistuivat.
- `./scripts/cloud-build.sh` rakensi Docker-imagen pilven proxy-/CA-reitillä TLS-tarkistuksia säilyttäen. `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app, PostgreSQL ja Keycloak healthy olemassa olevilla voluumeilla.
- `.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q`: **39 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Viimeisen auth-testin tiukennuksen jälkeen 8 auth-testiä ajettiin erikseen uudelleen onnistuneesti; kyse ei ole 8 lisätestistä.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **7 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Oikea Chromium ja Keycloak, kaksi käyttäjää profiilitiedoston tuonnista tarkastuksen ja julkaisun kautta anonyymiin hakuun. Myös CRUD, mobiili, organisaationäkymä, reader/anonymous, organisaation muokkauseristys ja vanhentunut istunto.
- Yhteensä **46 eri testiä** läpäisi. Kirjastojen Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohitettuja testejä.
- Vanhan phase 1 -DDL:n muokattu tuotetieto, koko metadata (myös tuntematon sisäkkäinen kenttä), UUID ja aikaleima säilyivät. Erilliset 2A- ja 2B-päivitykset säilyttivät organisaation ja 2B-jäsenyyden. Tyhjä alustus ja toistuva migraatio/restart testattu. Samannimisiä tarjoajia ei yhdistetty.
- Oikeasti rinnakkaiset kaksi If-Match-muokkausta: yksi 200, toinen 412. Oman sisällön hyväksyntäkielto, hyväksynnän mitätöinti, idempotenssi, snapshot-/audit-triggerit ja outbox-virheen aiheuttama koko julkaisun rollback testattu.
- RDF/XML/Turtle/JSON-LD tuottivat saman graafitunnisteen; alkuperäinen tiedosto ladattiin takaisin. Puuttuvat riippuvuudet, pelkkä OWL/konteksti/johdannainen, etäkonteksti, XML DTD/ENTITY, vieras organisaatio ja henkilökohtaisen koodin URL hylättiin odotetusti. Käytettävän VC-palvelun metadata- ja binding-polku testattiin synteettisenä, ilman yhteyttä kyseiseen palveluun.
- Tavallinen app-restart ja Compose-readiness ajettiin. Ennen/jälkeen tarkistetut kaikki katalogirivit säilyivät samoina: 6 tuotetta/luonnosta, 3 organisaatiota, 5 jäsenyyttä, 3 profiilisnapshotia, 3 julkaisua/tarkastusta/outboxia ja 21 audit-tapahtumaa. Kolme lisäjulkaisua ovat selaintestin synteettisiä, tarkoituksella muuttumattomaan historiaan jääviä tietueita. PostgreSQL-/Keycloak-volumea ei poistettu.
- Alembic current: `0004_publication (head)`. Alembic check: `No new upgrade operations detected.`
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: hostname/callback samalla portilla 8000, workspace service:app-verkossa, openBrowser ennallaan. `.devcontainer`-diff on tyhjä.
- `git diff --check`: ei whitespace-virheitä.

Kehityksen aikaiset epäonnistumiset korjattiin: migraatiotestien siivoukseen jäänyt PostgreSQL-funktio, versio-IRI:n muutosta vastaamattomat vientitestien oletukset ja pitkän julkaistun nimen mobiilirivitys. Lopulliset yllä raportoidut ajot läpäisivät korjausten jälkeen.

## Ajamattomat tarkistukset ja rajat

- Oikeaa GitHub Codespacea, GitHubin Private-portin pääsynvalvontaa ja automaattista selainvälilehteä ei ajettu tämän Linux-pilvikoneen sisältä. Asetusten staattinen tarkistus ei korvaa tätä. README sisältää ennen yhdistämistä käytettävän haaralinkin ja kokeilupolun.
- Windows/Docker Desktop, tavallinen `docker compose up --build` ilman tämän pilven build-wrapperia, tyhjän välimuistin Windows-build ja GitHub Actions -etäajo jäivät ajamatta. Niiden onnistumista ei väitetä. Ohjeen Windows-komento on `docker compose up --build`, osoite http://localhost:8000.
- Elävän Tietomallit-palvelun linkkituontia ei ajettu. Linkki/tiedosto-vaihtoehdon testissä verkkovastaus korvataan hallitulla fixturellä; todellinen tiedostotuonti ajettiin selaimessa. Synteettinen profiilifixture ei ole oikea Tietomallit-export.
- Myöntämistä, todellista issuer-linkin saavutettavuutta, myöntäjän luottamusta, EUDIW/EBW-yhteentoimivuutta, SHACL-instanssivalidointia tai DCAT-AP-vaatimustenmukaisuutta ei todennettu. Ei vaihetta 3.
- Yksi VC-jakelu/tuote; usean myöntäjän valinta, laajempi elinkaari ja jäsenyyksien hallinta jäävät jatkoon. Profiilin selainlomake on yksinkertainen; moniosaiset riippuvuudet/johdannaiset annetaan API:lla. VC-metatietoja ylläpidetään JSON-kentässä. Haku suodattaa demomäärän muistissa, suorituskykyä tai saavutettavuusvaatimusten täyttymistä ei ole auditoitu.

## Toimitus

Haara `feat/phase-2c-publication` on pushattu GitHubiin. Pull requestia **ei luotu**: sekä `gh pr create --base main --head feat/phase-2c-publication --title ... --body-file docs/pull-request.md` että REST-varayritys `gh api --method POST repos/jgmikael/metatietovaranto/pulls --input /tmp/phase2c-pr.json` palauttivat `Post https://api.github.com/...: Forbidden`. Tämä on ympäristön GitHub API -pääsyn este; Git-push onnistui. Valmis kuvaus on docs/pull-request.md. PR:n voi avata selaimessa https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2c-publication . Main-haaraan ei yhdistetty mitään.

---

# Aikaisempien toimitusten historia (ei tämän ajon tuloksia)

# Vaihe 2B — OIDC ja organisaatiokohtainen tuoteylläpito

Tarkistettu 14.10.2026. Pohjana `origin/main` commit `0e6a2a2` (käyttäjän yhdistämä ja selaimessa toimivaksi vahvistama vaihe 2A). Työhaara `feat/phase-2b-auth`. Main-haaraan ei yhdistetä automaattisesti.

## Toteutettu

- Keycloak OIDC Authorization Code + PKCE S256, selainkohtainen kertakäyttöinen state, nonce ja allekirjoitetun ID-tokenin issuer/audience/voimassaolo/azp-tarkistukset. Ei kirjautumisen demo-ohitusta tai luottamusta käyttäjän lähettämään organisaatio-otsakkeeseen.
- Palvelinistunto PostgreSQL:ssä, selaimessa opaque HttpOnly/SameSite=Lax-eväste (HTTPS:ssä Secure), CSRF-otsaketarkistus kirjoituksille ja uloskirjautumiselle. Access-/refresh-/ID-tokenit eivät päädy selaimen localStorageen tai pysyvään sovellusistuntoon. Auth-vastaukset ovat no-store. Deployatun Uvicornin access-log on pois käytöstä.
- Organisaation editor/reader-jäsenyydet tietokannassa. Tuotteen lisäys, muokkaus ja poisto tarkistavat oikeudet palvelimella; PUT tarkistaa sekä alkuperäisen että uuden tarjoajan. Jäsenyyden poisto vaikuttaa seuraavaan kirjoituspyyntöön, eikä restart palauta poistettuja oikeuksia.
- Anonyymi haku, tuotesivu, organisaatiot ja JSON-/JSON-LD-vienti säilyvät. Tässä vaiheessa ei ole luonnoksia tai rajattujen tietotuotteiden näkyvyysmallia.
- Kolme synteettistä demotunnusta: vero/demo-vero, yritys/demo-yritys ja lukija/demo-lukija. Muokkaajat kuuluvat kahteen eri alkuperäiseen demo-organisaatioon; lukija ei voi kirjoittaa. Muut organisaatiot eivät saa oikeuksia nimen perusteella.
- Uloskirjautuminen poistaa sovellusistunnon ja jatkaa Keycloakin standardiin Log out -vahvistukseen. Käyttäjän vaihtaminen samalla selaimella testattu. API:n pelkkä POST /auth/logout päättää vain sovellusistunnon; koko selainuloskirjautuminen sisältää IdP-vahvistuksen.
- Migraatio 0003_auth lisää jäsenyys-/istunto-/OIDC-tilataulut. Aiemmat 0001/0002-revisiot, organisaatioiden UUID:t ja tuotetiedot säilyvät. Demojäsenyydet lisätään vain kerran tunnetuilla UUID:illä.
- Codespaces käyttää edelleen yhtä Private-selainporttia 8000. /identity-proxy välittää vain oman realmin ja resurssien pyynnöt; ei admin-konsolia tai yleistä URL-proxyä. Keycloak lisättiin käynnistyspalveluihin ja saa Codespacesin tarkan hostname-/callback-osoitteen. onAutoForward=openBrowser ja portin 8000 määritys säilyvät.
- Keycloak on digestillä lukittu development-image, erillinen keycloakdata-volume. Java-heap 128–512 MiB hillitsee demon muistinkulutusta; oikean 2-core Codespacen resurssimittausta ei tehty.

## Tässä tehtävässä todella ajettu

- Uusien runtime-riippuvuuksien lukittu uv-asennus onnistui; httpx siirrettiin runtime-riippuvuudeksi, PyJWT/cryptography lisättiin.
- `npm run build --prefix apps/web`: TypeScript ja Vite-tuotantobuild onnistuivat.
- Keycloak-imagen lataus onnistui tarkistetulla digestillä; realm tuotiin omaan uuteen testivolumeen.
- `./scripts/cloud-build.sh` ja `docker compose up -d --no-build --wait`: app, db ja keycloak healthy. Käytettiin pilven olemassa olevaa proxy-/CA-reittiä; TLS-tarkistusta ei ohitettu.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest -q`: **33 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**: 9 API-/PostgreSQL-/RDF, 8 auth, 7 migraatio ja 3 osoitteenmuodostustestiä sekä 6 oikean Chromiumin selainkoetta.
- Selainkokeet: aiempi haku–lisäys–muokkaus–poisto kirjautuneena, mobiili, organisaationäkymä, anonyymi/lukija, toisen organisaation muokkaaja ja vanhentunut sovellusistunto. Oikea Keycloak-kirjautuminen kaikilla kolmella tunnuksella, HttpOnly/SameSite-eväste, uloskirjautuminen ja käyttäjän vaihtaminen samalla selaimella tarkistettu.
- API:n kielteiset testit: anonyymi ja väärennetty eväste, väärä/puuttuva CSRF, lukijan kirjoitus, toisen organisaation muokkaus/poisto, tuotteen siirto toiseen organisaatioon, väärennetyt identity-/organization-otsakkeet, vanhentunut istunto ja poistettu jäsenyys.
- OIDC-testit: PKCE/state/selaincookie-sidonta, state-vanheneminen ja uusintakäytön esto, virheellinen token, väärä issuer/audience/nonce/azp/algoritmi ja exp sekä HTTPS-cookien Secure-asetus. Proxy-rajan admin-/master-/traversal-pyynnöt hylätään.
- Vanhojen vaiheen 1 migraatiotestien lisäksi uusi 2A → 2B -testi säilyttää tuotteen ja organisaation kaikki kentät ja tunnisteet myös toistetussa päivityksessä. Custom-organisaatiolle ei synny automaattisia demooikeuksia.
- Java-heap-asetuksen jälkeen Keycloak käynnistettiin uudelleen samoilla voluumeilla ja kuusi selaintestiä läpäisi uudelleen. PostgreSQL-volumea ei poistettu.
- Alembic current: `0003_auth (head)`. Alembic check: `No new upgrade operations detected.`
- Codespacesin yhdistetty Compose validoitiin synteettisellä CODESPACE_NAME-arvolla: Keycloak-hostname osoittaa saman portin 8000 HTTPS-osoitteeseen, workspace jakaa app-palvelun verkon.

Testikehityksessä korjattiin puuttunut auth-routerin rekisteröinti, Keycloakin demoprofiilien sähköpostitiedot ja SQL-testifixturen JSON-parametrointi. Selainkoe paljasti, että pelkkä sovellusuloskirjautuminen jätti IdP-SSO:n voimaan; lopulliseen selainpolkuun lisättiin Keycloakin normaali end-session-vahvistus. Uusi, vain tässä tehtävässä luotu Keycloak-testivolume nollattiin fixtureiden korjausten yhteydessä; olemassa oleva PostgreSQL- ja tuotetieto säilyi. Lopullinen 33 testin ajo läpäisi. Neljä aiempaa Starlette/httpx- ja RDFLib-deprekaatiovaroitusta eivät ole ohitettuja testejä.

## Rajat ja ajamattomat tarkistukset

- Oikeaa GitHub Codespacea, sen Private-portin pääsynvalvontaa ja automaattista selainvälilehden avautumista ei ajettu tämän pilvikoneen sisältä. Tarkka ennen yhdistämistä tehtävä kokeilu on READMEssä.
- Windows/Docker Desktop, ensimmäinen build tyhjällä välimuistilla ja GitHub Actions -etäajo jäivät ajamatta. CI päivitettiin käynnistämään oikea Keycloak/Compose-demo selaintesteille erillisellä tietokannalla.
- Keycloak toimii development-konfiguraatiolla synteettisillä salasanoilla. Tuotannon IdP, MFA, jäsenyyksien hallinta-UI, sessionhallinnan UI ja back-channel logout eivät kuulu tähän rajaukseen. IdP-tilin poistaminen ei yksin peru jo myönnettyä kahdeksan tunnin sovellusistuntoa; organisaatiojäsenyyden peruminen estää kirjoittamisen heti.
- Hyväksyntä, julkaisuversiot, auditointi, optimistinen lukitus, SHACL ja ulkoiset integraatiot jäävät erillisiksi vaiheiksi. Julkisista metatiedoista ei tehdä tässä vaiheessa organisaatiolle piilotettuja luonnoksia.
- Haara `feat/phase-2b-auth` on pushattu GitHubiin. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2b-auth --title "Vaihe 2B: OIDC-kirjautuminen ja organisaatiokohtainen ylläpito" --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Valmis kuvaus on docs/pull-request.md ja PR:n voi avata selaimessa osoitteesta https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2b-auth . Main-haaraan ei yhdistetty mitään.

---

# Aikaisempien toimitusten historiatiedot

Alla ovat aiempien vaiheiden raportit. Vaihe 2A on käyttäjän ilmoituksen ja origin/mainin perusteella yhdistetty ja toimiva. Alla mainittu sen vanha PR-este on ratkaistu käyttäjän tekemällä PR:llä; yllä ovat tämän muutoksen tulokset.

# Vaihe 2A — migraatiot ja tarjoajaorganisaatiot

Tarkistettu 14.10.2026. Pohjana nykyinen `origin/main`, commit `c582dbc` (Codespaces-toimitus mukana). Uusi työhaara: `feat/phase-2a-organizations`. Main-haaraa ei muuteta eikä yhdistetä automaattisesti.

## Toteutettu

- Alembicin `0001_phase1` luo alkuperäisen skeeman tyhjään kantaan tai ottaa tarkistetun vanhan skeeman käyttöön. Tuntemattomat taulut, sarakkeet, tyypit, null-rajoitteet, indeksit tai pääavaimet keskeyttävät käyttöönoton. Ei sokeaa stamp-komentoa tai sovelluksen create_all-kutsua.
- `0002_organizations` lisää organisaatiot (UUID, legalName, country, scheme/value-tunnisteet, synthetic) ja tuotteen NOT NULL -vierasavaimen. Vanhojen tuotteiden kaikki aiemmat sarakkeet, UUID:t ja aikaleimat säilyvät. Jokainen vanha tarjoaja saa erillisen organisaation per tuote; samannimisiä ei yhdistetä. Tuntematon maa on ZZ eikä tunnisteita keksitä. legacyProductId säilyttää siirron alkuperän.
- Migraatiot suoritetaan yhdessä PostgreSQL-transaktiossa advisory-lukolla ennen fixtureitä ja readiness-tilaa. Sama FastAPI-startup toimii Composessa ja Codespacesissa. Migraatiovirhe estää käynnistyksen; tuntemattoman skeeman virhetesti varmisti transaktion peruuntumisen.
- Vanhaa kantaa ei siemennetä uudelleen, myöskään jos tuotteet on poistettu tai alustusmerkintä puuttuu. Uusi tyhjä demo saa edelleen kolme synteettistä tuotetta ja organisaatiota.
- Organisaatioiden listaus- ja yksittäisen organisaation luku-API, selainlista ja perustietonäkymä. Tuotelomakkeessa tarjoaja valitaan organisaation UUID:llä. Tarjoajanimi säilyy haussa, tuotesivulla ja JSON-/JSON-LD-viennissä.
- Tuotteen kirjoitus-API vaatii nyt providerOrganizationId-kentän vapaatekstisen provider-kentän sijaan. Tämä muutos ja migraatioiden rajoitukset on dokumentoitu READMEssä. Organisaatioiden luonti-/muokkausprosessia ei lisätty.
- Codespacesin `.devcontainer`-määritykset ja public_url-logiikka säilyivät muuttumattomina: portti 8000, openBrowser-automaattiavaus ja nykyinen app-verkon jakaminen. Ohje säilyttää portin Private-tilassa.

## Tässä tehtävässä todella ajettu

- Lukittu uv-asennus ja uuden Alembic-riippuvuuden asennus onnistui.
- `npm run build --prefix apps/web`: TypeScript-tarkistus ja Vite-tuotantobuild onnistuivat.
- `./scripts/cloud-build.sh`: Docker-imagen build onnistui pilven tuetulla proxy-/CA-reitillä. TLS-varmennusta ei ohitettu. Tavallisen Docker Desktopin kylmää buildia ei tässä tehtävässä ajettu.
- `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app ja db healthy olemassa olevan vaiheen 1 volumen päällä.
- `BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest -q`: **21 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. 9 API-/PostgreSQL-/RDF-testiä, 6 migraatiotestiä, 3 Chromium-selaintestiä ja 3 Codespaces-/paikallisosoitteen muodostustestiä.
- Migraatiotesteissä vanha rakenne luotiin riippumattomalla phase 1 -DDL:llä. Muokattu demo ja toinen samanniminen tarjoaja säilyttivät kaikki alkuperäiset sarakkeet (myös ylimääräisen sisäkkäisen JSON-metatiedon ja tarkat aikaleimat). Tuotteiden UUID:t ja organisaatioiden viitteet säilyivät uusinta-ajossa. Testi ajettiin sekä olemassa olevan alustusmerkinnän kanssa että ilman sitä.
- Tyhjä kanta, ensimmäinen migraatio erikseen, toistetut upgrade-ajot, tyhjä vanha kanta, FK:n pakollisuus ja tuntemattoman skeeman transaktionaalinen hylkäys testattu. Testit tyhjensivät vain `catalog_test`-kantaa.
- Aiemmat haku–tuotesivu–lisäys–muokkaus–poisto- ja mobiiliselainpolut läpäisivät. Ainoana tarvittavana sopeutuksena vanhan tarjoajatekstin syöttö vaihdettiin organisaatiovalintaan. Uusi organisaatiopolku tarkisti listan, perustiedot, uudelleenlatauksen ja tuotteen tarjoajalinkin.
- `docker compose exec -T app .venv/bin/alembic current`: `0002_organizations (head)`.
- `docker compose exec -T app .venv/bin/alembic check`: `No new upgrade operations detected.`
- Codespacesin Compose-tiedostojen yhdistäminen `docker compose ... config --format json` onnistui; workspace jakaa edelleen app-palvelun verkon. `.devcontainer`-tiedostojen diff on tyhjä.

Ensimmäinen selainajo paljasti valinnan kenttäotsikon kohdistusongelman; korjattu eksplisiittisellä label/htmlFor/id-yhdistelmällä. Alembicin CLI-ajon tiedosto-oikeusongelma korjattiin antamalla pyproject.toml/uv.lock-tiedostot imagessa sovelluskäyttäjän omistukseen. Lopullinen koko 21 testin ajo ja CLI-tarkistukset onnistuivat korjausten jälkeen. Neljä kirjastojen deprekaatiovaroitusta (Starlette/httpx ja RDFLib) eivät ole ohitettuja testejä.

## Ajamattomat ja ulkoiset tarkistukset

- Oikeaa GitHub Codespaces -ympäristöä, sen selainvälilehden automaattista avautumista ja Private-portin GitHub-pääsynvalvontaa ei voitu todentaa tämän Linux-pilvikoneen sisältä. Käyttäjän toimivaksi vahvistamia asetuksia ei muutettu. Kokeilu ennen yhdistämistä: READMEn linkki haaraan feat/phase-2a-organizations, uusi Codespace, PORTS → 8000 → Open in Browser, näkyvyys Private.
- Windows/Docker Desktop -ajoa tai GitHub Actions -etä-CI:tä ei tässä tehtävässä ajettu.
- Vaiheen 2A ulkopuolelle jäivät kirjautuminen, käyttöoikeudet, hyväksyntä, julkaisuversiot, SHACL ja ulkoiset integraatiot. Niiden toimivuutta tai DCAT-AP-vaatimustenmukaisuutta ei väitetä.
- Työ pushattu GitHubiin haaraan `feat/phase-2a-organizations`. Pull requestia **ei luotu**: `gh pr create --base main --head feat/phase-2a-organizations --title "Vaihe 2A: Alembic-migraatiot ja tarjoajaorganisaatiot" --body-file docs/pull-request.md` palautti `Post https://api.github.com/graphql: Forbidden`. Ympäristön GitHub API -verkkopääsy on avattava luontia varten, tai PR:n voi avata selaimessa osoitteesta https://github.com/jgmikael/metatietovaranto/compare/main...feat/phase-2a-organizations . Valmis kuvaus on `docs/pull-request.md`. Main-haaraan ei yhdistetty mitään.

---

# Aiemman toimituksen historiatiedot

Alla olevat vaiheen 1 ja Codespaces-toimituksen raportit ovat aikaisempia ajoja. Tämän muutoksen tulokset ovat yllä.

# Vaiheen 1 tila

## Selainkokeilu GitHub Codespacesissa

Lisätty haaraan `demo/codespaces` Dev Container -määritys. Se käynnistää nykyisen Compose-sovelluksen ja PostgreSQL:n sekä avaa portin 8000. Uusi työtilakontti jakaa sovelluksen verkon, joten porttiohjaus osuu FastAPI-palveluun. Paikallinen Compose säilyy ennallaan. Metatiedon URI voi käyttää Codespacesin välitettyä osoitetta ympäristömuuttujien perusteella.

Tässä muutoksessa ajettu: kolme `tests/test_public_url.py`-testiä onnistui; TypeScript-tarkistus ja Vite-tuotantobuild onnistuivat; Python-tiedostojen käännöstarkistus onnistui. Docker-/PostgreSQL-integraatioita, selaintestejä ja Codespacesin oikeaa käynnistystä ei ajettu tässä ympäristössä, jossa ei ole Dockeria tai PostgreSQL-palvelinta. Alla olevat aiemman toimituksen testitulokset säilyvät historiatietona eivätkä ole tämän muutoksen uusinta-ajo.

Ohje: `docs/verkkodemo.md`. Portti säilytetään Private-tilassa. Sovellukseen ei lisätty vaiheen 2 tunnistus- tai valtuutusjärjestelmää. Käynnistys GitHub-tilillä ja sen Codespaces-kiintiöllä on käyttäjän tehtävä.

Tarkistettu 14.10.2026. Työhaara: `feat/phase-1-local-demo`. Tavoitearkkitehtuuri säilyy alkuperäisessä suunnitteludokumentissa; tämän toimituksen rajaus on ROADMAPin vaihe 1.

## Toteutettu

| Vaiheen 1 vaatimus | Toteutus ja todennus |
| --- | --- |
| Tietotuotteiden ylläpito | React-lomake ja FastAPI CRUD; lisäys, muokkaus, poisto ja virheellisten syötteiden hylkäys testattu. |
| Haku | Tekstihaku, tarkka teema/tarjoaja ja sivutus PostgreSQL-kyselyillä; API- ja selaintestit. |
| Tuotesivu | Kuvaus, lähde, tarjoaja, käyttötarkoitus, rajaukset, käyttöehdot, saatavuus ja tietoelementit; selainpolku ja uudelleenlataus testattu. |
| PostgreSQL | Oikea PostgreSQL 17, pysyvä Compose-volume; tallennus varmistettu erillisellä DB-yhteydellä. |
| JSON-vienti | Tuote ja katalogi; vienti vastaa tallennettua tuotetta. |
| JSON-LD-vienti | Tuote ja DCAT-katalogi; RDFLib jäsentää RDF-graafin ja tarkistaa Dataset-, title- ja semanticUri-merkitykset. |
| Kolme synteettistä tuotetta | Verovelkatieto, yrityksen perustiedot ja ammattipätevyys; idempotentti kertaluonteinen siemennys säilyttää muokkaukset ja poistot. |
| Käynnistys | README: Compose ja host-kehitys; tässä pilvessä testattu cloud-build.sh ja Compose --no-build --wait. |
| Rajaus ja agenttiohjeet | ROADMAP.md, AGENTS.md ja arkkitehtuurikuvaus. |

## Ajettu todennus

- `uv sync --locked`: onnistui Python 3.12:lla.
- `npm ci --prefix apps/web` ja `npm run build --prefix apps/web`: onnistui; TypeScript-tarkistus ja Vite-tuotantobuild.
- `./scripts/cloud-build.sh`: Docker-image rakennettu onnistuneesti; TLS- ja pakettitarkistukset säilytetty.
- `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait`: app ja db healthy.
- `GET /health/ready`: `status=ready`, `database=postgresql`.
- `BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest -q`: **9 läpäissyttä, 0 epäonnistunutta, 0 ohitettua**. Seitsemän API-/PostgreSQL-/RDF-testiä ja kaksi oikealla Chromiumilla ajettua selaintestiä.
- Selainpolku: haku → tuotesivu → uuden synteettisen tuotteen lisäys → uudelleenlataus → muokkaus → vahvistettu poisto. Reactin skriptitekstin käsittely tekstinä tarkistettu. Mobiilinäkymän vaakasuuntainen mahtuminen tarkistettu.
- `docker compose restart app` ja uusi Compose-readiness: onnistui; toiminnallinen haku palautti edelleen kolme demotuotetta.
- Sovelluksen uudelleenalustustesti varmistaa, että muokkaus ja poistettu demotuote eivät palaudu alkuperäiseen tilaan.
- `git diff --check`: ei whitespace-virheitä.

Ensimmäisessä testikehityksen ajossa fixture-apufunktion matala kopio aiheutti kahden testin epäonnistumisen; korjattu syvällä kopiolla. Ensimmäisen konttikäynnistyksen tiedosto-oikeusongelma korjattu COPY --chown -asetuksella. Koko yhdeksän testin sarja ajettu uudelleen onnistuneesti korjattua Compose-sovellusta vasten. Testikirjastot tuottavat kolme deprekaatiovaroitusta (Starletten TestClient/httpx sekä RDFLibin ConjunctiveGraph); testitulokset eivät ole ohituksia.

## Rajat ja myöhemmät vaiheet

- Ei kirjautumista, organisaatiokohtaisia oikeuksia, hyväksyntää, julkaisuversioita tai SHACL:ia: vaihe 2.
- Ei ulkoisia lompakko-, QEAA- tai data-avaruusintegraatioita: vaihe 3.
- DCAT-AP-vaatimustenmukaisuutta, tuotantovalmiutta, WCAG-vaatimustenmukaisuutta tai kuormitustavoitteiden toteutumista ei ole todennettu. Mobiilin ja lomakkeiden perustestit eivät korvaa saavutettavuusauditointia.
- Vaiheen 1 skeema luodaan SQLAlchemyllä. Lisää Alembic ennen skeeman ensimmäistä muutosta.
- GitHub Actions -workflow on mukana, mutta etä-CI:n suoritusta ei ole tässä todettu.

## Toimitus ja pilviasetukset

Asennusskripti ja palvelujen käynnistysohjeet tallennettu pilviympäristön luonnokseen (`install_script`, `start_skill`); tallennus ei julkaise ympäristöä. Verkkoluonnokseen lisätty GitHub API ja Playwrightin latausosoitteet. Nykyisessä koneessa selaintestit käyttävät valmista Chromiumia, eikä latauksia tarvittu. Haara `feat/phase-1-local-demo` on pushattu onnistuneesti GitHubiin. Pull requestia ei ole luotu: `gh pr create --base main --head feat/phase-1-local-demo` pysähtyi `POST https://api.github.com/graphql: Forbidden` -virheeseen. Aktivoi `api.github.com` ympäristön verkkoasetuksissa ja suorita tämän jälkeen `gh pr create --base main --head feat/phase-1-local-demo --title "Vaihe 1: paikallinen PostgreSQL-metatietohakemisto" --body-file docs/pull-request.md`. PR-kuvaus on tallennettu tiedostoon `docs/pull-request.md`. Main-haaraan ei ole yhdistetty muutoksia eikä vaihetta 2 aloitettu.

