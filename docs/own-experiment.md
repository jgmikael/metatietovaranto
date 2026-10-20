# Oma kokeilu: vain selaimessa

Pagesin **Aloita oma kokeilu** avaa osoitteen `#kokeilu`. Ensimmäinen avaus kopioi julkaisuun sisältyvien neljän synteettisen tuotteen ja organisaatioiden muokattavan metadatan. Myöhemmät avaukset jatkavat tallennettua kokeilua. Julkisen esittelyn aineisto ei muutu. Kirjautumista tai palvelinpalveluja ei tarvita.

Tuotteita ja organisaatioita voi lisätä, muokata ja poistaa. Tarjoajan ja toimitustapojen organisaatioviittausten on säilyttävä: käytössä olevaa organisaatiota ei voi poistaa. JSON API-, W3C VC- ja SD-JWT VC -metatietoja muokataan samoilla komponenteilla kuin varsinaisessa sovelluksessa. Profiilin voi valita mukana toimitetuista lukituista snapshoteista; lähde-SHACLia voi tarkastella ja ladata. Paikallinen Turtle-tuonti ja rajattu tekninen generointi on nyt lisätty: [tarkka käyttö ja rajaus](browser-shacl-generation.md). Täydellistä SHACL-validointia, hyväksyntää tai julkaisua ei tehdä.

**Kaikki paikalliset tuotteet ovat ”Ei validoitu tässä kokeilussa”.** Myös tuotteen saatavuus, oikeudellinen luokka ja lompakkotiedot ovat tarkistamattomia käyttäjän syötteitä. Myöntämis- ja lähdetietotoiminnot ovat pois käytöstä. Alkuperäinen tekninen kuvauspaketti voidaan näyttää erillisenä lähtöesimerkkinä vain täsmälleen samalla tuote-, versio-, paketti- ja tarkisteviitteellä. Sen raportit eivät koske paikallisesti muokattua tuotetta.

## Tallennus ja palautuminen

Muutos käynnistää automaattitallennuksen noin 500 ms:n viiveellä. Näytöllä ovat tilat **Tallennetaan…**, **Tallennettu** tai **Tallennus epäonnistui**. Tallennetuksi merkitään vasta onnistunut kirjoitus ja takaisinluku. Kokeilua ylläpidetään tämän sivuston alkuperässä, selaimessa ja selainprofiilissa, ei käyttäjätilillä tai palvelimella. Yksityinen selaus, selaintietojen poistaminen ja sulkeminen ennen tallennusta voivat hävittää tietoja. Selain voi myös eviktoida tallenteita. Vie tärkeä kokeilu JSON-varmuuskopioksi.

Ainoa kirjoitettava localStorage-avain on `fi.metatietovaranto.pages.own-experiment.v1`. Sen sisäinen kääre on `{storageVersion:1, revision:UUID, data:Workspace}`. Suuret muuttumattomat artefaktit eivät kopioidu tallenteeseen; mukana ovat vain profiili- ja alkuperäisen paketin tunnisteet/tarkisteet. Tallenteessa ei ole istuntoja, tunnuksia, tokeneita, validointiraportteja tai allekirjoitettuja todistuksia.

Web Locks -lukko ja lukon sisällä tehty täsmällisen edellisen tallenteen vertailu estävät kahden välilehden päällekirjoituksen. `storage`-tapahtuma ilmoittaa muutoksesta. Häviävä välilehti säilyttää omat muutoksensa muistissa vietäviksi mutta estää kirjoittamisen. Vie ne ensin ja valitse **Avaa selaimen tallennettu kokeilu**, jos haluat jatkaa toisen välilehden versiosta. Ilman Web Locks -tukea ei käytetä turvatonta tallennusvaramenetelmää: virhe ilmoitetaan ja muistissa olevan kokeilun voi viedä JSONiksi. Käytä ajantasaista selainta ja HTTPS:ää tai localhostia.

Kiintiö- ja käyttöestovirheissä muutokset jäävät muistiin. **Yritä tallennusta uudelleen** ei ohita välilehtiristiriitaa. Virheellistä tai tuntemattoman version tallennetta ei korvata automaattisesti. **Lataa alkuperäinen tallenne talteen** antaa raakatallenteen vian selvittämiseen; se ei ole tuontiformaatti. **Palauta alkuperäiset esimerkit** korvaa vain oman kokeilun erillisen vahvistuksen jälkeen. Muiden sovellusten tallennusavaimia ei poisteta.

Uusi Pages-julkaisu ei nollaa kokeilua. `sourceDemoVersion` säilyy alkuperäisenä. Puuttuva tai muuttuneella tarkisteella löytyvä profiili/paketti näytetään puuttuvana viittauksena; sitä ei korvata lähimmällä uudella esimerkillä. Tuntemattomien formaattiversioiden automaattista migraatiota ei ole: säilytä alkuperäinen tallenne ja käytä erikseen toteutettua muunnosta, jos sellainen myöhemmin tarvitaan.

## Siirtoformaatti 1

**Vie kokeilu JSONina** tuottaa kompaktin UTF-8-JSONin. Vienti ja tuonti käyttävät samaa versiota, eivät palvelimen julkaisuvientiä. Pienin kelvollinen esimerkki:

```json
{"format":"fi.metatietovaranto.own-experiment","schemaVersion":1,"synthetic":true,"sourceDemoVersion":"1.0.0","products":[],"organizations":[],"exportedAt":"2026-10-19T12:00:00.000Z"}
```

Tuotteen rakenne on `{id, metadata, profileReference, originalPackageReference}`. `id` on vakaa UUID. `metadata` sisältää yhteisten tyyppien kuvauskentät, `providerOrganizationId`, `synthetic:true`, `availability`, `profileSnapshotId`, `distributions` ja `primaryDistributionId`. Profiiliviite on `null` tai `{snapshotId,sha256}`. Pakettiviite on `null` tai `{productId,version,packageId,sha256}`. Organisaatio sisältää UUID:n, `legalName`, `country`, `identifiers:[{scheme,value}]` ja `synthetic:true`. Täsmällinen rekursiivinen sallittujen kenttien, toimitustapatyyppien ja enumien tarkistus on [experimentStore.ts](../apps/web/src/experimentStore.ts); yhteiset tietotyypit ovat [types.ts](../apps/web/src/types.ts).

Koko tiedoston enimmäiskoko on **2 MiB**. Työtilan rajassa varataan 512 tavua vientikääreelle. Enintään 100 tuotetta, 50 organisaatiota, 10 toimitustapaa tuotetta kohti ja 200 kenttävastaavuutta mappingia kohti; organisaatiolla enintään 20 tunnistetta. Kuvauskentillä on yhteisen lomakkeen pituusrajat. Keskeneräiset tekstikentät sallitaan, mutta vierasavainten, tunnisteiden ja rakenteen on oltava ehjiä. `sourceDemoVersion` ei saa olla tyhjä. Tuontiajan `exportedAt` on oltava kelvollinen aikaleima.

Tuonti tarkistaa ennen muutoksia koon, JSONin, formaatin/version, sallitut kentät, tyypit, enumit, syntetisyyden, pituudet, UUID:t ja tarkisteiden muodon, yksilölliset tunnisteet, organisaatioviittaukset, ensisijaisen toimitustavan sekä profiiliviittausten keskinäisen yhtäpitävyyden. Tuntemattomat kentät hylätään, myös asiakaspuolen validointi-/hyväksyntäväitteet. Tarkisteviite ei todista paikallisten muutosten oikeellisuutta. Puuttuvaa julkaisuun sisältyvää profiilia/pakettia ei noudeta verkosta.

Tarkistuksen jälkeen näytetään tuotavien tuotteiden ja organisaatioiden lukumäärä. Vasta **Korvaa kokeilu tuodulla aineistolla** ja erillinen vahvistus korvaavat koko kokeilun. Yhdistämistä olemassa oleviin tietueisiin ei tehdä. Epäonnistunut tarkistus, peruutus tai tallennusvirhe jättää aiemman kokeilun muuttumattomaksi. Ehdokas kirjoitetaan onnistuneesti ennen muistissa olevan työtilan vaihtamista.

Tuodut tekstit ovat epäluotettavia: React näyttää ne tekstinä, eikä HTML:ää tai skriptejä suoriteta. Syötettyjä palveluosoitteita ei avata tai noudeta paikallisessa tilassa. Mukana toimitettujen alkuperäisten artefaktien tarkastelu/lataus käyttää vain staattisia julkaisutiedostoja. Käytä vain synteettistä aineistoa; merkintä `synthetic:true` ei tunnista henkilötietoja automaattisesti.

## Build ja julkaisu

Samat Pages-komennot säilyvät, ilman tietokantaa tai tunnistuspalvelua:

```sh
bash scripts/build-pages.sh
.venv/bin/pytest tests_static -q
npm run build --prefix apps/web
```

Windowsin ja paikallisen HTTP-preview'n ohjeet ovat [READMEssä](../README.md). Staattiset selaintestit ajavat oikeassa `/metatietovaranto/`-alipolussa ja kieltävät API-, auth-, identity- ja ulkoiset pyynnöt sekä kaikki kirjoituspyynnöt. Normaali palvelinsovellus säilyttää omat kirjoitus- ja hyväksymisprosessinsa; sen build ei ota kokeilutilaa käyttöön.

PR:n yhdistämisen jälkeen nykyinen **Public Pages demo** -workflow rakentaa, testaa ja julkaisee mainin. Tarkista vihreä deploy ja sen HTTP-varmistus. Vaihtoehtoisesti Actions → Public Pages demo → Run workflow → main. Pages-asetuksia tai maksullisia resursseja ei tarvitse muuttaa, jos nykyinen julkaisu toimii. Uuden paikallistilan julkista käyttöönottoa ei ole tehty tämän PR:n valmistelussa.

## Valinnainen SHACL-generoinnin laajennus

Formaatti 1 hyväksyy nyt myös `localProfiles`-kokoelman sekä tuotteen `generation`-asetukset/paketin. Vanhoja v1-tallenteita ei nollata tai muuteta avauksessa. Tuodut profiilit sisältävät alkuperäiset Turtle-tavut UTF-8-merkkijonoina ja hashit; ne eivät ole toimimattomia File-/blob-viittauksia. Laajennuksen tarkka rakenne ja rajat: [browser-shacl-generation.md](browser-shacl-generation.md). Sama 2 MiB kokonaisraja ja alkuperäisen avaimen reset-/ristiriitasuoja säilyvät.
