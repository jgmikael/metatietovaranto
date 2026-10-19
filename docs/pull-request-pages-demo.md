## Ongelma ja tulos

Esittely on tähän asti vaatinut käynnissä olevan palvelinsovelluksen ja Codespacen tai paikallisen asennuksen. Tämä muutos lisää samalle React-käyttöliittymälle erillisen GitHub Pages -build-tilan. Julkaisun jälkeen synteettistä katalogia voi selata ilman kirjautumista, FastAPIa, PostgreSQL:ää tai Keycloakia.

Pohja: ajantasainen main **6b48536**, joka yhdisti PR #13:n. Toteutus ei muuta nykyisiä julkaisuja, snapshotteja, käyttöoikeuksia tai Codespacesin käynnistystä. Tätä PR:ää ei yhdistetä automaattisesti.

## Toteutus

- Sama App, yhteiset tietotyypit, komponentit ja ulkoasu. Pieni vain lukua tukeva adapteri lukee staattisen JSON-katalogin; palvelinbuild jatkaa nykyisen APIn käyttöä. Pages ei kutsu /api-, /auth- tai /identity-palveluja eikä näytä kirjautumista tai ylläpitoa.
- Lista, tekstihaku, teema/tarjoajasuodatus, suorat hash-tuotelinkit, organisaatiot, SHACL-lähde, kolmen toimitustavan kuvaukset sekä artefaktien tarkastelu/lataus ja attribuuttien semanttiset viittaukset.
- Kolme vanhaa synteettistä fixturetuotetta ja yksi kattava yhteisen SHACL-perustan esimerkki. Kaikki toimitustavat ovat planned; ei myöntämis- tai tietosisällön hakemisen onnistumisväitteitä. Esimerkkiversiot eivät ole varsinaisen sovelluksen hyväksyntäpäätöksiä.
- `bash scripts/build-pages.sh` muodostaa aineiston nykyisillä tyypitetyillä sopimuksilla ja generaattorilla sekä rakentaa erillisen dist-pages-hakemiston. Ei tietokannan tai käyttäjäaineiston vientiä. Buildin valitut syötteet ovat versionhallittuja, generoituja kuvauksia ei ylläpidetä käsin.
- Lopullinen Pages-perusosoite ja staattinen snapshot-URL annetaan ennen generointia/tarkisteita. Alkuperäiset IRI:t säilyvät. Uusista synteettisistä build-snapshoteista jätetään ajokohtaiset aikaleimat pois; vanhoja varsinaisen sovelluksen snapshotteja ei muokata.
- JSON-LD-serialisointi jaettiin tietokannattomaksi apumoduuliksi muuttamatta nykyisen APIn sisältöä. Generaattorin valinnainen snapshot_url vaikuttaa vain sitä erikseen käyttäviin staattisiin paketteihin; palvelimen oletusarvo säilyy.
- Virallinen Pages Actions -työnkulku rakentaa/testaa PR:n ilman deployta. Vain refs/heads/main saa julkaista, myös workflow_dispatch-ajossa. Deploy tarkistaa oikean julkaistun HTML:n ja katalogin HTTP-vastaukset.

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


## Käyttäjän tehtävät yhdistämisen jälkeen — ensimmäinen julkaisu

1. Yhdistä PR vasta vihreiden tarkistusten ja tarkastuksen jälkeen.
2. Repositorio → **Settings → Pages → Build and deployment → Source: GitHub Actions**. Älä muuta näkyvyyttä tai maksullisia asetuksia tätä tehtävää varten.
3. **Actions → Public Pages demo → Run workflow → main**. Jos Pages oli jo käytössä, main-merge käynnistää ajon automaattisesti. Jos deploy ehti epäonnistua ennen Pages-asetusta, käynnistä ajo uudelleen mainista.
4. Hyväksy tarvittaessa GitHubin github-pages-ympäristön deployment ja rajaa ympäristön julkaisu mainiin.
5. Varmista vihreät build/test/deploy/**Verify published HTTP responses** -vaiheet. Kokeile vasta tämän jälkeen tavoitetta **https://jgmikael.github.io/metatietovaranto/**, suoraa tuotelinkkiä, uudelleenlatausta ja context.jsonld-latausta.

**Osoitetta ei väitetä nyt julkaistuksi tai toimivaksi.** PR-haarasta ei julkaista. GitHubin Pages-/repoasetusten luku estyi tämän ympäristön API-yhteydellä Forbidden-vastaukseen, joten nykyistä Pages-tilaa, näkyvyyttä ja tilausrajoituksia ei voitu varmistaa. Jos Pages-valinta estyy tilauksen tai organisaatiopolitiikan vuoksi, käyttäjän on ratkaistava se omistajana. Tässä ei luoda uutta repositoriota tai muuteta maksullisia asetuksia.

## Rajat

Windows PowerShell -komennot on dokumentoitu, mutta Windowsia tai uutta Codespacea ei ajettu tässä ympäristössä. Varsinainen Pages-deploy ja GitHubin CDN/mediatyypit jäävät main-mergen jälkeiseen kokeeseen. GitHub Pages valitsee HTTP-mediatyypin tiedostopäätteestä; .schema.json voi saada application/jsonin, vaikka manifesti ilmoittaa application/schema+jsonin. Palvelinsovelluksen tarkat mediatyypit säilyvät.

Ei kirjautumista, luonnosten tallennusta, hyväksyntää, julkaisutoimintoa, palvelinpuolen generointia/validointia, lähdetietopalvelua, allekirjoitusta tai lompakkointegraatiota Pages-tilassa. Staattinen SHACL on nykyinen synteettinen ohjelmistofixture, ei aidoksi väitetty Tietomallit-export. Nykyisen rajatun generaattorin kattavuutta ei laajennettu.

[Tarkat komennot, aineiston alkuperä ja käyttöönotto](docs/github-pages-demo.md).
