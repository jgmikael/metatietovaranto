"""One-time additive synthetic draft. Never rewrites existing fixtures/publications."""
import json
from datetime import datetime,timezone
from uuid import UUID,uuid4
from sqlalchemy import select
from apps.api.models import Product,Organization,DemoInitialization,SemanticProfile,ProfileSnapshot,Draft
from apps.api.profiles import ProfileInput,snapshot_manifest,checksum
from apps.api.contracts import ProductWrite
from apps.api.semantic_validation import validation_report
from apps.api.derived_validation import reports, POLICY as DERIVED_POLICY, ENGINE as DERIVED_ENGINE
from apps.api.distributions import normalize_distributions,assess, POLICY as DISTRIBUTION_POLICY

MARKER='phase-2e-distribution-demo'
PRODUCT_ID=UUID('00000000-0000-4000-8000-000000000004')


def seed_distribution_demo(session,root):
    if session.get(DemoInitialization,MARKER):return
    definitions=json.loads((root/'fixtures/distributions-demo.json').read_text())
    org=session.get(Organization,UUID(definitions[0]['providerOrganizationId']))
    # Explicitly authorised additive demo, only in the known synthetic demo organization.
    # No name-based rights, no collision overwrite, no seeding in arbitrary legacy organizations.
    original=session.get(Product,UUID('00000000-0000-4000-8000-000000000001'))
    if org and org.synthetic and original and original.provider_organization_id==org.id and original.metadata_.get('synthetic') is True and not session.get(Product,PRODUCT_ID):
        source={'organizationId':str(org.id),'profileUri':'https://example.org/metatietovaranto/demo/profile','ingestionMethod':'upload',
            'sourceVersion':'synthetic-demo-2e','sourceDeclaration':'Synteettinen ohjelmistofixture; ei oikea Tietomallit-export tai rekisteriote.',
            'vocabularyReferences':[{'uri':'https://example.org/metatietovaranto/demo/','location':'external'}],
            'artifact':{'serialization':'turtle','content':(root/'fixtures/semantic-profile-demo.ttl').read_text()},
            'derivedArtifacts':[{'serialization':kind,'content':(root/'fixtures'/filename).read_text(),'schemaPointer':pointer,
                'semanticMappings':json.loads((root/'fixtures/derived-mappings-demo.json').read_text())} for kind,filename,pointer in
                [('jsonSchema','derived-schema-demo.json',''),('openapi','derived-openapi-demo.json','/components/schemas/DemoCompany')]]}
        # These are small, trusted repository fixtures, not an HTTP upload. User input always uses bounded workers.
        manifest=snapshot_manifest(ProfileInput.model_validate(source))
        profile=session.scalar(select(SemanticProfile).where(SemanticProfile.profile_uri==manifest['profileUri']))
        if profile is None:profile=SemanticProfile(profile_uri=manifest['profileUri']);session.add(profile);session.flush()
        snapshot=ProfileSnapshot(profile_id=profile.id,owner_organization_id=org.id,manifest=manifest,checksum=checksum(manifest),
            graph_hash=manifest['graphHash'],created_at=datetime.now(timezone.utc));session.add(snapshot);session.flush()
        for item in definitions:item['profileSnapshotId']=str(snapshot.id)
        api=definitions[0]['api'];api['jsonSchemaArtifactId']=manifest['derivedArtifacts'][0]['id'];api['openApiArtifactId']=manifest['derivedArtifacts'][1]['id']
        body=ProductWrite(title='Yrityssisältö — JSON API, W3C VC ja SD-JWT VC (synteettinen demo)',
            description='Yksi synteettinen tietosisältö, yhteinen SHACL-profiili ja kolme rinnakkaista suunniteltua toimitustapaa.',
            providerOrganizationId=org.id,theme='Yritykset',source='Synteettinen ohjelmistofixture; ei oikea tietovaranto.',
            purpose='Toimitustapojen ja versioitujen semanttisten kenttävastaavuuksien kokeilu.',limitations='Ei varsinaista lähdepalvelua, myöntämistä, allekirjoitusta tai lompakkotoimitusta.',
            accessConditions='Vain synteettiseen demokäyttöön.',profileSnapshotId=snapshot.id,distributions=definitions,
            syntheticExample={'serialization':'turtle','content':(root/'fixtures/semantic-example-demo.ttl').read_text(),'synthetic':True},
            derivedExamples=[{'artifactId':artifact['id'],'content':(root/'fixtures/derived-example-demo.json').read_text(),'synthetic':True} for artifact in manifest['derivedArtifacts']]).model_dump(mode='json')
        normalize_distributions(body,snapshot)
        body|={'provider':org.legal_name,'modifiedAt':datetime.now(timezone.utc).isoformat(),
            'dataElements':manifest['elements'],'semanticValidation':validation_report(manifest,snapshot.checksum,body['syntheticExample'])|{'exampleSerialization':'turtle'},
            'derivedValidation':reports(manifest,body['derivedExamples'])|{'policy':DERIVED_POLICY,'engine':DERIVED_ENGINE,'profileSnapshotSha256':snapshot.checksum,'examplesHash':checksum(body['derivedExamples'])},
            'distributionValidation':assess(manifest,body['distributions'])|{'policy':DISTRIBUTION_POLICY,'profileSnapshotSha256':snapshot.checksum,'distributionsHash':checksum(body['distributions'])}}
        product=Product(id=PRODUCT_ID,title=body['title'],description=body['description'],theme=body['theme'],provider=org.legal_name,
            provider_organization_id=org.id,owner_organization_id=org.id,metadata_={},modified_at=datetime.now(timezone.utc))
        session.add(product);session.flush()
        session.add(Draft(product_id=product.id,content=body,profile_snapshot_id=snapshot.id,revision=1,status='draft',
            checksum=checksum(body),contributors=['synthetic:fixture'],modified_at=product.modified_at))
    session.add(DemoInitialization(name=MARKER))
