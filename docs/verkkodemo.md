# Kokeile Metatietovarantoa selaimessa

Tämä käynnistää nykyisen demon (vaiheet 1–2G) GitHub Codespacesissa. Paikallisia asennuksia tai uutta hosting-tiliä ei tarvita. GitHub käynnistää sovelluksen, PostgreSQL:n ja Keycloakin omassa kehitysympäristössäsi. Tämä ei ole jatkuvasti käynnissä oleva tuotantopalvelu.

## Ensimmäinen käynnistys

1. Avaa https://codespaces.new/jgmikael/metatietovaranto?ref=main . Kirjaudu GitHubiin samalla tilillä, jolla pääset yksityiseen repositorioon.
2. Tarkista Branch `main` (tai ennen yhdistämistä `feat/phase-2g-lifecycle`), valitse 2-core-kone ja **Create codespace**. Tarkista GitHubin näyttämä käyttö- ja laskutustieto ennen luontia.
3. Odota konttien ensimmäistä rakennusta. Tähän voi kulua useita minuutteja. Sovellus ja tietokanta käynnistyvät automaattisesti; terminaalikomentoja ei tarvita tavallisessa käynnistyksessä.
4. Demo pyritään avaamaan automaattisesti uuteen selainvälilehteen. Jos selain estää avaamisen, avaa editorin alaosan **PORTS**-välilehti. Etsi portti **8000**, jonka nimi on **Avaa Metatietovarannon demo**, ja valitse maapallokuvake **Open in Browser**.
5. Säilytä portin näkyvyys arvossa **Private**. GitHub-kirjautuminen suojaa pääsyn; vaiheessa 2B sovelluksen tuoteylläpito vaatii lisäksi OIDC-kirjautumisen.

Selaimen osoite on GitHubin luoma `https://<codespacen-nimi>-8000.app.github.dev`. Lopullinen osoite syntyy vasta codespacea luotaessa, eikä sitä voi päätellä etukäteen repositorion nimestä. Älä vaihda protokollaa HTTPS:ksi PORTS-asetuksissa: sisäinen sovellus käyttää HTTP:tä ja GitHub huolehtii ulkoisesta HTTPS-yhteydestä.

## Kokeile

Vaiheen 2E tyhjällä kannalla julkinen haku on aluksi tyhjä: kolme vanhaa esimerkkiä ja uusi kolmen toimitustavan synteettinen esimerkki ovat keskeneräisiä yksityisiä luonnoksia. Kirjaudu `vero` / `demo-vero` ja avaa **Omat luonnokset**. [README](../README.md#kokeilupolku) kertoo valmiin kolmen toimitustavan esimerkin, toimitusmuotojen muokkauksen, profiili-/mapping-raportit sekä toisen käyttäjän hyväksynnän ja julkaisun. `yritys` / `demo-yritys` tarkastaa verotuotteen; se ei voi muokata sitä. `lukija` / `demo-lukija` vain lukee oman organisaationsa luonnoksia. Keycloakin Log out -vahvistus tarvitaan käyttäjää vaihdettaessa.

Vanhojen tuotteiden tunnisteet ja sisältö säilyvät. Älä lisää aitoja rekisteri- tai henkilötietoja. Julkaisu tulee hakuun ja vienteihin vasta hyväksynnän jälkeen. Katalogi ei myönnä todistuksia.

## Lopeta ja jatka myöhemmin

Avaa https://github.com/codespaces ja valitse tämän ympäristön kolmen pisteen valikosta **Stop codespace**. Pelkkä selainvälilehden sulkeminen ei välttämättä pysäytä ympäristöä heti. Jatka avaamalla sama codespace uudelleen; avaa portti 8000 uudelleen tarvittaessa. PostgreSQL-volume säilyy samassa codespacessa, mutta codespacen poistaminen tai säilytysajan umpeutuminen poistaa myös sen demotiedot. Ota talteen tärkeät synteettiset kuvaukset JSON-viennillä ennen poistamista.

GitHubin henkilökohtaisiin tileihin sisältyy rajallinen Codespaces-käyttökiintiö. Tarkista jäljellä oleva kiintiö GitHubin laskutusnäkymästä. Pysäytä ympäristö kokeilun jälkeen; myös pysäytetty ympäristö kuluttaa tallennuskiintiötä, kunnes poistat sen.

## Jos käynnistys epäonnistuu

Kopioi **Creation log** -näkymän virhe ja pyydä korjaamaan se. Älä tee portista julkista virheen kiertämiseksi. Sovelluksen terveystarkistus on `/health/ready`. README:n paikallinen Compose-käynnistys on edelleen käytettävissä, mutta sitä ei tarvitse suorittaa omalla koneella tämän verkkodemon vuoksi.

Tämän toimituksen paikallinen tarkistus ei yksin todista, että oman tilisi Codespaces-luonti onnistuu. Ensimmäinen oikea käynnistys vahvistetaan tililläsi, jossa ovat repositorion ja Codespacesin käyttöoikeudet.

## Muutoksen kokeilu ennen yhdistämistä

Luo uusi Codespace [haarasta feat/phase-2g-lifecycle](https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2g-lifecycle). Säilytä portti 8000 Private-tilassa. Käytä yllä olevaa kahden käyttäjän kokeilupolkua. Pysäytä Codespace kokeilun jälkeen. Vanhan Codespacen päivityksessä ota ensin READMEn varmuuskopio ja valitse Rebuild Container; älä poista sen volumea.

Vaiheen 2F [muunnoskokeilu](phase-2f.md) toimii editorin luonnossivulla: synteettinen JSON-sisältö → mappingin RDF → offline SHACL ja graafien vertailu. Kokeilu ei tallenna syötettä tai raporttia eikä käsittele myönnettyjä todistuksia.

Vaiheen 2G [elinkaari](phase-2g.md) kirjataan erillisiksi muuttumattomiksi versiotapahtumiksi. Julkaisijan deprecated/withdrawn-komento, audit ja oma outbox ovat atomisia. Snapshot säilyy; ajantasainen tila on erillinen resurssi. Katalogin withdrawn ei peru ulkoisia käyttöoikeuksia tai myönnettyjä todistuksia.
