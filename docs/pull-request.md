## Muutos

Editor voi kokeilla luonnoksen JSON API-, W3C VC- ja SD-JWT VC -toimitustapamappingeja synteettisillä sisältöolioilla. Uusi yksityinen esikatselu muuntaa sisällöt lukitun SHACL-profiilin mukaiseksi RDF:ksi, tarkistaa ne offline SHACL Corella ja näyttää, ovatko graafit samoja. JSON API:n lukitut JSON Schema/OpenAPI -tarkistukset näkyvät erikseen.

Sisäkkäiset oliot ja moniarvoisuus käsitellään vanhemman jokaisessa esiintymässä. Väärät tyypit, kartoittamattomat kentät, RDF-joukossa häviävät arvot ja tukemattomat rakenteet estävät onnistumisen. Istunto, omistajaorganisaation editor, CSRF ja If-Match vaaditaan. Verkoton aliprosessi on resurssirajattu.

Kokeilu ei tallenna syötteitä tai raportteja, muuta hyväksyntää tai kirjoita vanhoja julkaisuja/fixtureitä uudelleen. Ei relaatiomigraatiota. Ei lähdepalvelua, kokonaisten VC-kuorien tarkistusta, JWT:n purkamista, JSON-LD-kontekstin laajennusta, allekirjoitusta tai lompakkointegraatiota. Codespacesin Private-portti/openBrowser säilyvät.

## Kokeilu ennen yhdistämistä

https://codespaces.new/jgmikael/metatietovaranto?ref=feat%2Fphase-2f-json-rdf

Kirjaudu vero / demo-vero → Omat luonnokset → Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo) → JSON → RDF -muunnoskokeilu. Täytä esimerkki, vahvista synteettisyys ja vertaa. Vaihda SD-JWT-esimerkin nimeä nähdäksesi eron tai anna null nähdäksesi hylkäyksen. Portti 8000 Private.

## Rajaus ja todennus

130 erilaista API-/PostgreSQL-/migraatiotestiä ja 10 oikean OIDC-ketjun selaintestiä läpäisi. Lopullinen web-/Docker-build, Compose-readiness, Alembic check ja restartin tietojen säilyvyys tarkistettiin. Windows, oikea Codespace ja etä-CI jäivät ajamatta.

Tarkka muunnossopimus: docs/phase-2f.md. Ajetut tarkistukset, tulokset ja ajamattomat ympäristöt: STATUS.md. Main-haaraan ei yhdistetä automaattisesti.
