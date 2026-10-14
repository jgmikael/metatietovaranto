# Vaiheen 1 arkkitehtuuri

React/TypeScript rakennetaan Viten avulla. FastAPI palvelee rakennetun käyttöliittymän ja REST API:n samasta alkuperästä. Näin ei tarvita CORS-asetuksia. Tuotesivut käyttävät hash-reititystä; `/id/products/{uuid}` neuvottelee JSON-/JSON-LD-esityksen tai ohjaa selaimen tuotesivulle (303, `Vary: Accept`). Paikallisen demon URI on HTTP; tuotannon HTTPS-tunnisteet kuuluvat myöhempään käyttöönottoon.

SQLAlchemy käyttää PostgreSQL:ää psycopgin kautta. Tuotteiden tunnisteet ovat UUID:itä. Nimi, kuvaus, tarjoaja ja teema ovat relaatiokenttiä; muut vaiheen 1 kuvauskentät ja tietoelementit ovat JSONB:ssä. Palvelin tuottaa muokkausajan. API validioi pakolliset kentät, pituusrajat, saatavuuden ja tietoelementtien URI:t Pydanticilla. Demo hyväksyy vain synteettisiä kuvauksia ja planned/sandbox-saatavuuden.

Vaiheessa 1 on yksi alkuperäisskeema, joka luodaan SQLAlchemyllä. Ennen skeeman muuttamista vaiheessa 2 otetaan käyttöön Alembic. Siemennys on transaktionaalinen ja käyttää PostgreSQL:n advisory-lukkoa; alustustaulu varmistaa, ettei uudelleenkäynnistys palauta poistettuja demotuotteita tai korvaa muokkauksia. Tietokantavolume säilyy pysäytyksissä.

JSON-LD käyttää DCAT Dataset-/Catalog-termejä, Dublin Core -kuvauksia ja paikallista `https://example.org/metatietovaranto/demo/`-nimiavaruutta. Konteksti on inline eikä jäsentäminen edellytä ulkoisten kontekstien noutamista. Semanttiset URI:t ovat näkyvästi paikallisia demotermejä. Viennissä kuvataan metatiedot, ei varsinaisia rekisteritietueita. DCAT-AP:n koko profiilia tai SHACL-validointia ei toteuteta tässä vaiheessa.

Vaiheen 1 API on avoin, muutokset tulevat heti näkyviin eikä tuotteella ole julkaisuversiota. Avoin ylläpito ei sovellu tuotantoon. Compose sitoo portit vain paikalliseen koneeseen ja palvelin edellyttää eksplisiittistä DEMO_MODE-asetusta. React käsittelee tekstit tekstinä; käyttäjän HTML:ää ei renderöidä. Palvelin ei nouda käyttäjän syöttämiä URI:eja. Kirjoitusten oikeudet, auditointi ja samanaikaisten muokkausten hallinta kuuluvat vaiheeseen 2.
