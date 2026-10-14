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

## Vaiheen 2 myöhemmät osat — erillinen toimeksianto

Kirjautuminen/OIDC, organisaatiokohtaiset käyttöoikeudet, hyväksyntäprosessi, muuttumattomat julkaisuversiot, optimistinen lukitus, auditointi ja SHACL-validointi. Laajenna tämän jälkeen kielituki, tietomalli ja vientien profiilit tavoitearkkitehtuurin mukaisiksi; varmista DCAT-AP-vaatimustenmukaisuus erikseen. Näitä ei toteuteta vaiheessa 2A.

## Vaihe 3 — ulkoiset integraatiot

Ulkoiset lompakko-, QEAA- ja data-avaruusintegraatiot sekä niiden adapterit ja oikeita vertaispalveluja vastaan tehtävä todennus.

Vaiheen 2A jälkeen jatketaan vain erillisellä toimeksiannolla. Työhaaroja ei yhdistetä automaattisesti main-haaraan.
