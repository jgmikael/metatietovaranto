/** Read-only adapter for the shared UI. Server writes/auth remain in main.tsx. */
import type {Item,Org,Profile} from './types';
import type {Lifecycle} from './Lifecycle';
export const pagesMode=import.meta.env.MODE==='pages';
export type Snapshot=Profile&{manifest:{sourceArtifacts:{id:string;serialization:string;content:string}[]}};
export type Catalogue={version:string;items:Item[];organizations:Org[];profiles:Snapshot[];resources:Record<string,string>};
let catalogue:Catalogue|undefined;
let pending:Promise<Catalogue>|undefined;
export function loadCatalogue(){
 return pending??=(async()=>{
  const response=await fetch(import.meta.env.BASE_URL+'demo/catalog.json');
  if(!response.ok)throw new Error('Esittelyaineistoa ei voitu lukea.');
  catalogue=await response.json() as Catalogue;return catalogue;
 })();
}
export function resourceUrl(path:string){
 if(!pagesMode)return path;
 if(!catalogue)return undefined;
 const resource=catalogue.resources[path];
 if(!resource)throw new Error('Staattinen lataus puuttuu: '+path);
 return import.meta.env.BASE_URL+resource;
}
export async function staticRequest<T>(path:string,options:RequestInit={}):Promise<T>{
 if(options.method&&options.method!=='GET')throw new Error('Esittelydemo on vain lukua varten.');
 const data=await loadCatalogue(),url=new URL(path,'https://static.invalid'),parts=url.pathname.split('/').filter(Boolean);
 let result:unknown;
 if(url.pathname==='/api/v1/products'){
  const text=(value:string)=>value.toLocaleLowerCase('fi');
  const match=(value:string,key:string)=>text(value).includes(text(url.searchParams.get(key)||''));
  const state=url.searchParams.get('lifecycleStatus')||'current';
  const found=data.items.filter(item=>match([item.title,item.description,item.provider,item.theme].join(' '),'q')&&match(item.theme,'theme')&&match(item.provider,'provider')&&(['current','all','published'].includes(state)));
  const offset=Number(url.searchParams.get('offset')||0),limit=Number(url.searchParams.get('limit')||20);
  result={items:found.slice(offset,offset+limit),total:found.length};
 }else if(parts[2]==='organizations'){
  result=parts.length===3?{items:data.organizations}:data.organizations.find(item=>item.id===parts[3]);
 }else if(parts[2]==='profile-snapshots'){
  result=parts.length===3?{items:data.profiles}:data.profiles.find(item=>item.id===parts[3]);
 }else if(parts[2]==='products'){
  const item=data.items.find(item=>item.id===parts[3]);
  if(item){
   const lifecycle=item.lifecycle as Lifecycle;
   if(parts.length===4)result=item;
   else if(parts[4]==='versions'){
    if(parts.length===5)result={items:[{version:item.version,sequence:1,sha256:item.contentHash,lifecycle}]};
    else if(parts[5]===item.version)result=parts[6]==='lifecycle'?lifecycle:item;
   }
  }
 }
 if(result===undefined)throw new Error('Sivua ei ole julkisessa esittelyaineistossa. Ylläpito kuuluu palvelinsovellukseen.');
 return structuredClone(result) as T;
}
