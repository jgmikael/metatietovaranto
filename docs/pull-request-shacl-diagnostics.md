# SHACL-määrärajoitteet ja lähdeprofiilin diagnostiikka

Tietomallit-exportin `"0"^^xsd:int` ja `"1"^^xsd:int` pysäyttivät selaimen harhaanjohtavaan CARDINALITY-ilmoitukseen. Nyt määrärajoitteiden lukija hyväksyy tuetun XSD-kokonaislukuperheen ja kertoo erikseen RDF-termin/tietotyypin, leksikaalin, arvoavaruuden, ristiriidan ja generaattorin resurssirajan virheet. Tarkistuspainikkeen alla näkyvä raportti kokoaa myös virheelliset datatype-termit ja epäselvät semanttiset polut samalla ajolla.

## Rajaus ja toteutus

- Täsmällinen kokonaislukukäsittely: selaimen BigInt, palvelimen normalisoitujen desimaalimerkkijonojen vertailu; tavalliseen Number/int-arvoon siirrytään vasta 0–10 000 -rajauksen jälkeen. Ei merkkijono-/desimaali-/eksponenttipakotusta. Myös tuhansien numeroiden luvut/etunollat testattu. Tyypit/rajat ovat yhteisessä generointisopimuksessa.
- Palvelingeneraattorin Turtle-lukija säilyttää literaalin alkuperäisen kirjoitusasun erillisellä RDFLib-sinkillä. Prosessin NORMALIZE_LITERALS-asetusta, alkuperäistä profiilituontia tai vanhoja snapshotteja ei muuteta. Näin esimerkiksi `1_0` ei muutu normalisoinnissa huomaamatta kymmeneksi ennen tarkistusta.
- Luokat: lähdevirhe, generaattorin tukirajoite, resurssiraja, huomio. Raportissa juuri/luokkamuoto, ominaisuusrajoitteet ja nimet, lähdetiedosto, predikaatti, havaittu arvo/termin tyyppi, odotettu tyyppi sekä datatype-korjausesimerkki. Nimetön PropertyShape näkyy paikallisena kohtana ja null-URI:na. Ei keksittyjä ominaisuus-IRI:jä tai URI-merkkijonojen korjaamista.
- Saman tavallisen polun yhteensopivat **nimetyt literaalirajoitteet** muodostavat yhden kentän: minCountien maksimi / maxCountien minimi, yksi yhteinen literaalityyppi ja kaikki alkuperäiset rajoiteviitteet `shacl.contributingConstraints`-tiedossa. Nimetön toisto, eri tyypit ja moninkertaiset oliorajoitteet jäävät dokumentoiduiksi tukirajoitteiksi. Usean owl:topObjectProperty-rajoitteen mapping-este ei väitä SHACLia syntaktisesti virheelliseksi.
- Esitarkistus on read-only ja rajattu (8 tasoa / 200 kenttää / 200 havaintoa sekä nykyiset tiedosto-/kolmikko-/15 s Worker-rajat). Muut generaattoritarkistukset voivat edelleen pysähtyä ensimmäiseen havaintoon. Keskeneräistä tai virheellistä pakettia ei palauteta valmiina.
- Virhe kohdistetaan näkyviin tarkistuspainikkeen alle. Aiempi ehdotus tyhjennetään uudelleentarkistuksessa. Ohjeen vianmääritys ja kenttäselitteet tulevat edelleen yhteisestä Markdownista.
- Generaattorit versioitu: palvelin `technical-package/1.1.2`, selain `browser-technical-package/1.0.1`. Uusi versio vanhentaa aiemman paikallisen paketin sidonnan, säilyttäen sen ja lähteet luettavina. Ei tietokantamigraatiota, oikeusmuutosta, hyväksynnän keventämistä tai vanhojen julkaisujen uudelleenkirjoitusta.

## Alkuperäinen tapaus ja lähteen korjaustarpeet

Alkuperäinen aineisto löytyi työtilasta ja tallennettiin tavuntarkasti testifixtureksi `fixtures/tietomallit/verovelka-2026-10-21/original.ttl` provenansseineen. **70 390 tavua, 1 015 kolmikkoa**, SHA-256 `576c4e7dbded346df0da2626eaac0b556ace059d36d6c8b2316416aced5969aa`. Käyttäjän toimittama export; ei riippumatonta verkkovarmennusta tai keksittyä lähdeversiota. Ei tietosisältöä/henkilötietoja sisältävä verorekisterivienti. Fixture ei kuulu Pages-katalogiin.

Juurena `https://iri.suomi.fi/model/verovelka/Debtor` uusi esitarkistus raportoi **38 DATATYPE_TERM**, **2 SEMANTIC_TOP_PROPERTY** ja **2 PROPERTY_CONSTRAINT_UNSUPPORTED** -havaintoa. Ei CARDINALITY-virheitä. Debtorin viisi topObjectProperty-rajoitetta näkyvät kaikki nimineen. Alkuperäisen lähteen hash/sisältö ja snapshotin sidonta säilyvät; valmis paketti estyy.

Sovelluksessa korjattiin lukijan yhteensopivuus ja diagnostiikka. **Lähteen/exportin ylläpitäjälle jää** datatype-arvojen antaminen IRI-termeinä sekä tarkoitettujen semanttisten ominaisuuksien/polkujen määrittäminen ja uusi export. Lähdettä ei korjata automaattisesti edes muistissa generoinnin jatkamiseksi.

## Validoinnin rajat

Lukijan hyväksymä xsd:int-luku ei ole väite täydellisestä SHACL-kelpoisuudesta. Nykyinen pySHACL vaatii sh:minCount/maxCount-parametrilta täsmälleen xsd:integer-tyypin. Palvelimen täydellinen SHACL-/julkaisuvalidointi säilyttää tämän ehdon; selain ei aja sitä. Rajoitteiden yhdistämisen JSON-LD/RDF/SHACL-koe käyttää alun perinkin xsd:integer-parametreja, ei korjattua käyttäjäexportia.

Numeerinen selain-/palvelinparity on testattu samoilla Turtle-aineistoilla. Palvelimen RDF/XML- ja JSON-LD-lähteiden jäsennys säilyy entisenä; niiden mahdollisesti normalisoitua leksikaalia ei tässä muutoksessa palauteta. Vain selainpolku kokoaa usean havainnon raportin. Nämä rajat on kirjattu tekniseen ohjeeseen.

## Tarkistukset

- **99 staattista testiä läpäisi** (`.venv/bin/pytest tests_static -q`), joista 37 uutta lukija-/parity-/diagnostiikkatapausta. Mukana alkuperäinen muuttamaton export, termi-/leksikaali-/arvo-/ristiriita-/resurssiluokat, hyvin suuret luvut/etunollat, alkuperäisen sisällön/hashien säilyminen, viisi topObjectProperty-rajoitetta, nimetön PropertyShape, samaan polkuun kohdistuva kelvollinen leikkaus, Unicode-IRI:en järjestys, virheellisen paketin esto sekä oikean JSON-LD-prosessorin RDF/SHACL-koe. Kaikki vanhat staattiset testit mukana. Ei API-/tunnistus-/ulkoverkkopyyntöjä tai selainvirheitä.
- Viimeisen kohdistus-/vierityskorjauksen jälkeen **8 kohdennettua selaintestiä läpäisi**: lähderaportin näkyvyys navigaation alapuolella, syntaksi-/koko-/keskeytys-/aikarajapolku ja koko kenttäohjesarja. Alkuperäisellä exportilla tehty visuaalinen HTTP-koe varmisti fokusoidun raportin alun näkyvän 112 px:n kohdalla (ylänavigaation alapuolella).
- **209 API-/profiili-/migraatiotestiä läpäisi** (`.venv/bin/pytest tests --ignore=tests/test_browser.py -q`) lopullisella palvelinlukijalla. Erillinen testikanta; ei kahta tyhjentävää sarjaa rinnakkain. Vain nykyisten rdflib/Starlette-riippuvuuksien deprekaatiovaroituksia.
- **13 palvelinselaintestiä läpäisi** (`BROWSER_BASE_URL=http://localhost:8000 .venv/bin/pytest tests/test_browser.py -q`), oikea Keycloak-kirjautuminen sekä ylläpito/hyväksyntä/julkaisu ja elinkaari mukana. Ensimmäinen ajo aikakatkaisi yhdessä elinkaaritestin withdrawn-hakutuloksen odotuksessa. Sama testi läpäisi erillisen uusinnan (1/1) ja koko sarja uusinnan (13/13) ilman tämän polun tai testin muuttamista. Ensimmäisen aikakatkaisun syytä ei yksilöity; ei toistuvaa estettä viimeisissä ajoissa.
- **Tavallinen web-build, Pages-build ja Docker-build läpäisivät.** Komennot `npm run build --prefix apps/web`, `UV_CACHE_DIR=/workspace/.cache/uv bash scripts/build-pages.sh` (myös 3 ohjekääntäjän testiä) ja `DOCKER_CONFIG=/workspace/.cache/docker bash scripts/cloud-build.sh`. Viimeinen Docker-image käynnistettiin `docker compose up -d --no-build --wait` -komennolla. Kaikkien 13 live-katalogitaulun sisältöhashit ja Alembic-head säilyivät ennen/jälkeen uudelleenkäynnistyksen. Dockerin käyttämätöntä build-välimuistia vapautettiin levytilan vuoksi; tietokantavolumeja ei poistettu.
- **124 vanhaa julkaisuversiota**, **10 vanhaa generaattoripakettia** ja **102 vanhaa artefaktia** luettiin erillisessä HTTP-yhteensopivuuskokeessa, artefaktien alkuperäiset tavut/tarkisteet varmennettu.
- Jaettu contract vastaa palvelinvakioita. `node apps/web/scripts/build-help.mjs --check` ja `git diff --check` läpäisivät.
- **Ajamattomat:** Firefox/Safari, oikea NVDA/VoiceOver, fyysinen puhelin, Windows Docker Desktop ja Codespacesin oma käynnistys. Julkista deployta tai GitHub Actionsin tulosta ei tarkistettu tästä haarasta; PR-haara ei julkaise.


**Yhdistämisen esteet:** viimeisissä paikallisissa tarkistuksissa ei toistuvaa estettä. Katselmoi erityisesti rajattu saman polun literaalirajoitteiden leikkaus ja rajoiteviitteet. Odota PR:n GitHub-tarkistuksia. Alkuperäisen lähdeprofiilin korjaustarpeita ei väitetä ratkaistuiksi tällä PR:llä.

## Kokeilu ennen yhdistämistä

```bash
uv sync --locked
npm ci --prefix apps/web
bash scripts/build-pages.sh
uv run --locked python -m scripts.preview_pages
```

Avaa `http://127.0.0.1:4173/metatietovaranto/#kokeilu`, avaa synteettinen tuote ja tuo alkuperäinen Turtle-fixture. Liitä profiili, anna juuri `https://iri.suomi.fi/model/verovelka/Debtor` ja paina **Tarkista tuki ja muodosta mapping-ehdotus**. Raportti näkyy painikkeen alla, erottaa lähdevirheet/mapping-esteet eikä väitä pakettia valmiiksi. Vertailuksi nykyinen `fixtures/semantic-profile-demo.ttl` tuottaa edelleen onnistuneen esitysehdotuksen ja paikallisen paketin ohjeen mukaisilla valinnoilla.

Mainiin yhdistäminen käynnistää nykyisen Pages-työnkulun. PR-haara ei julkaise. Ei automaattista yhdistämistä tai ulkoisia integraatioita.
