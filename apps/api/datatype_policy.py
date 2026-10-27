"""Bounded local OWL range assessment, not OWL inference or SHACL validation."""
from rdflib import URIRef, Literal, RDFS, OWL

RANGE_POLICY = {
    'version': 'locked-explicit-disjoint-v1',
    'literal': str(RDFS.Literal),
    'range': str(RDFS.range),
    'disjoint': str(OWL.disjointWith),
}


def term_info(term):
    if isinstance(term, URIRef):return {'value': str(term), 'termType': 'NamedNode'}
    if isinstance(term, Literal):
        from rdflib import RDF, XSD
        return {'value': str(term), 'termType': 'Literal',
                'datatype': str(term.datatype or (RDF.langString if term.language else XSD.string)),
                'language': term.language or ''}
    return {'value': str(term), 'termType': 'BlankNode'}


def datatype_issue(datatype, node_kind, supported):
    if datatype is not None and not isinstance(datatype, URIRef):
        value = str(datatype)
        # Suggest the observed IRI only; never use the literal's own datatype.
        import re
        suggestion = ('sh:datatype <'+value+'> .' if re.fullmatch(r'[A-Za-z][A-Za-z0-9+.-]*:[^\s<>"{}|^`\\]+', value)
                      else 'Anna sh:datatype-arvoksi tarkoitetun konkreettisen tietotyypin IRI.')
        return 'DATATYPE_TERM', 'sourceError', 'sh:datatype tarvitsee IRI:n, ei literaalia.', suggestion
    if datatype == RDFS.Literal or datatype is None and isinstance(node_kind, URIRef) and str(node_kind) == 'http://www.w3.org/ns/shacl#Literal':
        return 'DATATYPE_REPRESENTATION_REQUIRED', 'generatorLimit', 'Konkreettinen literaalin esitysratkaisu puuttuu. sh:datatype rdfs:Literal ei tarkoita mitä tahansa literaalia; sh:nodeKind sh:Literal jättää konkreettisen tyypin avoimeksi.', None
    if datatype is not None and str(datatype) not in supported:
        return 'DATATYPE_UNSUPPORTED', 'generatorLimit', 'Kelvollinen tietotyyppi-IRI ei kuulu generointiprofiiliin: '+str(datatype)+'. Kielimerkittyjä arvoja ei muuteta merkkijonoiksi eikä kielitietoa poisteta.', None
    return None


def assess_range(graph, datatype, owl_range):
    # Explicit disjointness takes precedence over any accepted refinement.
    if (datatype, OWL.disjointWith, owl_range) in graph or (owl_range, OWL.disjointWith, datatype) in graph:
        return 'OWL_SHACL_CONFLICT', 'sourceError', 'Lukitussa aineistossa on eksplisiittinen owl:disjointWith SHACL-tietotyypin ja OWL-arvoalueen välillä.'
    if isinstance(owl_range, URIRef) and owl_range == datatype:
        return 'OWL_RANGE_COMPATIBLE', 'warning', 'SHACL-tietotyyppi ja paikallinen OWL-arvoalue ovat samat.'
    if owl_range == RDFS.Literal:
        return 'OWL_RANGE_REFINEMENT', 'warning', 'OWL:n rdfs:Literal sallii SHACLin konkreettisen literaalityypin tarkennuksen.'
    return 'OWL_RANGE_UNASSESSED', 'warning', 'Rajattu tarkistus ei ratkaise tämän OWL-arvoalueen yhteensopivuutta. Eri IRI ei yksin todista ristiriitaa; OWL-päättelyä ei suoritettu.'
