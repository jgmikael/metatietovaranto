import React,{useEffect,useRef,useState} from 'react';
import {runWorker} from './browserGeneration/client';
import {type ImportedProfile,type RepairChange} from './browserGeneration/model';
import {downloadLocal} from './localDownload';
type Proposals={ruleId:string;version:string;changes:RepairChange[];skipped:{sourceName:string;line:number;reason:string}[]};
type Props={profile:ImportedProfile;enabled:boolean;disabled:boolean;selected:string[];onSelection:(ids:string[])=>void;onStore:(profile:ImportedProfile)=>void;onUse:(profile:ImportedProfile)=>void};
export function LocalRepair({profile,enabled,disabled,selected,onSelection,onStore,onUse}:Props){
 const [proposals,setProposals]=useState<Proposals|null>(null),[created,setCreated]=useState<ImportedProfile|null>(null),[error,setError]=useState(''),[busy,setBusy]=useState(false);
 const controller=useRef<AbortController|null>(null),mounted=useRef(true);
 useEffect(()=>()=>{mounted.current=false;controller.current?.abort();},[]);
 async function run<T,>(request:unknown,done:(value:T)=>void){setBusy(true);setError('');controller.current=new AbortController();try{const value=await runWorker<T>(request,controller.current.signal);if(mounted.current)done(value);}catch(e){if(mounted.current)setError((e as Error).message);}finally{if(mounted.current)setBusy(false);}}
 const original=profile.repair?.originalSources||profile.sources;
 function select(ids:string[]){setCreated(null);onSelection(ids);}
 return <section aria-label="SHACL-tuonnin paikallinen korjaus"><h3>Käyttäjän hyväksymä tuontikorjaus</h3>
 <p>Vain tunnetun tietotyyppi-URI:n merkkijonoliteraali voidaan muuttaa sh:datatype-objektina IRI:ksi. Korjaus ei muuta tietotyyppiä, polkua, kardinaliteettia tai OWL-arvoaluetta. Se ei ole SHACL-validointi tai alustan varmennus.</p>
 {original.map((file,i)=><p key={i}>Alkuperäinen: {file.name} · SHA-256 <code>{file.sha256}</code> <button className="text-link" onClick={()=>downloadLocal(file.content,file.name,'text/turtle')}>Lataa alkuperäinen Turtle {i+1}</button></p>)}
 {profile.repair?<><p><strong>Metatietovarannossa korjattu paikallinen kopio – ei alkuperäinen export</strong></p><p>Generoinnin valittu aineisto: korjattu kopio. Sääntö {profile.repair.ruleId} / {profile.repair.version}, {profile.repair.changes.length} käyttäjän hyväksymää muutosta. Hyväksyntä on paikallinen tapahtumatieto, ei allekirjoitus tai riippumaton hyväksyntä.</p>
 {profile.sources.map((file,i)=><p key={i}>Korjattu: {file.name} · SHA-256 <code>{file.sha256}</code> <button className="text-link" onClick={()=>downloadLocal(file.content,'korjattu-'+file.name,'text/turtle')}>Lataa korjattu Turtle {i+1}</button></p>)}
 <button onClick={()=>downloadLocal(JSON.stringify(profile.repair,null,2),'tuontikorjausraportti.json')}>Lataa korjausraportti</button>
 <button disabled={disabled||busy} onClick={()=>void run<ImportedProfile>({action:'prepare',sources:original,profileUri:profile.profileUri,sourceVersion:profile.sourceVersion},onUse)}>Käytä alkuperäistä aineistoa generoinnissa</button></>:<><p>Generoinnin valittu aineisto: alkuperäinen. Alkuperäistä ei muuteta.</p>
 <button disabled={disabled||busy||!enabled&&!proposals} onClick={()=>void run<Proposals>({action:'repair-proposals',profile},setProposals)}>Tarkastele ehdotettuja tuontikorjauksia</button>
 {!enabled&&!proposals&&<p>Tarkista ensin generointituki. DATATYPE_TERM-havainto avaa korjausehdotusten tarkastelun.</p>}
 {proposals&&<><p>Sääntö {proposals.ruleId} / {proposals.version}. {proposals.changes.length} ehdotusta koko lähdeaineistosta, ei vain valitusta juurimuodosta. Valinnat vanhentavat aiemman paikallisen paketin ja tyhjentävät hyväksynnät.</p>
 <button disabled={disabled||busy} onClick={()=>select(proposals.changes.map(c=>c.id))}>Valitse kaikki ehdotetut korjaukset</button><button disabled={disabled||busy} onClick={()=>select([])}>Tyhjennä korjausvalinnat</button>
 {proposals.changes.map((c,i)=><fieldset key={c.id} disabled={disabled||busy}><legend>Korjausehdotus {i+1}: {c.sourceName}, rivi {c.line}</legend>
 <label className="check"><input type="checkbox" checked={selected.includes(c.id)} onChange={e=>select(e.target.checked?[...selected,c.id]:selected.filter(id=>id!==c.id))}/>Hyväksyn korjauksen {i+1}</label>
 <p>PropertyShape: <code>{c.propertyShapeUri||'nimetön solmu (lähdealue yksilöi paikallisen kohdan)'}</code><br/>Luokkamuodot: {c.nodeShapes.join(', ')||'ei suoraa sh:property-viitettä'}<br/>sh:path: {c.paths.join(', ')||'puuttuu'}</p>
 <p>Alkuperäinen objekti: <code>{c.before}</code> · Literal<br/>Ehdotettu objekti: <code>{c.after}</code> · NamedNode</p>
 <p>Perustelu: sh:datatype tarvitsee IRI:n. Havaittu kielimerkitön xsd:string-literaali sisältää korjauslistaan kuuluvan absoluuttisen tietotyyppi-IRI:n. {c.limitation}</p></fieldset>)}
 {proposals.skipped.length>0&&<details><summary>Käsin tarkastettavat arvot ({proposals.skipped.length})</summary><ul>{proposals.skipped.map((s,i)=><li key={i}>{s.sourceName}, rivi {s.line}: {s.reason}</li>)}</ul></details>}
 <button disabled={disabled||busy||!selected.length} onClick={()=>void run<ImportedProfile>({action:'apply-repairs',profile,selected},value=>{onStore(value);setCreated(value);})}>Luo korjattu paikallinen kopio</button>
 <button className="secondary" disabled={busy} onClick={()=>{select([]);setProposals(null);}}>Hylkää korjausehdotukset</button></>}
 {created&&<div role="status"><p>Korjattu kopio luotu ja tallennettu paikalliseen kokeiluun. Alkuperäinen on edelleen generoinnin aineistona.</p><button disabled={disabled||busy} onClick={()=>onUse(created)}>Käytä korjattua kopiota generoinnissa ja tarkista tuki</button></div>}
 </>}
 {busy&&<p role="status">Tarkistetaan paikallisesti Workerissa… <button onClick={()=>controller.current?.abort()}>Keskeytä korjaus</button></p>}{error&&<p role="alert">{error}</p>}
 </section>;
}
