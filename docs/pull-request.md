Vaihe 2C lisää organisaatioiden yksityiset luonnokset, eri kirjoittajan hyväksynnän ja muuttumattomat julkaisut. Julkinen haku ja JSON-/JSON-LD-viennit näyttävät vain julkaisuja; vanhat demotuotteet säilyvät tunnisteineen ja tietoineen keskeneräisinä luonnoksina. Työkopion muutokset eivät muuta vanhaa julkaisua.

PR:ien 5 ja 6 suunnitteluperiaatteet huomioidaan ennen julkaisurakenteen lukitsemista: SHACL-sisältöprofiili annetaan linkkinä tai tiedostona, snapshot säilyttää alkuperäiset artefaktit/IRI:t/riippuvuudet, ja tietoelementit johdetaan profiilista. W3C VC on ensisijainen toimitusmuoto, oletuksena näkyvästi planned. Käytettävän palvelun kuvaus tarvitsee myöntäjän metatiedot ja pysyvän HTTPS-asiointilinkin. Katalogi ei myönnä todistuksia tai toteuta lompakkointegraatiota. Lähdeilmoituksen käsintarkastus on eri asia kuin alustan automaattinen alkuperätodistus tai SHACL-instanssivalidointi.

- Alembic 0004 säilyttää vanhat tuotteet ja lisää profiili-/julkaisusnapshotit, tarkastukset, pysyvän omistajaorganisaation, auditin, idempotenssit ja outboxin. Vanhoja migraatioita ei muuteta.
- If-Match, transaktion rivilukot, kirjoittajien oman hyväksynnän esto ja hyväksynnän mitätöinti muutoksessa. Julkaisu/snapshot/audit/outbox samassa transaktiossa; tietokantatriggerit suojaavat historiaa.
- Sama Keycloak-realmi ja kolme tunnusta. vero/yritys muokkaavat omaa ja tarkastavat toisen organisaation sisältöä. Muokkaus ja julkaisu ovat erilliset oikeudet.
- Codespacesin Private-portti 8000 ja automaattinen selainavaus säilyvät. README kertoo päivityksen, varmuuskopion ja koko kokeilupolun.

Todennus: 39 API-/PostgreSQL-/migraatio-/osoitetestiä ja 7 oikean Chromiumin selaintestiä läpäissyt. Mukana muokatun phase 1/2A/2B-kannan säilyminen, tyhjä kanta, toistuvat päivitykset, todellinen rinnakkaismuokkaus, hyväksynnän mitätöinti, idempotenssi, muuttumattomat versiot ja julkaisun rollback. Kahden oikean Keycloak-käyttäjän selainketju tiedostotuonnista julkiseen hakuun toimii. TypeScript/Vite-build, pilven Docker-build, Compose-readiness ja Alembic check läpäisevät.

Ajamattomat: oikea GitHub Codespace/Private-portin pääsynvalvonta/automaattinen välilehti, Windows Docker Desktop, GitHub Actions -etäajo, elävän Tietomallit-palvelun linkkituonti ja oikeat myöntäjä/lompakkokokeet. Linkkituonnin testissä verkko korvataan hallitulla vastauksella. Tarkat tulokset ja rajat STATUSissa.

Kokeile ennen yhdistämistä: https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2c-publication → Create codespace → portti 8000 Private. README sisältää vero → profiili → yritys-hyväksyntä → julkaisu -polun. Älä yhdistä mainiin automaattisesti.
