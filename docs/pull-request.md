## Vaihe 2A: Alembic ja tarjoajaorganisaatiot

Nykyisen main-haaran demo säilyttää tietotuotteiden ylläpidon, haun, tuotesivun ja viennit. Tämä muutos lisää tietoja säilyttävän Alembic-päivityspolun sekä tarjoajaorganisaation pakollisen UUID-vierasavaimen. Codespacesin nykyisiä käynnistys-, portti- tai openBrowser-määrityksiä ei muuteta.

`0001_phase1` kuvaa alkuperäisen skeeman ja tarkistaa vanhan kannan ennen käyttöönottoa. `0002_organizations` luo kullekin vanhalle tuotteelle erillisen tarjoajaorganisaation: samannimisiä tarjoajia ei yhdistetä ilman identiteettinäyttöä. Maa on vanhassa aineistossa ZZ (tuntematon), tunnisteet tyhjiä ja alkuperä näkyy legacyProductId-kentässä. Migraatiot suoritetaan transaktion ja advisory-lukon alla ennen fixtureitä/readiness-tilaa. Vanhoja tuotteita, muokkauksia, aikaleimoja tai UUID:itä ei korvata.

Organisaatioita voi lukea API:sta ja uudesta näkymästä. Tuotelomake valitsee tarjoajan organisaatiolistasta. Tuotteiden kirjoitus-API edellyttää nyt providerOrganizationId-kenttää; provider-nimi säilyy vastauksissa ja vienneissä. README sisältää varmuuskopioinnin, päivityksen ja selainkokeilun ennen yhdistämistä.

## Todennus

- TypeScript-/Vite-build onnistui.
- Docker-image rakennettu ja Compose app/db healthy aiemman vaiheen 1 volumen päällä.
- 21 testiä läpäisi, ei ohituksia: 9 API/PostgreSQL/RDF, 6 migraatio, 3 Chromium, 3 osoitteenmuodostus.
- Vanhan skeeman muokatut tuotteet, kaikki alkuperäiset sarakkeet, sisäkkäiset JSON-tiedot ja tarkat aikaleimat säilyvät. Samannimisten tarjoajien identiteetit erottuvat. Testit kattavat tyhjän kannan, toistetut päivitykset ja virheellisen skeeman rollbackin.
- Alembic current: 0002_organizations (head). Alembic check: ei puuttuvia upgrade-operaatioita.
- Codespacesin yhdistetty Compose validoitu; oikeaa Codespacea, automaattista selainavausta tai etä-CI:tä ei tässä koneessa ajettu.

Ei kirjautumista, käyttöoikeuksia, hyväksyntää, julkaisuversioita, SHACL:ia tai ulkoisia integraatioita. Ei automaattista mergeä.

## Selainkokeilu ennen yhdistämistä

Luo uusi Codespace haarasta feat/phase-2a-organizations READMEn linkillä. Odota käynnistys, avaa PORTS → 8000 → Open in Browser ja säilytä näkyvyys Private. Kokeile Organisaatiot-näkymää sekä tuotteen Tarjoaja-valintaa ja aiempaa hakua/vientejä. Uusi Codespace käyttää omaa tyhjää kantaansa; olemassa olevan kannan tietojen säilyttävän päivityksen ohje on READMEssä.
