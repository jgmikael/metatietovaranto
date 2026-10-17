"""Offline, non-persistent synthetic JSON content laboratory; never decode credentials."""
import hashlib
import math
import multiprocessing
import re
from datetime import date, datetime, timezone
from typing import Annotated, Literal as Choice
from uuid import UUID

from pydantic import Field, StringConstraints, field_validator, model_validator
from rdflib import BNode, Graph, Literal, RDF, SH, URIRef, XSD
from rdflib.compare import to_canonical_graph

from apps.api.contracts import Contract
from apps.api.derived_validation import artifact_report, strict_json
from apps.api.distributions import assess
from apps.api.profiles import checksum
from apps.api.semantic_validation import ENGINE, locked_graph, validation_report

POLICY = 'synthetic-json-rdf-v1'


class ConversionExample(Contract):
    distributionId: UUID
    content: Annotated[str, StringConstraints(strip_whitespace=False)] = Field(min_length=1, max_length=100000)
    synthetic: Choice[True]

    @field_validator('content')
    @classmethod
    def byte_limit(cls, value):
        if len(value.encode()) > 100000:
            raise ValueError('Esimerkin UTF-8-raja on 100 kB')
        return value


class ConversionRequest(Contract):
    examples: list[ConversionExample] = Field(min_length=1, max_length=3)

    @model_validator(mode='after')
    def unique_and_bounded(self):
        if len({item.distributionId for item in self.examples}) != len(self.examples):
            raise ValueError('Yksi esimerkki per toimitustapa')
        if sum(len(item.content.encode()) for item in self.examples) > 200000:
            raise ValueError('Esimerkkien yhteisraja on 200 kB')
        return self


class ConversionError(ValueError):
    def __init__(self, rule, message, path=''):
        self.finding = {'ruleId': rule, 'message': message, 'path': path}


def fail(rule, message, path=''):
    raise ConversionError(rule, message, path)


def tokens(path):
    return [part.replace('~1', '/').replace('~0', '~') for part in path[1:].split('/')]


def join(path, token):
    return path + '/' + str(token).replace('~', '~0').replace('/', '~1')


def bounded_json(content):
    try:
        value = strict_json(content)
    except (ValueError, RecursionError):
        fail('JSON_SYNTAX', 'JSON-syntaksi, päällekkäinen avain tai lukuarvo on virheellinen')
    count = 0
    def walk(node, depth):
        nonlocal count
        count += 1
        if depth > 20 or count > 5000:
            fail('JSON_RESOURCE_LIMIT', 'JSON-rakenteen syvyys- tai solmuraja ylittyi')
        if isinstance(node, dict):
            # Unresolved SD disclosures and real credential material are outside this laboratory.
            if {'_sd', '_sd_alg', '...', 'proof', 'jwt', 'access_token', 'credential_offer'} & node.keys():
                fail('CREDENTIAL_MATERIAL', 'Syötä vain synteettinen sisältöolio ilman todistusta, disclosureja tai tokeneita')
            for child in node.values():walk(child, depth + 1)
        elif isinstance(node, list):
            for child in node:walk(child, depth + 1)
        elif isinstance(node, float) and not math.isfinite(node):
            fail('JSON_NUMBER', 'Luvun on oltava äärellinen')
    walk(value, 0)
    if not isinstance(value, dict):fail('JSON_OBJECT', 'Esimerkin on oltava synteettinen JSON-sisältöolio')
    return value


def typed_literal(value, datatype, path):
    name = datatype.removeprefix(str(XSD))
    if datatype != str(XSD) + name:
        fail('DATATYPE_UNSUPPORTED', 'Tätä literaalin tietotyyppiä ei tueta', path)
    valid = False
    if name == 'string':valid = isinstance(value, str)
    elif name == 'boolean':valid = type(value) is bool
    elif name in ('integer', 'nonNegativeInteger', 'positiveInteger'):
        valid = type(value) is int and (name == 'integer' or value >= (1 if name == 'positiveInteger' else 0))
    elif name == 'double':valid = type(value) in (int, float) and math.isfinite(value)
    elif name == 'decimal':valid = isinstance(value, str) and re.fullmatch(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)', value) is not None
    elif name == 'anyURI':valid = isinstance(value, str) and re.fullmatch(r'[A-Za-z][A-Za-z0-9+.-]*:[^\s<>"{}|^`\\]+', value) is not None
    elif name in ('date', 'dateTime'):
        valid = isinstance(value, str) and re.fullmatch(
            r'[0-9]{4}-[0-9]{2}-[0-9]{2}' if name == 'date' else
            r'[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]{1,6})?(?:Z|[+-](?:0[0-9]|1[0-3]):[0-5][0-9]|[+-]14:00)?', value) is not None
        if valid:
            try:(date if name == 'date' else datetime).fromisoformat(value.replace('Z', '+00:00'))
            except ValueError:valid = False
    else:fail('DATATYPE_UNSUPPORTED', 'Tätä XSD-literaalia ei tueta muunnosprofiilissa', path)
    if not valid:fail('JSON_DATATYPE', 'JSON-arvo ei vastaa mappingin eksplisiittistä XSD-tietotyyppiä', path)
    lexical = ('true' if value else 'false') if type(value) is bool else str(value)
    return Literal(lexical, datatype=URIRef(datatype), normalize=False)


def convert(manifest, item, instance):
    """Correlate nested fields within each parent occurrence, never via Cartesian joins."""
    shapes = locked_graph(manifest)
    entries = item['mapping']['entries']
    roots = {entry['shapeUri'] for entry in entries}
    if len(roots) != 1:fail('ROOT_UNSUPPORTED', 'Muunnos tarvitsee yhden yksiselitteisen juurimuodon')
    root = URIRef(next(iter(roots)))
    classes = list(shapes.objects(root, SH.targetClass))
    if len(classes) != 1 or not isinstance(classes[0], URIRef):
        fail('ROOT_UNSUPPORTED', 'Juurimuoto tarvitsee yhden sh:targetClass-IRI:n')
    graph = Graph();subject = BNode();graph.add((subject, RDF.type, classes[0]))
    consumed = {''};children = {}
    for entry in entries:
        children.setdefault(tuple(entry['semanticPath'][:-1]), []).append(entry)

    def occurrences(node, relative, base):
        path = base;values = [(node, path)]
        for index, token in enumerate(relative):
            next_values = []
            for current, current_path in values:
                consumed.add(current_path)
                if token == '*':
                    if index != len(relative) - 1:
                        fail('PATH_UNSUPPORTED', 'Taulukon alkiot tarvitsevat eksplisiittisen oliovanhemman', current_path)
                    if not isinstance(current, list):fail('JSON_ARRAY', 'Mapping odottaa JSON-taulukkoa', current_path)
                    next_values.extend((child, join(current_path, i)) for i, child in enumerate(current))
                else:
                    if not isinstance(current, dict):fail('JSON_OBJECT', 'Mapping odottaa JSON-oliota', current_path)
                    if token in current:next_values.append((current[token], join(current_path, token)))
            values = next_values
        for _, path in values:consumed.add(path)
        return values

    def visit(node, rdf_subject, semantic_parent=(), field_parent=(), base=''):
        for entry in children.get(semantic_parent, []):
            full = tuple(tokens(entry['fieldPath']))
            if full[:len(field_parent)] != field_parent or len(full) <= len(field_parent):
                fail('MAPPING_NESTING', 'Kenttä ei sijoitu oliovanhemman alle')
            values = occurrences(node, full[len(field_parent):], base)
            if len(values) < entry['minCount'] or entry['maxCount'] is not None and len(values) > entry['maxCount']:
                fail('JSON_CARDINALITY', 'Arvojen määrä rikkoo mappingin kardinaliteettia', entry['fieldPath'])
            seen = set()
            for value, path in values:
                if entry['valueKind'] == 'literal':
                    rdf_value = typed_literal(value, entry['datatype'], path)
                    if rdf_value in seen:fail('RDF_VALUE_LOSS', 'Toistuva literaali häviäisi RDF-joukossa', path)
                    seen.add(rdf_value)
                else:
                    if not isinstance(value, dict):fail('JSON_OBJECT', 'Sisäkkäisen arvon on oltava olio', path)
                    rdf_value = BNode()
                    if entry['classUri']:graph.add((rdf_value, RDF.type, URIRef(entry['classUri'])))
                    visit(value, rdf_value, tuple(entry['semanticPath']), full, path)
                graph.add((rdf_subject, URIRef(entry['semanticPath'][-1]), rdf_value))
                if len(graph) > 2000:fail('RDF_RESOURCE_LIMIT', 'Muunnoksen 2000 kolmikon raja ylittyi')
    visit(instance, subject)

    def covered(value, path=''):
        if path not in consumed:fail('JSON_UNMAPPED', 'JSON-kenttä tai säiliö jää mappingin ulkopuolelle', path)
        if isinstance(value, dict):
            for key, child in value.items():covered(child, join(path, key))
        elif isinstance(value, list):
            for index, child in enumerate(value):covered(child, join(path, index))
    covered(instance)
    return graph


def preview(manifest, profile_hash, items, examples):
    metadata = assess(manifest, items)
    report = {'status': 'invalid', 'metadataValidation': metadata, 'examples': [],
              'comparison': {'status': 'notCompared'}, 'results': [],
              'scope': 'synthetic content preview only; no credential structure, JSON-LD expansion, JWT decoding or cryptographic verification'}
    if metadata['status'] != 'conforms':return report
    by_id = {item['id']:item for item in items};hashes = []
    for example in examples:
        item = by_id.get(example['distributionId'])
        row = {'distributionId': example['distributionId'], 'status': 'invalid', 'results': [],
               'exampleSha256': hashlib.sha256(example['content'].encode()).hexdigest(),
               'structureValidation': {'status': 'notAssessed', 'scope': 'credential envelope not assessed'}}
        report['examples'].append(row)
        if not item:
            row['results'] = [{'ruleId': 'DISTRIBUTION_UNKNOWN', 'path': '', 'message': 'Toimitustapaa ei ole tallennetussa luonnoksessa'}];continue
        row.update({'type':item['type'], 'mappingVersion':item['mapping']['version'], 'mappingHash':checksum(item['mapping'])})
        try:
            instance = bounded_json(example['content'])
            if item['type'] == 'jsonApi':
                refs = {item['api']['jsonSchemaArtifactId'], item['api']['openApiArtifactId']} - {None}
                artifacts = [artifact for artifact in manifest['derivedArtifacts'] if artifact['id'] in refs]
                checks = [artifact_report(artifact, example, None, include_coverage=False) for artifact in artifacts]
                row['structureValidation'] = {'status': 'conforms' if checks and all(check['status'] == 'conforms' for check in checks) else 'invalid' if checks else 'notAssessed', 'artifacts': checks, 'scope':'JSON Schema/OpenAPI structure and instance only; no semantic coverage or credential envelope'}
                if any(check['status'] != 'conforms' for check in checks):
                    fail('JSON_SCHEMA_INVALID', 'JSON API -esimerkki ei läpäise lukittua teknistä skeemaa')
            graph = convert(manifest, item, instance)
            turtle = graph.serialize(format='turtle')
            row['semanticValidation'] = validation_report(manifest, profile_hash,
                {'content':turtle, 'serialization':'turtle', 'synthetic':True})
            canonical = to_canonical_graph(graph)
            row.update({'rdf':turtle, 'tripleCount':len(graph),
                'graphSha256':checksum(sorted((s.n3(), p.n3(), o.n3()) for s, p, o in canonical))})
            row['status'] = row['semanticValidation']['status']
            if row['status'] == 'conforms':hashes.append(row['graphSha256'])
        except ConversionError as error:row['results'] = [error.finding]
        except Exception:row['results'] = [{'ruleId':'CONVERSION_ERROR', 'path':'', 'message':'Muunnosta ei voitu tehdä tällä profiililla ja mappingilla'}]
    if len(hashes) == len(examples) and len(hashes) >= 2:
        same = len(set(hashes)) == 1
        report['comparison'] = {'status': 'sameGraph' if same else 'differentGraphs', 'method':'RDF graph isomorphism; unordered multivalues'}
        report['status'] = 'conforms' if same else 'different'
    elif len(hashes) == len(examples):report['status'] = 'conforms'
    return report


def _worker(manifest, profile_hash, items, examples, writer):
    try:
        import resource, socket
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        resource.setrlimit(resource.RLIMIT_AS, (512*1024*1024, 512*1024*1024))
        def offline(*args, **kwargs):raise ValueError('Offline')
        socket.socket.connect = offline;socket.socket.connect_ex = offline;socket.getaddrinfo = offline
        writer.send(preview(manifest, profile_hash, items, examples))
    except Exception:
        writer.send({'status':'error', 'examples':[], 'comparison':{'status':'notCompared'},
                     'results':[{'ruleId':'CONVERSION_ERROR', 'message':'Muunnoksen tarkistus epäonnistui'}]})
    finally:writer.close()


def conversion_preview(snapshot, items, examples):
    context = multiprocessing.get_context('spawn');reader, writer = context.Pipe(duplex=False)
    process = context.Process(target=_worker, args=(snapshot.manifest, snapshot.checksum, items, examples, writer))
    process.start();writer.close()
    try:
        if not reader.poll(15):raise ValueError('Timeout')
        try:report = reader.recv()
        except EOFError:raise ValueError('Resource limit') from None
    except ValueError:
        report = {'status':'error', 'examples':[], 'comparison':{'status':'notCompared'},
                  'results':[{'ruleId':'CONVERSION_RESOURCE_LIMIT', 'message':'Muunnoksen aika- tai resurssiraja ylittyi'}]}
    finally:
        reader.close();process.join(.2)
        if process.is_alive():process.terminate();process.join(1)
    return report | {'policy':POLICY, 'engine':ENGINE, 'profileSnapshotId':str(snapshot.id),
        'profileSnapshotSha256':snapshot.checksum, 'checkedAt':datetime.now(timezone.utc).isoformat()}
