## Ongelma ja muutos

SD-JWT VC:n claim-polku ei yksin kerro alkuperäistä semanttista ominaisuutta tai sen SHACL-käyttöyhteyttä. Tämä 2H:n jatko johtaa attribuuttiviittaukset samasta lukitusta lähteestä JSON Schemaan (x-term/x-mtv-shacl), Type Metadataan (x-mtv-semantic) ja yhteiseen mappingiin. Sisäkkäinen rooli, nimetön PropertyShape, ulkoinen nimiavaruus sekä lähdeversio ja snapshotin SHA säilyvät. Ei uutta käsin ylläpidettävää sisältömallia.

**Pohja:** `feat/phase-2h-technical-packages`, commit ace80e3. Origin/main on vielä 2G ac002ad. Tarkasta tämän PR:n erot 2H-haaraa vasten; yhdistä pohja ensin ja muuta tämän base mainiksi sen jälkeen. Ei automaattista yhdistämistä.

Oma semanttinen laajennusprofiili 1.0.0 määrittelee x-kentät ja eksplisiittisen skeeman/mappingin löydettävyyden; niitä ei esitetä IETF:n schema/schema_uri-standardikenttinä. SD-JWT VC pysyy draft-19:ssä. Type Metadata, skeema, mapping ja profiili julkaistaan muuttumattomina oikeista koneellisista reiteistä. Syklitön standardin base64-SRI-ketju ja myöntäjän vct#integrity-ohje eivät toteuta allekirjoittamista tai myöntäjän luottamuksen todentamista. Vanhoja julkaisuja ei päivitetä.

Valinnaiset attribuutti-/järjestelykatalogivastaavuudet ovat tyypitettyjä, alkuperätiedollisia ja normaalisti hyväksyttäviä väitteitä. Uusi muokkauskenttä säilyy uudelleenavaamisessa; vanhojen asiakkaiden kentän poisjättäminen säilyttää tiedot. Vastaavuuden muutos vanhentaa paketin/hyväksynnän. Koneellinen puuteraportti ja [ETSI/EU/TS11-vastaavuustaulukko](docs/attribute-semantics.md) erottavat attribuuttikatalogin, todistusjärjestelykatalogin ja yksittäisen skeeman. TS11 1.0.1 ja molemmat viralliset tietomallit ovat alkuperäisinä tarkisteineen mukana.

## Konkreettinen ketju

Synteettisen demo-SHACLin `ProductShape` → hyväksytty `/companyName`-mapping → annotoitu content.schema.json, JSON-LD-konteksti ja SD-JWT Type Metadata → JSON-LD/PyLD-graafi, odotetun RDF-graafin vertailu ja lähde-SHACL → eri käyttäjän hyväksymä muuttumaton julkaisu → julkiset 12 artefaktia.

`["companyName"]`-claimin x-mtv-semantic palauttaa ominaisuuden `https://example.org/metatietovaranto/demo/companyName`, erillisen PropertyShape-viitteen ja lähdesnapshotin version/tarkisteen. Type Metadatasta löytyvät profiloidut, tarkistesidotut mapping-/schema-osoitteet. `examples/semantic_consumer.py` lukee saman semantiikan suoraan julkaistuista kuvauksista ilman esimerkkien tai muiden väitteiden arvoja. Sisäkkäisen taulukon polku esitetään esimerkiksi `["groups",null,"members",null,"city"]`, ei sisäisellä /*-merkkijonolla. Sama `city` eri rooleissa säilyttää eri ominaisuus-IRI:n ja rajoitepolun.

## Todella suoritetut tarkistukset

- Koko README/CI:n 13 tiedoston API-/PostgreSQL-/migraatiosarja: **196 passed, 4 warnings in 317.51s (0:05:17)**. Ei epäonnistuneita tai ohitettuja. Mukana vanhojen kantojen päivitykset, tyhjä kanta/toistuvat migraatiot, käyttöoikeudet, hyväksynnän mitätöinti, muuttumattomat julkaisut, oikea PyLD + lukittu lataaja + RDF-graafivertailu + lähde-SHACL, sisäkkäiset taulukot/roolit, nimetön PropertyShape, ulkoinen nimiavaruus, ristiriitaisten annotaatioiden hylkäys ja SRI-ketjun muutosten havaitseminen.
- Kohdennettu paketti-/attribuuttisemantiikan ajo: **49 passed** (sisältyy edellä olevaan 196 testiin). Näistä 15 on uuden jatkon testejä.
- Oikea Chromium ja Keycloak, lopullista Docker-imagea vasten: **13 passed, 1 warning in 106.27s (0:01:46)**. Aiempien polkujen lisäksi katalogiviitteen syöttö → tallennus → uudelleenavaaminen → paketin generointi → toisen käyttäjän hyväksyntä/julkaisu → julkisten kuvausten tarkisteketju ja yhden claimin semantiikka. Ensimmäinen selainajo löysi uuden JSON-kentän nimilappuongelman; eksplisiittinen label/id-yhteys korjattiin ja koko selainajo uusittiin onnistuneesti.
- **209 eri pytest-testiä**, ei ohituksia. Deprekaatiovaroitukset ovat Starlette/httpx- ja RDFLib-varoituksia.
- `npm run build --prefix apps/web` läpäisi (TypeScript/Vite). Docker-image rakennettiin varmennukset säilyttävällä `scripts/cloud-build.sh`-reitillä ja käynnistettiin `docker compose up -d --no-build --wait`: app/db/Keycloak healthy. Tavallista `docker compose up --build` -rakennusreittiä ei ajettu uudelleen tässä jatkossa; pilviympäristön aiemmin todettu build-DNS-rajaus edellytti proxy-/CA-asetukset säilyttävää apureittiä.
- Olemassa olevan catalog-kannan uudelleenkäynnistys: **13 metatietotaulun kaikki rivit täsmälleen ennallaan**, mukana 71 tuotetta, 71 luonnosta, 36 profiilisnapshotia ja 64 julkaisua ennen selaintestien uusia synteettisiä julkaisuja. `alembic current`: **0005_lifecycle (head)**. Ei uutta skeemamigraatiota; toimitetut revisiot ennallaan. Tyhjentävät API-testit käyttivät vain erillistä catalog_test-kantaa.
- Julkisten vanhojen tietojen erillinen HTTP-toimintakoe: **73 julkaisuversiota luettavissa**, mukaan lukien kaikki testien jättämät historiat. **6 vanhan 1.0.0-generaattorin pakettia / 54 artefaktia** haettiin ja alkuperäiset tavut/tarkisteet säilyivät.
- Dockerissa ajettu `examples/semantic_consumer.py` luki oikean julkisen Type Metadatan ja palautti `["companyName"]`-polulle alkuperäisen ominaisuus-IRI:n, NameShape-kytkennän ja lähdesnapshotin/version/SHA:n. Kaikki **12 uuden paketin artefaktia** haettiin julkisista HTTP-reiteistä ja niiden tavut, mediatyypit ja SHA:t tarkistettiin. Tämä on kuvausten toimintakoe, ei SD-JWT:n kryptografinen verifiointi.
- `git diff --check` läpäisi. `.devcontainer`/Private-portin määrityksiä, Composea tai Alembic-revisioita ei muutettu.


## Ajamattomat ja yhdistämisen esteet

- ETSI TS 119 472-1 V1.2.1 / TS 119 478 V1.1.1 ja EU 2025/1569 artiklat 7/8 myöhempine muutoksineen: alkuperäislähteiden nouto **403**, joten tarkka normatiivinen vastaavuus ja ajantasaisuus vahvistamatta. TS11 itse viittaa 119 478 V0.0.7:ään, eikä sitä sekoiteta lopulliseen versioon. Tarvitaan alkutekstien tarkistus ennen yhdistämissuositusta.
- Pohja-2H:n vaadittu aito muuttamaton Tietomallit-exportin koe puuttuu edelleen noutoeston vuoksi. Synteettiset tapaukset ja upstream-migraatiotestiaineisto eivät korvaa sitä.
- Windows Docker Desktop, uuden Codespacen luonti/automaattinen selainavaus/Private-portin ajonaikainen tila, tuotanto-HTTPS ja GitHub Actionsin etätulos varmistamatta. Niiden asetuksia ei muutettu.
- Ei katalogiin rekisteröintiä, täyttä katalogipalvelua, kryptografisia SD-JWT-tarkistuksia, oikeaa myöntämistä tai lompakkointegraatiota. Nämä eivät kuulu toimitukseen. Osittaisen esityksen piilotettuja attribuutteja ei tulkita alkuperäisestä todistuksesta puuttuviksi.

Avaa **draft**-PR. Ei yhdistämissuositusta ennen yllä olevien lähde-/hyväksymispuutteiden sulkemista. README sisältää haaran Codespaces- ja Docker-kokeiluohjeet; [laajennussopimus ja kuluttajan komento](docs/attribute-semantics.md).
