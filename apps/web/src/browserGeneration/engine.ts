import {readCount,CountError,recordSource,preflight,groupProperties,propertyValues,propertyLocator} from './diagnostics';
import {Parser,Store,DataFactory,type Term} from 'n3';
import Ajv2020 from 'ajv/dist/2020';
import jsonld from 'jsonld';
import contract from './contract.json';
import {BROWSER_GENERATOR,FILE_LIMIT,TRIPLE_LIMIT,FIELD_LIMIT,DEPTH_LIMIT,canonical,sha256,bytes,profileBody,generationBinding,type ImportedProfile,type SourceFile,type GenerationSettings,type Tree,type Row,type Finding,type LocalPackage} from './model';
import type {Distribution} from '../Distributions';
const {namedNode}=DataFactory;
const SH='http://www.w3.org/ns/shacl#',RDF='http://www.w3.org/1999/02/22-rdf-syntax-ns#',XSD='http://www.w3.org/2001/XMLSchema#',OWL='http://www.w3.org/2002/07/owl#';
const GENERATOR=BROWSER_GENERATOR;
export class GenerationError extends Error {findings?:Finding[];finding:Finding;constructor(ruleId:string,path:string,message:string){super(message);this.finding={ruleId,path,message,category:ruleId.endsWith('_LIMIT')?'resourceLimit':['TURTLE_SYNTAX','TURTLE_PROFILE','RELATIVE_IRI','CARDINALITY_TERM','CARDINALITY_LEXICAL','CARDINALITY_VALUE','CARDINALITY_CONFLICT','DATATYPE_TERM'].includes(ruleId)?'sourceError':'generatorLimit'};}}
function fail(rule:string,path:string,message:string):never{throw new GenerationError(rule,path,message);}
function compare(a:string,b:string){const left=Array.from(a,v=>v.codePointAt(0)!),right=Array.from(b,v=>v.codePointAt(0)!);for(let i=0;i<Math.min(left.length,right.length);i++)if(left[i]!==right[i])return left[i]-right[i];return left.length-right.length;}
export function absolute(value:string){return /^[a-zA-Z][a-zA-Z0-9+.-]*:\S+$/.test(value);}
export function parseSources(sources:SourceFile[]){
 if(!sources.length||sources.length>10||sources.reduce((n,s)=>n+bytes(s.content),0)>FILE_LIMIT)fail('FILE_LIMIT','/sources','Turtle-tiedostojen yhteisraja on 256 KiB, enintään 10 tiedostoa.');
 const graph=new Store();let parsedTriples=0;
 for(const [index,source] of sources.entries()){
  let quads;try{quads=new Parser({format:'text/turtle',blankNodePrefix:'file'+index+'_',factory:{...DataFactory,quad:(s:any,p:any,o:any,g?:any)=>{if(++parsedTriples>TRIPLE_LIMIT)fail('TRIPLE_LIMIT',source.name,'Jäsennettyjen kolmikoiden raja on 10 000.');return DataFactory.quad(s,p,o,g);}}}).parse(source.content);}catch(e){if(e instanceof GenerationError)throw e;fail('TURTLE_SYNTAX',source.name,'Turtle-syntaksivirhe: '+(e as Error).message);}
  for(const q of quads!){
   if(q.graph.termType!=='DefaultGraph'||[q.subject,q.predicate,q.object].some(t=>!['NamedNode','BlankNode','Literal'].includes(t.termType)))fail('TURTLE_PROFILE',source.name,'Vain Turtle / RDF 1.1 ilman nimettyjä graafeja tai RDF-star-rakenteita.');
   for(const t of [q.subject,q.predicate,q.object])if(t.termType==='NamedNode'&&!absolute(t.value))fail('RELATIVE_IRI',source.name,'Suhteellinen IRI tarvitsee tiedostossa eksplisiittisen @base-määrityksen: '+t.value);
   recordSource(graph,q.subject,source.name);graph.addQuad(q);if(graph.size>TRIPLE_LIMIT)fail('TRIPLE_LIMIT',source.name,'Profiilin kolmikkoraja on 10 000.');
  }
 }
 return graph;
}
const values=(g:Store,s:Term,p:string)=>g.getObjects(s,namedNode(p),null);
const subjects=(g:Store,p:string,o:Term)=>g.getSubjects(namedNode(p),o,null);
export async function inspectFiles(sources:SourceFile[]){
 for(const s of sources)if(await sha256(s.content)!==s.sha256)fail('SOURCE_HASH',s.name,'Lähdetiedoston tarkiste ei täsmää.');
 const graph=parseSources(sources);
 const ontologies=subjects(graph,RDF+'type',namedNode(OWL+'Ontology')).filter(t=>t.termType==='NamedNode');
 const oneOntology=ontologies.length===1?ontologies[0]:null;
 const versions=oneOntology?values(graph,oneOntology,OWL+'versionInfo'):[];
 const iriVersions=oneOntology?values(graph,oneOntology,OWL+'versionIRI'):[];
 const imports=graph.getQuads(null,namedNode(OWL+'imports'),null,null).map(q=>({uri:q.object.value,resolved:graph.countQuads(q.object,null,null,null)>0,scope:'OWL-viite; ei verkkonoutoa. Tarvittava sh:node tarkistetaan erikseen.'}));
 const shapes=subjects(graph,RDF+'type',namedNode(SH+'NodeShape')).map(s=>({iri:s.termType==='NamedNode'?s.value:null,targets:values(graph,s,SH+'targetClass').map(t=>t.value),properties:values(graph,s,SH+'property').map(p=>({shape:p.termType==='NamedNode'?p.value:null,paths:values(graph,p,SH+'path').map(t=>t.value)}))})).sort((a,b)=>(a.iri||'').localeCompare(b.iri||''));
 const namespaces=[...new Set(graph.getQuads(null,null,null,null).flatMap(q=>[q.subject,q.predicate,q.object].filter(t=>t.termType==='NamedNode').map(t=>t.value.replace(/[^/#:]*$/,''))))].sort();
 return {tripleCount:graph.size,shapes,namespaces,imports,profileUri:oneOntology?.value||'',sourceVersion:versions.length===1?versions[0].value:iriVersions.length===1?iriVersions[0].value:null};
}
export async function prepareProfile(sources:SourceFile[],profileUri:string,sourceVersion:string|null):Promise<ImportedProfile>{
 await inspectFiles(sources);
 if(!absolute(profileUri)||profileUri.length>2048)fail('PROFILE_URI','/profileUri','Anna lähdeprofiilin absoluuttinen tunniste.');
 const checksum=await sha256(canonical(profileBody({profileUri,sourceVersion,sources})));
 const id=checksum.slice(0,8)+'-'+checksum.slice(8,12)+'-5'+checksum.slice(13,16)+'-a'+checksum.slice(17,20)+'-'+checksum.slice(20,32);
 return {id,profileUri,sourceVersion,sha256:checksum,sources};
}
export async function inspectProfile(profile:ImportedProfile,rootUri:string,names:GenerationSettings['names']){
 if(await sha256(canonical(profileBody(profile)))!==profile.sha256)fail('PROFILE_HASH',profile.id,'Profiilisnapshotin tarkiste ei täsmää.');
 await inspectFiles(profile.sources);
 const graph=parseSources(profile.sources),root=namedNode(rootUri),rows:Row[]=[];
 if(!graph.countQuads(root,namedNode(RDF+'type'),namedNode(SH+'NodeShape'),null))fail('ROOT_SHAPE',rootUri,'Valitse lähteessä oleva IRI-luokkamuoto.');
 const findings=preflight(graph,root),errors=findings.filter(f=>f.category!=='warning');
 if(errors.length){const first=errors[0],error=new GenerationError(first.ruleId,first.path,first.message);error.finding=first;error.findings=findings;throw error;}
 const overrides=new Map(names.map(n=>[canonical(n.semanticPath),n.fieldName])),used=new Set<string>();
 if(overrides.size!==names.length)fail('NAME_DUPLICATE',rootUri,'Saman polun nimivalinta on annettu kahdesti.');
 const one=(s:Term,p:string,required=false)=>{const list=values(graph,s,SH+p);if(list.length>1||required&&list.length!==1)fail('SHACL_AMBIGUOUS',s.termType==='BlankNode'?rootUri:s.value,'Tarvitaan yksi sh:'+p);return list[0];};
 function supported(s:Term,allowed:string[]){for(const q of graph.getQuads(s,null,null,null))if(q.predicate.value.startsWith(SH)&&!allowed.includes(q.predicate.value.slice(SH.length)))fail('SHACL_UNSUPPORTED',s.termType==='BlankNode'?rootUri:s.value,'Generointiprofiilin ulkopuolinen rajoite: '+q.predicate.value);}
 function count(t:Term|undefined,def:number|null,path:string){try{return readCount(t,def);}catch(e){const error=e as CountError;fail(error.code,path,error.message);}}
 async function visit(shape:Term,path:string[],pointer:string,ancestors:Set<string>,declared?:Term,constraints:Record<string,string|null>[]=[]):Promise<Tree>{
  const shapeKey=shape.termType+shape.value;
  if(ancestors.has(shapeKey)||path.length>DEPTH_LIMIT)fail('RECURSION',path.join(' → '),'Rekursio tai yli kahdeksan tason rakenne ei ole tuettu.');
  supported(shape,contract.nodeAllowed);
  if(one(shape,'closed')||one(shape,'ignoredProperties'))fail('BROWSER_CLOSED_UNSUPPORTED',rootUri,'Selainversion rajaus: sh:closed ja sh:ignoredProperties eivät ole tuettuja.');
  const cls=one(shape,'targetClass',!path.length)||declared;
  if(!cls||cls.termType!=='NamedNode')fail('CLASS_REQUIRED',rootUri,'Oliolle tarvitaan yksi luokka-IRI. Ratkaise tarvittava sh:node paikallisella riippuvuustiedostolla.');
  if(declared&&cls.value!==declared.value)fail('CLASS_CONFLICT',rootUri,'sh:class ja kohdemuodon luokka eroavat.');
  const props=groupProperties(graph,shape);if(!props.length)fail('EMPTY_SHAPE',shape.termType==='BlankNode'?rootUri:shape.value,'Tyhjä tai ratkaisematon sisältömuoto; liitä tarvittaessa paikallinen Turtle-riippuvuus.');
  const result:Tree={shapeUri:shape.termType==='NamedNode'?shape.value:'',classUri:cls.value,fields:[]},siblings=new Set<string>(),paths=new Set<string>();

  for(const group of props){
   const prop=group[0];for(const member of group)supported(member,contract.propertyAllowed);
   const read=(p:string,required=false)=>{const list=propertyValues(graph,group,SH+p);if(list.length>1||required&&list.length!==1)fail('SHACL_AMBIGUOUS',rootUri,'Tarvitaan yksi yhteinen sh:'+p);return list[0];};
   const predicate=one(prop,'path',true)!;
   if(predicate.termType!=='NamedNode')fail('COMPLEX_PATH',rootUri,'Vain suora ominaisuus-IRI sh:path tuetaan.');
   paths.add(predicate.value);
   const semantic=[...path,predicate.value],low=Math.max(...group.map(p=>count(one(p,'minCount'),0,predicate.value)!)),highValue=Math.min(...group.map(p=>count(one(p,'maxCount'),null,predicate.value)??Infinity)),high=highValue===Infinity?null:highValue;
   if(high!==null&&high<low)fail('CARDINALITY_CONFLICT',predicate.value,'maxCount on minCountia pienempi.');
   const datatype=read('datatype'),objClass=read('class');let node=read('node');
   if(datatype&&(node||objClass))fail('VALUE_AMBIGUOUS',predicate.value,'Kenttä ei voi olla sekä literaali että olio.');
   if(datatype&&(datatype.termType!=='NamedNode'||!contract.datatypes.some(v=>datatype.value===XSD+v)))fail('DATATYPE_UNSUPPORTED',predicate.value,'Tukematon literaalityyppi: '+datatype.value);
   if(objClass&&objClass.termType!=='NamedNode')fail('CLASS_REQUIRED',predicate.value,'sh:class tarvitsee IRI:n.');
   if(!datatype&&!node&&objClass){const candidates=subjects(graph,SH+'targetClass',objClass);if(candidates.length===1)node=candidates[0];}
   if(!datatype&&!node)fail('OBJECT_AMBIGUOUS',predicate.value,'Eksplisiittinen tuettu sh:datatype tai yksi lukittu sisäkkäinen sh:node/sh:class-muoto tarvitaan.');
   if(node&&!graph.countQuads(node,null,null,null))fail('UNRESOLVED_SHAPE',node.value,'Ratkaisematon sh:node: liitä sen sisältävä paikallinen Turtle-riippuvuus.');
   const explicit=[...new Set(propertyValues(graph,group,'http://uri.suomi.fi/datamodel/ns/iow#localName').map(t=>t.value))];
   if(explicit.length>1)fail('TECHNICAL_NAME_AMBIGUOUS',predicate.value,'Lähteen eksplisiittiset tekniset nimet eroavat.');
   const local=predicate.value.replace(/[/#]+$/,'').split(/[/#:]/).pop()!;
   let name=explicit[0]||(/^[A-Za-z][A-Za-z0-9_]*$/.test(local)?local:'field_'+(await sha256(predicate.value)).slice(0,12));
   let origin=explicit.length?'explicitSource':'iriLocalNameOrHash';const key=canonical(semantic);
   if(overrides.has(key)){name=overrides.get(key)!;used.add(key);origin='reviewedChoice';}
   if(!/^[A-Za-z][A-Za-z0-9_]*$/.test(name)||name.length>100||contract.reserved.includes(name)||name.startsWith('Class_'))fail('RESERVED_NAME',predicate.value,'Varattu tai virheellinen tekninen nimi: '+name);
   if(siblings.has(name))fail('NAME_COLLISION',predicate.value,'Nimi törmää samassa oliossa: '+name);siblings.add(name);
   const multi=high!==1,fieldPath=pointer+'/'+name+(multi?'/*':'');
   const locator=[...constraints,{nodeShapeUri:shape.termType==='NamedNode'?shape.value:null,propertyPath:predicate.value,propertyShapeUri:prop.termType==='NamedNode'?prop.value:null}];
   const row:Row={name,nameOrigin:origin,labels:propertyValues(graph,group,SH+'name').filter(t=>t.termType==='Literal').map(t=>({locale:t.termType==='Literal'?t.language||'und':'und',label:t.value})).sort((a,b)=>compare(a.locale,b.locale)||compare(a.label,b.label)),mapping:{shapeUri:rootUri,semanticPath:semantic,fieldPath,valueKind:datatype?'literal':'object',datatype:datatype?.value||null,classUri:null,minCount:low,maxCount:high,disclosure:null},multi,shacl:{nodeShapeUri:shape.termType==='NamedNode'?shape.value:null,propertyShapeUri:prop.termType==='NamedNode'?prop.value:null,propertyShapeKind:prop.termType==='NamedNode'?'iri':'blankNode',constraintPath:locator,...(group.length>1?{contributingConstraints:group.map(p=>propertyLocator(shape,p,predicate.value))}:{})}};
   rows.push(row);if(rows.length>FIELD_LIMIT)fail('FIELD_LIMIT',rootUri,'Enintään 200 kenttää.');
   if(node){row.child=await visit(node,semantic,fieldPath,new Set([...ancestors,shapeKey]),objClass,locator);row.mapping.classUri=row.child.classUri;}
   result.fields.push(row);
  }
  return result;
 }
 const tree=await visit(root,[],'',new Set());
 if([...overrides.keys()].some(k=>!used.has(k)))fail('NAME_UNKNOWN',rootUri,'Nimivalinta viittaa puuttuvaan semanttiseen polkuun.');
 return {tree,rows,findings};
}
export async function contextFor(tree:Tree):Promise<Record<string,any>>{
 const ctx:Record<string,any>={'@version':1.1,'@protected':true};ctx['Class_'+(await sha256(tree.classUri)).slice(0,12)]=tree.classUri;
 for(const row of tree.fields){const term:Record<string,any>={'@id':row.mapping.semanticPath.at(-1)};if(row.multi)term['@container']='@set';if(row.child)term['@context']=await contextFor(row.child);else term['@type']=row.mapping.datatype;ctx[row.name]=term;}return ctx;
}
export function schemaFor(tree:Tree):Record<string,any>{
 const schema:Record<string,any>={type:'object',properties:{},additionalProperties:false,required:[]};
 for(const row of tree.fields){const m=row.mapping,dt=(m.datatype||'').slice(XSD.length);let value:Record<string,any>;
  if(row.child)value=schemaFor(row.child);else{value={type:({boolean:'boolean',integer:'integer',nonNegativeInteger:'integer',positiveInteger:'integer',double:'number'} as Record<string,string>)[dt]||'string'};if(['nonNegativeInteger','positiveInteger'].includes(dt))value.minimum=dt==='positiveInteger'?1:0;if(dt==='decimal')value.pattern='^[+-]?(?:[0-9]+(?:\\.[0-9]*)?|\\.[0-9]+)$';}
  if(row.multi){value={type:'array',items:value,minItems:m.minCount};if(m.maxCount!==null)value.maxItems=m.maxCount;if(m.valueKind==='literal')value.uniqueItems=true;}
  if(row.semantic){value['x-term']=row.semantic.term;value['x-mtv-shacl']=row.semantic;}
  schema.properties[row.name]=value;if(m.minCount>0)schema.required.push(row.name);
 }return schema;
}
async function withTypes(tree:Tree,example:any):Promise<any>{const result={...example,'@type':'Class_'+(await sha256(tree.classUri)).slice(0,12)};for(const row of tree.fields)if(row.child&&row.name in result)result[row.name]=row.multi?await Promise.all(result[row.name].map((v:any)=>withTypes(row.child!,v))):await withTypes(row.child,result[row.name]);return result;}
function integrity(hex:string){return 'sha256-'+btoa(String.fromCharCode(...hex.match(/../g)!.map(v=>parseInt(v,16))));}
function plannedBase(value:string){let url:URL;try{url=new URL(value);}catch{fail('PUBLICATION_BASE','/publicationBase','Anna suunniteltu lopullinen HTTPS-perusosoite.');}if(url!.protocol!=='https:'||url!.username||url!.password||url!.search||url!.hash||url!.hostname==='jgmikael.github.io')fail('PUBLICATION_BASE','/publicationBase','HTTPS-osoite ilman tunnuksia, hakua tai fragmenttia. Demon Pages-osoitetta ei voi käyttää käyttäjäaineiston julkaisuosoitteena.');return value.replace(/\/+$/,'');}
function lexical(tree:Tree,obj:any){for(const row of tree.fields){if(!(row.name in obj))continue;for(const value of row.multi?obj[row.name]:[obj[row.name]]){if(row.child){lexical(row.child,value);continue;}const dt=row.mapping.datatype!.slice(XSD.length);if(['integer','nonNegativeInteger','positiveInteger'].includes(dt)&&!Number.isSafeInteger(value))fail('EXAMPLE_INTEGER',row.mapping.fieldPath,'Selain tukee vain tarkkoja JSON-kokonaislukuja (safe integer).');if(dt==='anyURI'&&!absolute(value))fail('EXAMPLE_URI',row.mapping.fieldPath,'Absoluuttinen URI tarvitaan.');if(dt==='date'||dt==='dateTime')fail('BROWSER_EXAMPLE_LEXICAL',row.mapping.fieldPath,'Selainversion esimerkkitarkistus ei tue vielä date/dateTime-leksikaalista avaruutta; älä muuta lähteen tyyppiä kiertääksesi rajoitusta.');}}}
export async function generate(profile:ImportedProfile,settings:GenerationSettings,metadata:{title:string;description:string;distributions:Distribution[]|null},binding:string):Promise<LocalPackage>{
 if(!settings.acceptRepresentation||!settings.acceptFormatPolicies||!settings.synthetic)fail('ACCEPTANCE_REQUIRED','/settings','Tarkasta ja hyväksy esitysvalinnat, esimerkin synteettisyys ja toimitustapojen päätökset.');
 if(!/^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$/.test(settings.mappingVersion))fail('MAPPING_VERSION','/mappingVersion','Anna mappingin versio muodossa 1.0.0.');
 if(settings.profileId!==profile.id||(metadata as any).profileSnapshotId!==profile.id)fail('PROFILE_BINDING','/profile','Valitse sama tuotu profiili tuotteelle ja generointiin.');
 const base=plannedBase(settings.publicationBase),{tree,rows}=await inspectProfile(profile,settings.rootShapeUri,settings.names),items=structuredClone(metadata.distributions||[]);
 if(items.length!==3||new Set(items.map(i=>i.type)).size!==3)fail('THREE_DISTRIBUTIONS','/distributions','Tallenna yksi JSON API-, W3C VC- ja SD-JWT VC -toimitustapa.');
 const sd=items.find(i=>i.type==='sdJwtVc')!,w3c=items.find(i=>i.type==='w3cVc')!;
 if(items.some(i=>i.availability!=='planned'))fail('BROWSER_SERVICE_SCOPE','/distributions','Selainversion paketointi tukee vain planned-toimitustapoja. Tämä ei ole toimivan palvelun metadatavalidointi.');
 for(const item of items){
  if(item.profileSnapshotId!==profile.id)fail('PROFILE_BINDING','/distributions','Kaikkien toimitustapojen on käytettävä samaa paikallista profiilisnapshotia.');
  if(item.api&&(item.api.openApiArtifactId||item.api.jsonSchemaArtifactId))fail('BROWSER_DERIVED_REFERENCE','/distributions','Selainversion tiedostotuonti ei tue ulkoisten OpenAPI-/JSON Schema -artefaktien validointia.');
  if(item.credential?.legalCategory==='QEAA')fail('QEAA_UNVERIFIED','/distributions','Selainkokeilu ei vahvista QEAA-asemaa.');
 }
 if(!w3c.w3c?.vcTypes.includes('VerifiableCredential')||!w3c.w3c.contexts.includes(contract.baseContextUrl))fail('W3C_PROFILE_REQUIRED','/distributions','W3C VC tarvitsee VCDM 2.0:n perustyypin ja kontekstin.');
 if(!sd.sdJwt?.profileVersion||!['required','optional','none'].includes(sd.sdJwt.holderBinding))fail('SDJWT_PROFILE_REQUIRED','/distributions','Täydennä nimetty SD-JWT-profiiliversio ja haltijasidontapäätös.');
 if(sd.credential?.credentialIssuer&&sd.credential.credentialIssuer===w3c.credential?.credentialIssuer&&sd.credential.configurationIds.some(id=>w3c.credential!.configurationIds.includes(id)))fail('CONFIGURATION_AMBIGUOUS','/distributions','Saman myöntäjän muodoilla on oltava erilliset credential configuration -tunnisteet.');

 if(!sd.sdJwt?.vct||!absolute(sd.sdJwt.vct)||!sd.security.profileUri||!sd.security.algorithms.length||!w3c.security.profileUri||!w3c.w3c||w3c.w3c.contentPath!=='/credentialSubject'||w3c.security.mechanism==='jose'&&!w3c.security.algorithms.length)fail('FORMAT_POLICY_REQUIRED','/distributions','Täydennä vct, W3C credentialSubject-polku, suojausprofiilit ja tarvittavat algoritmit toimitustapojen muokkauksessa.');
 const choices=new Map<string,'selective'|'always'>();
 for(const row of rows){const old=sd.mapping.entries.find(e=>canonical(e.semanticPath)===canonical(row.mapping.semanticPath))?.disclosure;const choice=sd.sdJwt.selectiveDisclosure==='always'?'selective':sd.sdJwt.selectiveDisclosure==='never'?'always':old;if(choice!=='selective'&&choice!=='always')fail('DISCLOSURE_REQUIRED',row.mapping.fieldPath,'Täydennä kenttäkohtainen paljastamispäätös tai valitse yhteinen aina/ei koskaan -käytäntö.');choices.set(canonical(row.mapping.semanticPath),choice);}
 const known=new Set(rows.flatMap(r=>[r.mapping.fieldPath,...(r.multi?[r.mapping.fieldPath.slice(0,-2)]:[])]));
 for(const p of sd.sdJwt.nonDisclosableClaims)if(!known.has(p)&&!['/iss','/sub','/aud','/jti','/iat','/exp','/nbf','/vct','/cnf','/status'].includes(p))fail('DISCLOSURE_PATH_REVIEW',p,'Tarkasta aina näkyvien väitteiden polut uutta mappingia vasten.');
 for(const row of rows){const path=row.mapping.fieldPath,choice=choices.get(canonical(row.mapping.semanticPath));if(choice==='selective'&&sd.sdJwt.nonDisclosableClaims.includes(path))fail('SDJWT_DISCLOSURE',path,'Pakollisesti näkyvä väite ei voi olla valikoivasti paljastettava.');if(choice==='always'&&rows.some(parent=>path.startsWith(parent.mapping.fieldPath+'/')&&choices.get(canonical(parent.mapping.semanticPath))==='selective'))fail('SDJWT_DISCLOSURE',path,'Aina näkyvä väite ei voi olla valikoivasti paljastettavan vanhemman alla.');}
 const source={uri:profile.profileUri,version:profile.sourceVersion,snapshotId:profile.id,snapshotSha256:profile.sha256,snapshotUrl:null};
 for(const row of rows){row.semantic={rootShapeUri:settings.rootShapeUri,semanticPath:row.mapping.semanticPath,term:row.mapping.semanticPath.at(-1),fieldPath:row.mapping.fieldPath,claimPath:row.mapping.fieldPath.slice(1).split('/').map(v=>v==='*'?null:v),sourceProfile:source,shacl:row.shacl};}
 for(const item of items)item.mapping={version:settings.mappingVersion,entries:rows.map(row=>({...row.mapping,fieldPath:(item.type==='w3cVc'?'/credentialSubject':'')+row.mapping.fieldPath,disclosure:item.type==='sdJwtVc'?choices.get(canonical(row.mapping.semanticPath))!:null}))};
 if(bytes(settings.exampleContent)>100000)fail('EXAMPLE_LIMIT','/example','Esimerkin raja on 100 kB.');
 let example:any;try{example=JSON.parse(settings.exampleContent);}catch{fail('EXAMPLE_JSON','/example','Esimerkki ei ole kelvollista JSONia.');}
 const stack:[any,number][]=[[example,0]];let nodes=0;while(stack.length){const [v,depth]=stack.pop()!;if(typeof v==='number'&&!Number.isFinite(v))fail('EXAMPLE_NUMBER','/example','JSON-luku ylittää selaimen äärellisen numeroavaruuden.');if(++nodes>2000||depth>20)fail('EXAMPLE_DEPTH','/example','JSON-esimerkin raja: 20 tasoa / 2000 arvoa.');if(v&&typeof v==='object')for(const [key,value] of Object.entries(v)){if(['__proto__','constructor','prototype'].includes(key))fail('EXAMPLE_RESERVED','/example','Varattu JSON-avain.');stack.push([value,depth+1]);}}
 const schema={$schema:'https://json-schema.org/draft/2020-12/schema',...schemaFor(tree)};
 const validate=new Ajv2020({strict:false,allErrors:false}).compile(schema);if(!validate(example))fail('EXAMPLE_SCHEMA','/example','JSON-esimerkki ei vastaa muodostettua skeemaa: '+JSON.stringify(validate.errors));lexical(tree,example);
 const packageId=await sha256(binding),prefix=base+'/id/technical-packages/'+packageId+'/',context={'@context':await contextFor(tree)};
 const subject=await withTypes(tree,example),contextUrl=prefix+'context.jsonld';
 const loader=async(url:string)=>{const document=url===contextUrl?context:url===contract.baseContextUrl?contract.baseContext:null;if(!document)throw new Error('Konteksti ei kuulu lukittuun paikalliseen dokumenttijoukkoon: '+url);return {contextUrl:null,documentUrl:url,document};};
 const rdf=await jsonld.toRDF({'@context':contextUrl,...subject},{documentLoader:loader as any,format:'application/n-quads'});
 const vc={'@context':[contract.baseContextUrl,contextUrl],type:['VerifiableCredential',...w3c.w3c!.vcTypes.filter(v=>v!=='VerifiableCredential')],issuer:'https://issuer.example.org/synthetic-unissued',description:'SYNTHETIC UNSIGNED STRUCTURE EXAMPLE — NOT ISSUED',credentialSubject:subject};
 await jsonld.toRDF(vc,{documentLoader:loader as any,format:'application/n-quads'});
 const attributes=rows.map(r=>r.semantic!),mapping:Record<string,any>={sourceSnapshotId:profile.id,sourceSnapshotSha256:profile.sha256,rootShapeUri:settings.rootShapeUri,rootClassUri:tree.classUri,distributions:items,formatPolicies:{sdJwt:sd.sdJwt,security:sd.security},attributes,catalogueReferences:[]};
 const ext={...contract.extensionDefinition,id:prefix+'semantic-extension-profile.json'},descriptor={version:ext.version,uri:ext.id,integrity:integrity(await sha256(canonical(ext)))};
 mapping.extensionProfile=descriptor;
 const mappingRef={uri:prefix+'semantic-mapping.json',integrity:integrity(await sha256(canonical(mapping)))};
 const annotatedSchema={...schema,'x-mtv-profile':descriptor,'x-mtv-mapping':mappingRef};
 const schemaRef={uri:prefix+'content.schema.json',integrity:integrity(await sha256(canonical(annotatedSchema)))};
 const claims:Record<string,any>[]=[];
 for(const row of rows){const m=row.mapping,mandatory=rows.filter(r=>r.mapping.semanticPath.every((v,i)=>v===m.semanticPath[i])&&r.mapping.semanticPath.length<=m.semanticPath.length).every(r=>r.mapping.minCount>0);claims.push({path:row.semantic!.claimPath,sd:choices.get(canonical(m.semanticPath))==='selective'?'always':'never',mandatory,display:row.labels.length?row.labels:[{locale:'und',label:row.name}],'x-mtv-semantic':row.semantic});if(row.multi)claims.push({path:row.semantic!.claimPath.slice(0,-1),sd:'never',mandatory,'x-mtv-semantic':row.semantic});}
 const typeMetadata={vct:sd.sdJwt!.vct,name:metadata.title,description:metadata.description,claims,'x-mtv-profile':descriptor,'x-mtv-mapping':mappingRef,'x-mtv-schema':schemaRef};
 const validation={turtle:'parsed',generationSupport:'checked-browser-subset',jsonSchema:'conforms',jsonLdProcessor:'jsonld.js',jsonLdExpansion:'succeeded-locked-loader',shacl:'not-run',graphComparison:'not-run-in-browser',publication:'not-published',scope:'Local synthetic descriptions only. No full SHACL validation, independent approval, issuer/signature/disclosure/holder binding or wallet test.'};
 const values:Record<string,[string,unknown]>={'context.jsonld':['application/ld+json',context],'content.schema.json':['application/schema+json',annotatedSchema],'semantic-mapping.json':['application/json',mapping],'semantic-extension-profile.json':['application/json',ext],'sd-jwt-type-metadata.json':['application/json',typeMetadata],'issuer-metadata-binding.json':['application/json',{vct:sd.sdJwt!.vct,'vct#integrity':integrity(await sha256(canonical(typeMetadata))),typeMetadataUri:prefix+'sd-jwt-type-metadata.json',scope:'PLANNED PUBLICATION; NOT A CREDENTIAL'}],'content-example.json':['application/json',example],'sd-jwt-claims-example.json':['application/json',example],'unsigned-vc-example.jsonld':['application/ld+json',vc],'example.nq':['application/n-quads',rdf],'validation.json':['application/json',validation]};
 const artifacts:LocalPackage['artifacts']={};
 for(const [index,file] of profile.sources.entries())values['source-'+index+'.ttl']=['text/turtle',file.content];
 for(const [name,[mediaType,value]] of Object.entries(values)){const content=typeof value==='string'?value:canonical(value);artifacts[name]={mediaType,content,sha256:await sha256(content),url:prefix+name};}
 const manifest={packageId,generator:GENERATOR,serverReference:contract.serverGenerator,policy:contract.policy,standards:contract.standards,standardSourcePins:contract.standardSourcePins,baseContextSha256:contract.baseContextSha256,sdSpecificationSha256:contract.sdSpecificationSha256,scope:'local experiment; planned URLs are not published or verified',inputs:{sourceProfile:source,sourceFiles:profile.sources.map(({name,sha256})=>({name,sha256})),settings,metadata,bindingSha256:packageId},artifacts:Object.fromEntries(Object.entries(artifacts).map(([name,{content:_,...rest}])=>[name,rest])),validation};
 const content=canonical(manifest);artifacts['manifest.json']={mediaType:'application/json',content,sha256:await sha256(content),url:prefix+'manifest.json'};
 return {status:'local',binding,packageId,artifacts,validation};
}
export async function execute(request:any){
 switch(request.action){
  case 'verify':{
   for(const profile of request.profiles||[]){for(const source of profile.sources)if(await sha256(source.content)!==source.sha256)fail('SOURCE_HASH',source.name,'Tuotavan lähteen tarkiste ei täsmää.');const prepared=await prepareProfile(profile.sources,profile.profileUri,profile.sourceVersion);if(prepared.sha256!==profile.sha256||prepared.id!==profile.id)fail('PROFILE_HASH',profile.id,'Tuotavan profiilin tarkiste ei täsmää.');}
   for(const pkg of request.packages||[]){if(await sha256(pkg.binding)!==pkg.packageId)fail('PACKAGE_HASH','/package','Paketin syötehash ei täsmää.');for(const [name,artifact] of Object.entries(pkg.artifacts) as [string,any][])if(await sha256(artifact.content)!==artifact.sha256)fail('ARTIFACT_HASH',name,'Tuotavan artefaktin tarkiste ei täsmää.');const manifest=JSON.parse(pkg.artifacts['manifest.json'].content);if(manifest.packageId!==pkg.packageId)fail('PACKAGE_HASH','/manifest','Manifestin pakettitunniste ei täsmää.');for(const [name,entry] of Object.entries(manifest.artifacts) as [string,any][]){if(pkg.artifacts[name]?.sha256!==entry.sha256)fail('ARTIFACT_HASH',name,'Manifestin artefaktiviite ei täsmää.');}}return true;
  }
  case 'inspect':return inspectFiles(request.sources);
  case 'prepare':return prepareProfile(request.sources,request.profileUri,request.sourceVersion);
  case 'proposal':return inspectProfile(request.profile,request.settings.rootShapeUri,request.settings.names);
  case 'generate':return generate(request.profile,request.settings,request.metadata,generationBinding(request.profile,request.metadata,request.settings));
  default:throw new Error('Tuntematon toiminto.');
 }
}
