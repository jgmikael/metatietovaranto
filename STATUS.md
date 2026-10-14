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

Pull requestin kuvaus: docs/pull-request.md. Haaran push ja PR:n avaustulos kirjataan seuraavaksi. Mainiin ei yhdistetä automaattisesti.

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

