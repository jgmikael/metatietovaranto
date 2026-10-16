# Vaihe 2E: rinnakkaiset toimitustavat ja mapping-kuvaukset

Pohja: main `5611be2`, PR #8:n kautta yhdistetty 2D. Käyttäjän 2E-täsmennys laajentaa aiempaa JSON Schema/OpenAPI -tarkistusten suunnitelmaa. Ensisijainen tavoite on yksi tietotuote, kolme rinnakkaista toimitustapaa ja yhteinen semanttinen perusta. Tämä dokumentti täydentää ja täsmentää aiempia periaatteita.

## Tietomalli ja työnjako

Uusi `distributions` on tyypitetty kokoelma: `jsonApi`, `w3cVc`, `sdJwtVc`. Tuotteen `primaryDistributionId` valitsee ensisijaisen; oletus on W3C VC, kun sellainen on mukana. Tuotteella voi olla myös vain osa vaihtoehdoista tai useita saman tyypin palveluita. Yksi toimitustapa ei korvaa muita eikä yhden palvelun saatavuus tee muista käytettäviä.

Kaikilla on UUID, sisältöformaatti, planned/sandbox/production/suspended-saatavuus, ympäristö, tarjoaja-/operaattori-/lähdevastuuorganisaatiot, profiilisnapshotin viite, versioitu mapping ja erillinen suojausprofiili. Julkaisu lisää `distributionBindings`-tiedot: sama tuoteversio ja sama SHACL-snapshotin UUID/SHA-256 kaikille toimitustavoille sekä kunkin mappingin versio. Asiakas ei aseta julkaisuversiota, profiilitarkistetta tai todettua validointiraporttia.

| Toimitustapa | Sisältöformaatti | Protokolla | Muotokohtainen kuvaus |
| --- | --- | --- | --- |
| JSON API | application/json | HTTPS REST | Palveluosoite, rajapintakuvauksen osoite, saman snapshotin OpenAPI-/JSON Schema -artefaktit, none/oauth2/apiKey/mtls, tarvittavat oikeudet ja ajantasaisuus. |
| W3C VC | application/vc+ld+json | OpenID4VCI 1.0 | VCDM 2.0, VC-tyypit, v2-konteksti ja muut kontekstit, credentialSubject/sovittu sisältöpolku, dataIntegrity/jose-suojausprofiili. |
| SD-JWT VC | application/dc+sd-jwt | OpenID4VCI 1.0 | vct, nimetty profiiliversio, erillinen väitemapping, perClaim/always/never-paljastamiskäytäntö, kenttäkohtainen selective/always ja required/optional/none-haltijasidonta, sdJwt-suojausprofiili. |

SD-JWT VC on itsenäinen tietorakenne: sen sisälle ei vaadita JSON-LD-kontekstia tai W3C VC -kuorta. Mediatyyppi on kuvattu metadatana; demo ei muodosta, jäsennä tai todenna SD-JWT VC -todistuksia eikä väitä toteuttavansa tiettyä interoperabiliteettiprofiilia pelkän mediatyypin perusteella. Profiiliversio on ilmoitettava erikseen.

Todistusjakelut sisältävät myöntäjäorganisaation ja credentialIssuer-tunnisteen, pysyvän HTTPS-aloituslinkin, credential configuration -tunnisteet, voimassaolo- ja statustietoprofiilit, kohdeluokat, edustamisen, tuen, mahdollisen maksun, oikeudellisen luokan ja lompakkonäytöt. Sama OpenID4VCI-palvelu voi tarjota molemmat todistusmuodot eri konfiguraatiotunnisteilla. Samalle issuer-tunnisteelle ei sallita päällekkäisiä konfiguraatioita kuvatuissa toimitustavoissa.

Katalogi kuvaa ja ohjaa; tarjoajan API palauttaa varsinaisen sisällön käyttöoikeuksien mukaisesti. Myöntäjä vastaa tunnistamisesta, asiointivaltuuksista, lähdetiedon hakemisesta, myöntämispäätöksestä, suojauksesta ja lompakkoprotokollasta. Myöntäjä voi käyttää samaa JSON APIa kuin muut valtuutetut asiakkaat tai muuta sovitinta. Kolmea erillistä lähdeintegraatiota ei edellytetä. Katalogin JSON-/JSON-LD-metatietovienti ei ole tämä lähde-API.

## Metadata, mapping ja kolme erillistä validointitasoa

1. Pydantic tarkistaa tyypitetyt tekniset valinnat, tunnisteet, URI:t, ympäristöt, kenttien rakenteen ja muotokohtaiset erot. Token-/salaisuusparametreja ei ole. Linkit ovat pysyviä HTTPS-osoitteita; käyttäjäkohtaiset tarjoukset, QR-koodit, koodit ja tokenit eivät kuulu malliin. Esimerkkidomaineja ei hyväksytä toimivaksi palveluosoitteeksi. planned/suspended ei tarjoa toimintolinkkiä, vaikka osoite olisi kuvattu.
2. `distributionValidation` tarkistaa mapping-ilmoitukset lukittua SHACL-graafia vasten. Tämä ei muunna payloadia RDF:ksi tai jäsennä JWT:tä. 2D:n `semanticValidation` tarkistaa erillisen synteettisen RDF-esimerkin; se säilyy julkaisuehtona. Aiemmin 2E:ssä aloitetut johdannaisten tarkistukset ovat erillisessä `derivedValidation`-raportissa.
3. Todistuksen kryptografinen tarkistus, avainten ja myöntäjän luottamus, haltijasidonnan todentaminen, revokaatio/statuksen käyttö ja lompakkoyhteentoimivuus kuuluvat integraatiovaiheeseen. Formaatti tai onnistunut metadata-/SHACL-tarkistus ei todista QEAA-asemaa tai EUDIW-/EBW-yhteensopivuutta.

`mapping.version` on semver. Jokainen kenttä kertoo juurimuodon alkuperäisen IRI:n, semanttisen ominaisuuspolun IRI-ketjuna, toimitusmuodon kenttäpolun, literaali-/oliorakenteen, tietotyypin tai luokan sekä min/maxCountin. JSON Pointer -mallin `*` tarkoittaa taulukon alkiota: esimerkiksi `/addresses/*/postal_code`, `/credentialSubject/addresses/*/postalCode` tai SD-JWT:n `/addresses/*/postal_code`. Tämä on mallipolku, ei jo myönnetyn yksittäisen todistuksen osoite.

Sisäkkäiset oliot kuvataan sekä vanhempana että lapsina. Palvelin vertaa IRI-ketjua sh:property/sh:path/sh:node- tai yksiselitteiseen sh:class-kohdeluokkaan. Jokaiselle kohdistuvalle kentälle vaaditaan vastaavuus, eikä tuntemattomia termejä, ristiriitaisia tietotyyppejä, kardinaliteetteja, puuttuvia vanhempia tai moniarvoisuuden hukkaavia polkuja hyväksytä. Moniarvoinen kenttä päättyy `/*`-osaan. SD-JWT:n varattuja kuoriväitteitä ei saa korvata sisältömappingilla, eikä aina näkyväksi kuvattua kenttää sijoiteta valikoivasti paljastettavan olion alle.

Mapping ei synny kentän nimestä. Rekursiiviset muodot, usean sisäkkäisen muodon leikkaukset ja monimutkaiset SHACL-polkulausekkeet säilyvät lähdegraafissa mutta saavat tässä mapping-profiilissa arvioimatta-tuloksen ja estävät uuden toimitustapakuvauksen julkaisun. Tämä on näkyvä rajaus, ei rajoitteiden hiljainen ohitus.

Muutos mappingin sisältöön saman toimitustapa-UUID:n seuraavassa julkaisussa vaatii suuremman mapping-version. Mapping-version alentaminen estetään. Raportti, mappingit ja toimitustapakuvaus kuuluvat sisältötarkisteeseen ja erilliseen hyväksyntään. Prosessilla on CPU 5 s, muisti 512 MiB ja seinäkello 15 s; ulkoisia lähteitä ei noudeta tarkistuksessa.

## Erillinen rajattu johdannaistarkistus

SHACL säilyy auktoritatiivisena. JSON Schema/OpenAPI ovat muuttumattomaan snapshotiin kuuluvia teknisiä johdannaisia, joilla on alkuperäinen raakasisältö, SHA-256 ja dialekti. JSON Schema tukee eksplisiittisiä draft 4/6/7/2019-09/2020-12-dialekteja, OpenAPI 3.0.x/3.1.x-versioita. JSON-muotoinen OpenAPI-dokumentti tarkistetaan kokonaisena ja yksi `/components/schemas/{nimi}`-skeema valitaan esimerkin tarkistukseen. YAML ei kuulu tähän tuontiin.

`derivedExamples` sisältää kunkin liitetyn JSON Schema/OpenAPI -artefaktin synteettisen JSON-esimerkin. Esimerkki tarkistetaan alkuperäisellä validatorilla, ei automaattisesti 2020-12:ksi muunnettuna. `semanticMappings` kuvaa johdannaisen suoran JSON-juurikentän, shapeUri:n ja semanticUri:n. Tämä aiemman suunnitelman lisätarkistus vertailee vain suoria kenttiä, tietotyyppiä, kardinaliteettia ja literaalikoodistoa. Se ei ole yllä kuvatun sisäkkäisen `distributions.mapping`-mallin korvike eikä yleinen mallien ekvivalenssitodistus.

JSON Schema -johdannaisen suoran vertailun ulkopuoliset rajoitteet, objektit/koosteet tai puuttuvat vastaavuudet estävät liitetyn johdannaisen hyväksynnän. JSON Schema/OpenAPI -tarkistus ei todista, että JSON- ja RDF-esimerkki ovat saman yksittäisen rekisteritietueen esityksiä. Niiden välinen hallittu sisältömuunnos kuuluu alla olevaan integraatioon.

Viitteet rajataan saman lukitun tiedoston JSON Pointer -viitteisiin. Ulkoisia viitteitä ei noudeta. Dynaamisia/rekursiivisia JSON Schema -viitteitä, sisäkkäisiä $id-resursseja ja fragmenttiankkureita ei tueta tässä rajauksessa. Virheellinen JSON, päällekkäiset avaimet ja NaN/Infinity hylätään. Esimerkin koko on 100 kB, yhteensä 200 kB, korkeintaan yksi esimerkki per artefakti. Näyttö rajataan 100 havaintoon ilman tuloksen muuttamista onnistumiseksi.

## Vanhojen tietojen yhteensopivuus

Ei uutta relaatiomigraatiota: luonnosten ja julkaisuversioiden nykyinen JSONB-sisältö riittää, Alembic head säilyy 0004_publication. Jo julkaistuja 2C/2D-versioita ja snapshotteja ei kirjoiteta uudelleen. Versioluku, tarkiste ja vanha issuance palaavat ennallaan. Käyttöliittymä näyttää vanhan yhden toimituksen kuvauksen, kun distributions puuttuu.

Vanha issuance-kirjoitussopimus säilyy vanhoille luonnoksille/asiakkaille. Uuteen kokoelmaan siirtyminen tehdään luonnoksen normaalissa muokkauksessa. Uuden kokoelman hiljainen pudottaminen vanhaan issuance-malliin estetään. Uusissa kuvauksissa distributions ja primaryDistributionId ovat määrääviä; issuance on yhteensopivuustieto, ei rinnakkainen auktoritatiivinen toimitustapamalli. Sivut ja uudet koneluettavat kentät käyttävät kokoelmaa.

Neljäs synteettinen esimerkkituote lisätään kertaluonteisella `phase-2e-distribution-demo`-merkinnällä vain tunnettuun alkuperäiseen synteettiseen demo-organisaatioon. Alkuperäisen tunnetun tuote-/organisaatio-UUID-parin ja molempien synteettisyys tarkistetaan; nimestä, maasta tai virallisesta organisaatiotunnisteesta ei päätellä oikeuksia. Myös vaiheen 1 kautta migroitunut demo, jolla maa on ZZ ja tunnisteet puuttuvat, saa uuden synteettisen esimerkin. Tunnistekollisiota ei kirjoiteta yli. Muut vanhat kannat jäävät ennalleen. Esimerkki ei julkaise itseään. Kaikki kolme tarjontamuotoa ovat planned ja sama profiili/johdannaiset/mappingit ovat valmiina kokeiltavaksi. Poisto tai muokkaus ei palaudu restartissa. Vain pienet versionhallinnassa olevat luotetut fixturet tarkistetaan alustuksessa suoraan; HTTP-tuonnit käyttävät aina rajattuja prosesseja.

## Integraatiovaiheen hyväksymiskriteerit

- Yksi synteettinen sisältö ja yksi lukittu Tietomallit SHACL -profiili. Sama sisältö haetaan tarjoajan JSON APIsta ja myönnetään W3C VCDM 2.0 JSON-LD VC:nä sekä SD-JWT VC:nä. Yksi lähde-API/sovitin saa palvella molempia myöntämiskonfiguraatioita.
- JSON-sisältö ja kummankin muodon purettu sisältö tarkistetaan niiden omia JSON Schema -kuvauksia vasten. Mapping-version ja profiilitarkisteen perusteella tehdään hallittu muunnos RDF:ksi: sisäkkäiset oliot, IRI:t, tietotyypit, listat ja moniarvoisuus käsitellään eksplisiittisesti. Samoille semanttisille ominaisuuksille saadaan samat arvot ja SHACL-tulos. Puuttuva tai häviöllinen mapping estää yhteensopivuusväitteen.
- W3C VC:n JSON-LD-kontekstit ovat lukittuja. SD-JWT VC:n sisältö puretaan valitun SD-JWT VC -profiilin mukaisesti ja validoidaan sen erillisellä mappingilla ilman pakotettua JSON-LD-kontekstia. SHACL-moottorille ei anneta JWT-merkkijonoa.
- Myöntäjän tunnistautuminen, asiointivaltuudet, configuration-valinta, myöntämispäätös, allekirjoitus/avaimet, haltijasidonta, valikoiva paljastaminen, statustieto ja OpenID4VCI/lompakkotoimitus testataan erikseen nimettyä palvelu-/lompakkoversiota vasten. Credential Offerit ja tokenit pysyvät myöntäjän prosessissa.
- Kryptografinen, rakenteellinen ja semanttinen raportti erotetaan. QEAA- ja EUDIW-/EBW-väitteet edellyttävät erillistä näyttöä. Katalogin metatietovientiä ei esitetä toimivaksi lähdesisällön APIksi.
