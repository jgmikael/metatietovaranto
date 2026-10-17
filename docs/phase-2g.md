# Vaihe 2G — julkaisuversioiden elinkaari

Pohja main `79dc9d1` (PR #10 / 2F). Käyttäjän tilaama rajaus: deprecated ja withdrawn, erillinen muuttumaton tapahtumahistoria, käyttöoikeudet, auditointi sekä haku/sivut/viennit. Ei archived/retired-tilaa, ajastettuja siirtymiä, ulkoisia integraatioita tai uuden sisällön hyväksynnän ohitusta.

## Tilat ja vastuut

- Varhaisesta 2C-snapshotista voi puuttua versionUri. Elinkaaren lukuesitys johtaa sen alkuperäisestä tuotteen URI:sta ja version tunnuksesta (puuttuvan tuote-URI:n tapauksessa nykyisestä palvelun perusosoitteesta ja tuotteen UUID:stä). Snapshotin sisältöä tai sen alkuperäistä JSON-LD-esitystä ei täydennetä taustalla.
- Julkaisu ilman elinkaaritapahtumia on published. Migraatio ei lisää tapahtumia vanhoille versioille eikä muuta niiden sisältöä/tarkisteita.
- published → deprecated tai withdrawn; deprecated → withdrawn. Withdrawn on lopullinen tälle versiolle. Paluu aiempaan sisältöön tehdään uutena normaalisti hyväksyttynä julkaisuna.
- Deprecated: poistumassa käytöstä, näkyvä varoitus; palvelutoiminnot säilyvät toimitustavan oman saatavuuden mukaan. Valinnainen korvaava versio on saman tuotteen jo julkaistu suuremman järjestysnumeron versio, joka ei ole withdrawn kirjaushetkellä. Ei itseviitteitä, takautuvia ketjuja tai luonnosviitteitä. Korvaava versio voi myöhemmin muuttua; linkin kohteen oma ajantasainen tila ratkaisee sen käytettävyyden.
- Withdrawn: poistettu käytöstä; pysyvä sivu ja historia säilyvät. Katalogin tuotesivun palvelutoiminnot estetään myös vanhaa versiota suoraan katsottaessa. Metatietojen/profiilien lataus ja version historian luku säilyvät. Tämä ei peruuta tarjoajan tai myöntäjän ulkoisia käyttöoikeuksia eikä myönnettyjä todistuksia.
- Omistajaorganisaation publisher kirjaa tapahtuman, pakollisena julkinen perustelu (10–2 000 merkkiä, ei henkilötietoja/salaisuuksia). Editor, reviewer tai reader ei saa tätä oikeutta roolinsa perusteella. Kyse on operatiivisesta tilamuutoksesta ilman uutta sisältöhyväksyntää; julkaistua sisältöä, luonnosta, hyväksyntää tai snapshotia ei muuteta.

## API ja atomisuus

GET `/api/v1/products/{id}/versions/{version}/lifecycle` palauttaa julkisen tilan, revision, ETagin, version sisältötarkisteen ja tapahtumahistorian. Tapahtumissa näkyvät julkinen perustelu, aika ja vastuullinen omistajaorganisaatio; käyttäjän subject-tunniste on vain suojatussa auditoinnissa.

POST `/api/v1/products/{id}/lifecycle-events`, body `{version, status, reason, replacementVersion?}`. Istunto + CSRF + omistajan publisher-jäsenyys. If-Match on **elinkaarivastauksen** ETag, ei luonnoksen revision tai muuttumattoman sisällön ETag. Idempotency-Key vaaditaan (24 h, subject/tuote/pyyntösisältö/If-Match). Sama pyyntö palauttaa alkuperäisen vastauksen, vaikka nykytila olisi sittemmin edennyt; lue GETillä tuore tila. Puuttuvat otsakkeet 428, vanha tila 412, ristiriitainen uusintapyyntö/siirtymä/korvaava versio 409.

PostgreSQL:n tuoterivilukko sarjoittaa julkaisemisen ja elinkaarikomennot. Tapahtuma, auditointi, erillinen lifecycle_outbox_events ja idempotenssivastaus tallennetaan samassa transaktiossa. Append-only-triggerit suojaavat molempia uusia tauluja. Vanhaa version-kohtaista julkaisuoutboxia ei muuteta. Ulkoista outbox-kuluttajaa ei lisätä.

Uusi Alembic `0005_lifecycle` luo vain kaksi taulua, rajoitteet ja triggerit. Aiemmat migraatiot säilyvät. Tyhjä ja 0004:ään päivitetty kanta tuetaan; historian tuhoavaa downgradea ei tarjota.

## Julkinen luku ja viennit

- Tuotteen nykyversio tarkoittaa edelleen uusinta julkaistua järjestysnumeroa. Withdrawn-uusimman tilalle ei nosteta vanhempaa versiota. Uusi normaalisti hyväksytty julkaisu voi jälleen olla published.
- Oletushaku näyttää uusimmat published/deprecated-versiot. `lifecycleStatus=current|published|deprecated|withdrawn|all` rajaa uusimpien versioiden joukon ennen sivutusta ja lukumääriä; current on oletus. Vanhojen versioiden tilat näkyvät versiolistassa.
- Nykyinen tuote-API ja versiotunnukseton JSON/JSON-LD-vienti saavat erillisen lifecycle-lukuesityksen, kun tapahtumia on. contentHash koskee muuttumatonta alkuperäistä sisältöä; elinkaariesitys on sen ulkopuolella ja sillä on oma ETag. Tapahtumattomat vanhat vastaukset säilyvät ennallaan.
- Versio-API, version pysyvä URI sekä `export?version=...` palauttavat edelleen alkuperäisen snapshotin ja sisältö-ETagin. Ne ilmoittavat ajantasaisen tilan `X-Product-Lifecycle-Status`-otsakkeessa ja Link: describedby -viitteellä elinkaariresurssiin. Käyttöliittymä hakee tilan erikseen ennen palvelutoimintojen näyttämistä; hakuvika estää ne.
- Katalogivienti jättää uusimmat withdrawn-versiot pois oletuksena. `includeWithdrawn=true` sisällyttää ne tilatietoineen poistojen havaitsemiseen. JSON-LD:n elinkaaritieto on erillinen paikallisen demo-nimiavaruuden resurssi; DCAT-AP-vaatimustenmukaisuutta ei väitetä.
- Julkiset vastaukset säilyvät no-store. Tilamuutoksen jälkeen käyttöliittymä päivittää elinkaaritiedon ja versiolistan. Avoin vanha välilehti ei ole ulkoisen palvelun pääsynvalvonta.

## Todennus

API/PostgreSQL: siirtymät ja korvaava versio, rajaroolit ja omistaja vs tarjoaja, CSRF, erilliset ETagit, rinnakkaisuus/idempotenssi, rollback, triggerit, julkisten toimijoiden rajaus, haku/sivutus/viennit/URI:t ja muuttumaton vanha sisältö. Migraatiot: tyhjä kanta, täytetty 0004-kanta, kaikki vanhat rivit/tarkisteet säilyvät, toistuva suoritus ja restart. Selain: oikea OIDC, uusi synteettinen julkaisu → deprecated → withdrawn → oletushaku/erillinen rajaus/pysyvä versiosivu. Aktiivisten toimituslinkkien estoa voidaan testata selaimessa tallentamatta olemattomia palveluita katalogiin.
