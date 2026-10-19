## Ongelma ja tulos

SD-JWT VC:n väitepolku ei yksin kerro alkuperäistä semanttista ominaisuutta tai sen SHACL-käyttöyhteyttä. Tämä jatko johtaa attribuuttiviittaukset samasta lukitusta SHACL-lähteestä JSON Schemaan (x-term/x-mtv-shacl), Type Metadataan (x-mtv-semantic) ja yhteiseen mappingiin. Sisäkkäinen rooli, nimetön PropertyShape, ulkoinen nimiavaruus sekä lähdeversio ja snapshotin SHA säilyvät. Ei uutta käsin ylläpidettävää sisältömallia.

**Base: main**, `9258fff` (PR #12 yhdistetty). Main sisältyy työhaaraan. Ei automaattista yhdistämistä.

## Toteutus ja yhteensopivuus

- Oma semanttinen laajennusprofiili 1.0.0 määrittelee x-kentät sekä eksplisiittisen schema-/mapping-löydettävyyden. Ne eivät ole IETF:n schema/schema_uri-standardikenttiä. SD-JWT VC pysyy draft-19:ssä.
- Type Metadata, skeema, mapping ja profiili julkaistaan muuttumattomista tuoteversioista oikeilla mediatyypeillä. Syklitön standardin base64-SRI-ketju ja myöntäjän vct#integrity-ohje eivät toteuta allekirjoittamista tai myöntäjän luottamuksen todentamista. Withdrawn ei poista julkaistuja artefakteja.
- Nimetöntä PropertyShapea ei nimetä keksityllä alkuperäisellä URI:lla: snapshot + rootShapeUri + constraintPath yksilöivät sen. Claim Path käyttää sisäkkäisten taulukoiden kohdalla nullia, ei sisäistä /*-merkkijonoa.
- Valinnaiset attribuutti-/järjestelykatalogivastaavuudet ovat tyypitettyjä, alkuperätiedollisia ja normaalisti hyväksyttäviä väitteitä. Muutos mitätöi hyväksynnän ja paketin. Vanhan asiakkaan pois jättämä uusi kenttä säilyttää aiemmat viitteet.
- Esimerkkikuluttaja `examples/semantic_consumer.py` lukee yhden claimin kuvauksen ilman väitearvoja tai JSON Schemaa. Se ei ole SD-JWT-/allekirjoitusverifioija eikä tulkitse piilotettua väitettä alkuperäisestä todistuksesta puuttuvaksi.

## Alkutekstien vertailu ja asiakirjatietosivun tulos

Käyttäjän toimittamat **ETSI TS 119 472-1 V1.2.1 (2026-02)**, **ETSI TS 119 478 V1.1.1 (2026-01)** ja **EU 2025/1569:n konsolidointi 11.8.2026 / 001.001** on luettu relevanttien kohtien osalta ja lukittu alkuperäisinä PDF-kopioina tarkisteineen. Tämä ei väitä riippumatonta verkkovertausta tai koko standardiprofiilin vaatimustenmukaisuutta.

Generaattori **1.1.1** korjaa katalogin puuteraportin: luettuja tekstejä ei enää merkitä kokonaan puuttuviksi. Jäljelle erotellaan alkuperäisen asetuksen oikaisusuhteiden tarkistus, ETSI:n draft-13-viitteen ja paikallisen draft-19:n ero sekä ulkoisen myöntäjän vct-löydettävyyden/integrityn ja suojausprofiilin todentaminen. Oma laajennus ei muutu standardikentäksi. Täyttä EU-katalogia, rekisteröintiä, allekirjoitusta tai lompakkopalvelua ei toteuteta.

[Kohta-/artiklakohtainen vertailu ja asiakirjatietosivun ohje](https://github.com/jgmikael/metatietovaranto/blob/feat/phase-2h-attribute-semantics/docs/pr13-source-comparison.md): ETSI 472-1 4.2.1, 5.2.1 ja 7.2.1; ETSI 478 3.1 ja 5.2/5.3; EU art.7(5)–(10), art.8(3)–(8), M1:n 3(2) ja liite IV. Artiklat 7/8 ovat toimitetussa konsolidoinnissa B-merkittyjä; etusivu luettelee EU 2026/1735 -muutoksen. Liitteen IV mukautuksia ei saa korvata pelkällä ETSI-perustekstillä myöhemmässä integraatiossa.

**Asiakirjatietosivu saatu 19.10.2026:** sen aikajanassa viimeisin esitetty konsolidointi on 11.8.2026. Sivu koskee konsolidoitua tekstiä (02025R1569-20260811), ja Relationship between documents sisältää vain linkin alkuperäiseen asetukseen 32025R1569. Kopio on lukittu SHA-256:lla. **Avoin yhdistämisen tarkistus:** alkuperäisen asetuksen muutos-/oikaisusuhteet eivät näy tässä liitteessä. `EU_CORRIGENDUM_STATUS_UNVERIFIED` säilyttää tämän täsmällisen puutteen; ei väitettä oikaisujen puuttumisesta eikä vielä lopullista yhdistämissuositusta.

## Konkreettinen ketju

Synteettinen SHACL ProductShape → hyväksytty /companyName-mapping → JSON-LD-konteksti ja annotoitu JSON Schema/SD-JWT Type Metadata → PyLD:n todellinen RDF, käsin määritelty graafi ja lähde-SHACL → toisen käyttäjän hyväksymä muuttumaton julkaisu → 12 julkista artefaktia → esimerkkikuluttajan ominaisuus-IRI, PropertyShape ja lähdesnapshot.

Aito WE BUILD 0.0.2 -export säilyy tavuntarkasti: koko profiilin puuttuvat literaalityypit ja SKOS-importti estävät valmiin paketin. Erillinen nimetty paikallinen testiprojektio on testattu; sen lisättyä tyyppiä ei väitetä alkuperäiseksi. Vanhoja julkaisuja ei päivitetä.

## Asiakirjatietoliitteen täydennyksen tarkistukset 19.10.2026

- `pytest tests/test_technical_packages.py tests/test_attribute_semantics.py -q`: **61 passed, 1 warning in 55.00s**. Ei epäonnistuneita tai ohitettuja. Mukana oikea paikallinen JSON-LD/RDF/SHACL, attribuuttien yhdenmukaisuus, pakettien tarkisteketju sekä uusi asiakirjatietokopion pinnaus ja generoituun raporttiin päätyvä täsmällinen näyttöraja. Varoitus koskee Starlette/httpx-deprekaatiota.
- `git fetch origin main`: main on edelleen **9258fff** ja sisältyy työhaaraan. Työhaara vastasi etähaaraa ennen tätä lisäystä; ei muiden muutosten ylikirjoitusta. `git diff --check` läpäisi.
- Tämä täydennys muuttaa lähdepinnit, raportin syötteet, testit ja dokumentaation. Sovelluskoodia, käyttöliittymää, tietokantaskeemaa tai käynnistysasetuksia ei muutettu. Ei uutta migraatiota. Muuttumattomia julkaisuja tai demokantaa ei päivitetty.
- Koko API-/migraatiosarjaa, selaintestejä, web-buildia, Docker-buildia tai toimintakokeilua ei toistettu tässä liitetäydennyksessä. Alla oleva **207 API-/migraatiotestin ja 13 selaintestin** läpäisy sekä build-/säilymiskokeet ovat edellisen toteutusmuutoksen tuloksia, eivät uusia ajoja. Uusi 61 testin ajo menee osittain niiden kanssa päällekkäin, joten lukuja ei lasketa yhteen.
- Avoin sisältötarkistus: alkuperäisen asetuksen muutos-/oikaisusuhteet ja mahdolliset niistä löytyvät uudet tekstit. GitHub API palauttaa edelleen **Forbidden**; PR:n kuvaus ja etätarkistusten tila eivät päivity tai varmistu tämän ympäristön kautta. Kuvausteksti on repositoriossa `docs/pull-request-attribute-semantics.md`. Ei automaattista yhdistämistä.

## Aiemman toteutuskorjauksen tarkistukset (18.10.2026)

- Mainin 9258fff sisältävän korjatun toteutuksen koko 13 tiedoston API-/PostgreSQL-/migraatiosarja: **207 passed, 4 warnings in 357.80s (0:05:57)**. Ei epäonnistuneita tai ohitettuja. Mukana aiemmat 205 testiä sekä kaksi uutta lähdekopioiden pinnaus-/tarkiste- ja puuteraporttitestiä.
- Kohdennettu paketti-/attribuuttisarja: **60 passed, 1 warning in 51.17s**; nämä sisältyvät täyteen 207 testin ajoon.
- Oikea Chromium + Keycloak, korjattua Docker-sovellusta vasten: **13 passed, 1 warning in 116.18s (0:01:56)**. Tallennus/uudelleenavaaminen, eri käyttäjän hyväksyntä, julkaisu, julkiset artefaktit ja semantiikan lukija säilyivät.
- **220 eri pytest-testiä** yhteensä. Starlette/httpx- ja RDFLib-deprekaatiovaroitukset eivät ole ohituksia.
- Web-build läpäisi. Docker-image rakennettiin varmennukset säilyttävällä scripts/cloud-build.sh-reitillä; `docker compose up -d --no-build --wait` käynnisti app/db/Keycloakin healthy-tilaan. Tavallista `docker compose up --build` -reittiä tai Windows Docker Desktopia ei ajettu tässä täydennyksessä.
- **13 oikean catalog-kannan metatietotaulua säilyi tarkalleen ennallaan uudelleenkäynnistyksen yli** ennen uusia synteettisiä selainjulkaisuja. Ei uutta relaatiomigraatiota; aiemmat migraatiot tarkistettiin erillisessä catalog_test-kannassa. Demokantaa ei tyhjennetty.
- Julkinen HTTP-yhteensopivuuskoe: **83 julkaisuversiota luettavissa**, **8 vanhan generaattorin pakettia / 78 artefaktia** tavuntarkasti alkuperäisillä SHA-arvoilla. Uusi lähdetarkistus ei kirjoittanut vanhojen julkaisujen raportteja uudelleen.
- `git diff --check` läpäisi. PR #13:n GitHub-mergeviite vahvisti basen mainiksi 9258fff; käyttäjä vahvisti saman. Main-haaraa ei muutettu eikä PR:ää yhdistetty.
- Ajamattomat: alkuperäisen asetuksen oikaisusuhteet ja mahdolliset uudet säädöstekstit, Windows, uuden Codespacen luonti/Private-portin ajonaikainen tila, tuotanto-HTTPS ja GitHub Actionsin etätulos. Ei allekirjoittamista, lompakkoa, EU-katalogirekisteröintiä tai koko ETSI-profiilin vaatimustenmukaisuusarviota.


## Ajamattomat / rajauksen ulkopuolella

Viimeisin toimitetulla aikajanalla näytetty versio on tarkistettu; alkuperäisen asetuksen oikaisusuhteiden luettelo jää avoimeksi. Windows Docker Desktopia, uuden Codespacen luontia/automaattista selainavausta/Private-portin ajonaikaista tilaa, tuotanto-HTTPS:ää ja GitHub Actionsin etätulosta ei voitu varmistaa tässä ympäristössä. Ei kuorma-/tietoturva-auditointia, EU-katalogirekisteröintiä tai kryptografista myöntäjä-/lompakkotestiä. Olemassa olevat oikeudet, hyväksyntä, muuttumattomuus ja Codespaces-asetukset säilyvät.
