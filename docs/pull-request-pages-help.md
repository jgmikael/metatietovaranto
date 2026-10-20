# Pages: käyttöohje näkymäksi ja kenttäkohtaiset ohjeet

Pages-demon käyttäjä saa nyt apua suoraan muokkaamansa kentän vierestä. **Ohje** avaa/sulkee lyhyen selitteen ja **Lue lisää** vie saman käyttöohjeen oikeaan osioon. Navigaation **Käyttöohje** sisältää sisällysluettelon ja pysyvät hash-linkit. Ohjeesta palaaminen säilyttää kentät, kohdistuksen ja vierityskohdan sekä vielä liittämättömän Turtle-tuonnin, mapping-ehdotuksen ja kuittaukset.

## Kattavuus ja ylläpitotapa

- 104 yhteistä kenttä-/käsiteavainta ja 19 pysyvää osiota. Kattavuus: julkinen haku, organisaatiot, tuotteen perustiedot, kolmen toimitustavan yhteiset/muotokohtaiset asetukset, kaikki nykyiset mapping-/lompakkokentät, SHACL-tuonti, generointi, tallennus/tuonti/vienti/palautus ja tulosten tulkinta. Ehdolliset olio- ja lompakkokentät sisältyvät selainkattavuuskokeeseen. Pagesin nykyisiä muokattavia kenttiä ei tunnistettu jääneen ilman selitettä. Palvelinsovelluksen omiin ylläpitolomakkeisiin ei lisätä uutta ohjetoiminnallisuutta tässä PR:ssä.
- Yksi ylläpidettävä sisältö: `docs/pages-kayttoohje.md`. Kenttäselitteet poimitaan sen taulukoista; config määrittää vakaat kytkennät ilman kopioitua proosaa. Markdownin luettelot/taulukot/koodiesimerkit renderöidään käyttöliittymässä. Markdown-versio on ladattavissa.
- Buildissa unified/remark-parse/remark-gfm; selaimessa vain rajattu React-renderöijä ja buildin tuottama rakenne. Ei runtime-ohjehakua, raakaa HTML:ää, kuvien noutoa tai koodin suorittamista. Vaaralliset linkkiprotokollat poistetaan.
- Ohjeet erottavat metatiedot, sisällön ja todistuksen kuoren sekä paikallisen kokeilun, riippumattoman hyväksynnän ja julkaisun. Ei uutta sisältömallia, myöntämistä tai julkaisutoimintoa.
- Ylläpito-ohje: `docs/pages-help-maintenance.md`. Docker-build kopioi kääntäjän tarvitsemat lähdetiedostot; tietokannan rakennetta, käyttöoikeuksia tai tallennusformaattia ei muuteta.

## Todennus

- Ohjekääntäjän `npm run test:help --prefix apps/web`: **3 läpäisi** (otsikko-/kenttäkytkennät, puutteiden/duplikaattien hylkäys, HTML/linkkien turvallisuus ja koodiesimerkin käsittely tekstinä).
- `npm run build --prefix apps/web` sekä `UV_CACHE_DIR=/workspace/.cache/uv bash scripts/build-pages.sh`: **läpäisivät**. Pages-build ajaa myös ohjekääntäjän testit. `node apps/web/scripts/build-help.mjs --check` ja `git diff --check`: läpäisivät.
- `.venv/bin/pytest tests_static -q`: **62 läpäisi** lopullisesta buildista `/metatietovaranto/`-alipolussa. Kuusi uutta ohjekoetta: avaus/sulku/näppäimistö ilman lomakelähetystä, suorat linkit/reload/Markdown-rakenteet/lataukset, ehdollisten kenttien kattavuus, keskeneräinen tiedostotuonti ja muokkaus, mapping/kuittaukset/fokus/vieritys sekä julkisen tuotesivun paluu ja Chromium-kosketustapahtuma kapeassa näkymässä. Kaikki ulkoiset/API-/tunnistuspyynnöt estetty; ei yrityksiä niihin tai JavaScript-/konsolivirheitä. Nykyiset vienti-/palautus-, Worker-parity-, JSON-LD/RDF- ja generointikokeet mukana.
- Palvelinregressiot: **193 läpäisi** (`test_api`, `test_auth`, `test_publication`, `test_public_url`, `test_semantic_validation`, `test_derived_validation`, `test_distributions`, `test_conversion`, `test_lifecycle`, `test_technical_packages`, `test_attribute_semantics`) ja tämän jälkeen **16 läpäisi** (`test_migrations`, `test_profiles`). Yhteensä **209** erilliseen testikantaan; tyhjentäviä testisarjoja ei ajettu rinnakkain samaan kantaan.
- Lopullinen Docker-image rakennettu `DOCKER_CONFIG=/workspace/.cache/docker bash scripts/cloud-build.sh` -komennolla (ympäristön välityspalvelin/CA huomioitu); `DOCKER_CONFIG=/workspace/.cache/docker docker compose up -d --no-build --wait` käynnisti terveen sovelluksen. Kaikkien 13 katalogitaulun sisältöhashit ja Alembic-head verrattu ennen/jälkeen: **muuttumattomat**. PostgreSQL-volumeja ei poistettu. Levytilan loppuminen korjattiin poistamalla käyttämätön Docker-build-välimuisti, minkä jälkeen lopulliset buildit ja testit ajettiin uudelleen.
- `BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`: **13 läpäisi** lopullista imagea vasten, oikea Keycloak-kirjautuminen mukana. Sarjoissa vain nykyisten Starlette/rdflib-riippuvuuksien deprekaatiovaroituksia.
- Erillinen HTTP-yhteensopivuuskoe: **108 vanhaa julkaisuversiota luettavissa**, **8 vanhaa generaattoripakettia** ja **78 artefaktin** alkuperäiset tavut/tarkisteet varmennettu. Hakunäkymä/avoin selite ja ohjeosio tarkastettu lisäksi kuvakaappauksista Chromiumissa.

**Ajamattomat:** NVDA/VoiceOver, fyysinen puhelin, Firefox/Safari, Windows Docker Desktop ja Codespacesin oma käynnistys. Ohjelmallinen saavutettavuus ja kosketus on kokeiltu Chromiumissa; ei väitettä varsinaisen ruudunlukijan käyttäjäkokeesta. GitHub Actionsin / julkisen Pages-deployn tulosta ei ole tässä työssä tarkistettu.

**Yhdistämisen esteet:** paikallisissa automaattisissa tarkistuksissa ei havaittu estettä. Odota tämän PR:n GitHub-tarkistusten läpäisyä ja tee normaali katselmointi. Ei muutosta tietomalliin, oikeuksiin, validointiin tai julkaisuprosessiin. Main on tarkistettu uudelleen eikä siihen tullut muutoksia työn aikana.

## Kokeilu ennen yhdistämistä

```bash
uv sync --locked
npm ci --prefix apps/web
bash scripts/build-pages.sh
uv run --locked python -m scripts.preview_pages
```

Avaa `http://127.0.0.1:4173/metatietovaranto/`. Valitse **Aloita oma kokeilu**, avaa tuote ja muokkaus, täytä kenttä, avaa **Ohje → Lue lisää → Palaa edelliseen näkymään**. Tarkista myös `/metatietovaranto/#ohje/shacl-tuonti` ja sivun uudelleenlataus. Muuta selaimen leveyttä ja kokeile näppäimistöä.

Hyväksytyn main-yhdistämisen jälkeen nykyinen **Public Pages demo** -työnkulku rakentaa ja julkaisee uuden version. PR-haara ei julkaise. Ei uusia Pages-asetuksia tai tietokantamigraatiota. Tätä haaraa ei ole yhdistetty tai julkaistu automaattisesti; tuotannon URL-vastausta ei ole tässä muutoksessa tarkistettu.
