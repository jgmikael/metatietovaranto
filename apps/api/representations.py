"""Bounded representation choices; never invent source content constraints."""
import re
from rdflib import URIRef,Literal,RDF,RDFS,OWL,SH
from apps.api.shacl_cardinality import read_count
LANGUAGE_PATTERN=r'^[a-z]{2,3}(?:-[a-z]{4})?(?:-(?:[a-z]{2}|[0-9]{3}))?$(?![\s\S])'
LANGUAGE_PROFILE='valueLanguage-v1'
REFERENCE_PROFILE='classOnlyIri-v1'
LANG_CONTEXT={'value':'@value','language':'@language'}
LANG_SCHEMA={'type':'object','properties':{'value':{'type':'string'},'language':{'type':'string','pattern':LANGUAGE_PATTERN}},'required':['value','language'],'additionalProperties':False}
IRI_PATTERN=r'^[A-Za-z][A-Za-z0-9+.-]*:[^\s<>"{}|^`\\]+$(?![\s\S])'
class RepresentationError(ValueError):pass

def language_value(value):
    if not isinstance(value,dict) or set(value)!={'value','language'} or not isinstance(value['value'],str) or not isinstance(value['language'],str) or not re.fullmatch(LANGUAGE_PATTERN,value['language']):
        raise RepresentationError('Kieliarvo tarvitsee value-tekstin ja language-tunnisteen. Profiili tukee pienaakkosin 2–3 kirjaimen kieltä, valinnaista kirjoitusjärjestelmää/aluetta; ei oletuskieltä.')
    return Literal(value['value'],lang=value['language'],normalize=False)

def reference_class(graph,prop):
    classes=list(graph.objects(prop,SH['class']))
    if len(classes)!=1 or not isinstance(classes[0],URIRef) or any(graph.objects(prop,SH.node)) or any(graph.objects(prop,SH.datatype)):
        raise RepresentationError('IRI-viittaus tarvitsee yhden sh:class-IRI:n eikä sh:node- tai sh:datatype-rajoitetta. sh:node vaatii kohteen sisältöä.')
    kinds=list(graph.objects(prop,SH.nodeKind))
    if kinds and kinds!=[SH.IRI]:raise RepresentationError('IRI-viittaus ei täytä ilmoitettua sh:nodeKind-rajoitetta.')
    if any(any(graph.triples((None,p,None))) for p in (SH.targetNode,SH.targetSubjectsOf,SH.targetObjectsOf)):
        raise RepresentationError('Muut kuin sh:targetClass-kohdistukset estävät viittauksen rajatun riittävyystarkistuksen.')
    for kind in (RDFS.Class,OWL.Class):
        for candidate in graph.subjects(RDF.type,kind):
            if any(str(p).startswith(str(SH)) for p in graph.predicates(candidate)) or any((candidate,RDF.type,t) in graph for t in (SH.NodeShape,SH.PropertyShape)):
                raise RepresentationError('Implisiittinen SHACL-luokkakohdistus vaatii laajemman viittausprofiilin: '+str(candidate))
    cls=classes[0]
    if any(graph.objects(cls,RDFS.subClassOf)):
        raise RepresentationError('Kohdeluokan ylaluokkakohdistukset vaativat laajemman viittausprofiilin: '+str(cls))
    # Every local target shape must accept a node containing only its rdf:type.
    annotations={'name','description','order','group','message','severity','defaultValue'}
    for shape in graph.subjects(SH.targetClass,cls):
        for p in graph.predicates(shape):
            if str(p).startswith(str(SH)) and str(p)[len(str(SH)):] not in annotations|{'targetClass','property'}:
                raise RepresentationError('Kohdemuodon rajoitteet vaativat laajemman viittausprofiilin: '+str(shape))
        for constraint in graph.objects(shape,SH.property):
            paths=list(graph.objects(constraint,SH.path))
            if len(paths)!=1 or not isinstance(paths[0],URIRef):raise RepresentationError('Kohdemuodon ominaisuuspolku puuttuu tai on monimutkainen.')
            if paths[0]==RDF.type:raise RepresentationError('Kohteen rdf:type on tyypityksen vuoksi läsnä; sen rajoitteet vaativat laajemman viittausprofiilin.')
            if any(len(list(graph.objects(constraint,p)))>1 for p in (SH.minCount,SH.maxCount)):raise RepresentationError('Kohdemuodon määrärajoite on epäselvä.')
            for maximum in graph.objects(constraint,SH.maxCount):read_count(maximum)
            if any(read_count(value,0)>0 for value in graph.objects(constraint,SH.minCount)):
                raise RepresentationError('Kohdemuoto vaatii sisältöä; pelkkä IRI ja rdf:type eivät riitä: '+str(shape))
            if any(str(p).startswith(str(SH)) and str(p)[len(str(SH)):] not in annotations|{'path','datatype','class','node','nodeKind','minCount','maxCount'} for p in graph.predicates(constraint)):
                raise RepresentationError('Kohdemuodon muuta sisältöä ei voida todeta valinnaiseksi: '+str(shape))
    return cls

def reference_value(value,cls):
    if not isinstance(value,str) or not re.fullmatch(IRI_PATTERN,value) or value==str(cls):raise RepresentationError('Viittaus tarvitsee absoluuttisen instanssi-IRI:n; kohdeluokan IRI ei ole instanssin tunniste.')
    return URIRef(value)

def reference_nodes(tree,content):
    out=set()
    def visit(node,value):
        for row in node['fields']:
            if row['name'] not in value:continue
            for v in value[row['name']] if row['multi'] else [value[row['name']]]:
                if row['mapping'].get('representation')=='iriReference':
                    iri=reference_value(v,row['mapping']['classUri']);out.add((str(iri),row['mapping']['classUri']))
                elif 'child' in row:visit(row['child'],v)
    visit(tree,content)
    return [{'@id':iri,'@type':cls} for iri,cls in sorted(out)]
