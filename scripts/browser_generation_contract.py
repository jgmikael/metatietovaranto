"""Export existing server constants; fail tests if the checked-in browser contract drifts."""
import json,hashlib
from pathlib import Path
from apps.api import technical_packages as server
from apps.api.conversion import RDF_TRIPLE_LIMIT
from apps.api.representations import LANGUAGE_PATTERN,LANGUAGE_PROFILE,REFERENCE_PROFILE,LANG_SCHEMA,LANG_CONTEXT,IRI_PATTERN
from apps.api.shacl_cardinality import COUNT_TYPES, COUNT_LIMIT
from apps.api.profiles import checksum
from apps.api.semantic_extension import profile_definition
ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'apps/web/src/browserGeneration/contract.json'
def contract():
    data={'serverGenerator':server.GENERATOR,'policy':server.POLICY,'standards':server.STANDARDS,
        'standardSourcePins':json.loads((server.FIXTURES/'provenance.json').read_text()),
        'baseContextSha256':hashlib.sha256((server.FIXTURES/'credentials-v2.jsonld').read_bytes()).hexdigest(),
        'sdSpecificationSha256':hashlib.sha256((server.FIXTURES/(server.SD_STANDARD+'.md')).read_bytes()).hexdigest(),
        'rdfTripleLimit':RDF_TRIPLE_LIMIT,'representations':{'referenceProfile':REFERENCE_PROFILE,'languageProfile':LANGUAGE_PROFILE,'languagePattern':LANGUAGE_PATTERN,'languageSchema':LANG_SCHEMA,'languageContext':LANG_CONTEXT,'iriPattern':IRI_PATTERN},'rangePolicy':server.RANGE_POLICY,'countTypes':{name:list(bounds) for name,bounds in COUNT_TYPES.items()},'countLimit':COUNT_LIMIT,'datatypes':sorted(server.DATATYPES),'reserved':sorted(server.RESERVED),
        'nodeAllowed':sorted(server.NODE_ALLOWED),'propertyAllowed':sorted(server.PROP_ALLOWED),
        'baseContextUrl':server.BASE_CONTEXT,'baseContext':json.loads((server.FIXTURES/'credentials-v2.jsonld').read_text()),
        'extensionDefinition':profile_definition('urn:placeholder:replaced-before-generation')}
    return data|{'sha256':checksum(data)}
if __name__=='__main__':TARGET.write_text(json.dumps(contract(),ensure_ascii=False,sort_keys=True,indent=2)+'\n')
