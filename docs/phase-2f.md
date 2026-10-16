# Vaihe 2F — hallittu synteettisen JSON-sisällön RDF-esikatselu

Pohja main `feca7b8`, käyttäjän yhdistämä PR #9 (2E). ROADMAPin seuraavista avoimista töistä rajataan hallittu JSON → RDF -muunnos paikalliseksi valmisteluksi. Vaiheen 3 integraatioita ei toteuteta.

## Sopimus ja suunnitelma

- Editor kokeilee tallennetun luonnoksen toimitustapamappingeja synteettisillä JSON-objekteilla. W3C-esimerkki on vain mappingin sisältöpolun mukainen sisältöolio; SD-JWT-esimerkki on erillinen synteettinen väiteolio. Kokonaista VC:tä, JWT:tä tai disclosureja ei vastaanoteta tai pureta.
- POST `/api/v1/drafts/{draftId}/conversion-preview`: istunto, CSRF, omistajaorganisaation editor ja ajantasainen If-Match. Body `{examples: [{distributionId, content, synthetic: true}]}`. 1–3 eri toimitustapaa, 100 kB per UTF-8-sisältö, yhteensä 200 kB. Vain yksityinen esikatselu; ei tallennusta, audit-sisältökopioita, julkaisuporttia tai hyväksynnän muutosta.
- Raportti yksilöi luonnoksen revision/sisältötarkisteen, profiilin UUID/SHA-256:n, toimitustapojen mapping-versiot/tarkisteet, syötteiden tarkisteet ja muunnos-/SHACL-käytännöt. Raporttia ei oteta asiakkaalta vastaan julkaisutodisteena.
- Vain yksi yksiselitteinen juurimuoto ja sen yksi sh:targetClass. Muunnos käyttää 2E:n IRI-ketjuja ja JSON Pointer -mallipolkuja; sisäkkäiset oliot ja /*-taulukot käsitellään vanhemman jokaisen esiintymän sisällä. Ei nimistä arvattuja semanttisia ominaisuuksia tai liiketoimintatunnisteita.
- Juuritietue ja sisäkkäiset oliot saavat anonyymit RDF-solmut; lähteen ominaisuus- ja luokka-IRI:t säilyvät. IRI-viitearvot, kielitunnisteet, RDF-listat, rekursio, monijuuriset profiilit ja identiteettien yhdistäminen eivät kuulu tähän profiiliin. Tukematon rakenne ei saa onnistumista.
- JSON-taulukko tarkoittaa järjestyksetöntä moniarvoista ominaisuutta. Järjestystä ei väitetä säilytettävän. Toistuvat samat literaalit hylätään, koska RDF-joukko hävittäisi ne. Olioiden erilliset esiintymät säilyvät anonyymeinä solmuina. Null, kartoittamaton kenttä tai tyhjä tuntematon säiliö hylätään.
- Tuetut XSD-literaalit: string, boolean, integer, nonNegativeInteger, positiveInteger, decimal, double, date, dateTime ja anyURI. Integer/boolean/double käyttävät JSONin omia tyyppejä; decimal annetaan tarkkana merkkijonona. Date/dateTime ovat rajattuja ISO-esityksiä (dateTime enintään kuusi desimaalia ja aikavyöhyke ±14:00); anyURI on absoluuttinen IRI literaalina, ei RDF-solmun tunniste. Tyyppejä ei arvata tai merkkijonoja pakoteta numeroiksi.
- JSON API:n liitetyt lukitut JSON Schema/OpenAPI -skeemat tarkistavat syötteen omalla dialektillaan. Muunnos ja SHACL ovat erillisiä tuloksia. VC-muotojen kuoriskeemaa tai JSON-LD-kontekstin laajennusta ei suoriteta; niitä ei merkitä tarkistetuiksi.
- Muodostettu RDF tarkistetaan 2D:n offline SHACL Corella. Vähintään kahden onnistuneen muunnoksen RDF-graafeja verrataan isomorfisesti (blank node -nimet eivät vaikuta). Tämä on rajattu graafien samuus, ei OWL-ekvivalenssi eikä eri aikavyöhyke-/literaaliesitysten yleinen arvoyhtäläisyys.
- Yksi verkoton aliprosessi, CPU 5 s, muisti 512 MiB, seinäkello 15 s; JSON syvyys 20 / 5 000 solmua, RDF 2 000 kolmikkoa per esimerkki, enintään 100 havaintoa. Virhe tai resurssiraja sulkee onnistumisen.
- Käyttöliittymässä sisältökentät, synteettisyyden vahvistus, muunnos, erilliset rakenne-/SHACL-tulokset, RDF-teksti ja graafivertailu. Valmis esimerkkipainike täyttää vain versionhallinnassa olevan neljännen demon tunnetun mappingin; ei muuta palvelun planned-tilaa tai kantaa.
- Vanhat luonnokset ja muuttumattomat julkaisut, fixturet, OIDC, hyväksyntä sekä Private-portti/openBrowser säilyvät. Ei uutta relaatiomigraatiota.

## Todennus ja jatkoraja

Testataan kolme saman sisällön esitystä, eri arvot, sisäkkäisten moniarvoisten olioiden korrelaatio, tyypit/kardinaliteetit, SHACL-koodisto, kadottavat/epäselvät/ylimääräiset kentät, puuttuvat disclosuret/kuoret, rajat, skeemat, käyttöoikeudet, CSRF, vanha If-Match ja tietokannan muuttumattomuus. Ajetaan nykyiset API-/migraatiotestit, web-build ja oikean OIDC-ketjun selaintestit.

Vaiheessa 3 tarvitaan edelleen todellinen lähde-API, muotokohtainen kuoren rakennetarkistus, lukittu W3C-kontekstin käsittely, SD-JWT-profiilin mukainen luotettava purku ja disclosurejen tarkistus, kryptografia, luottamus, valtuudet, myöntäminen ja lompakkotoimitus. Tämän laboratorion tulos ei vahvista näitä. Katalogin metatietovienti säilyy eri palveluna.
