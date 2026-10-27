# Pages: käyttäjän hyväksymä paikallinen SHACL-tuontikorjaus

Tietomallit-exportin `sh:datatype "http://www.w3.org/2001/XMLSchema#string"` on merkkijonoliteraali, joten se pysähtyy edelleen DATATYPE_TERM-tarkistukseen. Tämä muutos tarjoaa erillisen, käyttäjän hyväksymän tuontikorjauksen: vain versionhallittuun listaan kuuluva tietotyyppi-URI voidaan muuttaa kyseisen kolmikon IRI-objektiksi. SHACLin sisältörajoitteita ei päätellä tai muuteta.

## Konkreettinen ennen/jälkeen ja työnkulku

```turtle
# Alkuperäisessä lähteessä; alkuperäinen säilytetään tavuineen/hashineen:
sh:datatype "http://www.w3.org/2001/XMLSchema#string" .

# Käyttäjän hyväksymässä erillisessä kopiossa:
sh:datatype <http://www.w3.org/2001/XMLSchema#string> .
```

1. Tuo ja liitä profiili normaalisti. Tarkista generointituki; DATATYPE_TERM avaa **Tarkastele ehdotettuja tuontikorjauksia**.
2. Tarkasta koko aineiston ehdotukset (lähde/rivi, PropertyShape, polku, alkuperäinen termi, ehdotettu IRI ja tuen rajoite) ja valitse hyväksyttävät muutokset. Mitään ei valita automaattisesti.
3. **Luo korjattu paikallinen kopio** tallentaa uuden profiilin ja raportin. Alkuperäinen jää edelleen generoinnin aineistoksi.
4. **Käytä korjattua kopiota generoinnissa ja tarkista tuki** vaihtaa aineiston eksplisiittisesti ja tarkistaa juuren tuen uudelleen. Muut esteet eivät katoa termikorjauksella. Hyväksynnät tyhjennetään ja aiempi paketti vanhenee.
5. Tuettu synteettinen demotapaus muodostaa paketin normaaleilla tarkastetuilla esitys-/toimitustapavalinnoilla. Paketin manifesti sitoo korjatut lähteet, alkuperäiset lähteet ja korjausraportin tarkisteketjuun. Ei SHACL-validoinnin, riippumattoman hyväksynnän tai julkaisun väitettä.

**Metatietovarannossa korjattu paikallinen kopio – ei alkuperäinen export** näkyy valitulle korjatulle aineistolle. Alkuperäinen, korjattu tiedosto ja raportti ovat ladattavissa. Alkuperäiseen voi palata ja saada alkuperäiset lähdehavainnot takaisin.

## Toteutus ja eheys

- N3-parserin tokenisijainnit + RDF-quad kohdistavat objektin. Vain hyväksytyt lähdealueet korvataan; alkuperäistä ei uudelleenserialisoida. Kommentteja sisältävä epäselvä typed literal -alue estää korjauksen. Ei koko tiedoston regex-korvausta.
- Sääntö `mtv-shacl-datatype-iri/1.0.0`: 10 tuettua XSD-tyyppiä ja rdf:langString. Korjauskelpoisuus ja generointituki ovat erillisiä. Ei trimmausta, kielimerkittyjen arvojen pakotusta, tuntemattomia tyyppejä, rdfs:Literal-tulkintaa tai nimeämis-/kardinaliteetti-/OWL-muutoksia.
- Täysi rajatun editin kolmikkolistavertailu sallii vain hyväksytyt objektimuutokset. Nimetyt ja nimettömät solmut, tiedostorajat, BOM/rivinvaihdot ja muu sisältö säilyvät. Ei yleistä RDF-isomorfismialgoritmia tai SHACL-/OWL-päättelyä.
- Raportti sekä alkuperäiset/korjatut sisällöt ja SHA-256:t säilyvät v1-kokeilun tallennuksessa ja JSON-viennissä/palautuksessa. Worker toistaa korjaukset ja tarkistaa raportin, graafimuutokset ja hashit tuonnissa sekä ennen generointia. Pakettiin upotettu raportti/lähteet tarkistetaan myös erikseen. Pelkkä tarkisteiden uudelleenlaskenta ei hyväksy väärää korjausraporttia.
- Käyttäjän approved-merkintä on paikallinen ilmoitus; se ei todenna henkilöllisyyttä, hyväksymishetkeä tai alustalta saatua alkuperää. Ei allekirjoituksia, verkkoon lähetettäviä aineistoja tai etäriippuvuuksien noutoa.
- Selainversion tunniste 1.0.3; palvelingeneraattori 1.1.3 ennallaan. Ei backend-, migraatio-, käyttöoikeus-, hyväksyntä- tai vanhojen julkaisuversioiden muutoksia. Vanha v1-kokeilu avautuu ilman muunnosta; aiemman generaattoriversion paketti säilyy mutta vanhenee version mukana.

## DigiOne OSAD -koe ja rajoitteet

Alkuperäinen käyttäjän toimittama export on tavuntarkka testifixture provenansseineen: 65 833 tavua / 1 043 kolmikkoa, SHA-256 `2ec18648da935748d2371d76885ee998279aa5b458e41d2cff12461bbb49cf75`. Ilmoitettu lähdeversio 1.0.0; ei verkkovarmennusta. Fixture ei kuulu julkiseen Pages-katalogiin.

52 lainatusta tietotyyppiarvosta **51 tuottaa korjausehdotuksen**. Yksi rdfs:Literal jää käsin tarkastettavaksi. rdf:langStringin termi voidaan korjata, mutta generointi pysyy tukemattomana kielitietoa menettämättä. Learner-juuren valitut id-1/rightToStudyId-korjaukset poistavat kaksi DATATYPE_TERM-havaintoa. Sen jälkeen oletusnimi id tuottaa nykyisen RESERVED_NAME-eston; Worker-testin erikseen tarkastettu learnerId-nimivalinta mahdollistaa juuri tämän juuren mapping-ehdotuksen. Käyttöliittymän virheellisen ehdotuksen nimeämistoimintoa ei laajenneta tässä tehtävässä. **Koko DigiOne-profiilia tai valmista pakettia ei väitetä tuetuksi.** Date/dateTime-esimerkkien selainleksikaali jää aiemmaksi rajoitteeksi.

## Tarkistukset

- 33 uutta kohdennettua testiä läpäisi: valitut ja idempotentit korjaukset, sallittujen graafimuutosten vertailu, NamedNode/URI-literaali, kielitieto, rdfs:Literal, muut predikaatit/kommentit, typed/triple-quoted/escaped literalit, BOM/CRLF, nimetön solmu, toistuvat lauseet, prefixin uudelleenmäärittely, muokatut raportit/hashit ja DigiOne.
- Todellinen Chromiumin UI-polku: hyväksyntä/peruutus, erillinen aineistovalinta ja tuen uusintatarkistus, paketin generointi, molempien lähteiden/raportin lataus, tallennus/uudelleenavaaminen, JSON-vienti/palautus, lähde- ja valintamuutosten vanheneminen. Sekä muokatun profiiliraportin että paketin raportin hylkäys, myös kun artefaktihashit lasketaan uudelleen.
- 78 API-/profiiliregressiota läpäisi: `tests/test_technical_packages.py`, `tests/test_semantic_validation.py`, `tests/test_attribute_semantics.py`. Erillinen catalog_test; mukaan kuuluvat oikeudet, hyväksyntä, julkaisu ja artefaktien eheys.
- 13 palvelinselaintestiä läpäisi lopullista Docker-imagea vasten: oikea Keycloak, tallennus/uudelleenavaaminen, oikeudet, riippumaton hyväksyntä, julkaisu, artefaktit ja elinkaari.
- Tavallinen web-build, Pages-build (myös ohjekääntäjän 3 testiä), Docker-build ja Compose-käynnistys läpäisivät. Katalogin 13 taulun hashit ja Alembic-head säilyivät ennen/jälkeen uudelleenkäynnistyksen.
- **152/152 staattista testiä läpäisi** (33 uutta). Ei API-/auth-/ulkoisia verkkopyyntöjä eikä JavaScript-virheitä. Olemassa oleva oikean JSON-LD-prosessorin RDF/SHACL-vertailukoe sisältyy sarjaan.
- Erillinen HTTP-yhteensopivuuskoe luki 136 julkaisuversiota ja vertasi 12 valitun tallennetun paketin 126 artefaktin sisältöjä/SHA-256-tarkisteita alkuperäisiin tietokantaan tallennettuihin tavuihin. Jaettu contract ja ohjeiden ajantasaisuus sekä git diff --check läpäisivät.

**Ajamattomat:** koko backend-testisarja ja erillinen legacy-migraatiokoe (backend/skeema/migraatiot eivät muutu), Firefox/Safari, Windows Docker Desktop, Codespacesin oma käynnistys, fyysinen puhelin ja oikea ruudunlukija sekä julkinen deploy/Actions. Aiemmat generointirajoitteet ja DigiOnen yllä kuvatut esteet säilyvät; ei väitettä koko profiilin tai standardien täydellisestä tuesta.

## Kokeile ennen yhdistämistä ja julkaisun jälkeen

Checkout `feat/local-shacl-repair`, aja `bash scripts/build-pages.sh` ja `uv run --locked python -m scripts.preview_pages --port 4173`. Avaa `http://127.0.0.1:4173/metatietovaranto/#kokeilu`. Käyttöohjeen osio 12 kuvaa uudet kentät ja valinnat. Realistiseen virhekokeeseen voit tuoda `fixtures/tietomallit/digione-osad-2026-10-27/original.ttl` ja käyttää Learner-juurta. Onnistuneen generoinnin synteettinen testi käyttää erillistä kopiota semantic-profile-demo.ttl:stä, jonka vain sh:datatype xsd:string kirjoitetaan lainatuksi URI-literaaliksi. Alkuperäisiä fixtureitä ei muokata.

Yhdistämisen jälkeen nykyinen mainin **Public Pages demo** julkaisee hyväksytyn version. Varmista buildin, testien, deployn ja HTTP-varmistuksen onnistuminen. PR-haaraa ei julkaista. Tätä PR:ää ei yhdistetä automaattisesti.
