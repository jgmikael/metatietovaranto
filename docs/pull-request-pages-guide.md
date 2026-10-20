## Käyttäjän ongelma ja ohje

Oma kokeilu -lomakkeessa on runsaasti teknisiä kenttiä, eikä käyttäjälle ollut selvää, mitä pitää täyttää paketin generointiin. Uusi docs/pages-kayttoohje.md sisältää:

- toimivan ensikokeilun valmiilla synteettisellä Turtlella ja kopioitavilla arvoilla;
- työnkulun omalle organisaatiolle/tuotteelle ja profiilille;
- jokaisen näkyvän täytettävän kentän selitteen, esimerkin ja tiedon siitä, voiko sen jättää tyhjäksi;
- kaikki kolme toimitustapaa, lompakkoprofiilit, editorimappingit, generointivalinnat ja kuittaukset;
- tulosten, tallennustilojen, varmuuskopioiden ja palautuksen tulkinnan sekä vianmäärityksen.

Linkitetty READMEstä ja nykyisistä teknisistä ohjeista. Päähaaran pohja 0f26969. Vain dokumentaatio; ei muutoksia sovellukseen, tietokantaan, oikeuksiin tai julkaistuihin snapshotteihin. Ei mainin automaattista yhdistämistä.

## Todennus

Kenttänimien vertailu käyttöliittymälähteisiin: 49 toimitustapa-/mapping-selitettä, 10 generointikenttää, 5 kokeilu-/organisaatiokentän labelia ja 7 perustietokenttää löytyvät oppaasta. Dokumenttien suhteelliset tiedostolinkit ja git diff --check läpäisivät. Pages-build läpäisi.

Ohjeen omat esimerkkiarvot kokeiltiin oikealla Chromiumilla tavallisessa staattisessa /metatietovaranto/-HTTP-palvelimessa: tiedostotuonti, mapping-ehdotus, kolme kuittausta, generointi, 13 artefaktia, kontekstitiedoston lataus ja reload läpäisivät. Ulkoiset/kirjoituspyynnöt estettiin; ei niitä tai JS-/konsolivirheitä. Preview pysäytettiin.

Koko API-/migraatio-/selainregressiosarjaa ei toistettu dokumentaatiomuutokselle. Julkista Pages-versiota ja muita selaimia ei testattu tässä tehtävässä. Sovelluskäyttäytyminen ei muutu.

## Yhdistämisen jälkeen

Ohje on luettavissa README-linkistä. Tähän muutokseen ei kuulu sovelluksen kenttäkohtaisia tooltippejä tai uusi Pages-toiminto; kyse on kattavasta käyttäjän täyttöohjeesta. Nykyinen Pages-workflow saa toimia normaalisti. Ei uusia asetuksia tai palveluita.
