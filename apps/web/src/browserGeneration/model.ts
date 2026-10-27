import contract from './contract.json';
export const BROWSER_GENERATOR='browser-technical-package/1.0.3';
/** Local, untrusted files and derived descriptions. Never an application publication. */
export const FILE_LIMIT=256*1024,TRIPLE_LIMIT=10000,FIELD_LIMIT=200,DEPTH_LIMIT=8;
export const WORKER_LIMIT_MS=15000;
export type SourceFile={name:string;content:string;sha256:string};
export type RepairChange={id:string;sourceIndex:number;sourceName:string;line:number;start:number;end:number;propertyShapeUri:string|null;nodeShapes:string[];paths:string[];before:string;after:string;datatypeIri:string;limitation:string};
export type RepairReport={ruleId:string;version:string;approved:true;originalProfileSha256:string;originalSources:SourceFile[];correctedSourceHashes:string[];changes:RepairChange[]};
export type ImportedProfile={id:string;profileUri:string;sourceVersion:string|null;sha256:string;sources:SourceFile[];repair?:RepairReport};
export type NameChoice={semanticPath:string[];fieldName:string};
export type GenerationSettings={profileId:string;rootShapeUri:string;names:NameChoice[];mappingVersion:string;publicationBase:string;exampleContent:string;acceptRepresentation:boolean;acceptFormatPolicies:boolean;synthetic:boolean;repairSelection?:string[]};
export type Artifact={mediaType:string;sha256:string;content:string;url:string};
export type LocalPackage={status:'local';binding:string;packageId:string;artifacts:Record<string,Artifact>;validation:Record<string,string>};
export type GenerationState=GenerationSettings&{package?:LocalPackage};
export type Finding={ruleId:string;path:string;message:string;category?:'sourceError'|'generatorLimit'|'resourceLimit'|'warning';rootShapeUri?:string;nodeShapeUri?:string|null;predicate?:string;observed?:{value:string;termType:string;datatype?:string;language?:string};owlRanges?:{value:string;termType:string;datatype?:string;sources?:string[]}[];expected?:string;suggestion?:string;propertyShapes?:{uri:string|null;kind:string;labels:string[];sources:string[];localIndex:number}[]};
export type Mapping={shapeUri:string;semanticPath:string[];fieldPath:string;valueKind:'literal'|'object';datatype:string|null;classUri:string|null;minCount:number;maxCount:number|null;disclosure:null|'selective'|'always'};
export type Row={name:string;nameOrigin:string;labels:{locale:string;label:string}[];mapping:Mapping;multi:boolean;shacl:{nodeShapeUri:string|null;propertyShapeUri:string|null;propertyShapeKind:string;constraintPath:Record<string,string|null>[];contributingConstraints?:Record<string,string|null>[]};child?:Tree;semantic?:Record<string,any>};
export type Tree={shapeUri:string;classUri:string;fields:Row[]};
export function canonical(value:unknown):string {
 if(Array.isArray(value))return '['+value.map(canonical).join(',')+']';
 if(value&&typeof value==='object')return '{'+Object.keys(value).sort().map(key=>JSON.stringify(key)+':'+canonical((value as Record<string,unknown>)[key])).join(',')+'}';
 return JSON.stringify(value);
}
export async function sha256(value:string){return [...new Uint8Array(await crypto.subtle.digest('SHA-256',new TextEncoder().encode(value)))].map(v=>v.toString(16).padStart(2,'0')).join('');}
export const bytes=(s:string)=>new TextEncoder().encode(s).length;
export function profileBody(profile:Pick<ImportedProfile,'profileUri'|'sourceVersion'|'sources'|'repair'>){return {profileUri:profile.profileUri,sourceVersion:profile.sourceVersion,sources:profile.sources.map(({sha256})=>({sha256})),...(profile.repair?{repair:{...profile.repair,originalSources:profile.repair.originalSources.map(({name,sha256})=>({name,sha256}))}}:{})};}
export function generationBinding(profile:ImportedProfile,metadata:unknown,settings:GenerationSettings){
 const {profileId,rootShapeUri,names,mappingVersion,publicationBase,exampleContent,repairSelection}=settings;
 return canonical({generator:BROWSER_GENERATOR,contractSha256:contract.sha256,profileSha256:profile.sha256,metadata,settings:{profileId,rootShapeUri,names,mappingVersion,publicationBase,exampleContent,...(repairSelection?{repairSelection}:{})}});
}
