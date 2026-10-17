## Muutos

Julkaistulle tuoteversiolle voidaan merkitä deprecated tai withdrawn julkaisijan perustelemalla komennolla. Deprecated näkyy varoituksella oletushaussa; withdrawn jää pois oletushausta ja katalogiviennistä. Pysyvä sivu, alkuperäinen sisältö/tarkiste ja julkinen tapahtumahistoria säilyvät. Withdrawn-versiolla ei näytetä palvelutoimintoja, myöskään vanhaa versiota suoraan avattaessa tai ajantasaisen tilatiedon puuttuessa.

Migraatio 0005 lisää erilliset append-only-elinkaaritapahtumat ja outboxin. Tapahtuma, audit ja idempotenssivastaus tallentuvat samassa transaktiossa. Kirjoitus vaatii omistajaorganisaation publisher-jäsenyyden, istunnon, CSRF:n, elinkaaren oman If-Match-ETagin ja Idempotency-Keyn. Korvaava versio on saman tuotteen myöhempi julkaisu. Vanhoja ProductVersion-snapshotteja, hyväksyntöjä, luonnoksia, oikeuksia tai fixtureitä ei kirjoiteta uudelleen.

Alkuperäiset versio-API:t ja version vienti säilyvät. Link- ja X-Product-Lifecycle-Status-otsakkeet ohjaavat ajantasaiseen erilliseen tilaan. Oletushaun voi laajentaa lifecycleStatus=all/withdrawn-rajauksella ja katalogiviennin includeWithdrawn=true-parametrilla. Vanhempaa versiota ei nosteta automaattisesti poistetun uusimman tilalle.

## Kokeilu ennen yhdistämistä

https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2g-lifecycle

Portti 8000 Private. Luo/julkaise synteettinen tuote kahden käyttäjän polulla: vero / demo-vero muokkaa ja lähettää tarkastukseen, yritys / demo-yritys hyväksyy ja julkaisee. Julkaisun tuotesivulla yritys voi merkitä version poistuvaksi ja sitten poistetuksi käytöstä. README kertoo tarkat kentät ja hakurajaukset. Valmiit palvelut säilyvät planned-tilassa.

## Rajaus ja todennus

147 API-/PostgreSQL-/migraatiotestiä ja 12 oikean OIDC-ketjun selaintestiä läpäisi. Web-/pilvi-Docker-build, Compose-readiness, Alembic check, vanhan kannan päivitys ja restartin tietojen säilyvyys tarkistettiin. Tavallinen Compose-build epäonnistui tämän pilven DNS-virheeseen; wrapper-build toimii. Windows, oikea Codespace ja etä-CI jäivät ajamatta.

Täsmällinen sopimus: docs/phase-2g.md. Ajetut API-/PostgreSQL-/migraatio-/selaintestit, buildit ja säilyvyystarkistukset sekä ajamattomat ympäristöt: STATUS.md.

Ei archived/retired-tilaa tai ajastuksia. Katalogimerkintä ei peru ulkoisen palvelun käyttöoikeuksia tai myönnettyjä todistuksia. Codespacesin openBrowser/Private-ohje säilyvät. Main-haaraan ei yhdistetä automaattisesti.
