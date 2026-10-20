// Stable IDs are the public #ohje/<id> contract. Keep IDs when renaming a heading.
export const sections=[
 ['alku','Public Pages -demon käyttöohje: Oma kokeilu'],
 ['julkinen-esittely','0. Julkisen esittelyn selaaminen'],['sanasto','Sanasto ja vastuunjako'],
 ['ensikokeilu','1. Ensimmäinen onnistuva kokeilu valmiilla esimerkillä'],['tyonkulku','2. Työnkulku omalle tuotteelle'],
 ['tallennus','3. Aloitusnäkymä, tallennus ja varmuuskopiot'],['organisaatiot','4. Organisaation kaikki täytettävät kentät'],
 ['perustiedot','5. Tuotteen perustietojen kaikki kentät'],['toimitustavat','6. Kolmen toimitustavan yhteiset kentät'],
 ['json-api','7. JSON API -kuvauksen kaikki omat kentät'],['myontaja','8. W3C VC:n ja SD-JWT VC:n yhteiset myöntäjätiedot'],
 ['lompakot','Valinnaiset lompakkoprofiilit'],['w3c-vc','9. W3C VC -kuvauksen omat kentät'],
 ['sd-jwt-vc','10. SD-JWT VC -kuvauksen omat kentät'],['mapping','11. Versioitu kenttämapping: kaikki lisäkentät'],
 ['shacl-tuonti','12. SHACL-tuonnin kaikki kentät ja valinnat'],['generointi','13. Generoinnin kaikki täytettävät kentät'],
 ['tulokset','14. Tuloksen lukeminen ja lataaminen'],['virheet','15. Kun työnkulku pysähtyy'],
];
// Each short explanation is extracted from this row of the Markdown, not copied here.
export const groups={
 search:['julkinen-esittely',['Hakusana','Teema','Tarjoaja','Version elinkaaritila']],
 metadata:['perustiedot',['Tarjoaja','Nimi','Kuvaus','Teema','Synteettinen lähde','Käyttötarkoitus','Rajaukset — mitä tuote ei todista','Käyttöehdot','Sisältöprofiilin snapshot']],
 organization:['organisaatiot',['Organisaation virallinen nimi','Maa','Tunnistejärjestelmä','Organisaatiotunniste']],
 distribution:['toimitustavat',['ensisijainen','saatavuus','ympäristö','tarjoaja','operaattori','lähdevastuu','suojausmekanismi','suojausprofiilin IRI','ES256 / ES384 / EdDSA']],
 api:['json-api',['palveluosoite','rajapintakuvauksen osoite','OpenAPI-artefakti','JSON Schema -artefakti','tunnistautuminen','tarvittavat oikeudet (yksi rivillä)','ajantasaisuus']],
 credential:['myontaja',['myöntäjäorganisaatio','myöntäjäpalvelun HTTPS-tunniste','pysyvä myöntämisen aloituslinkki','credential configuration -tunnisteet (yksi rivillä)','voimassaoloprofiili','tilatietoprofiili','edustamisen ehdot','tuki','maksu','oikeudellinen luokka','oikeudellinen näyttö','kohde person','kohde legalPerson']],
 wallet:['lompakot',['profiili','versio','tila','näyttö','testiaika (ISO 8601)']],
 w3c:['w3c-vc',['VC-tyypit (yksi rivillä)','JSON-LD-kontekstit (yksi rivillä)','sisältöpolku']],
 sd:['sd-jwt-vc',['vct','SD-JWT-profiilin versio','valikoiva paljastaminen','haltijasidonta','aina näkyvät väitteet (yksi kenttäpolku rivillä)']],
 mapping:['mapping',['mappingin versio','juurimuodon IRI','semanttinen IRI-polku','toimitusmuodon kenttäpolku','arvon rakenne','tietotyypin IRI','olion luokan IRI','minCount','maxCount (tyhjä = rajaton)','paljastaminen']],
 source:['shacl-tuonti',['SHACL Turtle -tiedosto','Paikalliset Turtle-riippuvuudet','Lähdeprofiilin tunniste','Lähdeprofiilin versio (jos tiedossa)','Käytä aiemmin tuotua profiilia']],
 generation:['generointi',['Generoinnin juurimuodon IRI','Valitse juurimuoto','Kenttänimi [semanttinen polku]','Mappingin paikallinen versio','Suunniteltu HTTPS-julkaisemisen perusosoite','Synteettinen yhteisen sisällön JSON-esimerkki','Olen tarkastanut yhteiset kenttänimet ja hyväksyn paketin mapping-ehdotukset','Olen tarkastanut toimitustapojen vct-, suojaus-, algoritmi-, haltijasidonta- ja paljastamisvalinnat','Vahvistan JSON-esimerkin synteettiseksi']],
 storage:['tallennus',['Tallennuksen tila','Tuotava kokeilutiedosto','Vie kokeilu JSONina','Palauta alkuperäiset esimerkit']],
 topic:['sanasto',['Metatiedot','Tietosisältö','Todistuksen kuori','IRI','SHACL','API','VC','SD-JWT VC','JSON-LD-konteksti','Type Metadata','Semanttiset annotaatiot','Omistajaorganisaatio','Organisaatioroolit','UUID ja XSD']],
 result:['tulokset',['Paikallinen kokeilupaketti – ei julkaistu','SHA-256 / snapshot / UUID','Alkuperäinen lähtöesimerkki – ei tämän tuotteen validointitulos']],
};
