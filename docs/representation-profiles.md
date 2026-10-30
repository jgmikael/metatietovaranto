# Rajatut kieli- ja IRI-viittausesitykset

Palvelingeneraattori **1.2.0**, selaingeneraattori **1.1.0**. Uusien pakettien syötteet nimeävät esitysprofiilit `valueLanguage-v1` ja `classOnlyIri-v1`. Jaettu selaincontract johdetaan palvelimen vakioista. Sisältö ja alkuperäiset ominaisuus-/luokka-IRI:t tulevat lukitusta SHACLista; esitysvalinnat eivät vaihda sisältörajoitteita. Palvelimen JSON→RDF-esikatselun muunnosprofiili on nyt `synthetic-json-rdf-v2`. Ei uutta tietokantamigraatiota, OWL-päättelyä tai myöntäjäintegraatiota.

## Kielimerkitty literaali: valueLanguage-v1

`sh:datatype rdf:langString` on yksi semanttinen literaali, jonka JSON-esitys on `{"value":"teksti","language":"fi"}`. Käyttäjä valitsee `languageRepresentation: "valueLanguage-v1"` ennen mapping-ehdotusta ja hyväksyy yhteisen esityksen pakettia muodostettaessa. Puuttuva valinta tuottaa `LANGUAGE_REPRESENTATION_REQUIRED`-havainnon (esityspäätös, ei RDF-termivirhe).

`value` on merkkijono (myös tyhjä merkkijono sallitaan, jos lähde ei sitä estä). `language` on pakollinen. V1 tukee syntaktisesti 2–3 pienaakkosisen ASCII-kirjaimen ensisijaista kieltä sekä valinnaista nelikirjaimista kirjoitusjärjestelmää ja kaksikirjaimista tai kolminumeroista aluetta: `fi`, `sv-fi`, `zh-hant-tw`. Kaikki osat annetaan pienaakkosin; tätä kanonista esitystä ei muuteta huomaamatta. `FI` ja laajemmat BCP47-muodot, kuten laajennukset, variantit, private use tai grandfathered-tunnisteet, ovat tämän profiilin ulkopuolella, eivät yleisesti virheellistä BCP47:ää. Rekisteriin kuulumista ei varmenneta. Oletuskieltä ei arvata. Sama tarkka regex ja JSON Schema jaetaan molemmille toteutuksille. Puuttuva kieli, ylimääräinen avain tai profiilin ulkopuolinen arvo estää esimerkin; kielitietoa ei poisteta.

JSON Schema vaatii täsmälleen value/language-parin. Min/maxCount ja moniarvoisen kentän taulukko koskevat literaaleja, eivät parin kahta osaa. Mappingin `valueKind: literal` ja datatype rdf:langString säilyvät: tästä ei tehdä uutta sisältöoliota tai kahta käsin ylläpidettävää semanttista ominaisuutta. Sisäkkäiset ja moniarvoiset kielikentät käyttävät samoja sääntöjä.

JSON-LD 1.1:n ominaisuuskohtaisessa kontekstissa value on @value-avainsanan ja language @language-avainsanan alias. Moniarvoisuus käyttää aiempaa @set-esitystä. Konteksti tuottaa oikeita kielimerkittyjä RDF-literaaleja, ei blank node -olioita. VCDM-peruskontekstin suojattuja termejä ei määritellä uudelleen. SD-JWT:n JSON-väitesisältö käyttää samaa paria ilman sisäistä JSON-LD-kontekstia. Type Metadata kuvaa tämän semanttisen väitteen polun; x-mtv-semantic/x-term säilyttävät alkuperäisen ominaisuus-IRI:n ja SHACL-käyttöyhteyden. Parin osat eivät saa keksittyjä erillisiä sisältöominaisuuksia. Myöntämisessä pari on looginen kokonaisuus: paljastamispäätös koskee mappingin väitettä, ei erillistä value- ja language-sisältömallia. Osittaisen esityksen käsittely tai kryptografinen SD-JWT-verifiointi ei kuulu tähän toteutukseen.

## Assosiaatio IRI:nä: classOnlyIri-v1

Käyttäjä valitsee assosiaation täydellisen semanttisen polun `references`-listaan. Mapping säilyy olioarvoisena ja saa valinnaisen `representation: iriReference` -kentän. datatype on null, classUri on alkuperäisen sh:class-rajoitteen IRI. Muualla mappingin vanha olioesitys säilyy oletuksena. Nimetty viittausvalinta ei ohita lähteen tarkistusta.

V1 hyväksyy vain:

- yhden NamedNode-muotoisen sh:class-arvon; ei sh:datatype- tai sh:node-rajoitetta;
- puuttuvan nodeKindin tai eksplisiittisen sh:IRI:n;
- paikallisen targetClass-kohdistuksen: kaikki kyseiseen luokkaan kohdistuvat lukitut muodot sallivat pelkän rdf:type-solmun; ominaisuudet ovat valinnaisia ja niiden rajattu rakenne/määrärajoitteet voidaan tarkistaa;
- ei sh:closed-/loogisia/qualified-/hasValue- tai muita tuntemattomia kohderajoitteita eikä targetNode-/targetSubjectsOf-/targetObjectsOf-kohdistuksia tai implisiittisiä SHACL-luokkakohdistuksia aineistossa.

Kohdeluokan rdfs:subClassOf-hierarkia ja kohdemuodon rdf:type-ominaisuusrajoitteet estetään v1:ssä erikseen: tyypitetty solmu voi aktivoida ylaluokan kohdistuksen tai tyyppiarvon rajoitteen myös silloin, kun ominaisuudella ei ole minCountia. Näitä ei käsitellä valinnaisena puuttuvana sisältönä.

Pakollinen kohdeominaisuus, epäselvä polku/rajoite, sh:node tai laajempi kohdemuoto tuottaa `REFERENCE_UNSUPPORTED`-eston. Ei kohdesisällön katoamista, syklin hiljaista katkaisua tai mielivaltaista etähakua. Tämä on konservatiivinen riittävyyskoe paikalliselle rajatulle profiilille, ei koko SHACLin/OWLin päättelyä.

JSON-arvo on absoluuttinen **instanssi-IRI**. Kohteen luokka-IRI ei kelpaa sen arvoksi. Molemmilla toteutuksilla on yhteinen 2 000 sisältökolmikon resurssiraja myös kohteiden rdf:type-lauseet laskien. JSON Schema tarkistaa IRI:n rajatun leksikaalin ja moniarvoisuuden; muunnos tarkistaa lisäksi eron kohdeluokkaan. Viittauksia ei arvata esimerkistä tai ominaisuusnimestä. Sama viite kahdessa roolissa voi osoittaa samaan kohteeseen, mutta saman kentän toistuvat identtiset viitteet estetään RDF-arvohäviön välttämiseksi.

JSON-LD:n ominaisuus saa @type: @id. Generaattori lisää synteettiseen validointigraafiin jokaiselle viitatulle instanssi-IRI:lle lähteen määräämän rdf:type-luokan. Tämä ei varmista ulkoisen kohteen todellista olemassaoloa tai tyyppiä. Kohdetietoja ei noudeta. Root ja sisäkkäiset sisältöoliot säilyvät anonyymeinä kuten aiemmin; viitearvo ei anna niille arvaamalla identiteettiä. Viitteellisessä VC-rakenne-esimerkissä credentialSubject on juuren ja tyypitettyjen kohdesolmujen joukko; JSON-LD-esimerkkigraafi käyttää vastaavaa @graph-esitystä. JSON- ja SD-JWT-sisältöesimerkki sisältää vain varsinaisen sisältöolion, jossa viitteet ovat IRI-merkkijonoja.

Palvelin vertaa oikean JSON-LD-prosessorin RDF-graafia mapping-muunnoksen graafiin ja ajaa lisäksi lähde-SHACLin offline. Selaimen esimerkkipaketti ilmoittaa yhä täydellisen SHACL-validoinnin ja riippumattoman graafivertailun suorittamattomiksi; niiden riippumaton koe ajetaan testeissä. Pakollista kohdesisältöä ei hyväksytä pelkkänä viittauksena kummassakaan toteutuksessa.

## Lähteen epäselvyydet ja työnkulku

Lainattu rdfs:Literal tuottaa edelleen DATATYPE_TERM-havainnon ja lisäselitteen: termimuodon lisäksi konkreettinen sisältötyyppi puuttuu. IRI:nä annettu rdfs:Literal tuottaa DATATYPE_REPRESENTATION_REQUIRED-havainnon. Kumpikaan ei saa string-oletusta. Konkreettinen rajoite täsmennetään lähde-SHACLissa uutena aineistona. Paikallinen tuontikorjaussääntö 1.0.0 ei laajene tämän vuoksi.

Puuttuva sh:path tuottaa PATH_REQUIRED-lähdehavainnon: luokkamuoto, PropertyShape, lähdetiedosto ja sh:path-predikaatti yksilöidään, polku merkitään puuttuvaksi. Ryhti-AKR:n ylaluokka-rajoitteen sh:class ja nimi eivät yksilöi puuttuvaa ominaisuutta; sille ei muodosteta automaattista polkukorjausta.

Esitysvalinnat ovat muokattavissa ennen onnistunutta ehdotusta molemmissa käyttöliittymissä. Myös tarkastetut tekniset nimet voi syöttää ennen ehdotusta. Valinta ei muuta datatypea, luokkaa tai kardinaliteettia. Luonnoksen uusi paketti kulkee aiemman editor → riippumaton tarkastus → publisher -prosessin kautta; onnistunut uudelleengenerointi mitätöi hyväksynnän. Epäonnistunut generointi ei korvaa tallennettua luonnosta. Julkaistut vanhat paketit ja profiilisnapshotit säilyvät.

Paikalliset valinnat kuuluvat kokeilun v1-siirtoon ja paketin sidontaan; muutokset vanhentavat paketin ja tyhjentävät paikalliset hyväksynnät. Vanhat korjausraportit toistetaan entisellä v1-säännöllä. Raportin historiallista rdf:langString-tukitekstiä ei kirjoiteta uudelleen; käyttöliittymä selittää nykyisen hyväksyttävän kieliesityksen erikseen. Alkuperäiset tavut ja korjausketju säilyvät.

[Todellisen Ryhti-aineiston 15 juurimuodon ennen/jälkeen-raportti](ryhti-generation.md). Onnistuneet kieli-/viittausesimerkit ovat erillisiä synteettisiä fixtures/representations-aineistoja. Ulkoiselle tarjoajalle/myöntäjälle jäävät lähdesisältö, tunnistaminen, valtuudet, myöntämispäätös, allekirjoitus ja lompakkotoimitus. Paketti ei ole myönnetty tai kryptografisesti tarkistettu todistus.

## Toistettavat onnistuneet esimerkit

Riippuvuuksien asennuksen (`uv sync --locked`) jälkeen molemmat synteettiset paketit voi muodostaa ilman tietokantaa tai tunnistuspalvelua:

```bash
uv run --locked python -m scripts.representation_examples --output /tmp/representation-examples
```

`language/` sisältää suomen- ja ruotsinkieliset labels-arvot sekä sisäkkäisen englanninkielisen notes-arvon. `reference/` sisältää parent-assosiaation instanssiin `https://synthetic.example/entities/parent`, jonka luokka on erillinen `https://example.org/representation/Entity`. Molemmat lähteet ja JSON-sisällöt ovat fixtures/representations-hakemistossa. Generaattori tarkistaa kontekstin oikealla paikallisella JSON-LD-prosessorilla ja vertaa RDF-graafeja sekä validoi esimerkin lähde-SHACLilla. Komento tulostaa tarkistusten tulokset ja kirjoittaa valmiit artefaktit. Perusosoite `https://planned.example.org` on suunniteltu esimerkkiosoite, ei julkaisu. Yhtään tiedostoa ei lähetetä verkkoon.

Samojen syötteiden uusinta-ajo tuottaa samat artefaktit ja packageId:t. Komento ei tallenna luonnosta, anna riippumatonta hyväksyntää tai julkaise pakettia.
