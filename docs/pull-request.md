## Vaiheen 1 paikallinen demo

Repositoriossa oli vain tavoitearkkitehtuuri. Tämä muutos lisää ajettavan React/TypeScript- ja FastAPI-demon PostgreSQL-tallennuksella: tietotuotteiden lisäys, muokkaus ja poisto, haku, tuotesivu, JSON-/JSON-LD-viennit sekä kolme synteettistä tuotetta. Compose-volume säilyttää muutokset ja poistot uudelleenkäynnistyksissä.

ROADMAP.md, AGENTS.md, STATUS.md ja README määrittelevät rajauksen ja täsmällisen käynnistyksen. Kirjautuminen, organisaatio-oikeudet, hyväksyntä, julkaisuversiot ja SHACL siirtyvät vaiheeseen 2; ulkoiset lompakko-, QEAA- ja data-avaruusintegraatiot vaiheeseen 3. Demo on avoin ja tarkoitettu vain paikalliseen synteettiseen käyttöön.

## Todennus

- Lukitut Python- ja npm-asennukset sekä TypeScript-/Vite-build onnistuvat.
- Docker-image rakennettu ja Compose app/db healthy; PostgreSQL-readiness onnistuu.
- 9 testiä läpäisi: 7 API-/PostgreSQL-/RDF-testiä ja 2 Chromium-selaintestiä. Ei ohitettuja testejä.
- CRUD, tallennus erillisellä DB-yhteydellä, suodatettu haku/sivutus, JSON-vienti, JSON-LD:n RDF-merkitykset ja idempotentti siemennys testattu.
- Selainpolku lisää, muokkaa ja poistaa tuotteen sekä tarkistaa uudelleenlatauksen, skriptitekstin turvallisen esityksen ja mobiilinäkymän.

Etä-CI:n tulosta, SHACL-/DCAT-AP-vaatimustenmukaisuutta tai tuotantovalmiutta ei väitetä. Ei automaattista mergeä main-haaraan.
