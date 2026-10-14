# Suunnitteluperiaate 2 W3C VC ensisijaisena toimitusmuotona

Päiväys 14.10.2026. Käyttäjän toinen perusoletus täydentää `docs/semanttinen-periaate-1.md`:tä. Tämä on suunnittelupäätös, ei vielä toimeksianto tuotannollisen myöntämispalvelun tai lompakkointegraation toteutukselle.

## Lähtökohta

Tietotuotteen ensisijainen toimitusmuoto on W3C Verifiable Credential. Tavoiteltu sisältömalli on W3C VCDM 2.0 ja semanttinen JSON-LD-esitys. Myöntäjä suojaa VC:n nimetyn ja lompakon kanssa yhteensopivan mekanismin avulla. Pelkkä suojaamaton JSON-/JSON-LD-tiedosto ei ole valmis myönnetty todistus.

REST/JSON on vaihtoehtoinen jakelu. SD-JWT VC:tä tai mdocia ei merkitä automaattisesti saman W3C VC:n esityksiksi: muut formaatit edellyttävät erikseen kuvattua adapteria, kartoitusta ja todennusta. EUDIW- ja EBW-tuki kuvataan nimettyä lompakkoprofiilia ja versiota vasten. Niiden tukea ei päätellä pelkästä VC- tai OpenID4VCI-nimestä.

## Työnjako

| Vastuu | Metatietovaranto | Myöntäjäpalvelu ja sen taustapalvelut |
| --- | --- | --- |
| Sisältö | Tietomallit-profiilin versio, OWL-viitteet ja todistusprofiili | Lähdetiedon haku ja muunnos samaan sisältöprofiiliin |
| Löydettävyys | Tuotesivu, koneellinen kuvaus ja pysyvä asiointilinkki | Oikean tuotteen asioinnin vastaanotto |
| Tunnistaminen | Kuvauksen ylläpitäjien kirjautuminen | Hakijan ja todistuksen kohteen tunnistaminen |
| Edustaminen | Vaadittavan valtuuden kuvaus | Yksittäisen pyynnön edustamisoikeuden ja toimivallan tarkistus |
| Myöntämispäätös | Edellytysten kuvaus | Oikeusperustan, kelpoisuuden ja luovutusedellytysten arviointi |
| VC:n muodostus | VC-tyypin, profiilin ja suojausmekanismin kuvaus | Henkilö-/yrityskohtaisen sisällön validointi ja VC:n suojaaminen |
| Toimitus | Lompakkoprofiilit ja palveluosoitteet | Myöntämisprotokolla, haltijasidonta ja toimitus lompakolle |
| Elinkaari | Voimassaolon ja statuksen tarkistusmenettelyn kuvaus | Myönnettyjen todistusten statuksen ylläpito ja uusiminen |

Myöntäjä, tekninen operaattori ja lähderekisteristä vastaava viranomainen voivat olla eri toimijoita. Yksi tuotekuvaus voi johtaa moniin henkilöille tai yrityksille myönnettäviin todistuksiin. Katalogikuvauksen julkaisu ei ole myöntämispäätös tai QEAA-aseman vahvistus. W3C VC -muoto ja oikeudellinen luokka pidetään erillään.

## Käyttäjän polku

1. Käyttäjä löytää tuotteen kuvauksen, myöntäjän, edellytykset ja tuetut lompakkoprofiilit.
2. **Pyydä todistus lompakkoon** avaa myöntäjän pysyvän HTTPS-asiointilinkin valitun tuotteen kohdalla.
3. Myöntäjän palvelussa hakija tunnistetaan ja todistuksen kohde yksilöidään. Yrityksen puolesta toimimisessa tarkistetaan edustamisoikeus.
4. Myöntäjä muodostaa tarvittavan lompakkoprosessin. Se voi näyttää saman laitteen lompakon avaustoiminnon tai QR-koodin toisessa laitteessa olevaan lompakkoon. OpenID4VCI:n Credential Offer voi käynnistää myöntämisprotokollan.
5. Myöntäjä muodostaa ja suojaa todistuksen sekä toimittaa sen vastaanottavalle lompakolle protokollan mukaisesti. Mahdollinen katalogiin palaaminen on käyttöliittymätoiminto, ei luotettava todiste myöntämisen onnistumisesta.

Tunnistamisen ja tarjouksen muodostamisen tarkka järjestys riippuu valitusta virrasta. Tarkistukset on tehtävä ennen myöntämistä; transaktiokohtainen tila kuuluu myöntäjälle. Käyttäjä, todistuksen kohde, lompakon haltija ja yrityksen edustaja voivat olla eri tahoja. Yrityksen taloustodistuksen kohde säilyy yrityksenä, vaikka pyynnön aloittaa sen edustaja.

## Kaksi eri linkkiä

Katalogin `issuanceInitiationUrl` on pysyvä asioinnin aloitusosoite. Esimerkki `https://issuer.example.org/request/tax-debt` on paikallinen asiointisopimus, ei OpenID4VCI:n määrittelemä yleinen URL-rakenne. Mukana voi kulkea julkinen tuote-, profiili- tai konfiguraatiotunniste. Myöntäjä tarkistaa tunnisteen omia sallittuja tuotteitaan vasten.

Credential Offer ja `credential_offer_uri` kuuluvat lompakkoprotokollaan. Käyttäjäkohtaiset tarjoukset ja mahdolliset pre-authorized code -arvot muodostetaan myöntäjän hallitsemassa prosessissa. Katalogiin ei tallenneta näitä koodeja, käyttöoikeustokeneita, henkilötunnuksia, valtuutustodistuksia tai lompakon avaimia. Myöntäjän geneerinen julkinen tarjouslinkki voidaan myöhemmin tukea erillisenä linkkityyppinä. Oletusratkaisu on pysyvä HTTPS-asiointilinkki, josta pääsee myös ohjeisiin ja lompakon valintaan.

Metatietovaranto ei toimi Credential Endpointin välityspalvelimena tai myöntämisistuntojen rekisterinä. Myöntäjä voi hyödyntää katalogin koneellisia kuvauksia ja lukittuja profiiliartefakteja. Katalogin ylläpitäjän nykyinen Keycloak-istunto ei sellaisenaan anna oikeutta henkilö- tai yrityskohtaiseen todistukseen.

## Tuotekuvauksen myöntämistiedot

Tuoteversiolla on yksi tai useampi lompakkojakelu. Jokaisella on todistusprofiili ja myöntämispalvelun viite. Lompakkojakelu on ensisijainen tai näkyvästi suunnitteilla; REST ei hiljaisesti korvaa puuttuvaa VC-jakelua.

| Kenttä | Merkitys |
| --- | --- |
| primaryDelivery | Arvo `w3cVc`; planned-tuki näkyvästi erikseen. |
| issuanceInitiationUrl | Pysyvä myöntäjän asiointilinkki; pakollinen käytettävälle palvelulle. |
| issuerOrganizationId ja operatorOrganizationId | Oikeudellinen myöntäjä ja tekninen operaattori. |
| sourceProviderOrganizationId | Lähdetiedosta vastaava organisaatio. |
| productVersion ja semanticProfileSnapshot | Tuotteen ja Tietomallit-sisältöprofiilin lukitut viitteet. |
| credentialProfile | VC-tyypit, VCDM-versio, konteksti, sisältökartoitus ja suojausmekanismi. |
| credentialIssuer | OpenID4VCI-palvelun HTTPS-tunniste, jos tätä protokollaa käytetään. |
| credentialConfigurationIds | Myöntäjän metadatassa olevat tuetut konfiguraatiot. |
| issuanceProtocol ja protocolVersion | Nimetty protokolla; OpenID4VCI 1.0 on ensisijainen tavoite. |
| walletCompatibility | EUDIW-/EBW-profiili ja versio; planned, declared, tested tai incompatible sekä näyttö ja testipäivä. |
| subjectTypes ja representationRequirements | Kohdeluokat ja edustamisen ehdot. |
| serviceAvailability ja environment | planned, sandbox, production tai suspended; käyttöympäristö erikseen. |
| legalCategory ja qualificationEvidence | Oikeudellinen luokka ja luottamusnäyttö aiemman suunnitelman mukaan. |
| validityPolicy, statusPolicy ja support | Voimassaolo, statuksen tarkistus ja tukiyhteys. |

Kenttänimet ovat katalogin sisäisiä suunnittelunimiä. Standardiadapteri käyttää oikeita protokollanimiä kuten `credential_issuer` ja `credential_configuration_ids`. Standardin issuer-palvelutunniste ja myönnetyn VC:n `issuer` voivat olla erilaisia tunnisteita; niiden yhteys dokumentoidaan ja todennetaan.

Katalogin JSON API tarjoaa samat löydettävyystiedot lompakoille ja ohjelmistoagenteille ilman HTML-sivun kaapimista. Automaattinen hankinta tapahtuu valtuutetun asiakkaan tai lompakon ja myöntäjän välillä. Löydettävyys ei anna pääsyoikeutta.

## Yhteys ensimmäiseen periaatteeseen

Tietomallit-profiili määrittää tietotuotteen semanttisen sisällön. Todistusprofiili kertoo, miten se sijoitetaan VC:n `credentialSubject`-rakenteeseen tai erikseen määriteltyyn sisältöpolkuun, millä kontekstilla JSON-LD tulkitaan ja miten VC suojataan. Myöntäjä validoi sisällön sovittua profiilisnapshotia vasten ja VC-kuoren erikseen. Profiili-IRI ei ole automaattisesti credential configuration id tai todistuksen kohteen tunniste.

Yhteistä sisältöprofiilia voidaan käyttää usean myöntäjän ja todistusprofiilin kanssa. Jokainen tarjottu yhdistelmä yksilöidään jakelun kuvauksessa. Yhteisen tuotemäärittelyn ja viranomaisen tarjonnan tarkka käsitemalli voidaan ratkaista erikseen.

## Käyttöliittymä ja vaiheistus

Tuotesivun ensisijainen toiminto on **Pyydä todistus lompakkoon**. Sen yhteydessä näytetään myöntäjä, mahdollinen maksu, ympäristö ja lompakkoyhteensopivuuden tila. Usean myöntäjän tapauksessa valitaan ensin sopiva palvelu. Planned- tai suspended-palvelulla ei ole toimivaa myöntämispainiketta. Suunnitellun jakelun teksti on **Lompakkotodistus suunnitteilla**. Esimerkkiverkkotunnusta ei esitetä toimivana myöntämispalveluna.

Ensimmäinen toteutusaskel on profiili- ja myöntämispalvelun metatietomalli sekä pysyvä linkki. Katalogiin ei rakenneta omaa lompakkoa tai myöntämisprotokollaa. Vaiheessa 3 voidaan liittää erillinen myöntäjäsimulaattori ja myöhemmin oikea palvelu. Linkin saavutettavuus, palvelun luotettavuus ja lompakkoyhteentoimivuus ovat eri tarkistuksia.

## Hyväksymisehdot tulevalle toteutukselle

1. Tuote kertoo VC-toimituksen ensisijaisuuden, sisältö- ja todistusprofiilin, myöntäjän ja saatavuuden.
2. Painike avaa oikean myöntäjän oikean tuotteen asioinnin; suunniteltua jakelua ei esitetä käytettävänä.
3. Linkki on uudelleenkäytettävä. Katalogi ja sen lokit eivät sisällä henkilökohtaisia myöntämiskoodeja tai tokeneita.
4. Sisällön, profiilin, suojatun todistuksen ja myöntämisprotokollan vastuut voidaan osoittaa erikseen.
5. Yritystapauksessa yritys säilyy kohteena ja myöntäjä tarkistaa pyynnön aloittajan edustamisoikeuden.
6. EUDIW-/EBW-tuki merkitään testatuksi vain nimettyä lompakkoprofiilia vastaan saadun näytön perusteella.
7. Katalogin ylläpitäjäistunto ei ohita myöntäjän tunnistamista tai valtuutuksen tarkistuksia.

## Lähteet

- W3C Verifiable Credentials Data Model 2.0: https://www.w3.org/TR/vc-data-model-2.0/
- OpenID for Verifiable Credential Issuance 1.0, Final 16.9.2025: https://openid.net/specs/openid-4-verifiable-credential-issuance-1_0.html

W3C:n tietomalli ja OpenID4VCI ovat eri kerroksia. Pysyvä asiointilinkki, katalogin työnjako, kenttien pakollisuus ja W3C VC:n ensisijaisuus ovat tämän hankkeen suunnitteluratkaisuja, eivät väite kaikkien lompakoiden automaattisesta tuesta.
