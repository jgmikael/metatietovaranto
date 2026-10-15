# Vaiheen 2C ratkaisu ja suunnittelumuutosten vaikutukset

Tämä kuvaa 2C-toimitusta. Vaihe 2D lisää offline SHACL Core -tarkistuksen ja synteettiset esimerkit uusille julkaisuille muuttamatta vanhoja julkaisuja. Ajantasainen rajaus ja päivitysohje ovat READMEssä.

Pohja main `0dd6555`: PR 5 (`8146ed5`, semanttinen periaate 1) ja PR 6 (`0dd6555`, VC-periaate 2) on luettu ennen julkaisumallin toteutusta. Suunnitteludokumenttia ei muuteta jälkikäteen vastaamaan toteutuksen rajauksia. ROADMAP kertoo puuttuvat osat.

## PR 5: sisältömalli ja alkuperä

Tietoelementtien käsin kirjoittaminen lopetetaan uudessa kirjoitus-API:ssa. Vanha luettelo säilytetään legacy-luonnoksessa; sitä ei vahvisteta automaattisesti. SemanticProfile-UUID ja alkuperäinen profileUri yksilöivät mallin, mutta eivät organisaation oikeuksia. Samalla IRI:llä tuodut eri organisaatioiden snapshotit pysyvät itsenäisinä, omistajakohtaisina tietueina. Tuote lukitsee ProfileSnapshot-UUID:n, manifestin SHA-256:n ja alkuperäiset artefaktit; ulkoisen tiedoston muutos ei muuta vanhaa julkaisua.

Tuonti hyväksyy linkin TAI tiedoston. Linkin on osoitettava sallittuun koneluettavaan HTTPS-exportiin. Sallitut hostit ovat tietomallit.suomi.fi ja iri.suomi.fi; redirectit, sisäverkon DNS-tulokset ja HTML torjutaan. Latausta ei tehdä julkaisuhetkellä. Tiedostotuonti hyväksyy alkuperäisen UTF-8-esityksen sisällön; esim. UTF-16-vienti on muunnettava UTF-8:ksi ennen tuontia. Tallennettujen UTF-8-tavujen tarkiste on eri asia kuin RDF-graafin ekvivalenssi.

Turtle/RDFXML/JSON-LD säilyttävät koko alkuperäisen artefaktin. OWL-viitteet voivat sijaita ulkoisessa nimiavaruudessa. SHACL NodeShape, PropertyShape, kohdeluokka, semanttinen property-IRI ja profiili-IRI pysyvät erillisinä. Assosiaatioluokka ja monimutkaisen polun tieto näkyvät johdetuissa elementeissä; täydet rajoitteet, koodistot ja sisäkkäiset muodot säilyvät alkuperäisessä graafissa. Käyttöliittymä ei väitä elementtilistaa täydelliseksi SHACL-esitykseksi.

OWL-importit ja puuttuvat sh:node-viitteet merkitään ratkaisemattomiksi, kunnes riippuvuuden artefakti tuodaan samalla pyynnöllä. Verkkokonteksteja ei seurata JSON-LD:ssä; konteksti annetaan paikallisena. JSON Schema/OpenAPI säilyttää alkuperäisen dialektinsa erillisessä johdannaisartefaktissa; sitä ei muunnettaisi huomaamatta toiseen versioon eikä hyväksytä SHACL:n korvaajaksi. API tukee riippuvuus- ja johdannaislistoja, selainlomake yhden pääartefaktin tuontia.

Profiili tallentuu pending- tai needsAttention-tilaan. Julkaisu vaatii ratkaistut rakenne-/alkuperätiedot, näkyvät tietoelementit ja toisen käyttäjän lähdeilmoituksen tarkastuksen. Julkaisun semanticProfileAssessment tallentaa manualReview-menetelmän, tarkastajan, perustelun ja snapshot-tarkisteen. Sen verified kuvaa käsin tarkastettua ilmoitusta; se ei ole alustan alkuperän automaattinen tai kryptografinen todistus. Itse snapshotin ilmoitus säilyy muuttumattomana. SHACL-instanssivalidointimoottoria ei tässä toimituksessa ole.

Parseri ja RDF-kanonisointi toimivat aliprosessissa: 1 MB/artefakti, 2 MB/pyyntö, 10 000 kolmikkoa, CPU 5 s, muisti 512 MiB ja seinäkello 25 s. DTD/ENTITY ja etäkontekstit torjutaan. Suuria profiileja ei tueta tässä demossa. Alkuperäiset artefaktit ovat organisaatiolle yksityisiä, kunnes niihin viittaa julkaistu versio.

## PR 6: VC-toimitus ilman myöntämispalvelua

Jokaisella tuotteella on yksi ensisijainen w3cVc-jakelukuvaus. Vanhoille tuotteille asetetaan planned; todistuksia tai myöntäjäpalvelua ei keksitä. Tämä on tietomallin ensimmäinen jakelu; useiden myöntäjä-/jakeluvaihtoehtojen UI kuuluu jatkoon.

Issuance sisältää issuer/operator/sourceProvider-organisaatiot, CredentialProfilen (VCDM 2.0, VC-tyypit, kontekstit, sisältöpolku, property-IRI → VC-kenttä -kartoitus, suojausmekanismi), OID4VCI-palvelutunnisteen ja konfiguraatiot, nimetyn protokollaversion, lompakkoprofiilit ja näyttötiedot, kohdeluokat/edustamisen, saatavuuden, ympäristön, oikeudellisen luokan, voimassaolon, statuksen, tuen ja maksun. Julkaisun issuanceBinding lukitsee tuotteen version ja profiilisnapshotin tunnisteen/tarkisteen.

Käytettävä sandbox/production-jakelu tarvitsee välttämättömät metatiedot ja uudelleenkäytettävän HTTPS-asiointilinkin. URL ei saa sisältää tunnuksia, fragmenttia tai henkilökohtaisia query-parametreja; sallitaan vain julkiset product/profile/configuration-arvot. Esimerkkidomaineja ei esitetä toimivina palveluina. Planned/suspended näyttää tilan ilman linkkiä. Käytettävän palvelun painike on **Pyydä todistus lompakkoon**; myöntäjä, ympäristö, maksu ja lompakkotuen tila näytetään samassa yhteydessä. Katalogi ei nouda issuer-metatietoja tai tarjoa Credential Endpointia. URL:n hyväksyntä ei todista palvelun saavutettavuutta tai luottamusta.

Testattu lompakkotuki tarvitsee nimetyn profiilin ja version sekä näytön ja testipäivän. Niiden aitouden arviointi kuuluu tarkastajalle; todellinen yhteentoimivuuskoe jää vaiheeseen 3. QEAA-julkaisu estetään tässä synteettisessä demossa. Keycloak-istunto ei anna oikeutta myöntäjän todistukseen. Luonnoksiin, lokiin tai outboxiin ei kuulu henkilökohtaisia tarjouksia tai tokeneita.

## Työnkulku, pysyvyys ja näkyvyys

Migraatio 0004 ei muuta vanhojen tuotteiden sisältösarakkeita: se lisää pysyvän owner_organization_id:n, luo yksityiset luonnokset ja uudet historian taulut. Provider-nimi säilyy vienneissä; myöhempi tarjoajan vaihto ei vaihda omistajaa. Kirjoitus vaatii omistajan editorin ja tarvittaessa myös uuden tarjoajan editorin.

Tilasiirtymät: draft → inReview → approved → published. Palautus perustelulla vie luonnokseksi. Kaikki nykyiseen luonnokseen kirjoittaneet subjectit kerätään ja estetään sen hyväksynnästä. Uuden julkaistun jälkeisen työkopion kirjoittajat kerätään uudelleen. Hyväksyntä sitoo tarkastajan, revision, sisältötarkisteen ja lähdearvion. Hyväksynnän jälkeinen muutos palauttaa draft-tilaan. Publisher voi tarkastaa ja julkaista, mutta ei muokata ilman editor-roolia.

Kaikki mutaatiot tarkistavat If-Matchin rivilukon alla. Luonnin/julkaisun Idempotency-Key rajataan käyttäjään ja operaatioon 24 tunniksi; sama avain eri sisällölle palauttaa 409. Julkaisu tallentaa muuttumattoman kuvauksen, profiiliviitteen, hyväksyntäviitteen, audit-tapahtuman ja outboxin yhdessä transaktiossa. Versio on käsin valittu kasvava major.minor.patch; semanttisen muutoksen suuruutta ei päätellä automaattisesti.

Julkinen haku, katalogivienti, pysyvät URI:t ja profiiliartefaktit paljastavat vain julkaisuja. Omien organisaatioiden yksityinen luku näyttää työkopiot editor/reader/reviewer/publisher-jäsenyyksille. Muut organisaatiot saavat 404. Tuotteen audit-API kuuluu editor/reviewer/publisher-rooleille; tapahtuma sisältää toimijan, ajan, toiminnon, tarkisteet ja perustelun, ei koko muutosrunkoa. Poistetun tarkastamattoman luonnoksen audit säilyy kannassa; nykyinen tuotekohtainen API ei enää löydä poistettua tuotetta. Laajempi audit-haku jää jatkoon.

Tietokantatriggerit estävät profiilisnapshotin, julkaisun, tarkastuksen, auditin ja outboxin UPDATE/DELETE-operaatiot normaalissa sovelluskäytössä. Tämä ei suojaa tietokannan pääkäyttäjän DDL/TRUNCATE-operaatioilta. Testit käyttävät TRUNCATEa vain erikseen vartioidussa catalog_test-kannassa. Outboxilla ei ole ulkoista kuluttajaa tässä toimituksessa.

## Todennus ja rajat

Testit kattavat muokatun vanhan kannan koko metadatan/UUID:n/aikaleiman säilymisen, tyhjän kannan, toistuvat migraatiot, rinnakkaiset kirjoitukset, hyväksynnän mitätöinnin, oman sisällön hyväksymiskiellon, idempotenssin, tietokantatason muuttumattomuuden ja julkaisun rollbackin. Kolme RDF-esitystä tuottaa saman graafitunnisteen. Selaintesti käyttää kahta oikeaa Keycloak-käyttäjää profiilitiedoston tuonnista julkiseen hakuun.

Laajempi semanttinen validointi, julkaistun withdrawn/deprecated/archived-elinkaari, tuotannon luottamuspalvelut, usean jakelun valinta, ulkoiset issuer/wallet-yhteydet ja palvelun suorituskykytavoitteet jäävät erikseen tilattaviksi. Ajettujen testien tulokset sekä Windows-/Codespaces-/etä-CI-rajoitukset raportoidaan STATUSissa.
