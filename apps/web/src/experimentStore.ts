/** Versioned, bounded metadata only. No network, content evaluation or server identity. */
import type {Input,Item,Org} from './types';
import {metadataFields as textFields} from './types';
import type {Catalogue} from './dataSource';
export const STORE_KEY='fi.metatietovaranto.pages.own-experiment.v1';
export const FORMAT='fi.metatietovaranto.own-experiment';
export const MAX_BYTES=2*1024*1024;
export type LocalMetadata=Pick<Input,typeof textFields[number][0]|'providerOrganizationId'|'distributions'|'primaryDistributionId'|'profileSnapshotId'|'synthetic'|'availability'>;
export type LocalProduct={id:string;metadata:LocalMetadata;profileReference:{snapshotId:string;sha256:string}|null;originalPackageReference:{productId:string;version:string;packageId:string;sha256:string}|null};
export type Workspace={format:typeof FORMAT;schemaVersion:1;synthetic:true;sourceDemoVersion:string;products:LocalProduct[];organizations:Org[]};
type Rule=(value:unknown,path:string)=>void;
const invalid=(path:string,message:string):never=>{throw new Error(path+': '+message);};
const str=(max:number):Rule=>(value,path)=>{if(typeof value!=='string'||value.length>max)invalid(path,`Tekstin enimmäispituus on ${max}.`);};
const choice=(...values:unknown[]):Rule=>(value,path)=>{if(!values.includes(value))invalid(path,'Tuntematon tai puuttuva arvo.');};
const nullable=(rule:Rule):Rule=>(value,path)=>{if(value!==null)rule(value,path);};
const optional=(rule:Rule):Rule=>(value,path)=>{if(value!==undefined)rule(value,path);};
const arr=(max:number,rule:Rule):Rule=>(value,path)=>{if(!Array.isArray(value)||value.length>max)invalid(path,`Listalla saa olla enintään ${max} alkiota.`);(value as unknown[]).forEach((v,i)=>rule(v,path+'/'+i));};
const obj=(shape:Record<string,Rule>):Rule=>(value,path)=>{
 if(!value||typeof value!=='object'||Array.isArray(value))invalid(path,'Objekti puuttuu.');
 const row=value as Record<string,unknown>;
 for(const key of Object.keys(row))if(!Object.hasOwn(shape,key)||['__proto__','prototype','constructor'].includes(key))invalid(path+'/'+key,'Tuntematon kenttä.');
 for(const [key,rule] of Object.entries(shape))rule(row[key],path+'/'+key);
};
const id:Rule=(value,path)=>{if(typeof value!=='string'||!/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i.test(value))invalid(path,'UUID-tunniste tarvitaan.');};
const hash:Rule=(value,path)=>{if(typeof value!=='string'||!/^[0-9a-f]{64}$/.test(value))invalid(path,'SHA-256-tarkiste tarvitaan.');};
const count:Rule=(value,path)=>{if(!Number.isInteger(value)||Number(value)<0||Number(value)>1000000)invalid(path,'Luvun tulee olla kokonaisluku 0–1000000.');};
const iri=str(2048),strings=(max=50,length=2048)=>arr(max,str(length));
const entry=obj({shapeUri:iri,semanticPath:strings(10),fieldPath:str(1000),valueKind:choice('literal','object'),datatype:nullable(iri),classUri:nullable(iri),minCount:count,maxCount:nullable(count),disclosure:optional(nullable(choice('selective','always')))});
const wallet=obj({profile:str(200),version:str(100),status:choice('planned','declared','tested','incompatible'),evidence:optional(nullable(iri)),testedAt:optional(nullable(str(100)))});
const credential=obj({issuerOrganizationId:nullable(id),credentialIssuer:nullable(iri),initiationUrl:nullable(iri),protocol:choice('OpenID4VCI'),protocolVersion:choice('1.0'),configurationIds:strings(),validityProfile:nullable(iri),statusProfile:nullable(iri),subjectTypes:strings(10,100),representationRequirements:str(2000),walletCompatibility:arr(20,wallet),legalCategory:choice('unassessed','nonQualified','publicSectorAttestation','QEAA'),qualificationEvidence:str(5000),fee:str(300),support:str(1000)});
const distribution=obj({id,type:choice('jsonApi','w3cVc','sdJwtVc'),format:choice('application/json','application/vc+ld+json','application/dc+sd-jwt'),availability:choice('planned','sandbox','production','suspended'),environment:choice('sandbox','production'),providerOrganizationId:id,operatorOrganizationId:id,sourceProviderOrganizationId:id,profileSnapshotId:nullable(id),mapping:obj({version:str(100),entries:arr(200,entry)}),security:obj({mechanism:choice('tls','dataIntegrity','jose','sdJwt'),profileUri:nullable(iri),algorithms:strings(20,100)}),protocol:optional(choice('httpsRest')),
 api:optional(obj({serviceUrl:nullable(iri),descriptionUrl:nullable(iri),openApiArtifactId:nullable(id),jsonSchemaArtifactId:nullable(id),authentication:choice('none','oauth2','apiKey','mtls'),requiredRights:strings(100,200),freshness:str(2000)})),credential:optional(credential),w3c:optional(obj({vcdmVersion:choice('2.0'),vcTypes:strings(20),contexts:strings(20),contentPath:str(1000)})),sdJwt:optional(obj({vct:nullable(iri),profileVersion:str(100),selectiveDisclosure:choice('perClaim','always','never'),holderBinding:choice('required','optional','none'),nonDisclosableClaims:strings(200,1000)}))});
const metadata=obj({...Object.fromEntries(textFields.map(([key,,max])=>[key,str(max)])),providerOrganizationId:id,distributions:nullable(arr(10,distribution)),primaryDistributionId:nullable(id),profileSnapshotId:nullable(id),synthetic:choice(true),availability:choice('planned','sandbox')});
const organization=obj({id,legalName:str(200),country:str(2),synthetic:choice(true),identifiers:arr(20,obj({scheme:str(200),value:str(200)}))});
const product=obj({id,metadata,profileReference:nullable(obj({snapshotId:id,sha256:hash})),originalPackageReference:nullable(obj({productId:id,version:str(100),packageId:hash,sha256:hash}))});
const workspaceShape=obj({format:choice(FORMAT),schemaVersion:choice(1),synthetic:choice(true),sourceDemoVersion:str(100),products:arr(100,product),organizations:arr(50,organization)});
function unique(values:string[],path:string){if(new Set(values.map(v=>v.toLowerCase())).size!==values.length)invalid(path,'Tunnisteet eivät ole yksilöllisiä.');}
export function orgReferences(product:LocalProduct){return [product.metadata.providerOrganizationId,...(product.metadata.distributions||[]).flatMap(d=>[d.providerOrganizationId,d.operatorOrganizationId,d.sourceProviderOrganizationId,...(d.credential?.issuerOrganizationId?[d.credential.issuerOrganizationId]:[])])];}
export function validateWorkspace(value:unknown):Workspace{
 workspaceShape(value,'kokeilu');const data=value as Workspace;
 if(!data.sourceDemoVersion.trim())invalid('sourceDemoVersion','Lähtöaineiston versiotunniste puuttuu.');
 unique(data.products.map(p=>p.id),'tuotteet');unique(data.organizations.map(o=>o.id),'organisaatiot');
 const orgs=new Set(data.organizations.map(o=>o.id));
 for(const p of data.products){
  if(orgReferences(p).some(ref=>!orgs.has(ref)))invalid(p.id,'Organisaatioviittaus puuttuu.');
  if((p.profileReference?.snapshotId||null)!==p.metadata.profileSnapshotId)invalid(p.id,'Profiiliviittaukset ovat ristiriidassa.');
  const distributions=p.metadata.distributions||[];unique(distributions.map(d=>d.id),p.id+'/toimitustavat');
  if(p.metadata.primaryDistributionId&&!distributions.some(d=>d.id===p.metadata.primaryDistributionId))invalid(p.id,'Ensisijainen toimitustapa puuttuu.');
  for(const d of distributions){
   if(d.profileSnapshotId!==p.metadata.profileSnapshotId)invalid(p.id,'Toimitustavan profiiliviittaus poikkeaa tuotteesta.');
   const format={jsonApi:'application/json',w3cVc:'application/vc+ld+json',sdJwtVc:'application/dc+sd-jwt'}[d.type];
   if(d.format!==format||d.type==='jsonApi'&&(!d.api||d.credential||d.w3c||d.sdJwt)||d.type==='w3cVc'&&(!d.credential||!d.w3c||d.api||d.sdJwt)||d.type==='sdJwtVc'&&(!d.credential||!d.sdJwt||d.api||d.w3c))invalid(p.id,'Toimitustavan tyyppi ja rakenne ovat ristiriidassa.');
  }
 }
 if(new TextEncoder().encode(JSON.stringify(data)).length>MAX_BYTES-512)invalid('kokeilu','Aineisto ylittää 2 MiB:n kokorajan.');
 return data;
}
export function seedWorkspace(catalogue:Catalogue):Workspace{
 const products=catalogue.items.map((item:Item):LocalProduct=>({id:item.id,metadata:{...Object.fromEntries(textFields.map(([key])=>[key,item[key]])) as Pick<LocalMetadata,typeof textFields[number][0]>,providerOrganizationId:item.providerOrganizationId,distributions:structuredClone(item.distributions),primaryDistributionId:item.primaryDistributionId,profileSnapshotId:item.profileSnapshotId,synthetic:true,availability:item.availability},profileReference:item.profileSnapshotId?{snapshotId:item.profileSnapshotId,sha256:catalogue.profiles.find(p=>p.id===item.profileSnapshotId)!.sha256}:null,originalPackageReference:item.technicalPackage?{productId:item.id,version:item.version!,packageId:item.technicalPackage.packageId!,sha256:item.technicalPackage.sha256!}:null}));
 return validateWorkspace({format:FORMAT,schemaVersion:1,synthetic:true,sourceDemoVersion:catalogue.version,products,organizations:catalogue.organizations.map(({id,legalName,country,identifiers})=>({id,legalName,country,identifiers:structuredClone(identifiers),synthetic:true}))});
}
export function parseTransfer(text:string):Workspace{
 if(new TextEncoder().encode(text).length>MAX_BYTES)throw new Error('Tiedoston enimmäiskoko on 2 MiB.');
 let value:unknown;try{value=JSON.parse(text);}catch{throw new Error('Tiedosto ei ole kelvollista JSONia.');}
 if(!value||typeof value!=='object'||Array.isArray(value))throw new Error('Siirtoformaatti puuttuu.');
 const {exportedAt,...data}=value as Record<string,unknown>;
 if(typeof exportedAt!=='string'||exportedAt.length>100||!/^\d{4}-\d{2}-\d{2}T/.test(exportedAt)||!Number.isFinite(Date.parse(exportedAt)))throw new Error('Viennin ajankohta puuttuu.');
 return validateWorkspace(data);
}
export function transfer(data:Workspace){return JSON.stringify({...validateWorkspace(data),exportedAt:new Date().toISOString()});}
export function readWorkspace(){
 const raw=localStorage.getItem(STORE_KEY);
 if(raw===null)return {raw,data:null};
 return {raw,data:parseStored(raw)};
}
export function parseStored(raw:string){
 if(new TextEncoder().encode(raw).length>MAX_BYTES+200)throw new Error('Paikallinen tallenne ylittää kokorajan.');
 const stored=JSON.parse(raw);obj({storageVersion:choice(1),revision:id,data:workspaceShape})(stored,'tallenne');
 return validateWorkspace(stored.data);
}
export class StorageConflict extends Error{}
export async function persist(data:Workspace,expected:string|null):Promise<string>{
 if(!navigator.locks)throw new Error('Selain ei tue turvallista välilehtilukitusta. Vie JSON-varmuuskopio ja käytä uudempaa selainta.');
 return navigator.locks.request(STORE_KEY,()=>{
  if(localStorage.getItem(STORE_KEY)!==expected)throw new StorageConflict('Kokeilu muuttui toisessa välilehdessä. Vie muistissa olevat muutokset JSONiksi ja avaa tallennettu kokeilu uudelleen.');
  const raw=JSON.stringify({storageVersion:1,revision:crypto.randomUUID(),data:validateWorkspace(data)});
  localStorage.setItem(STORE_KEY,raw);
  if(localStorage.getItem(STORE_KEY)!==raw)throw new StorageConflict('Tallennuksen tarkistus epäonnistui.');
  return raw;
 });
}
