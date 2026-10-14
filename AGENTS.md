# Ohjeet koodausagenteille

## Rajaus

Lue `ROADMAP.md`, `STATUS.md` ja `metatietovaranto_suunnittelu.md`. Suunnitelma kuvaa tavoitearkkitehtuurin. Nykyinen toimitus kattaa ROADMAPin vaiheet 1, 2A, 2B ja 2C (luonnokset, riippumaton hyväksyntä, lukitut profiili-/julkaisusnapshotit, VC-metatiedot ja auditointi). Lue myös docs/phase-2c.md. Älä toteuta SHACL-instanssivalidointipalvelua, laajempaa elinkaarta tai ulkoisia integraatioita ilman erillistä toimeksiantoa. Älä yhdistä main-haaraan automaattisesti.

## Sitova semanttinen suunnitteluperiaate

Lue `docs/semanttinen-periaate-1.md` ennen tietotuotteen sisällön, soveltamisprofiilien, skeematuonnin tai julkaisuversioiden suunnittelua. Sisältö perustuu Tietomallit-työkalun SHACL-soveltamisprofiiliin, joka annetaan linkkinä tai alustalta ladattuna tiedostona. OWL voi sijaita alustalla tai ulkoisessa nimiavaruudessa. JSON Schema/OpenAPI ovat johdannaisia; tietoelementtien käsin ylläpidettävä rinnakkaismalli ei ole tavoiteratkaisu. Nykyiset dataElements ovat väliaikaista demoa eivätkä vahvistettu profiilikytkentä. Periaatteen kirjaaminen ei vielä tilaa toteutusta.

## Sitova VC toimitusperiaate

Lue `docs/vc-periaate-2.md`. Ensisijainen toimitusmuoto on W3C VC. Tuotesivu tarjoaa pysyvän myöntäjän HTTPS-asiointilinkin **Pyydä todistus lompakkoon**. Myöntäjä vastaa henkilön/yrityksen tunnistamisesta, edustamisoikeudesta, lähdetiedosta, myöntämisestä, VC:n suojaamisesta ja lompakkoprotokollasta. Katalogi ei säilytä henkilökohtaisia tarjouksia tai tokeneita. Katalogin Keycloak-istunto ei ole myöntäjän pääsyoikeus. EUDIW-/EBW-yhteensopivuus kuvataan ja todennetaan erikseen. Tämä suunnittelupäätös ei vielä tilaa myöntämispalvelun tai lompakkointegraation toteutusta.

## Työskentelyn käytännöt

Käytä nykyistä checkoutia: pilvitehtävät ovat jo eristettyjä. Älä luo worktreea ilman käyttäjän pyyntöä. Säilytä käyttäjän muutokset. Kaikki fixturet ovat synteettisiä. Älä lisää salaisuuksia, aitoja rekisteritietoja tai väitteitä QEAA-/DCAT-AP-vaatimustenmukaisuudesta.

## Käynnistys ja todennus

Täsmälliset komennot ovat READMEssä. Sovellus käyttää aina PostgreSQL:ää, myös API-testeissä. Testit käyttävät erillistä `catalog_test`-kantaa; älä aja tyhjentäviä testejä `catalog`-kantaan. Aja muutoksen mukaan `uv sync --locked`, `npm ci --prefix apps/web`, `npm run build --prefix apps/web` ja API-, migraatio- ja osoitteenmuodostustestit. Älä aja samaa tyhjentävää testikantaa käyttäviä pytest-ajoja rinnakkain. Käyttöliittymämuutoksissa aja myös `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q` käynnistettyä demoa vasten. Raportoi ajamattomat ja ohitetut testit erikseen. Päivitä STATUS toteutuksen muuttuessa.

Kirjoitus-API vaatii palvelinistunnon ja CSRF-tarkistuksen. Luonnoksen muokkaus tarvitsee editor-jäsenyyden pysyvään omistajaorganisaatioon; tarkastus reviewer/publisher- ja julkaisu publisher-roolin. Älä anna kirjoittajan hyväksyä omaa sisältöään. Säilytä ETag/If-Match ja idempotenssi. Julkinen haku ja vienti käyttävät vain muuttumattomia julkaisuja. Älä lisää testejä tai demoa varten autentikoinnin ohitusreittiä. Käytä selaintesteissä oikeaa Keycloak-kirjautumista. Säilytä `DEMO_MODE=true`-käynnistysvaatimus ja Compose-porttien sidonta loopbackiin. Älä poista PostgreSQL-volumea tavallisen käynnistyksen yhteydessä.

## Migraatiot

Muuta skeemaa uusilla Alembic-revisioilla; älä muokkaa jo toimitettuja revisioita. Älä käytä sovelluksessa create_all-kutsua tai stamp-komentoa tuntemattoman skeeman hyväksymiseen. Säilytä legacy-päivityksen tietojen ja tunnisteiden säilymistestit. Älä yhdistä organisaatioita pelkän nimen perusteella. Tavallinen startup ei saa palauttaa vanhan kannan fixtureitä.

## Kirjautuminen

Lue docs/authentication.md. Keycloakin tunnukset ovat synteettisiä demotunnuksia, eivät tuotantosalaisuuksia. Älä lokita koodeja, tokeneita, evästeitä tai salasanoja. Säilytä --no-access-log deployatussa Uvicornissa. Älä myönnä oikeuksia organisaation nimen tai käyttäjän lähettämän organisaatiotiedon perusteella. Älä muuta vanhoja jäsenyyksiä fixtureiden perusteella uudelleenkäynnistyksissä.


