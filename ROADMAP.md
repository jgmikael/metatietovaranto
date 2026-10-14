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

## Vaihe 2 — hallittu ylläpito ja semanttinen validointi

Kirjautuminen/OIDC, organisaatiokohtaiset oikeudet, hyväksyntäprosessi, muuttumattomat julkaisuversiot, optimistinen lukitus, auditointi ja SHACL-validointi. Ennen tietomallin ensimmäistä muutosta lisää Alembic-migraatiohistoria nykyisen alkuperäisskeeman pohjalta. Laajenna tämän jälkeen kielituki, tietomalli ja vientien profiilit tavoitearkkitehtuurin mukaisiksi; varmista DCAT-AP-vaatimustenmukaisuus erikseen.

## Vaihe 3 — ulkoiset integraatiot

Ulkoiset lompakko-, QEAA- ja data-avaruusintegraatiot sekä niiden adapterit ja oikeita vertaispalveluja vastaan tehtävä todennus.

Vaiheisiin 2 ja 3 siirrytään erillisellä toimeksiannolla. Vaiheen 1 työhaaraa ei yhdistetä automaattisesti main-haaraan.
