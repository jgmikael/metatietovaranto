"""Offline SHACL Core checks, bounded in a subprocess; never validate issued credentials."""
import hashlib
import importlib.metadata
import multiprocessing
from datetime import datetime, timezone

from rdflib import Graph, RDF, SH, URIRef
from pyshacl import validate
from pyshacl.entrypoints import meta_validate
from pyshacl.shapes_graph import ShapesGraph

from apps.api.profiles import ArtifactInput, parse_artifact

POLICY = 'shacl-core-offline-v1'
ENGINE = 'pyshacl/' + importlib.metadata.version('pyshacl')
MAX_RESULTS = 100
# Every other SHACL predicate is rejected rather than silently ignored (including SPARQL/JS/AF).
CORE_PREDICATES = set('''targetClass targetNode targetSubjectsOf targetObjectsOf path property node
    class datatype nodeKind minCount maxCount minExclusive minInclusive maxExclusive maxInclusive
    minLength maxLength pattern flags languageIn uniqueLang equals disjoint lessThan lessThanOrEquals
    in hasValue not and or xone qualifiedValueShape qualifiedMinCount qualifiedMaxCount
    qualifiedValueShapesDisjoint closed ignoredProperties deactivated severity message name description order
    group defaultValue alternativePath inversePath zeroOrMorePath oneOrMorePath zeroOrOnePath'''.split())


def result_items(graph, stage):
    items = []
    for result in sorted(graph.subjects(RDF.type, SH.ValidationResult), key=str):
        if len(items) == MAX_RESULTS:
            break
        item = {'stage': stage, 'ruleId': str(graph.value(result, SH.sourceConstraintComponent) or 'SHACL'),
                'severity': str(graph.value(result, SH.resultSeverity) or SH.Violation),
                'path': '/syntheticExample' if stage == 'example' else '/profileSnapshotId'}
        for field, predicate in [('focusNode', SH.focusNode), ('resultPath', SH.resultPath), ('sourceShape', SH.sourceShape)]:
            value = graph.value(result, predicate)
            if value is not None:
                item[field] = str(value)[:1000]
        item['message'] = '; '.join(str(value) for value in graph.objects(result, SH.resultMessage))[:2000]
        items.append(item)
    return items


def profile_check(graph):
    unsupported = sorted({str(predicate) for _, predicate, _ in graph
                          if str(predicate).startswith(str(SH)) and str(predicate)[len(str(SH)):] not in CORE_PREDICATES})
    custom = list(graph.subjects(RDF.type, SH.ConstraintComponent))
    if unsupported or custom:
        return {'conforms': False, 'results': [{'stage': 'profile', 'ruleId': 'SHACL_UNSUPPORTED',
            'severity': str(SH.Violation), 'path': '/profileSnapshotId',
            'message': 'Tukematon SHACL-laajennus; vain offline SHACL Core on sallittu.',
            'predicates': unsupported[:20]}]}
    conforms, report, _ = meta_validate(graph, inference='none', advanced=False, js=False,
        do_owl_imports=False, allow_infos=False, allow_warnings=False, max_validation_depth=20)
    return {'conforms': bool(conforms), 'results': result_items(report, 'profile')}


def locked_graph(manifest):
    graph = Graph()
    sources = list(manifest['sourceArtifacts'])
    sources += [dep['artifact'] for dep in manifest['dependencies'] if 'artifact' in dep]
    for source in sources:
        if hashlib.sha256(source['content'].encode()).hexdigest() != source['sha256']:
            raise ValueError('Lukitun artefaktin tarkiste ei täsmää')
        parsed, _ = parse_artifact(ArtifactInput(serialization=source['serialization'], content=source['content']))
        if parsed is not None:
            # Scope blank nodes separately across imported documents.
            from rdflib import BNode
            nodes = {}
            def scoped(node):
                return nodes.setdefault(node, BNode()) if isinstance(node, BNode) else node
            for s, p, o in parsed:
                graph.add((scoped(s), p, scoped(o)))
        if len(graph) > 10000:
            raise ValueError('Profiilin kolmikkoraja ylittyi')
    return graph


def validation_report(manifest, profile_hash, example):
    report = {'policy': POLICY, 'engine': ENGINE, 'profileSnapshotSha256': profile_hash,
              'exampleSha256': hashlib.sha256(example['content'].encode()).hexdigest() if example else None,
              'checkedAt': datetime.now(timezone.utc).isoformat(), 'status': 'invalid',
              'profileConforms': False, 'exampleConforms': False, 'focusNodeCount': 0, 'results': []}
    graph = locked_graph(manifest)
    checked = profile_check(graph)
    report['profileConforms'] = checked['conforms']
    report['results'] = checked['results']
    if not checked['conforms']:
        return report
    if not example:
        report['results'].append({'stage': 'example', 'ruleId': 'EXAMPLE_REQUIRED', 'path': '/syntheticExample',
            'severity': str(SH.Violation), 'message': 'Synteettinen esimerkkisisältö puuttuu.'})
        return report
    data, _ = parse_artifact(ArtifactInput(serialization=example['serialization'], content=example['content']))
    if data is None:
        raise ValueError('Esimerkin on oltava RDF-aineistoa')
    if len(data) > 2000:
        raise ValueError('Esimerkin raja on 2000 RDF-kolmikkoa')
    shapes = list(ShapesGraph(graph).shapes)
    entry = {URIRef(uri) for uri in manifest.get('entryShapeUris', [])}
    targets = [shape for shape in shapes if not shape.deactivated and (shape.node in entry if entry else not shape.is_property_shape)]
    coverage = [(shape, shape.focus_nodes(data)) for shape in targets]
    focus_nodes = set().union(*(nodes for _, nodes in coverage))
    report['focusNodeCount'] = len(focus_nodes)
    if not focus_nodes or (entry and any(not nodes for _, nodes in coverage)) or (entry and len(coverage) != len(entry)):
        report['results'].append({'stage': 'example', 'ruleId': 'EXAMPLE_TARGET_REQUIRED', 'path': '/syntheticExample',
            'severity': str(SH.Violation), 'message': 'Esimerkki ei kohdista tietuetta profiilin aloitusmuotoihin (esimerkiksi rdf:type puuttuu).'})
        return report
    conforms, results, _ = validate(data, shacl_graph=graph, inference='none', advanced=False, js=False,
        do_owl_imports=False, allow_infos=False, allow_warnings=False, max_validation_depth=20)
    report['exampleConforms'] = bool(conforms)
    report['results'] = result_items(results, 'example')
    report['resultCount'] = len(list(results.subjects(RDF.type, SH.ValidationResult)))
    report['truncated'] = report['resultCount'] > MAX_RESULTS
    report['status'] = 'conforms' if conforms else 'invalid'
    return report


def _worker(manifest, profile_hash, example, writer):
    try:
        import resource
        import socket
        resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024, 512 * 1024 * 1024))
        def no_network(*args, **kwargs):
            raise ValueError('Validoinnissa ei sallita verkkoyhteyksiä')
        socket.socket.connect = no_network
        socket.socket.connect_ex = no_network
        socket.getaddrinfo = no_network
        writer.send(validation_report(manifest, profile_hash, example))
    except Exception:
        # No user source/query/content in exceptions, logs or IPC error responses.
        writer.send({'status': 'error', 'results': [{'stage': 'validation', 'ruleId': 'VALIDATION_ERROR',
            'path': '/syntheticExample', 'severity': str(SH.Violation),
            'message': 'SHACL-tarkistus epäonnistui: tarkista syntaksi, rajoitteet ja riippuvuudet.'}]})
    finally:
        writer.close()


def bounded_validation(manifest, profile_hash, example):
    context = multiprocessing.get_context('spawn')
    reader, writer = context.Pipe(duplex=False)
    process = context.Process(target=_worker, args=(manifest, profile_hash, example, writer))
    process.start()
    writer.close()
    try:
        if not reader.poll(15):
            raise ValueError('SHACL-validoinnin aikaraja ylittyi')
        try:
            return reader.recv()
        except EOFError:
            raise ValueError('SHACL-validoinnin resurssiraja ylittyi') from None
    finally:
        reader.close()
        process.join(.2)
        if process.is_alive():
            process.terminate()
            process.join(1)


def validate_snapshot(snapshot, example, root_shape=None):
    try:
        manifest={**snapshot.manifest,'entryShapeUris':[root_shape]} if root_shape else snapshot.manifest
        report = bounded_validation(manifest, snapshot.checksum, example)
    except ValueError:
        report = {'status': 'error', 'results': [{'stage': 'validation', 'ruleId': 'VALIDATION_RESOURCE_LIMIT',
            'path': '/syntheticExample', 'severity': str(SH.Violation),
            'message': 'SHACL-validoinnin aika- tai resurssiraja ylittyi. Julkaisua ei sallita.'}]}
    report.update({'policy': POLICY, 'engine': ENGINE, 'profileSnapshotSha256': snapshot.checksum,
        'exampleSha256': hashlib.sha256(example['content'].encode()).hexdigest() if example else None,
        'exampleSerialization': example['serialization'] if example else None})
    if root_shape:report['selectedRootShapeUri']=root_shape
    return report


def current_report(report, snapshot, example, root_shape=None):
    return bool(report and example and report.get('selectedRootShapeUri')==root_shape and example.get('synthetic') is True
        and report.get('exampleSerialization') == example.get('serialization') and report.get('policy') == POLICY and report.get('engine') == ENGINE
        and report.get('profileSnapshotSha256') == snapshot.checksum
        and report.get('exampleSha256') == hashlib.sha256(example['content'].encode()).hexdigest())
