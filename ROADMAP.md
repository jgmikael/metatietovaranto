# Toteutuksen vaiheistus

`metatietovaranto_suunnittelu.md` on tavoitearkkitehtuuri. Käyttäjän tehtävän 1 rajaus korvaa luvun 18 vaatimuksen koko ratkaisun toimittamisesta kerralla. Alla olevat vaiheet eivät ole suunnitteludokumentin A–D-vaiheistus.

## Vaihe 1 — paikallinen toimiva demo

- React/TypeScript-käyttöliittymä ja FastAPI-palvelin.
- Tietotuotteen lisäys, luku, muokkaus ja poisto.
- Tekstihaku, teema- ja tarjoajarajaus, sivutus ja tuotesivu.
- PostgreSQL ja pysyvä Compose-volume; kolmen synteettisen tuotteen kertaluonteinen siemennys.
- Tuote- ja katalogivienti JSONina ja JSON-LD:nä.
- Palvelimen validointi, API-/PostgreSQL-testit, RDF-jäsentämistestit ja selaintestit.
- Suomenkielinen responsiivinen demo, näkyvä demomerkintä ja dokumentoitu käynnistys.

## Vaihe 2A — migraatiot ja tarjoajaorganisaatiot

Tämä tehtävä on tilattu erikseen nykyisen main-haaran pohjalta.

- Alembic: ensimmäinen migraatio kuvaa alkuperäisen skeeman ja ottaa tarkistetun vaiheen 1 kannan käyttöön ilman tiedonmenetystä.
- Toinen migraatio lisää Organization-mallin ja pakollisen tuote–tarjoajaorganisaatio-vierasavaimen. Samannimisiä vanhoja tarjoajia ei yhdistetä nimen perusteella.
- Organisaation UUID, virallinen nimi, maa, tunnistejärjestelmä/tunniste-parit ja synteettisyys; luku-API ja yksinkertainen näkymä.
- Tuotteen ylläpidossa organisaatiovalinta; tarjoajanimi säilyy haussa, tuotesivulla ja vienneissä.
- Migraatiot ennen readiness-tilaa samalla käynnistyspolulla Composessa ja Codespacesissa; fixtureitä ei palauteta vanhaan kantaan.
- Vanhan muokatun kannan, tyhjän kannan ja toistuvien migraatioiden PostgreSQL-testit sekä aiempien selainpolkujen säilyttäminen.
- Codespacesin automaattinen selainavaus ja Private-portti säilyvät.

## Vaihe 2B — kirjautuminen ja organisaatiokohtainen ylläpito

- Keycloak OIDC authorization code + PKCE; ei demokäyttäjän identiteetin oikopolkua.
- Opaque palvelinistunto PostgreSQL:ssä, HttpOnly/SameSite-eväste, HTTPS:ssä Secure ja kirjoituspyyntöjen CSRF-tarkistus.
- Eksplisiittiset organisaatiojäsenyydet ja editor/reader-roolit. Muokkaaja ylläpitää vain omien organisaatioidensa tuotteita; palvelin tarkistaa myös vaihdettavan tarjoajan.
- Anonyymi haku, tuotesivut ja viennit säilyvät tämän demon julkisina metatietoina. Julkaisutiloja ja rajattua näkyvyyttä ei vielä ole.
- Kolme synteettistä demokäyttäjää (kaksi eri organisaation muokkaajaa, yksi lukija) ja oikean OIDC-ketjun selaintestit.
- Yksi selainportti 8000: rajattu saman alkuperän kirjautumisproxy Keycloakille. Codespacesin Private-portti ja automaattinen selainavaus säilyvät.
- Migraatio 0003_auth lisää istunnot, OIDC-tilat ja jäsenyydet; aiempia migraatioita tai tuotetietoja ei kirjoiteta uudelleen.

## Vaiheen 2 myöhemmät osat — erillinen toimeksianto

Seuraava ehdotettu rajaus on 2C: luonnokset, hyväksyntäprosessi, muuttumattomat julkaisuversiot, optimistinen lukitus ja auditointi. Sen jälkeen semanttinen validointi/SHACL ja vientien vaatimustenmukaisuus voidaan toteuttaa omana rajauksenaan. Myös organisaatiojäsenyyksien hallintakäyttöliittymä, tuotantotunnistautuminen ja kielituen laajennukset suunnitellaan erikseen. Näitä ei toteuteta vaiheessa 2B.

## Vaihe 3 — ulkoiset integraatiot

Ulkoiset lompakko-, QEAA- ja data-avaruusintegraatiot sekä niiden adapterit ja oikeita vertaispalveluja vastaan tehtävä todennus.

Vaiheen 2B jälkeen jatketaan vain erillisellä toimeksiannolla. Työhaaroja ei yhdistetä automaattisesti main-haaraan.
