# Pages-ohjeen ylläpito

Ohje koskee julkista Pages-esittelyä ja selaimen Oma kokeilu -tilaa. Palvelinsovelluksen lomakkeet käyttävät edelleen omia nykyisiä toimintojaan; niihin ei tässä muutoksessa lisätä Pages-ohjeita.

## Yksi sisältölähde

`docs/pages-kayttoohje.md` on sekä luettava/ladataan Markdown-ohje että käyttöliittymässä näytettävä koko ohje. Sen kenttätaulukoiden toisesta sarakkeesta poimitaan lyhyt selite ja mahdollisesta kolmannesta sarakkeesta esimerkki/toimintaohje. Älä kopioi selityksiä Reactiin.

`apps/web/help/config.mjs` yhdistää otsikoiden nimet pysyviin osiotunnisteisiin ja taulukoiden rivit kenttäavaimiin. Osiotunnisteet ovat julkisten hash-linkkien sopimus: esimerkiksi `/metatietovaranto/#ohje/shacl-tuonti`. Säilytä tunniste otsikon tekstiä muuttaessasi ja päivitä sen otsikkokytkentä. Älä muuta tietotuotteiden alkuperäisiä IRI:jä ohjelinkeiksi.

`npm run build:help --prefix apps/web` jäsentää Markdownin buildissa unified/remark-parse/remark-gfm-kirjastoilla. Generoitu `apps/web/src/help/generated/help.json` on gitignorettu; tavallinen ja Pages-build muodostavat sen automaattisesti. Dockerin web-build kopioi tarvitsemansa Markdownin, raportin ja synteettisen Turtle-esimerkin build-kontekstiin. Ohje ei edellytä käynnissä olevaa APIa tai ulkoista hakua. Markdown, esimerkkitiedosto ja raportti sisältyvät Viten staattisiin resursseihin. Muut teknisten dokumenttien linkit ovat erikseen avattavia GitHub-lähdelinkkejä.

Jäsennin hyväksyy rajatun Markdown-solmujoukon, poistaa raakaa HTML:ää ja kuvat sekä estää muun kuin HTTP(S)-protokollan linkit. React renderöi vain tämän rakenteen tekstinä/elementteinä; ei `innerHTML`:ää, raakaa HTML:ää tai koodin suorittamista. Fenced-koodi näkyy tekstinä. Selitteissä käytetään samaa sisältöä tiiviinä tekstinä; koko ohje säilyttää taulukot, listat ja muotoilun.

## Uuden kentän lisääminen

1. Lisää tai päivitä käyttäjän tehtävää vastaavan osion kenttätaulukon rivi. Kerro mitä annetaan, milloin se tarvitaan, mistä tieto saadaan ja synteettinen esimerkki. Älä esitä paikallista tietoa julkaistuna tai riippumattomasti validoituna.
2. Kytke rivi configin ryhmään. Avain on `ryhmä.kentän nimi`. Selitysteksti pysyy Markdownissa.
3. Käytä `HelpLabel`-komponenttia. Sisäkkäinen input/textarea/select saa automaattisesti oman tunnisteen ja `aria-describedby`-viittauksen. Erilliselle `htmlFor`-labelille lisää vastaava `helpFieldAttributes(id, avain)` itse kontrolliin. Samannimisissä hakukentissä käytä eksplisiittistä `helpKey="search.Teema"`-avainta.
4. Dynaamisten toimitustapa-, mapping- ja lompakkokenttien resolveri on `src/help/Help.tsx`: kentän numerot eivät kuulu sisältöavaimeen. Uusi nimeämismuoto vaatii resolverin ja kattavuustestin päivityksen. Read-only-käsitteelle tai toiminnolle voi käyttää `TopicHelp`-komponenttia.
5. Laajenna `tests_static/test_help.py`:n kattavuuskierrosta, jos uusi ehdollinen kenttä vaatii uuden näkymän, valinnan tai painikkeen. Testi tarkistaa myös kentän labelin, yksikäsitteisen kuvausviittauksen ja puuttuvan selitteen. Pagesissa tuntematon kenttä merkitään `data-help-missing`-attribuutilla, jolloin kattavuustesti epäonnistuu.

Build hylkää puuttuvan/duplikaatin otsikon sekä puuttuvan tai duplikaatin rekisteriin kytketyn kenttärivin. Lomakkeen puuttuva kytkentä havaitaan selainkattavuustestissä. `node apps/web/scripts/build-help.mjs --check` havaitsee vanhentuneen generoidun tiedoston.

## Ohjenavigaatio ja tila

`HelpProvider` säilyttää ennen ohjeeseen siirtymistä reitin, aktiivisen elementin ja vierityskohdan. `PagesViews` piilottaa nykyisen näkymän ohjevierailun ajaksi sen purkamisen sijaan. Näin myös valittu, vielä liittämätön Turtle-aineisto, mapping-ehdotus ja kuittaukset säilyvät. Julkisen sovelluksen reititin sivuuttaa ohje- ja kokeilureitit. Paluu ja selaimen Takaisin palauttavat kohdistuksen ja vierityksen. Suoran ohjelinkin avaaminen tai koko sivun lataaminen aloittaa uuden muistinvaraisen navigaatioistunnon; tallennettua kokeilua ei nollata. Tallentamaton tuontivalinta ei säily koko sivun uudelleenlatauksessa.

Ohjepainike on natiivi `type="button"` ja ilmoittaa `aria-expanded`/`aria-controls`-tilan. Kuvauspaneeli on suljettuna piilotettu, mutta kenttään sidottu `aria-describedby` säilyy. Linkin kohdeotsikko saa kohdistuksen ohjeessa. Natiivit painikkeet tukevat Enteriä, välilyöntiä ja kosketusta; apu ei perustu hoveriin.

## Tarkistukset

```bash
npm run test:help --prefix apps/web
bash scripts/build-pages.sh
.venv/bin/pytest tests_static -q
npm run build --prefix apps/web
BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q
```

Build-pages suorittaa myös ohjekääntäjän yksikkötestit. Staattiset testit toimivat aidolla HTTP-palvelimella `/metatietovaranto/`-alipolussa ja estävät ulkoiset sekä API-/tunnistuspyynnöt. Lisäksi tarkistetaan kosketustapahtuma ja kapea näkymä Chromiumissa. Nämä ohjelmalliset saavutettavuustarkistukset eivät korvaa oikealla ruudunlukijalla tehtävää käyttäjäkoetta.
