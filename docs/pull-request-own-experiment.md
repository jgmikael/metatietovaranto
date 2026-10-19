## Muutos

Pages-esittelyä pystyi aiemmin vain lukemaan. **Aloita oma kokeilu** kopioi nyt synteettiset tuotteet ja organisaatiot vain selaimen paikalliseen työtilaan. Käyttäjä voi ylläpitää niitä ja kolmen toimitustavan metadataa, valita mukana toimitetun SHACL-profiilin, tarkastella alkuperäisiä artefakteja sekä viedä/palauttaa koko kokeilun JSONina. Julkinen katalogi ja tavallinen palvelinsovellus säilyvät toimivina.

Yhteiset DTO:t, peruslomake, DistributionEditor/View ja TechnicalPackagePanel. Ei uutta palvelinta tai npm-riippuvuutta. Version 1 paikallistallenne, 500 ms automaattitallennus, takaisinlukuvahvistus, Web Locks + edellisen tallenteen vertailu. Kiintiö-/käyttöestot, välilehtiristiriidat, vioittunut/tuntematon tallenne ja muuttuneen demoversion puuttuvat tarkisteviitteet käsitellään ilman hiljaista korvaamista.

Siirtoformaatti 1 sallii vain tunnetun rakenteen, enintään 2 MiB. Tuonti tarkistaa koko tiedoston, yksilölliset tunnisteet ja organisaatio-/profiiliviitteet ennen erikseen vahvistettua kokonaiskorvaamista. Epäonnistunut tarkistus tai tallennus ei korvaa aiempaa kokeilua. Reset muuttaa vain oman kokeilun avainta. Ei HTML:n suorittamista tai tuonti-URLien automaattinoutoja.

Paikallinen tuote on aina **Ei validoitu tässä kokeilussa**; alkuperäisen paketin raportit ovat vain erillisen lähtöesimerkin tuloksia. Myöntämis- ja lähdetietotoiminnot estetään paikallisesti myös production-metadatalla. Ei uutta hyväksyntäprosessia, generointia, SHACL-validointia tai integraatioita. Ei muutoksia vanhoihin palvelinsovelluksen snapshotteihin/julkaisuihin tai tietokantaskeemaan.

## CI:ssä löytyneen tuonnin ajoitusvirheen korjaus

Vahvistettu JSON-tuonti ja alkuperäisten esimerkkien palautus jättivät näytölle edellisen operaation `Tallennettu`-tilan uuden asynkronisen kirjoituksen ajaksi. Alkuperäinen testi saattoi siksi jatkaa ennen uuden tallenteen valmistumista ja nähdä vanhan tuotteen nimen. Tämä ei osoittanut tietojen palautumista tuonnin jälkeen, vaan ennenaikaisen onnistumisilmoituksen.

Korvaaminen näyttää nyt heti `Tallennetaan…`. Myös edeltävän automaattitallennuksen valmistuminen estetään merkitsemästä kesken olevaa korvaamista tallennetuksi. Uudet tuonnin ja resetin regressiokokeet varaavat oikean Web Lockin: ennen lukon vapautusta vanha tallenne säilyy ja tila on keskeneräinen; vapautuksen jälkeen uusi aineisto tallentuu ja säilyy reloadissa. Molemmat kokeet epäonnistuivat ennen sovelluskorjausta.

Korjauksen jälkeen koko staattinen sarja: **30 passed in 63.99s**, Pages-build ja tavallinen web-build läpäisivät. API-/palvelinselaintulokset alla ovat aiemmalta toteutuscommitilta; niitä ei ajettu uudelleen tähän vain paikallisen korvaustilan muutokseen. GitHubin uusi PR-CI on tarkistettava erikseen.

## Ajetut tarkistukset

- Pages-build ja normaali TypeScript/Vite-build: läpäisivät.
- `pytest tests_static -q`: **30 passed**, ei ohituksia tai JavaScript-/konsolivirheitä. Todellinen staattinen HTTP-palvelin `/metatietovaranto/`-alipolussa, kaikki backend-, auth-, identity-, ulkoiset ja kirjoituspyynnöt kielletty. Kattaa julkisen esittelyn, CRUDin, reloadin, JSON-siirron ja virhetilanteet, kiintiö-/käyttöestot, kaksi oikeaa välilehteä Web Locks -jonossa, resetin ja puuttuvat profiili-/pakettiviitteet uuden version jälkeen. Väliajon ajoituksesta riippuva testijärjestys korjattiin odottamaan todellista lukkojonoa; lopullinen täysi ajo läpäisi.
- `pytest tests/test_api.py tests/test_auth.py tests/test_publication.py tests/test_public_url.py -q`: **24 passed**, 3 Starlette/RDFLib-varoitusta. Oma catalog_test-kanta.
- Oikea Docker-build ja Compose-startup: kaikki palvelut healthy. Ennen/jälkeen vertailu: 13 tuotantodemon tietokantataulua ja Alembic head muuttumattomia. Volumet säilytettiin.
- Vanhojen julkaisujen lisälukukoe: **97 versiota, 8 vanhaa pakettia, 78 artefaktia** läpäisi.
- `BROWSER_BASE_URL=http://localhost:8000 pytest tests/test_browser.py -q`: **13 passed**, 1 Starlette-varoitus. Oikea Chromium + Keycloak: tallennus/uudelleenavaaminen, oikeudet, hyväksyntä, julkaisu, elinkaari ja paketit. Testit jättävät omat synteettiset julkaisut historiaan.
- **67 eri pytest-testiä yhteensä**, ei ohituksia. Paikallinen dokumentoitu preview ja desktop-/390 px mobiilikuvakaappaus tarkastettu. `git diff --check` läpäisi.

## Rajat / ajamatta

Koko taustapalvelimen 209 testin SHACL-/muunnos-/migraatiosarjaa ja tyhjän/vanhan kannan migraatioajoja ei toistettu, sillä backend tai tietokantaskeema eivät muutu. Olemassa olevan kannan säilyminen tarkistettiin. Ei natiivia Windows-, Firefox- tai Safari-ajoa. Tallennuksen esto/kiintiö testattiin virheinjektiolla, ei täyttämällä levyn kiintiötä. Web Locks -tukea tarvitaan turvalliseen pysyvään tallennukseen; puuttumisesta ilmoitetaan. Selainkohtainen tallennus ei ole palvelinvarmuuskopio; selain voi poistaa sen. Vie tärkeä kokeilu JSONiksi.

Uutta kokeilutilaa ei ole julkaistu tai HTTP-varmennettu julkisessa Pagesissa. GitHubin PR-tarkistusten etätulos on tarkistettava ennen yhdistämistä. Toteutuksen paikallisissa tarkistuksissa ei todettu yhdistämisestettä. Älä yhdistä automaattisesti.

## Mitä käyttäjä tekee yhdistämisen jälkeen

1. Yhdistä tarkistettu PR mainiin normaalisti. Nykyinen **Public Pages demo** käynnistyy main-pushista; Pages-asetuksia ei tarvitse muuttaa, jos aiempi julkaisu toimii.
2. Odota vihreää build/deploy-ajoa ja sen **Verify published HTTP responses** -vaihetta. Tarvittaessa Actions → Public Pages demo → Run workflow → main.
3. Avaa https://jgmikael.github.io/metatietovaranto/ ja valitse **Aloita oma kokeilu**. Muuta synteettistä tuotetta, odota **Tallennettu**, lataa sivu uudelleen ja kokeile JSON-vientiä. Julkisen esittelyn aineisto pysyy ennallaan.

Käyttö, tallennuksen rajat ja siirtoformaatti: `docs/own-experiment.md`. Tarkempi todennus: `STATUS.md`.
