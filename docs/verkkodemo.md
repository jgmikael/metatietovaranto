# Kokeile Metatietovarantoa selaimessa

Tämä käynnistää nykyisen vaiheen 1 demon GitHub Codespacesissa. Paikallisia asennuksia tai uutta hosting-tiliä ei tarvita. GitHub käynnistää sovelluksen ja PostgreSQL:n omassa kehitysympäristössäsi. Tämä ei ole jatkuvasti käynnissä oleva tuotantopalvelu.

## Ensimmäinen käynnistys

1. Avaa https://codespaces.new/jgmikael/metatietovaranto?ref=demo%2Fcodespaces . Kirjaudu GitHubiin samalla tilillä, jolla pääset yksityiseen repositorioon.
2. Tarkista Branch `demo/codespaces`, valitse 2-core-kone ja **Create codespace**. Tarkista GitHubin näyttämä käyttö- ja laskutustieto ennen luontia.
3. Odota konttien ensimmäistä rakennusta. Tähän voi kulua useita minuutteja. Sovellus ja tietokanta käynnistyvät automaattisesti; terminaalikomentoja ei tarvita tavallisessa käynnistyksessä.
4. Demo pyritään avaamaan automaattisesti uuteen selainvälilehteen. Jos selain estää avaamisen, avaa editorin alaosan **PORTS**-välilehti. Etsi portti **8000**, jonka nimi on **Avaa Metatietovarannon demo**, ja valitse maapallokuvake **Open in Browser**.
5. Säilytä portin näkyvyys arvossa **Private**. GitHub-kirjautuminen suojaa pääsyn; sovelluksen oma kirjautuminen kuuluu myöhempään vaiheeseen.

Selaimen osoite on GitHubin luoma `https://<codespacen-nimi>-8000.app.github.dev`. Lopullinen osoite syntyy vasta codespacea luotaessa, eikä sitä voi päätellä etukäteen repositorion nimestä. Älä vaihda protokollaa HTTPS:ksi PORTS-asetuksissa: sisäinen sovellus käyttää HTTP:tä ja GitHub huolehtii ulkoisesta HTTPS-yhteydestä.

## Kokeile

- Hae `verovelka` ja avaa löytynyt tuote.
- Tutustu kuvaukseen ja tietoelementteihin; avaa JSON- ja JSON-LD-viennit.
- Lisää oma synteettinen tietotuote, muokkaa sitä ja lataa sivu uudelleen.
- Poista oma testituotteesi tarvittaessa. Kaikki tähän demoon pääsevät voivat muuttaa sen tietoja, joten pidä portti yksityisenä.

Kolme alkuperäistä esimerkkiä ovat verovelkatieto, yrityksen perustiedot ja ammattipätevyys. Älä lisää aitoja rekisteritietoja tai henkilötietoja.

## Lopeta ja jatka myöhemmin

Avaa https://github.com/codespaces ja valitse tämän ympäristön kolmen pisteen valikosta **Stop codespace**. Pelkkä selainvälilehden sulkeminen ei välttämättä pysäytä ympäristöä heti. Jatka avaamalla sama codespace uudelleen; avaa portti 8000 uudelleen tarvittaessa. PostgreSQL-volume säilyy samassa codespacessa, mutta codespacen poistaminen tai säilytysajan umpeutuminen poistaa myös sen demotiedot. Ota talteen tärkeät synteettiset kuvaukset JSON-viennillä ennen poistamista.

GitHubin henkilökohtaisiin tileihin sisältyy rajallinen Codespaces-käyttökiintiö. Tarkista jäljellä oleva kiintiö GitHubin laskutusnäkymästä. Pysäytä ympäristö kokeilun jälkeen; myös pysäytetty ympäristö kuluttaa tallennuskiintiötä, kunnes poistat sen.

## Jos käynnistys epäonnistuu

Kopioi **Creation log** -näkymän virhe ja pyydä korjaamaan se. Älä tee portista julkista virheen kiertämiseksi. Sovelluksen terveystarkistus on `/health/ready`. README:n paikallinen Compose-käynnistys on edelleen käytettävissä, mutta sitä ei tarvitse suorittaa omalla koneella tämän verkkodemon vuoksi.

Tämän toimituksen paikallinen tarkistus ei yksin todista, että oman tilisi Codespaces-luonti onnistuu. Ensimmäinen oikea käynnistys vahvistetaan tililläsi, jossa ovat repositorion ja Codespacesin käyttöoikeudet.
