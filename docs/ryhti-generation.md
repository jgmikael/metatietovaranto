# Ryhti AKR 1.0.5: generoinnin juurimuotokohtainen koe

Vertailu käyttää käyttäjän alkuperäistä exportia ja sen 62 hyväksytyn termikorjauksen raporttia. Alkuperäinen SHA-256 `c41ae51575c63daca16fdbbc07cd619230c4db7be65ee4063b7e76342207ef02`; korjattu SHA-256 `74130d8b542ab11db403b88f393ac704d09334bda3bed93b6de2afe6891034c2`. Molemmat varmennettu. Lähteen ilmoittama versio 1.0.5. Ei riippumatonta alustahakua tai -varmennusta. Aineisto ei kuulu julkiseen demokatalogiin.

Ennen: main 45fb95c, palvelin 1.1.3 / selain 1.0.3. Jälkeen: palvelin 1.2.0 / selain 1.1.0. Molemmissa käytetään samaa korjattua SHACL-graafia. Jälkeen-kokeessa kieliesitys valueLanguage-v1 hyväksytään; viittaus- tai nimivalintoja ei arvata. Tulos on mapping-ehdotus tai este, ei valmiin paketin tai täyden SHACL-validoinnin tulos.

| Juurimuoto | Ennen palvelin/selain | Jälkeen palvelin/selain | Palvelimen ensimmäinen este muutoksen jälkeen |
| --- | --- | --- | --- |
| `AlueidenkaytonRajoituksenAsia` | estetty/estetty | estetty/estetty | DATATYPE_TERM |
| `AlueidenkaytonRajoituksenAsianPaatos` | estetty/estetty | estetty/estetty | DATATYPE_TERM |
| `AlueidenkaytonRajoituksenAsianVaihe` | estetty/estetty | estetty/estetty | DATATYPE_TERM |
| `AlueidenkaytonRajoituksenKohde` | estetty/estetty | estetty/estetty | RECURSION |
| `AlueidenkaytonRajoitus` | estetty/estetty | estetty/estetty | RECURSION |
| `Asiakirja` | estetty/estetty | estetty/estetty | DATATYPE_TERM |
| `Asiasana` | ehdotus/ehdotus | ehdotus/ehdotus | – |
| `Henkilo` | ehdotus/ehdotus | ehdotus/ehdotus | – |
| `Kaava` | ehdotus/ehdotus | ehdotus/ehdotus | – |
| `Kasittelytapahtuma` | estetty/estetty | estetty/estetty | PATH_REQUIRED |
| `Organisaatio` | ehdotus/ehdotus | ehdotus/ehdotus | – |
| `Saadosviite` | ehdotus/ehdotus | ehdotus/ehdotus | – |
| `Sijainti` | estetty/estetty | estetty/estetty | DATATYPE_TERM |
| `Tapahtuma` | ehdotus/ehdotus | ehdotus/ehdotus | – |
| `Toimija` | ehdotus/ehdotus | ehdotus/ehdotus | – |

Seitsemän aiemmin onnistunutta juurta onnistuu edelleen molemmissa toteutuksissa. Muille ei luvata koko mallin generointia. `Asiakirja`: kielityypin aiempi tukiraja poistuu hyväksytyllä esityksellä, mutta seuraava lähteen lainattu rdfs:Literal estää ehdotuksen. `Kasittelytapahtuma`: ylaluokka-rajoitteessa on sh:class ja määrärajoitteet mutta ei sh:path-arvoa. Korjausperustetta ei löydy; luokka tai nimi ei yksilöi puuttuvaa ominaisuutta.

Rekursiivisten luokkien IRI-esitys vaatii erillisen assosiaatiokohtaisen valinnan. Tätä ei valita aineistolle automaattisesti. Tyypitetty kohdesolmu ei riitä, jos siihen kohdistuvat SHACL-muodot vaativat pakollista sisältöä. Tällainen valinta hylätään REFERENCE_UNSUPPORTED-havaintoon. sh:node, tuntemattomat kohderajoitteet ja muut kuin targetClass-kohdistukset jäävät tämän viittausprofiilin ulkopuolelle.

Selain kokoaa esihavaintoja, palvelin palauttaa ensimmäisen eston: siksi ensimmäinen koodi voi erota, vaikka molemmat estävät saman aineiston. Koneelliset kaikki koodit: [jälkeen](ryhti-generation-results.json), [ennen](../fixtures/tietomallit/ryhti-akr-1.0.5/before.json). Alkuperäinen ja raportti löytyvät saman fixturehakemiston erillisistä muuttumattomista tiedostoista.

Erillisillä synteettisillä language.ttl- ja reference.ttl-fixtureillä osoitetaan uudet onnistuneet esitykset. Niitä ei väitetä muokkaamattomaksi Ryhti-exportiksi. Kielikontekstin oikea JSON-LD-prosessointi ja odotettu RDF-graafi sekä viittauksen tyypitetty kohde tarkistetaan offline-SHACLilla.
