## Muutos

Julkaistun tuoteversion voi merkitä deprecated- tai withdrawn-tilaan omistajaorganisaation julkaisijan perustellulla komennolla. Deprecated näkyy varoituksella oletushaussa; withdrawn jää pois oletushausta ja katalogiviennistä. Pysyvä sivu, alkuperäinen sisältö/tarkiste ja julkinen tapahtumahistoria säilyvät. Withdrawn-versiolla ei näytetä palvelutoimintoja myöskään historiallisella versiosivulla. Puuttuva ajantasainen tilatieto estää palvelutoiminnot.

Migraatio `0005_lifecycle` lisää erilliset append-only-elinkaaritapahtumat ja outboxin. Tapahtuma, audit ja idempotenssivastaus tallentuvat samassa transaktiossa. Kirjoitus vaatii omistajan publisher-jäsenyyden, istunnon, CSRF:n, elinkaaren oman If-Match-ETagin ja Idempotency-Keyn. Korvaava versio on saman tuotteen myöhempi julkaisu. Vanhoja snapshotteja, hyväksyntöjä, luonnoksia, oikeuksia tai fixtureitä ei kirjoiteta uudelleen.

Versio-API:t ja version vienti säilyttävät alkuperäisen sisällön. Link- ja X-Product-Lifecycle-Status-otsakkeet ohjaavat erilliseen ajantasaiseen tilaan. Hakua voi laajentaa lifecycleStatus=all/withdrawn-rajauksella ja katalogivientiä includeWithdrawn=true-parametrilla. Poistetun uusimman tilalle ei automaattisesti nosteta vanhempaa versiota.

## Ennen yhdistämistä tehdyt tarkistukset — 17.10.2026

Tarkistettu sovelluskoodi `1146932`, haaran lähtötilana `d0a5232`; tässä esitarkistuksessa ei muutettu sovelluskoodia. Main on edelleen `79dc9d1` ja sisältyy työhaaraan. Käynnissä olevan imagen API-/migraatiotiedostojen ja web-buildin 26 tiedoston SHA-256-tarkisteet vastasivat checkoutia, joten selaintestit kohdistuivat tarkistettuun toteutukseen.

| Kohde | Todennus | Tulos |
| --- | --- | --- |
| API, PostgreSQL ja migraatiot | Koko nykyinen testisarja, erillinen catalog_test | **147 läpäissyttä**, 0 epäonnistunutta/ohitettua; 283,74 s |
| Käyttöliittymä | TypeScript + Vite-tuotantobuild | Läpäissyt |
| Oikea selain ja kirjautuminen | Koko selaintestisarja Chromiumilla ja oikealla Keycloak OIDC -ketjulla | **12 läpäissyttä**, 0 epäonnistunutta/ohitettua; 84,55 s |
| Vanhojen julkaisujen luettavuus | Kaikki demokannan 30 julkaisua: sisältötarkiste, tarkka versio-API-vastaus, elinkaari-GET ja julkinen haku | Läpäissyt; myös aito vanha julkaisu ilman versionUri-kenttää |
| Tallennus ja uudelleenavaus | Erillinen selainkokeilu: nimen muokkaus, tallennus, reload, revision/tarkisteen muutos | Läpäissyt |
| Validointi ja julkaisu | Virheellinen SHACL-esimerkki tallennettiin ja avattiin uudelleen; tarkastukseen lähetys palautti 422. Korjattu sisältö hyväksyttiin/julkaistiin eri käyttäjällä ja avattiin uudelleen | Läpäissyt |
| Käyttöoikeudet | Editorilta estettiin hyväksyntä ja elinkaarimuutos, publisherilta luonnoksen muokkaus; koko sarjassa myös reader, reviewer, väärä organisaatio, CSRF ja omistaja vs tarjoaja | Läpäissyt |
| Elinkaaren säilyminen | Deprecated ja withdrawn tallennettiin oikealla publisher-istunnolla; reload jokaisen jälkeen, historia 2 tapahtumaa, oletushaku/withdrawn-rajaus ja snapshot ennallaan | Läpäissyt |
| Atomisuus ja kilpailutilanteet | Testisarjan rollback, triggerit, rinnakkaiset komennot, idempotenssi ja vanha If-Match | Läpäissyt |
| Nykyinen tietokanta | Alembic current/check | 0005_lifecycle (head), ei skeemapoikkeamia |
| Migraatio vanhalla aineistolla | Alla kuvattu 0004 → 0005 -koe oikean demokannan metatietojen kopiolla sekä sarjan tyhjä/vanha kanta/toisto -testit | Läpäissyt |

Ajettu uudelleen tässä esitarkistuksessa:

```bash
.venv/bin/pytest tests/test_api.py tests/test_publication.py tests/test_profiles.py tests/test_semantic_validation.py tests/test_derived_validation.py tests/test_distributions.py tests/test_conversion.py tests/test_lifecycle.py tests/test_auth.py tests/test_migrations.py tests/test_public_url.py -q
npm run build --prefix apps/web
BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q
```

Yhteensä 159 eri pytest-testiä sekä erillinen toimintakokeilu ja aineistokopion migraatiokoe. Testitietokantaa tyhjentäviä ajoja ei ajettu samanaikaisesti. Starlette/httpx- ja RDFLib-varoitukset eivät ole ohituksia. Lyhyen selainkokeilun synteettinen tuote jää demokantaan withdrawn-tilassa; alkuperäisiä tuotteita ei muokattu. Aktiivisten palvelulinkkien renderöinti testattiin muistissa korvatuilla vastauksilla; olemattomia aktiivisia palveluita ei tallennettu eikä ulkoisia linkkejä avattu.

## Migraatio olemassa olevan aineiston kopiolla

Loin Alembicilla erilliseen catalog_test-kantaan toimitetun **0004-skeeman**, kopioin siihen nykyisen demokannan 11 yhteistä metatietotaulua ja ajoin **0004 → 0005**, migraation toiston ja oikean sovelluksen startupin. Kyse ei ollut elävän kannan downgradesta tai stampista. 2G:n uudet elinkaaritaulut eivät kuulu 0004-kopioon; ne luotiin migraatiossa tyhjinä. Istuntoja, OAuth-tiloja tai autentikoitujen pyyntöjen välimuisteja ei kopioitu.

Kopio sisälsi 37 tuotetta/luonnosta, 30 julkaisua/tarkastusta/julkaisuoutboxia, 22 profiilisnapshotia, 3 organisaatiota, 5 jäsenyyttä, yhden semanttisen profiilin, 197 audit-tapahtumaa ja 4 alustusmerkintää. **Kaikkien kopioitujen rivien koko sisältö ja tunnisteet säilyivät samoina** SHA-256-vertailussa päivityksen, toiston ja startupin jälkeen. Kaikki 30 versiota olivat luettavissa, mukaan lukien versionUri-kentätön julkaisu. Alkuperäinen catalog-kanta säilyi ennallaan koko kokeen ajan. Testikopio siivottiin kokeen jälkeen.

## Testaamatta jääneet asiat ja tunnetut rajat

- Windows/Docker Desktop, oikea Codespace sekä sen Private-portin pääsynvalvonta/automaattinen selainavaus ja GitHub Actionsin etätulos eivät ole tässä ympäristössä varmennettuja. Käyttäjän omaa demotestausta ei ole tehty eikä sitä oleteta tehdyksi.
- Tavallinen `docker compose up --build -d --wait` epäonnistui aiemmassa 2G-toteutusajossa tämän pilven build-verkon DNS-virheeseen Python-riippuvuuksien haussa. Pilven proxy-/CA-build-skripti ja sillä rakennetun imagen käynnistys toimivat. Tässä esitarkistuksessa Docker-imagea ei rakennettu uudelleen: sen vastaavuus nykyiseen sovelluskoodiin/buildiin tarkistettiin tiedostotarkisteilla. Suoran Compose-buildin virhettä ei kirjata läpäisseeksi tarkistukseksi.
- Ei kuormitus-, tuotantoturvallisuus- tai saavutettavuusauditointia eikä oikean lähde-/issuer-/wallet-palvelun testiä. Ulkoiset integraatiot eivät kuulu 2G:hen.
- Katalogin withdrawn ei peru ulkoisia käyttöoikeuksia tai myönnettyjä todistuksia. Alkuperäinen snapshot sisältää edelleen alkuperäiset palveluosoitteet; asiakas tarkistaa erillisen ajantasaisen tilan ennen niiden käyttöä.

## Yhdistämisarvio ja esteet

Paikallisissa automaattisissa tarkistuksissa, toimintakokeilussa ja aineistokopion migraatiossa **ei havaittu avointa toiminnallista yhdistämisestettä**. Oma demotestaus ei ole tämän arvion edellytys.

Suositus on ehdollinen: PR on saatava avattua ja sen pakollisten GitHub Actions -tarkistusten oltava vihreitä ennen yhdistämistä. GitHub API:n PR-tilan luku sekä PR:n luonti sekä GraphQL- että REST-reitillä palauttivat tässä ympäristössä Forbidden-vastauksen. PR:ää ei pystytty avaamaan eikä etä-CI:tä tai GitHubin mergeability-tilaa varmistamaan. Tämä on toimituksen este, ei testissä havaittu sovellusvirhe. Valmis kuvaus on tässä tiedostossa; luontiyritysten tiedot ovat STATUSissa. En anna varmennettua etä-CI:tä koskevaa hyväksyntää enkä yhdistä automaattisesti.

Täsmällinen toiminnallinen sopimus: docs/phase-2g.md. Tarkemmat tulokset: STATUS.md.
