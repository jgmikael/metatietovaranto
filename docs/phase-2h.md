# Vaihe 2H — SHACL-pohjainen tekninen kuvauspaketti

Pohja `ac002ad` (2G / PR #11). Tämä käyttäjän toimeksianto korvaa aiemman ehdotuksen käyttää 2H-tunnusta DCAT-AP-vientiin. DCAT-AP jää myöhemmäksi. Tietomallit on sisältömallinnustyökalu; Metatietovaranto hyväksyy vain esitysvalintoja ja tuottaa niistä johdannaisia.

## Tuettu generointiprofiili `shacl-tree-json-v1`

- Yksi eksplisiittinen IRI-juurimuoto (`sh:NodeShape`) ja täsmälleen yksi IRI-muotoinen `sh:targetClass`.
- Ominaisuudella yksi suora IRI-muotoinen `sh:path`. Samaa ominaisuutta ei määritellä samassa muodossa kahdesti.
- Literaalilla yksi eksplisiittinen XSD-tyyppi: string, boolean, integer, nonNegativeInteger, positiveInteger, decimal, double, date, dateTime tai anyURI. Decimal esitetään JSON-merkkijonona tarkkuuden säilyttämiseksi. Päivien, aikojen ja URI-literaalien leksikaalinen rajaus on sama kuin 2F:n `typed_literal`-muunnoksessa.
- Oliolla yksi `sh:node`, tai `sh:class`, jolle lukitusta graafista löytyy yksiselitteinen kohdemuoto. Sisäkkäisen olion luokka tulee kohdemuodosta tai `sh:class`-arvosta; ristiriita estää generoinnin. Syklitön puu, enintään kahdeksan sisäkkäistä tasoa ja 200 kenttää.
- `sh:minCount` / `sh:maxCount`, enintään 10 000. maxCount=1 tarkoittaa skalaaria/oliota; muu arvo, myös puuttuva yläraja, järjestyksetöntä taulukkoa. Literaalien duplikaatit estetään, koska ne häviäisivät RDF-joukkoon. Taulukon järjestykselle ei luvata semantiikkaa.
- `sh:name`, description, order, group, message, severity ja defaultValue säilyvät lähteessä; ne eivät muuta teknisiä nimiä tai tuota oletusarvoja. `sh:closed` sallitaan vain, kun tuotettu rdf:type on sallittu ignoredProperties-listassa.
- Muut kohdistuvan sisältömuodon SHACL-predikaatit estävät generoinnin yksilöidyllä havainnolla. Esimerkiksi pattern, in, kielirajoitteet, nodeKind, loogiset/yhtäsuuruus/qualified-rajoitteet ja deactivated eivät ole tämän generaattorin häviöttömästi tukemia. Myös rekursio, monimutkaiset polut, RDF-listasisältö, nimeämätön/epäselvä sisältörakenne ja tuntematon tietotyyppi estävät valmiin paketin.
- Lähteen koko graafi ja riippuvuudet säilyvät muuttumattomina. Valittu juuri on johdannaisen esitysvalinta; sitä ei kirjoiteta profiilisnapshotiin. Paketillisen luonnoksen mapping- ja esimerkkiraportti ilmoittaa valitun juuren. Muut 2D:n offline Core -turvarajat säilyvät.

JSON Schema on tämän profiilin rakenteellinen johdannainen, ei yleinen SHACL-käännös. Esimerkiksi XSD dateTime -leksikaalista avaruutta ei väitetä JSON Schema date-time -formaatin kanssa samaksi. Täsmällinen leksikaalinen tarkistus, JSON→RDF, JSON-LD-prosessointi ja lähde-SHACL ovat erillisiä tarkistuksia.

## Esitysvalinnat ja mappingit

`POST /api/v1/drafts/{id}/technical-package/proposal` saa `{rootShapeUri, names?}`. Omistajan editor, istunto, CSRF ja If-Match tarvitaan myös tallentamattomaan ehdotukseen. Ehdotus ei korvaa luonnosta tai mappingeja.

Nimeämisjärjestys on eksplisiittinen lähteen `iow:localName` / liitetyn johdannaisen `semanticMappings.propertyName`, muuten ominaisuus-IRI:n viimeinen `/`, `#` tai `:`-osa, jos se on ASCII-tekninen nimi. Muuten `field_` + ominaisuus-IRI:n SHA-256:n 12 ensimmäistä heksamerkkiä. Kääntyvästä näyttönimestä ei johdeta nimeä. Keskenään eri eksplisiittiset nimet, saman olion törmäykset ja VC/JWT/JSON-LD-/JavaScript-varatut nimet estävät ehdotuksen. Ylläpitäjä voi antaa tarkastetun nimen täydelle semanttiselle polulle; tyyppiä ja kardinaliteettia ei voi antaa generaatiopyynnössä. Nimien toistuminen eri sisäkkäisissä olioissa sallitaan scoped-konteksteilla.

`POST /api/v1/drafts/{id}/technical-package` saa lisäksi `acceptRepresentation:true`, `replaceMappings`, `mappingVersion`, `exampleContent`, `synthetic:true` ja `acceptFormatPolicies:true`. Kaikki kolme toimitustapaa on tallennettava ensin. Molemmat toiminnot tarkistavat myös nykyisen oikeuden lukea valittua profiilisnapshotia. Tallentava generointi vaatii lisäksi tarjoajaorganisaation editor-oikeuden kuten tavallinen luonnoksen tallennus. Olemassa olevan mappingin korvaaminen vaatii eksplisiittisen luvan ja muuttunut mapping suuremman version. Sama hyväksytty nimi/oliorakenne koskee kaikkia kolmea muotoa; W3C käyttää `/credentialSubject`-etuliitettä ja SD-JWT erillisiä paljastamispäätöksiä.

Puuttuva vct, suojausprofiili, tarvittavat algoritmit tai perClaim-kenttäpäätös estää generoinnin. Haltijasidonta, paljastamiskäytäntö ja suojaus tulevat tallennetun toimitustavan hyväksytyistä asetuksista ja sisältyvät tarkastettavaan mapping-artefaktiin. Niitä ei päätellä SHACLista. Epäonnistunut generointi palauttaa havainnot eikä korvaa mahdollista aiempaa pakettia; muutoksen jälkeen vanhentunut paketti ei kelpaa julkaistavaksi.

## Standardilukot ja artefaktit

SD-JWT:n lähde on virallisen OAuth-työryhmän `oauth-wg/oauth-sd-jwt-vc`-repositorio, julkaistu tagi **draft-ietf-oauth-sd-jwt-vc-19**, commit `aa2f9713659fc593b4361874f0667255b0ead8ae`. Se on Internet-Draft, ei lopullinen RFC. Toteutus aloitettiin 17.10.2026: IETF archive/datatracker -verkkonoudot saivat ympäristössä 403:n, joten tarkistus tehtiin virallisen Git-repositorion lähteestä. Päähaaran -20-työversion muutoksia ei oteta automaattisesti käyttöön. Lukittu teksti ja lisenssi ovat `fixtures/standards/`-hakemistossa, tarkiste generointimanifestissa.

W3C VCDM 2.0:n peruskonteksti on erillinen paikallinen kopio osoitteen `https://www.w3.org/ns/credentials/v2` aineistosta: virallinen `w3c/vc-data-model`, commit `69ebe41c2206e15da26473a800a405c5e4c4242f`, polku `contexts/credentials/v2`. Sen tavut ja tarkiste lukitaan paketin generointitietoihin. Oma JSON-LD 1.1 -konteksti ei määrittele `id`, `type`, `issuer` tai credentialSubject-termejä uudelleen.

| Artefakti | Mediatyyppi ja tehtävä |
| --- | --- |
| context.jsonld | application/ld+json; alkuperäiset ominaisuus-IRI:t, XSD-tyypit, luokka-IRI:en deterministiset aliasnimet, scoped oliokontekstit, @set-taulukot |
| content.schema.json | application/schema+json; yhteinen JSON-/SD-JWT-väitesisältö, JSON Schema 2020-12 |
| sd-jwt-type-metadata.json | application/json; vain IETF:n vct/name/description/claims-kentät, path/mandatory/sd/display |
| semantic-mapping.json | application/json; erillinen semanttinen mapping, profiiliviite ja hyväksytyt muotokohtaiset asetukset |
| content-example.json | application/json; synteettinen yhteinen sisältö |
| sd-jwt-claims-example.json | application/json; sama synteettinen sisältö, ei JWT/disclosureja/allekirjoitusta |
| unsigned-vc-example.jsonld | application/ld+json; VCDM-kuori, erilliset perus- ja oma konteksti, selvä SYNTHETIC UNSIGNED / NOT ISSUED -kuvaus, ei proofia |
| validation.json | application/json; erillisten tarkistusten tulokset ja laajuus |
| manifest.json | application/json; lähdesnapshot/tarkiste, esitysvalinnat/mappingit, generaattori/käytäntö, standardit/moottorit, artefaktien tarkisteet |

IETF:n claim path muodostuu JSON Pointer -mallista purkamalla escapet ja muuttamalla `*` JSON-nulliksi: `/addresses/*/city` → `["addresses", null, "city"]`. Taulukon säiliö on erillinen `sd:never`-kuvaus; alkion paljastamispäätös koskee null-polkua. Sisäinen `selective` → IETF `sd:always`, sisäinen aina näkyvä `always` → `sd:never`. JSON Schema, semanttiset IRI:t ja haltijasidonta eivät esiinny keksittyinä standardikenttinä Type Metadatassa. `mandatory` huomioi myös valinnaiset vanhemmat; tarkka ehdollinen kardinaliteetti tarkistetaan JSON Schemalla ja SHACLilla. vct säilyy toimitustavan hyväksyttynä tunnisteena; URN-vct ei muutu huomaamatta HTTP-noutolinkiksi.

## Determinismi, hyväksyntä ja julkaiseminen

Paketti on palvelimen muodostama JSONB-sisältö luonnoksessa ja muuttumattomassa ProductVersionissa. Uutta relaatiomigraatiota ei tarvita; Alembic head pysyy `0005_lifecycle`. Asiakas ei voi toimittaa valmista pakettia/raporttia ProductWrite- tai generaatiopyynnössä.

Sisältöosoitteinen packageId on lähdesnapshotin, juuren, hyväksyttyjen esitysvalintojen, mappingien, muotokohtaisten asetusten, synteettisen JSON-syötteen, generaattori-/käytäntö-/standardi-/moottoriversioiden ja julkaisuosoitteen tarkiste. Manifestilla ja jokaisen artefaktin UTF-8-tavuilla on omat tarkisteensa. Samat lukitut syötteet tuottavat samat tavut. Ajonaikaiset ajat jäävät luonnoksen modifiedAt-, audit- ja tavanomaisiin validointitietoihin; niitä ei lisätä deterministisiin artefakteihin. Profiilin aiempia acquisition-aikoja ei muuteta.

Generointi on editorin kirjoitus, joka kasvattaa revision, kirjaa auditin ja mitätöi hyväksynnän myös silloin, kun artefaktien tavut ovat samat. Sidotun profiilin, otsikon/kuvauksen, toimitustapojen/mappingien tai teknisten asetusten muutos merkitsee paketin needsRegeneration-tilaan. Lähetys, hyväksyntä ja julkaisu estetään vanhentuneelle paketille. Paketittomien vanhojen luonnosten prosessi säilyy; vanhoja julkaisuja ei muuteta eikä täydennetä taustalla.

Vain julkaistun ProductVersionin kautta saatava `GET /id/technical-packages/{packageId}/{artifactName}` palvelee tarkat lukitut tavut, oikean mediatyypin, SHA-ETagin, immutable-välimuistiohjeen, nosniff/CSP-otsakkeet ja julkisen CORS-lukuoikeuden. Luonnoksen julkinen osoite palauttaa 404. Withdrawn ei poista aiempien artefaktien saatavuutta. Uusi paketti saa uuden sisältöosoitteisen version; muuttumaton tuoteversio yksilöi sen hyväksynnän ja julkaisuversion.

Osoitteiden alkuperä on luotettu PUBLIC_BASE_URL / Codespaces-asetus, ei pyynnön Host. Codespaces käyttää HTTPS-osoitteita ja portti pysyy **Private**-tilassa: ulkoisen myöntäjän anonyymi kontekstinouto ei toimi GitHubin pääsynvalvonnan läpi. Tuotannollinen konekäyttö tarvitsee pysyvän HTTPS-julkaisualustan. Paikallinen Windows/Linux-demo käyttää tarkoituksella `http://localhost:8000`; manifesti ilmoittaa tämän local-demo-http-poikkeuksena eikä väitä localhostia HTTPS-palveluksi. Palvelun osoitteen vaihtaminen ei siirrä jo julkaistujen artefaktien alkuperää automaattisesti.

## Todennus ja realistisen aineiston rajoite

PyLD 2.0.4 käsittelee generoidun kontekstin oikeana JSON-LD 1.1 -kontekstina. Dokumenttilataaja sallii vain täsmällisen pakettikontekstin ja lukitun W3C-peruskontekstin; mielivaltaiset verkkokontekstit hylätään. Sekä sisältöolio että koko VC-kuori käsitellään prosessorilla. Sisältögraafia verrataan isomorfisesti erillisellä 2F-muunnoksella tuotettuun odotettuun graafiin (RDF 1.1:n simple literal / xsd:string -yhtäläisyys huomioidaan), ja todellinen prosessorin RDF tarkistetaan lähde-SHACLilla. Testissä verrataan lisäksi käsin kirjoitettuun odotettuun RDF-graafiin. Pelkkä 2F-laboratorion tulos ei riitä.

Generointi on verkoton aliprosessi: 8 CPU-sekuntia, 768 MiB muistia, 20 sekunnin seinäkelloraja. Aiemmat SHACL-/tuontirajat säilyvät. Esimerkin raja 100 kB ja JSON-rakenteen/kolmikoiden 2F-rajat estävät kohtuuttomat syötteet. SPARQL/JS/AF, OWL-päättely ja mielivaltaiset verkkoriippuvuudet eivät käynnisty.

`fixtures/tietomallit/fi-dcatap-upstream.ttl` on tavuntarkka kopio **virallisen työkalurepositorion migraatiotestiaineistosta**, alkuperä/commit/tarkiste `provenance.json`-tiedostossa. Se sisältää mm. testimuokkauksen `Invalid@fr`, joten sitä ei väitetä muuttamattomaksi aidoksi live-exportiksi. Koko aineiston sh:in/pattern-rajoitteet estävät tämän generaattorin; testissä muodostetaan erikseen merkitty suppea projektio, joka säilyttää kansallisen shape-IRI:n ja ulkoisen dct:modified-IRI:n. Alkuperäistä tiedostoa ei muokata. **Käyttäjän edellyttämä aidon julkisen Tietomallit-exportin hyväksymiskoe on vielä avoin**, koska iri.suomi.fi/tietomallit.suomi.fi:n verkkonouto on estetty 403:lla. Tämä on erotettava synteettisten ja upstream-testiaineiston onnistumisista ennen yhdistämissuositusta.

## Ulkoiselle myöntäjälle jää

Lähdetietojen haku, tunnistaminen, asiointivaltuudet, myöntämispäätös, todistuksen yksilökohtainen muodostus, allekirjoitus, disclosuret, haltijasidonnan toteutus, statuksen/voimassaolon toteutus ja lompakkotoimitus. Katalogin JSON-/JSON-LD-metatietovienti ei ole lähdetietorajapinta. Palveluiden saatavuus-/planned-merkinnät, pysyvät myöntäjän aloituslinkit ja 2G:n toimintojen estot säilyvät. Ei QR-koodeja tai uutta integraatiota.
