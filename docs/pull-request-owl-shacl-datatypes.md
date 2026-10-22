# Erota OWL-arvoalue, SHACL-tietotyyppi ja RDF-termin tyyppi

`sh:datatype`-virheen korjausesimerkki näytti aina boolean-tyypin. Nyt se käyttää havaitun URI-merkkijonon tarkoittamaa tyyppiä. Raportti erottaa lähteen RDF-termivirheen, tukemattoman tietotyypin, avoimen literaaliesityksen sekä eksplisiittiseen paikalliseen OWL-määritykseen perustuvan ristiriidan. Selain- ja palvelinnäkymä käyttävät samaa havaintokomponenttia.

## Tutkimustulos ja ennen/jälkeen

**Nordic Signatory Rights.ttl ei ollut käytettävissä. Alkuperäisen nsig/signatoryRights-tapauksen kuuden DATATYPE_TERM-havainnon juurisyytä ei ole varmennettu.** Koodista ei löytynyt OWL-/SHACL-IRI:en yhtäsuuruusvaatimusta. Synteettisessä kokeessa lainattu URI on Literal/xsd:string jo N3-parserin tuloksessa. Kelvollinen IRI pysyy NamedNodena Worker-, lähteen tallennus-, uudelleenlataus- ja kokeilun JSON-vienti/palautusketjussa. Tarkastusnäkymän DTO:ta ei käytetä generoinnin RDF-lähteenä.

| Lähde | Ennen | Jälkeen |
| --- | --- | --- |
| `sh:datatype "http://www.w3.org/2001/XMLSchema#date"` | DATATYPE_TERM, harhaanjohtava boolean-esimerkki | DATATYPE_TERM, havaittu Literal ja sen oma xsd:string erillään tarkoitetusta date-URI:sta; esimerkki `sh:datatype <http://www.w3.org/2001/XMLSchema#date> .` |
| OWL `rdfs:range rdfs:Literal` + SHACL `sh:datatype xsd:date` | Ei löytynyt yhtäsuuruuteen perustuvaa estoa | Sallittu tarkennus, yksilöity OWL_RANGE_REFINEMENT-huomio; mapping ja konteksti säilyttävät xsd:date-tyypin |
| `sh:datatype rdfs:Literal` / avoin `sh:nodeKind sh:Literal` | Yleinen tukemattoman tyypin/rajoitteen havainto | DATATYPE_REPRESENTATION_REQUIRED; ei string-oletusta |
| `sh:datatype rdf:langString` IRI:nä | Tukematon tietotyyppi | DATATYPE_UNSUPPORTED/tukirajoite, ei DATATYPE_TERM; alkuperäinen kielitieto säilyy lähteessä |

Korjausesimerkki korjaa vain termimuodon, ei lupaa kyseisen tietotyypin generointitukea. URI-literaaleja ei pakoteta IRI:iksi, lähteitä tai vanhoja julkaisuja ei muuteta.

## Rajattu yhteensopivuuskäytäntö

Yhteinen `locked-explicit-disjoint-v1` sallii saman tietotyypin ja rdfs:Literal-tarkennuksen. Estävä OWL_SHACL_CONFLICT vaatii lukitusta paikallisesta aineistosta eksplisiittisen `owl:disjointWith`-määrityksen tietotyypin ja arvoalueen välille (kumpi tahansa suunta); tämä tarkistetaan ennen sallittua tarkennusta. Muut arvoalueet ovat OWL_RANGE_UNASSESSED-huomioita. Ei XSD-/OWL-hierarkiapäättelyä, olioarvoalueiden yleistä arviointia tai väitettä koko OWL-mallin ristiriidattomuudesta. Eri IRI ei yksin todista ristiriitaa. Verkkoa ei käytetä riippuvuuksien ratkaisemiseen.

Generaattoriversiot palvelin 1.1.3 / selain 1.0.2; contract päivitetty. Konkreettista literaalityyppiä täydentävä sh:nodeKind sh:Literal on tuettu; muut nodeKind-rakenteet rajataan ulos. Date/dateTime-arvon sisältävä selain-esimerkki on edelleen BROWSER_EXAMPLE_LEXICAL-tukirajoite: date-kentän mapping/konteksti/skeema voidaan muodostaa, testissä vapaaehtoinen date-arvo jätetään esimerkistä pois. Ei rdf:langString-generaattorin laajennusta, allekirjoitusta, myöntämistä tai lompakkointegraatiota.

## Tarkistukset

- **119/119 staattista testiä**, joista 20 uutta (Chromium + todellinen Worker, ei API-/auth-/ulkoisia verkkopyyntöjä eikä JS-virheitä). Tuonti, RDF-termit, tallennus/uudelleenavaaminen, JSON-vienti/palautus, lähdetavut/hashit, luokitellut diagnostiikat, nimettömän PropertyShapen ja erillisen OWL-riippuvuuden provenanssi, arvoaluetarkennukset ja ristiriidat.
- Generoitujen artefaktien determinismi ja hashit; selain-/palvelinmappingin, kontekstin ja skeeman vastaavuus. Todellinen PyLD + lukittu lataaja: RDF-graafi vastaa odotettua graafia. Samasta synteettisestä profiilista muodostettu palvelinpaketti läpäisee offline-SHACLin. Selain ei väitä ajaneensa täydellistä SHACL-validointia.
- **209/209 API-/profiili-/tietokanta-/migraatiotestiä**, catalog_test-kannassa. Mukana vanha/tyhjä kanta ja migraatioiden toisto, oikeudet, hyväksymisprosessi ja julkaisujen muuttumattomuus. Viimeinen nodeKind-termityypin tarkennus testattu lopullisen staattisen ajon molempien toteutusten regressiossa.
- Tavallinen web-build, Pages-build, ohjekääntäjän 3 testiä, jaetun contractin drift-tarkistus, ohjeartefaktien ajantasaisuus ja git diff --check läpäisivät.
- Lopullinen Docker-build ja Compose-käynnistys läpäisivät; tietokannan 13 taulun sisältöhashit ja Alembic-head säilyivät. Kaksi väliaikaista uusintabuildia epäonnistui ENOSPC-levytilaan; siivouksen jälkeen build onnistui. Ei volume-operaatioita.
- HTTP-yhteensopivuuskoe: 129 julkaisuversiota luettavissa; 11 tallennetun paketin 114 artefaktin sisältö/hashit vastaavat tietokantaan tallennettuja alkuperäisiä tavuja.
- **13/13 palvelinselaintestiä lopullista Docker-imagea vasten**: oikea Keycloak-kirjautuminen, tallennus/uudelleenavaaminen, organisaatiorajat, riippumaton hyväksyntä, julkaisu, julkiset artefaktit ja elinkaari.

**Testaamatta:** alkuperäinen Nordic-tiedosto, Firefox/Safari, Windows Docker Desktop, Codespacesin oma käynnistys, fyysinen puhelin/ruudunlukija ja julkinen deploy. Riippuvuusvaroitukset ovat nykyisten rdflib/Starlette-versioiden deprekaatioita.

**Yhdistämisen arvio:** alkuperäisen Nordic-tapauksen toimivuutta ei ole vahvistettu. Rajatun korjauksen automaattisten tarkistusten tulokset yllä; ei tunnettuja tietokanta-/oikeusmuutoksia. Nykyiset generaattorin tukirajoitteet säilyvät. STATUS sisältää tarkat komennot ja tulokset.

Ei migraatiota, oikeusmuutosta, hyväksynnän ohituspolkua tai vanhojen snapshotien uudelleenkirjoitusta. Alkuperäisen Nordic-tapauksen hyväksyntää ei voi tämän PR:n perusteella luvata. Soveltuvuus siihen edellyttää alkuperäisen tiedoston erillistä tarkastusta. PR:ää ei yhdistetä automaattisesti eikä PR-haaraa julkaista Pagesiin.

## Kokeile ennen yhdistämistä

Checkout `fix/owl-shacl-datatypes`, aja `bash scripts/build-pages.sh` ja `uv run --locked python -m scripts.preview_pages --port 4173`. Avaa `http://127.0.0.1:4173/metatietovaranto/#kokeilu`, avaa yksi oma tuote ja tuo `fixtures/browser-generation/literal-refinements.ttl`. Anna lähdeprofiilin tunnisteeksi `urn:synthetic:refinements`, liitä profiili ja valitse juureksi `https://example.org/literal-refinements/Root`. Tuen tarkistus näyttää kolme sallittua OWL-tarkennusta. Virhekoetta varten tee erillinen kopio ja lainaa vain sh:datatype-kohdan date-URI; tarkistus näyttää DATATYPE_TERM-havainnon sekä date-korjausesimerkin. Tämä ei muokkaa alkuperäisiä projektifixtureitä eikä julkaise käyttäjän tiedostoja.

Yhdistämisen jälkeen nykyinen mainin Pages Actions -työnkulku julkaisee muutoksen. Varmista sen build-, testi- ja deploy-tulos ennen julkisen demon uusintakokeilua. Tässä tehtävässä ei ole deployattu julkista sivustoa.
