# Ohjeet koodausagenteille

## Rajaus

Lue `ROADMAP.md`, `STATUS.md` ja `metatietovaranto_suunnittelu.md`. Suunnitelma kuvaa tavoitearkkitehtuurin. Nykyinen toimitus kattaa ROADMAPin vaiheen 1 ja erikseen tilatun vaiheen 2A: Alembic-migraatiot ja tarjoajaorganisaatiot. Älä toteuta kirjautumista, organisaatiokohtaisia oikeuksia, hyväksyntää, julkaisuversioita, SHACL:ia tai ulkoisia integraatioita ilman erillistä toimeksiantoa. Älä yhdistä main-haaraan automaattisesti.

## Työskentely

Käytä nykyistä checkoutia: pilvitehtävät ovat jo eristettyjä. Älä luo worktreea ilman käyttäjän pyyntöä. Säilytä käyttäjän muutokset. Kaikki fixturet ovat synteettisiä. Älä lisää salaisuuksia, aitoja rekisteritietoja tai väitteitä QEAA-/DCAT-AP-vaatimustenmukaisuudesta.

## Käynnistys ja todennus

Täsmälliset komennot ovat READMEssä. Sovellus käyttää aina PostgreSQL:ää, myös API-testeissä. Testit käyttävät erillistä `catalog_test`-kantaa; älä aja tyhjentäviä testejä `catalog`-kantaan. Aja muutoksen mukaan `uv sync --locked`, `npm ci --prefix apps/web`, `npm run build --prefix apps/web` ja API-, migraatio- ja osoitteenmuodostustestit. Älä aja samaa tyhjentävää testikantaa käyttäviä pytest-ajoja rinnakkain. Käyttöliittymämuutoksissa aja myös `BROWSER_BASE_URL=http://127.0.0.1:8000 .venv/bin/pytest tests/test_browser.py -q` käynnistettyä demoa vasten. Raportoi ajamattomat ja ohitetut testit erikseen. Päivitä STATUS toteutuksen muuttuessa.

Vaiheen 1 avoin CRUD on vain paikalliseen demoon. Säilytä `DEMO_MODE=true`-käynnistysvaatimus ja Compose-porttien sidonta loopbackiin. Älä poista PostgreSQL-volumea tavallisen käynnistyksen yhteydessä.

## Migraatiot

Muuta skeemaa uusilla Alembic-revisioilla; älä muokkaa jo toimitettuja revisioita. Älä käytä sovelluksessa create_all-kutsua tai stamp-komentoa tuntemattoman skeeman hyväksymiseen. Säilytä legacy-päivityksen tietojen ja tunnisteiden säilymistestit. Älä yhdistä organisaatioita pelkän nimen perusteella. Tavallinen startup ei saa palauttaa vanhan kannan fixtureitä.
