# PR #13: normatiivisten lähteiden tarkistus ja main-pohja

**Päivitetty 19.10.2026:** pyydetyt PDF:t ja alkuperäisen asetuksen muutos-/oikaisuluettelon copy-paste on saatu. EN-metatietotehtävän lähdevertailu on päätetty ilmoitetuin rajauksin; PL-oikaisun ja tulevan 9 artiklan koko tekstejä ei saatu. [Nykyinen päätös, havainnot ja rajat](pr13-source-comparison.md). Alla oleva noutoestoloki on aiemman yrityksen historiaa. Käyttäjä vahvisti PR #13:n baseksi mainin.

18.10.2026 (Europe/Helsinki). **Tarkistus on kesken lähdetiedostojen puuttumisen vuoksi. PR #13:a ei vielä suositella yhdistettäväksi.** Main-pohjan tekniset tarkistukset ja alkutekstien sisällön tarkistaminen ovat erillisiä tuloksia.

## Main-pohja ja PR:n kohdehaara

PR #12 on yhdistetty mainiin commitissa `9258fffb4633c90240eddba1c09b6b135c3fb057`. Nykyinen main on tuotu PR #13:n työhaaraan merge-commitissa `339824ece0127f13cc17494efc13ef7d0c030ba0`. Yhdistäminen ei muuttanut sovellustiedostoja eikä main-haaraa. Näin työhaaran testit ajetaan nykyisen mainin sisältävällä historialla.

GitHubin `refs/pull/13/merge`-viitteen ensimmäinen vanhempi osoitti tarkistettaessa yhä `8bc37dc`:hen (vanha perus-2H-haara), ei nykyiseen mainiin. PR:n base-vaihto yritettiin REST PATCH -pyynnöllä (`base: main`), mutta GitHub API palautti **Forbidden**. Base on siksi tarkistettava GitHubin käyttöliittymässä: **PR #13 → Edit → base: main**. Työhaaran main-päivitys ei itsessään vaihda PR:n base-kenttää. Vaihdon jälkeen GitHubin tarkistusten tulee valmistua uudelleen.

## Todella tarkistetut lähteet

Virallisen EU-repositorion TS11:n 1.0.1 (2026-01-30) upstream HEAD on edelleen `ee91a294c833af5188726fd8c302c641212192aa`. Kaikkia kolmea paikallista tiedostoa (teksti ja kaksi JSON-tietomallia) verrattiin uudelleen virallisen Git-commitin tarkkoihin tavuihin ja lukittuihin SHA-256-arvoihin: täsmäävät.

TS11 viittaa ETSI TS 119 478:n **V0.0.7-luonnokseen**. Se ei korvaa pyydetyn **V1.1.1**-alkutekstin tarkistusta. TS11:n artiklojen 7/8 kuvaus on toissijainen lähde, ei EU-asetuksen ajantasainen konsolidoitu teksti. Catalogue of Attributes, Catalogue of Schemes/Attestations ja yksittäinen tekninen JSON Schema säilyvät erillisinä.

## Estyneet alkutekstinoudot

| Pyydetty lähde | Virallinen nouto-osoite | Tulos |
| --- | --- | --- |
| ETSI TS 119 472-1 V1.2.1 | https://www.etsi.org/deliver/etsi_ts/119400_119499/11947201/01.02.01_60/ts_11947201v010201p.pdf | HTTP 403, sisältöä ei saatu |
| ETSI TS 119 478 V1.1.1 | https://www.etsi.org/deliver/etsi_ts/119400_119499/119478/01.01.01_60/ts_119478v010101p.pdf | HTTP 403, sisältöä ei saatu |
| EU 2025/1569 alkuperäisteksti | https://eur-lex.europa.eu/eli/reg_impl/2025/1569/oj/eng | HTTP 403, sisältöä ei saatu |
| EU:n vaihtoehtoinen CELEX-reitti | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX:32025R1569 | HTTP 403, sisältöä ei saatu |
| EU:n vaihtoehtoinen ELI-reitti | https://data.europa.eu/eli/reg_impl/2025/1569/oj | HTTP 403, sisältöä ei saatu |

Hylättyjen noutojen perusteella ei päätellä, että versiota tai muutoksia ei olisi olemassa. Tiedostojen tarkisteet ovat puuttuvia, eivät keksittyjä. Konsolidoidun tekstin ajantasaisuus sekä mahdollisten muutos- ja oikaisusäädösten tilanne ovat **unknown**. Verkkotarkistusta ei korvata tuntemattomalla peilillä tai TS11:n vanhaa luonnosviitettä nimeämällä lopulliseksi standardiksi.

Koneellinen havaintoloki: `fixtures/catalog-standards/review-attempt-2026-10-18.json`. Se on tarkistusyrityksen loki, ei normatiivinen lähde eikä generaattorin uusi syöte. Nykyiset sources.json-lukot, julkaistut artefaktit ja muuttumattomat snapshotit säilyvät ennallaan. `NORMATIVE_SOURCES_UNVERIFIED` jää katalogin raporttiin.

## Mitä tarvitaan tarkistuksen jatkamiseen

Toimita tähän keskusteluun seuraavat virallisista lähteistä tallennetut tiedostot:

1. **ETSI TS 119 472-1 V1.2.1**, koko PDF yllä olevasta osoitteesta. Etusivun julkaisunumeron/version on oltava mukana.
2. **ETSI TS 119 478 V1.1.1**, koko PDF yllä olevasta osoitteesta.
3. **EU 2025/1569**: ajantasainen konsolidoitu koko teksti PDF-/HTML-muodossa. Jos konsolidoitua versiota ei ole, alkuperäinen koko teksti ja sitä muuttavat/oikaisevat säädökset.
4. **EUR-Lexin asiakirjatietojen muutos-/oikaisusuhteet**, tallennettu sivu tai muu virallinen asiakirjatieto, josta ilmenee tarkistuspäivän tilanne. Pelkästä alkuperäisestä asetuksen PDF:stä ei voi päätellä, ettei myöhempiä muutoksia olisi.

Mukaan lähdeosoite ja latauspäivä; englanninkielinen teksti helpottaa vertailua, suomenkielinen virallinen säädösteksti käy myös. Aineistoista tarkistetaan tunniste/versionumero, tallennetaan alkuperä ja tarkisteet sekä erotetaan oikeudellinen säädös, ETSI:n tekninen profiili, TS11-tietomalli ja Metatietovarannon oma laajennus. Vasta tämän jälkeen voidaan korjata pykälä-/kohtakohtainen taulukko ja tehdä sisältöön perustuvat koodikorjaukset.

## Main-pohjan tekniset tarkistukset

- Koko README/CI:n 13 tiedoston API-/PostgreSQL-/migraatiosarja: **205 passed, 4 warnings in 344.76s (0:05:44)**. Ei epäonnistuneita tai ohitettuja. Mukana oikeudet/CSRF, hyväksynnän mitätöinti, muuttumattomat julkaisut, tyhjä/vanha kanta ja toistuvat migraatiot, todellinen JSON-LD/RDF/SHACL, uusi WE BUILD -aineistokoe, attribuuttiannotaatiot sekä tarkisteketju.
- Oikea Chromium + Keycloak -selainajo käynnistettyä demoa vasten: **13 passed, 1 warning in 114.18s (0:01:54)**. Mukana tallennus/uudelleenavaaminen, riippumaton hyväksyntä/julkaisu, julkiset artefaktit ja semantiikan lukija. Vain erillinen API-sarja käyttää tyhjennettävää catalog_test-kantaa; live-katalogia ei nollattu.
- Yhteensä **218 eri pytest-testiä**. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia.
- `npm run build --prefix apps/web`: läpäisi (Vite 1,13 s). Käynnissä olevan Docker-sovelluksen **20 API-/lukijalähdetiedoston** SHA-256:t vastaavat checkoutia, ja **3 web-build-tiedoston** SHA-256:t vastaavat tuoretta paikallista buildia. Selainajo testasi näin nykyisiä sovellustavuja, ei aiempaa erilaista versiota.
- `git merge-base --is-ancestor origin/main HEAD`: läpäisi mainin 9258fff sisältävällä työhaaralla. `git diff --check` ja tarkistuslokin JSON-jäsennys läpäisivät.
- Ei uutta tietokantamigraatiota tai sovelluskoodimuutosta. Docker-imagea/compose-käynnistystä ei rakennettu uudelleen tässä dokumentaatio-/pohjapäivityksessä; päällä olevien palveluiden vastaavuus varmistettiin yllä. Windows Docker Desktopia, uuden Codespacen luontia/Private-portin tilaa, tuotanto-HTTPS:ää tai GitHub Actionsin etätulosta ei ajettu tässä ympäristössä.
- **Ajamattomat sisältötarkistukset:** pyydettyjen ETSI-alkutekstien kohta-/kenttävertailu, EU-asetuksen ajantasaisen konsolidoidun tekstin ja myöhempien muutosten/oikaisujen vertailu sekä niiden perusteella mahdollisesti tarvittavat koodikorjaukset. Näitä ei korvaa yllä oleva tekninen läpäisy.


Testien läpäisy ei sulje yllä olevaa lähdepuutetta eikä osoita vaatimustenmukaisuutta. Varsinaista myöntämistä, allekirjoittamista, lompakkoa tai EU-katalogiin rekisteröintiä ei toteuteta tässä tehtävässä. Alkuperäisen SHACL-aineiston tai julkaistujen versioiden sisältöä ei muuteta lähdetarkistuksen vuoksi.
