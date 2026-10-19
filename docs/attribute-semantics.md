# Vaiheen 2H jatko — attribuuttien semanttiset viittaukset

18.10.2026. Työhaara `feat/phase-2h-attribute-semantics`. Perus-2H:n PR #12 on yhdistetty mainiin (`9258fff`), ja main on tuotu tähän työhaaraan commitissa `339824e`. PR #13:n GitHub-base pitää tarkistaa/vaihtaa mainiksi; API-vaihto estyi Forbidden-vastaukseen. [Normatiivisen tarkistuksen nykytila, main-pohjan testit ja tarvittavat lähdetiedostot](pr13-normative-review.md). WE BUILD 0.0.2 -aineistokoe on tehty: [tulos ja tarkat rajoitteet](webcor-acceptance.md). Koko profiilia ei väitetä generaattorin tukemaksi. Automaattista yhdistämistä ei tehdä.

## Sopimus: Metatietovarannon semanttinen laajennus 1.0.0

Uudet paketit käyttävät generaattoria `technical-package/1.1.1`. Vanhoja julkaisuja ja niiden artefakteja ei kirjoiteta uudelleen. Generointiprofiili on edelleen 2H:n rajattu SHACL-puu. Lähde on lukittu alkuperäinen profiilisnapshot, ei käsin ylläpidettävä attribuuttimalli.

Jokaisella kuvatulla attribuutilla on sama palvelimen johtama viite:

```json
{
  "rootShapeUri": "https://example.org/metatietovaranto/demo/ProductShape",
  "semanticPath": ["https://example.org/metatietovaranto/demo/companyName"],
  "term": "https://example.org/metatietovaranto/demo/companyName",
  "fieldPath": "/companyName",
  "claimPath": ["companyName"],
  "sourceProfile": {
    "uri": "https://example.org/metatietovaranto/demo/profile",
    "version": "demo-1",
    "snapshotId": "<UUID>",
    "snapshotSha256": "<hex SHA-256 of immutable snapshot manifest>",
    "snapshotUrl": "<public snapshot API URL>"
  },
  "shacl": {
    "nodeShapeUri": "https://example.org/metatietovaranto/demo/ProductShape",
    "propertyShapeUri": "https://example.org/metatietovaranto/demo/NameShape",
    "propertyShapeKind": "iri",
    "constraintPath": [{
      "nodeShapeUri": "https://example.org/metatietovaranto/demo/ProductShape",
      "propertyPath": "https://example.org/metatietovaranto/demo/companyName",
      "propertyShapeUri": "https://example.org/metatietovaranto/demo/NameShape"
    }]
  }
}
```

`term` on alkuperäinen RDF/OWL-ominaisuus; `propertyShapeUri` on eri asia. Nimettömän lähdesolmun `propertyShapeUri` on **null**, `propertyShapeKind` on `blankNode`. Myös nimetön sisäkkäinen luokkamuoto merkitään nulliksi. Alkuperäiseksi väitettyä URI:a tai parsinnan satunnaista `_:`-tunnistetta ei tuoteta.

Käyttöyhteyden yksilöi snapshot + rootShapeUri + constraintPath: jokaisessa askeleessa valitaan nykyisen muodon `sh:property`, jonka suora `sh:path` on `propertyPath`; seuraavaan luokkamuotoon siirrytään 2H:n eksplisiittisellä sh:node- tai yksiselitteisellä sh:class/targetClass-valinnalla. Samalle polulle useat PropertyShapet, useat lapsimuodot, rekursio ja muut 2H:n epäselvyydet estävät generoinnin. Sama kenttänimi `city` eri rooleissa erotetaan koko semanttisella ja rajoitepolulla.

Puuttuva lähdeversio on null ja näkyy puuteraportissa. Snapshotin tarkiste ei muutu keksityksi versionumeroksi. `snapshotSha256` koskee alkuperäistä snapshot-manifestia, ei API-vastauksen kaikkia kenttiä tai yhden Turtle-tiedoston raakatavuja; lähdetiedoston oma tarkiste löytyy snapshotista.

## JSON Schema ja Type Metadata

JSON Schema 2020-12:n ominaisuuden `x-term` on URI-merkkijono. `x-mtv-shacl` sisältää yllä olevan täydellisen viitteen. Taulukon annotaatio on ominaisuuden/taulukkosäiliön kohdalla, ei kuvitteellisena uutena SHACL-rajoitteena sen `items`-kohdassa. Sisäkkäisten olioiden jokaisella ominaisuudella on oma viitteensä. `$ref` säilyy skeemaviittauksena eikä sitä käytetä OWL-termin viittauksena.

SD-JWT VC **draft-ietf-oauth-sd-jwt-vc-19** säilyy valittuna versiona. Kunkin Type Metadata `claims[]`-kohdan `x-mtv-semantic` sisältää täydellisen viitteen. `path` on IETF Claim Path, esimerkiksi `/groups/*/members/*/city` → `["groups", null, "members", null, "city"]`. Taulukon säiliön ja alkion erilliset `sd`-käytännöt säilyvät 2H:n mukaisina. Säiliöviite kuvaa samaa lähderajoitetta ja viitteessä säilyy alkion täydellinen polku.

Nämä **x-alkuiset kentät ovat Metatietovarannon oma laajennus**, eivät IETF:n tai ETSI:n standardikenttiä. Julkaistu `semantic-extension-profile.json` yksilöi version 1.0.0 ja määrittelyn koneellisesti. Type Metadatan omat löydettävyyskentät ovat:

- `x-mtv-profile`: `{version, uri, integrity}` laajennuksen määrittelyyn;
- `x-mtv-schema`: `{uri, integrity}` yhteisen JSON-/väitesisällön skeemaan;
- `x-mtv-mapping`: `{uri, integrity}` semanttiseen mappingiin.

JSON Scheman `x-mtv-profile` ja `x-mtv-mapping` sitovat sen samoihin aineistoihin. Mappingin `attributes` sisältää lähteestä johdetut viitteet ja `extensionProfile` saman määrittelyviitteen. Semantiikka voidaan selvittää Type Metadatasta ja mappingista **lukematta JSON Schemaa tai yhtäkään väitteen arvoa**.

Valitun IETF-version Type Metadata Format -kohdan standardikenttiin eivät kuulu aikaisempien luonnosten `schema`/`schema_uri`; niitä ei tuoteta. Standardi sallii tuntemattomat lisäjäsenet ja niiden sivuuttamisen. Tavallinen kuluttaja voi sivuuttaa x-laajennukset. Emme väitä lompakoiden tulkitsevan niitä.

## Tarkisteketju ja myöntäjän vastuu

Riippuvuudet ovat syklittömiä: **laajennusprofiili → mapping → JSON Schema → Type Metadata → myöntäjän metadata-pin**. Metadata viittaa myös suoraan mappingiin ja laajennusprofiiliin. Kunkin viitteen integrity on `sha256-` + **standardin base64** SHA-256-tavuista; ei heksadesimaali eikä base64url. Tarkiste lasketaan tarkalleen julkaistavista UTF-8-tavuista. Manifestin aiemmat hex-SHA:t säilyvät eri kenttinä.

`issuer-metadata-binding.json` on julkinen kuvausmalli, **ei todistus**, ja sisältää vct:n sekä standardin `vct#integrity`-arvon Type Metadatan tarkoille tavuille. Ulkoinen myöntäjä valitsee hyväksytyn tuoteversion ja kopioi nämä standardiväitteet omaan myöntämäänsä SD-JWT VC:hen ennen ulkoista allekirjoitusta. Tämän tiedoston muut kentät (`typeMetadataUri`, `scope`, `discovery`) ovat paikallista ohjeistusta. Myöntäjän on järjestettävä valitun IETF-version mukainen Type Metadatan löydettävyys: HTTPS-vct:n on osoitettava oikeaan metadataan tai käytetään määrittelyn muuta sovittua menetelmää. Vanhaa URN-vct:tä ei muuteta hiljaisesti URL:ksi.

Kuluttaja tarvitsee **luotetusta lähteestä odotetun** vct#integrityn; samasta muokatusta paketista haettu uusi tarkiste ei todista alkuperää. Tarkisteketju ei ole allekirjoituksen, myöntäjän luottamuksen, kelpoisuuden tai lompakon tarkistus. Metadataa ja generoinnin synteettistä täyttä sisältöä validoidaan erikseen. Osittaisesta esityksestä paljastamatta jätetty väite ei osoita puuttumista alkuperäisestä todistuksesta. Esimerkkikuluttaja ei edes vastaanota esityksen väitearvoja eikä tee täydellisyysarviota.

Paketin 12 artefaktia julkaistaan nykyisillä sisältöosoitteisilla `/id/technical-packages/{packageId}/...`-reiteillä. Kolme uutta ovat `semantic-extension-profile.json`, `issuer-metadata-binding.json` ja `catalogue-coverage.json`. Muut 2H:n artefaktit säilyvät, nyt semanttisesti annotoituina. Ennen julkaisua reitit palauttavat 404; withdrawn ei poista julkaistuja kuvauksia. Uusia migraatioita ei tarvita.

## Valinnaiset katalogiviitteet ja hyväksyntä

Luonnoksen `catalogueReferences` on lista attribuutti- (`kind:attribute`) tai todistusjärjestelyviitteitä (`kind:scheme`). Kentät: `catalogueUri`, `entryUri`, `version`, `relation` (equivalent/narrower/broader/related), `provenance` (`sourceUri`, `sourceVersion`, `evidenceSha256`, `statement`). Attribuuttiviite vaatii lisäksi rootShapeUrin ja semanticPathin. Järjestelyviite ei saa esiintyä yksittäisenä ominaisuutena.

Vastaavuus on ylläpitäjän **tarkastettava väite**, ei automaattinen OWL-samastus. Evidence-tarkiste ja lähdeilmoitus säilytetään; ulkoista todistusaineistoa ei noudeta tai sen oikeudellista pätevyyttä varmenneta generaattorissa. Ihmisen hyväksyntä, revision/sisältötarkiste, kirjoittajat ja auditointi ovat nykyisen prosessin mukaiset. Viitteen muutos mitätöi hyväksynnän ja paketin; SHACLista puuttuvaa käyttöyhteyttä ei hyväksytä valmiiseen pakettiin. Vanhat API-asiakkaat, jotka jättävät uuden valinnaisen kentän pois, eivät voi huomaamatta tyhjentää aiempia viitteitä. Tyhjä lista on eksplisiittinen poistopyyntö, joka kulkee uuden hyväksynnän kautta.

## ETSI-/EU-/TS11-vastaavuus ja lähdeversiot

Catalogue of Attributes kuvaa yksittäisten attribuuttien identiteetin, semantiikan, skeemaesitykset ja todentamispalvelut. Catalogue of Schemes kuvaa todistusjärjestelyn: omistaja, säännöt, vastuut, luottamus ja sen piiriin kuuluvat attribuutit. Yksittäinen JSON Schema on vain yksi tekninen rakenneartefakti. TS11 käyttää nykyisessä versiossaan myös nimitystä Catalogue of Attestations ja paikoin schema-termiä laajassa merkityksessä; tässä näitä kolmea tasoa ei yhdistetä yhdeksi olioksi.

**Todella tarkistettu lähde:** EU:n virallisen `eudi-doc-standards-and-technical-specifications`-repositorion TS11 **1.0.1 (2026-01-30)**, commit `ee91a294c833af5188726fd8c302c641212192aa`. Markdown ja molemmat julkaistut JSON-tietomallit säilytetään muuttamattomina `fixtures/catalog-standards/`-hakemistossa; tiedostokohtaiset SHA:t ovat `sources.json`-tiedostossa ja generointimanifestissa. CC BY 4.0 -lähde-/uudelleenkäyttötieto on TS11-tekstissä. ARF 3.0.0:n viite osoitti tähän erilliseen viralliseen repositorioon; ARF-tekstiä ei käytetä TS11:n korvikkeena.

**Toimitetut alkutekstit tarkastettu:** ETSI TS 119 472-1 V1.2.1 (2026-02), ETSI TS 119 478 V1.1.1 (2026-01) ja EU 2025/1569:n konsolidointi 11.8.2026 / 001.001 on saatu käyttäjältä PDF-kopioina ja relevantit kohdat luettu. Alkuperäiset kopiot ja tarkisteet ovat fixtures/catalog-standards/originals/ ja sources.json. [Kohta-/artiklakohtainen uusi vertailu](pr13-source-comparison.md) korvaa alla olevan aiemman noutoestoon perustuvan arvion niiltä osin kuin lähde on nyt saatavilla. Riippumatonta verkkovertausta ei väitetä tehdyksi.

**Ajantasaisuuden näyttö ja raja (19.10.2026):** saatu asiakirjatietosivu näyttää aikajanassaan viimeisimpänä konsolidoinnin 11.8.2026; teksti luettelee muutoksen EU 2026/1735. Kyse on konsolidoidun tekstin sivusta: alkuperäisen asetuksen muutos-/oikaisusuhteet eivät ole esillä. Niiden tarkistus jää avoimeksi; viimeisimmän näytetyn version havaintoa ei laajenneta väitteeksi oikaisujen puuttumisesta. ETSI 472-1 viittaa SD-JWT VC draft-13:een, kun paikallinen profiili käyttää draft-19:ää; ero on näkyvä puute, ei täysi yhteensopivuusväite. TS11:n oma V0.0.7-viite säilyy lähdehistoriana eikä sitä vaihdeta V1.1.1:ksi.

| Kohde ja lähteen tila | Paikallinen vastaavuus | Puuttuva tieto / raja |
| --- | --- | --- |
| ETSI 119 472-1 V1.2.1: konteksti (toimitettu PDF tarkastettu) | Erilliset VCDM 2.0 -perus- ja tuotekontekstit; SHACL-IRI:t/scoped-kontekstit | Kohdekerroksen paikallinen toteutus; ks. 4.2.1.3 ja 7.2.1.2; täysi profiiliehtojen täyttyminen arvioimatta |
| ETSI 119 472-1 V1.2.1: schema (toimitettu PDF tarkastettu) | Annotated content.schema.json + lähde-SHACL + tarkisteet | 4.2.1.4 ja 7.2.1.3: ei täydellisen schema-/myöntäjäprofiilin väitettä |
| ETSI 119 472-1 V1.2.1: SD-JWT Type Metadata (toimitettu PDF tarkastettu) | IETF draft-19 metadata + omat x-mtv-annotaatiot | 5.2.1: draft-13/draft-19-ero; oma x-mtv-laajennus ei ole standardikenttä |
| ETSI 119 478 V1.1.1: semantiikan/skeemien löydettävyys (toimitettu PDF tarkastettu) | Profiilin URI/snapshot; x-mtv-schema/mapping; valinnaiset ulkoiset attribuuttikatalogiviitteet | 5.2.3 ja 5.3: ei standardin DIP-/todentamispalvelun toteutusta |
| TS11 1.0.1 §2.1 Attribute: identifier/nameSpace | Alkuperäinen term-IRI ja eksplisiittinen catalogueReferences.attribute | OWL-ominaisuus ei ole automaattisesti katalogin antama attribuuttitunniste; namespace/local/version-katalogi-identiteetti puuttuu ilman hyväksyttyä viitettä |
| TS11 §2.1: name/description/semanticDataSpecification | SHACL-nimet/kuvaukset, lähdeprofiili ja versioitu snapshot | Englanninkielinen nimi/kuvaus ei ole taattu; näyttönimestä ei päätellä teknistä identiteettiä |
| TS11 §2.1.1 DataService / authenticSources | Olemassa olevat vastuuorganisaatiot ja ulkoiset palvelukuvaukset | Jäsenvaltion/tietolähteen viralliset tunnisteet ja hyväksytty todentamisosoite eivät synny skeemasta |
| TS11 §2.1.2 SchemaDistribution | Teknisen skeeman URI, mediatyyppi ja integrity; metadata/mapping erillisinä | Paikallinen application/schema+json ei ole automaattinen katalogirekisteröinti tai väite TS11:n tekstin application/json-schema-mediatyypistä |
| TS11 §4.3 SchemaMeta: id/version/rulebookURI | Paketilla oma CID ja generaattoriversio; valinnainen scheme-viite | Katalogipalvelimen schema-ID, järjestelyn versio/tila ja hyväksytty Rulebook eivät ole sama kuin tuotteen/snapshotin versio |
| TS11 SchemaMeta: supportedFormats/schemaURIs | Toimitustyyppi + formaattikohtaiset artefaktiosoitteet | Ei suoraa enum-muunnosta application/dc+sd-jwt → kaikkiin TS11-formaatteihin; mdoc ei kuulu toteutukseen |
| TS11 SchemaMeta: trustedAuthorities/attestationLoS/bindingType | Haltijasidonta/suojaus ovat erillisiä hyväksyttyjä toimitusasetuksia | Luottamusankkurit, järjestelyn LoS ja claim/key/biometric-bindingType vaativat erillisen arvion; holderBinding=required ei yksin ratkaise niitä |
| EU 2025/1569 art.7(5), toimitettu konsolidointi: attribuutin namespace/tunniste/semantiikka/tyyppi | Alkuperäiset IRI:t, SHACL, lähdeversio/SHA, datatype, skeema ja mahdollinen attribuuttikatalogiviite | Oikaisusuhteiden tarkistus, rekisteröinti, yhteystiedot, oikeusperusta ja authenticSources puuttuvat |
| EU 2025/1569 art.8(3), toimitettu konsolidointi: järjestelyn nimi/omistaja/tila/versio/säännöt/formaatit/attribuutit | Tuotemetatiedot, kolmen formaatin kuvaukset, valinnainen scheme-viite ja attribuuttimappingit | Järjestelyn hyväksytty omistajuus/yhteystiedot, säännöt, luottamus/governance/revokaatio, tarjoaja-/lähdevaatimukset ja oikeudellinen luokka eivät seuraa formaatista |
| EU 2025/1569 versio- ja oikaisutiedot | Aikajanassa viimeisin 11.8.2026 vahvistettu; `EU_CORRIGENDUM_STATUS_UNVERIFIED` raportissa | Konsolidoinnin sivu ei sisällä alkuperäisen asetuksen oikaisurekisteriä; ei väitettä myöhempien oikaisujen puuttumisesta |

`catalogue-coverage.json` sisältää tämän paikallisen kartoituksen keskeiset kentät, tarkistetut lähdepinnit, viitteet ja puuttuvat tiedot. Status on **partial**, conformanceClaim=false. Katalogiin rekisteröintiä, täyttä katalogipalvelua tai oikeudellista/ETSI-/EUDIW-vaatimustenmukaisuutta ei toteuteta.

## Esimerkkikuluttaja

`examples/semantic_consumer.py` käyttää vain Pythonin standardikirjastoa ja yhteistä `apps/semantic_reader.py`-lukijaa. Esimerkiksi paikallisessa Docker-demossa, tuotteen normaalin julkaisun jälkeen:

```sh
docker compose exec app .venv/bin/python examples/semantic_consumer.py \
  --type-metadata http://localhost:8000/id/technical-packages/PAKETIN_TUNNISTE/sd-jwt-type-metadata.json \
  --integrity 'sha256-ODOTETTU_STANDARD_BASE64' \
  --claim-path '["companyName"]'
```

Hae oikea tunniste ja myöntäjän käyttöön tarkoitettu pin julkaistun tuotteen `issuer-metadata-binding.json`-artefaktista. Demossa tämä on kuvausten kokeilu; tuotannossa odotetun pin-arvon alkuperä on varmistettava erikseen myöntäjän luottamusprosessissa. Lukija palauttaa propertyIrin, SHACL-kytkennän ja sourceProfilen. Se ei vastaanota tai pura JWT:tä, ei käsittele disclosureja eikä tarkista allekirjoitusta, esityksen täydellisyyttä tai myöntämisoikeutta.

Lukijan verkkosovitin noutaa vain käyttäjän eksplisiittisesti valitsemasta alkuperästä, ei seuraa uudelleenohjauksia, rajaa dokumentit 2 MB:iin ja käyttää 10 sekunnin aikarajaa. HTTPS vaaditaan paikallista localhost-demoa lukuun ottamatta. Generaattorin validoinnissa käytetään vain muistissa olevia lukittuja dokumentteja, ei tätä verkkosovitinta. Codespacesin Private-portti säilyy: ulkoinen anonyymi lukija ei pääse sen läpi. Tämä ei muuta portin näkyvyyttä tai lisää salaisia käyttöoikeustokeneita.

## Ajettu julkisen kuvauksen koe tässä ympäristössä

18.10.2026: selaintesti julkaisi synteettisen tuotteen `6e6214d0-82be-44ad-9495-3dd0ab388cf2` version 1.0.0 normaalilla eri käyttäjän hyväksynnällä. Paketin tunniste oli `4db0ebac58d0d485160ecf772ab0c9833d9864bb8ec7376291470c413bc6823e`. Kontissa ajettu kuluttaja palautti companyName-polun IRI:n `https://example.org/metatietovaranto/demo/companyName`, PropertyShapen `https://example.org/metatietovaranto/demo/NameShape` ja lähdeversion `synthetic-demo-2e`. Lähdesnapshotin tarkiste oli `e52039c7417a8869bee8a315f8d1884ce007c25886ca8082966e9c8b69a62749`. Type Metadatan vct#integrity oli `sha256-uFw1xGSU7N56JGoW1J3P8MQg4mwYHof/D3yoJSzmkSQ=`. Kaikkien 12 julkisen artefaktin tavut, tarkisteet ja mediatyypit tarkistettiin.

Nämä tunnisteet ovat tämän paikallisen testikannan havaintoja, eivät uudessa Codespacessa valmiiksi olemassa olevia fixtureitä tai pysyvän julkisen internet-palvelun julkaisu. Uudessa demossa julkaise oma synteettinen versio ja käytä sen artefaktiosoitteita/pin-arvoa yllä olevaan komentoon.

## WE BUILD -aineistokokeen tuonti jatkohaaraan

Perus-2H:n 8bc37dc yhdistettiin tähän työhaaraan; samalla testaamme generaattorin 1.1.0 todelliset attribuuttiannotaatiot erillisellä paikallisella projektiolla. `x-term` ja Type Metadatan `term` ovat eu-core:familyName; `propertyShapeUri` on eri webcor:familyName. SourceProfile pysyy paikallisena testiprofiilina (`urn:metatietovaranto:test:webcor-family-name`, `0.0.2-local-test-1`), koska lisätty xsd:string-rajoite ei ole alkuperäisen webcor 0.0.2:n vaatimus. Se ei saa vaihtua alkuperäisen mallin identiteetiksi pelkkien samojen IRI:en perusteella.

Jatkohaaran paketti-/attribuuttisemantiikan sarja: **58 passed, 1 warning in 50.08s**. Ei epäonnistuneita tai ohitettuja. Mukana kaikki 42 pakettitestiä (myös 8 uutta aidon aineiston tapausta) sekä 16 attribuuttisemantiikan testiä; uusi testi varmistaa paikallisen projektion lähde-identiteetin ja alkuperäisen ominaisuus-/PropertyShape-IRI:n eron. Tämä ei ole uusi täysi API-/migraatioajo tässä jatkohaarassa, eikä päällekkäisiä testejä lasketa uutena kokonaismääränä.

Tämä täydennys muuttaa vain testiaineistoa, testejä ja dokumentaatiota. Sovellus, UI, skeema ja käynnistyspolku eivät muutu; Docker-buildia, web-buildia tai selaintestejä ei ajettu uudelleen tätä täydennystä varten. Aiemmat ajot on erotettu STATUSissa. ETSI-/EU-alkutekstien varmistus on edelleen avoin.
