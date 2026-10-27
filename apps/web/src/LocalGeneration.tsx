import {SourceFindings} from './SourceFindings';
import {HelpLabel,TopicHelp} from './help/Help';
import React,{useEffect,useRef,useState} from 'react';
import {BrowserGenerationError,runWorker} from './browserGeneration/client';
import {FILE_LIMIT,WORKER_LIMIT_MS,bytes,sha256,generationBinding,type SourceFile,type ImportedProfile,type GenerationSettings,type LocalPackage,type Row,type Finding} from './browserGeneration/model';
import type {LocalProduct} from './experimentStore';
export function downloadLocal(content:string,name:string,mediaType='application/json'){
 const url=URL.createObjectURL(new Blob([content],{type:mediaType})),link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
export function settingsFor(profileId:string):GenerationSettings{return {profileId,rootShapeUri:'',names:[],mappingVersion:'1.0.0',publicationBase:'',exampleContent:'',acceptRepresentation:false,acceptFormatPolicies:false,synthetic:false};}
type Props={product:LocalProduct;profiles:ImportedProfile[];disabled:boolean;onProfile:(profile:ImportedProfile)=>void;onSettings:(settings:GenerationSettings)=>void;onPackage:(value:LocalPackage)=>void};
export function LocalGeneration({product,profiles,disabled,onProfile,onSettings,onPackage}:Props){
 const [sources,setSources]=useState<SourceFile[]>([]),[inspection,setInspection]=useState<any>(null),[uri,setUri]=useState(''),[version,setVersion]=useState(''),[proposal,setProposal]=useState<{rows:Row[]}|null>(null),[busy,setBusy]=useState(false),[error,setError]=useState(''),[notice,setNotice]=useState(''),[findings,setFindings]=useState<Finding[]>([]);
 const feedbackRef=useRef<HTMLDivElement|null>(null);
 const controller=useRef<AbortController|null>(null),mounted=useRef(true),fingerprint=useRef('');
 const settings=product.generation,profile=profiles.find(p=>p.id===settings?.profileId),pkg=settings?.package;
 const binding=profile&&settings?generationBinding(profile,product.metadata,settings):'';fingerprint.current=binding;
 const stale=!!pkg&&pkg.binding!==binding;
 useEffect(()=>()=>{mounted.current=false;controller.current?.abort();},[]);
 useEffect(()=>{setProposal(null);setFindings([]);},[profile?.sha256,settings?.rootShapeUri]);
 useEffect(()=>{if(error){feedbackRef.current?.focus({preventScroll:true});feedbackRef.current?.scrollIntoView({block:'start'});}},[error]);
 async function run<T,>(request:unknown,done:(value:T)=>void){
  setBusy(true);setError('');setNotice('');setFindings([]);const abort=new AbortController();controller.current=abort;const before=fingerprint.current;
  try{const result=await runWorker<T>(request,abort.signal);if(!mounted.current)return;if(before!==fingerprint.current)throw new Error('Syötteet muuttuivat suorituksen aikana. Muodosta tulos uudelleen.');done(result);}
  catch(e){if(mounted.current){setError((e as Error).message);if(e instanceof BrowserGenerationError)setFindings(e.findings);}}
  finally{if(mounted.current){setBusy(false);controller.current=null;}}
 }
 async function readFiles(files:File[],dependency:boolean){
  setError('');setNotice('');setFindings([]);if(!files.length)return;
  try{
   if(files.reduce((n,f)=>n+f.size,dependency?sources.reduce((n,s)=>n+bytes(s.content),0):0)>FILE_LIMIT||(dependency?sources.length:0)+files.length>10)throw new Error('Turtle-lähteiden yhteisraja on 256 KiB ja 10 tiedostoa.');
   const loaded=await Promise.all(files.map(async file=>{if(file.name.length>200)throw new Error('Tiedostonimen enimmäispituus on 200.');const content=new TextDecoder('utf-8',{fatal:true,ignoreBOM:true}).decode(await file.arrayBuffer());return {name:file.name,content,sha256:await sha256(content)};}));
   const next=dependency?[...sources,...loaded]:loaded;setInspection(null);setSources(next);
   await run<any>({action:'inspect',sources:next},result=>{setInspection(result);if(!dependency){setUri(result.profileUri);setVersion(result.sourceVersion||'');}});
  }catch(e){setError((e as Error).message);}
 }
 function update(patch:Partial<GenerationSettings>){setFindings([]);setError('');setNotice('');if(settings)onSettings({...settings,...patch,...('names' in patch||'rootShapeUri' in patch?{acceptRepresentation:false}:{})});}
 const feedback=<div ref={feedbackRef} tabIndex={-1} className="generation-feedback">
 {error&&<div role="alert">{findings.length>0&&<strong>Generointi estetty: {findings.filter(f=>f.category!=='warning').length} estävää havaintoa.</strong>}<p>{error}</p></div>}
 {busy&&<p>Käsitellään paikallisesti…</p>}{notice&&<p role="status">{notice}</p>}
 {!!findings.length&&<SourceFindings findings={findings}/>}
 </div>;
 return <section aria-label="Paikallinen SHACL-generointi"><h2>Tuo SHACL-profiili ja muodosta paikallinen paketti</h2>
 <p>Tuo Tietomallit-työkalusta ladattu Turtle-tiedosto. Generointi tukee rajattua SHACL-profiilia. Paketti tukee toteutustyötä; se ei myönnä tai allekirjoita todistuksia.</p>
 <p>Vain paikalliset UTF-8 Turtle-tiedostot. Ei verkkolinkkien tuontia tai riippuvuuksien noutoa. Raja yhteensä 256 KiB / 10 000 kolmikkoa, syvyys 8, kenttiä 200, aikaraja {WORKER_LIMIT_MS/1000} s. Selain ei tee täydellistä SHACL-validointia.</p>
 <fieldset disabled={disabled||busy}><legend>Tuo SHACL-profiili</legend>
 <HelpLabel>SHACL Turtle -tiedosto<input type="file" accept=".ttl,text/turtle" onChange={e=>{const files=[...e.target.files||[]];e.currentTarget.value='';void readFiles(files,false);}}/></HelpLabel>
 <HelpLabel>Paikalliset Turtle-riippuvuudet<input type="file" multiple accept=".ttl,text/turtle" disabled={!sources.length||disabled||busy} onChange={e=>{const files=[...e.target.files||[]];e.currentTarget.value='';void readFiles(files,true);}}/></HelpLabel>
 {!!sources.length&&<><ul>{sources.map((source,i)=><li key={i}>{source.name} · SHA-256 <code>{source.sha256}</code><button type="button" className="secondary" onClick={()=>downloadLocal(source.content,source.name,'text/turtle')}>Lataa muuttumaton lähde {i+1}</button></li>)}</ul><button className="secondary" onClick={()=>{setSources([]);setInspection(null);}}>Tyhjennä tuontivalinta</button></>}
 {inspection&&sources.length>0&&<><p>Turtle jäsennetty: {inspection.tripleCount} kolmikkoa. Tämä ei ole SHACL-validointi tai generointituen hyväksyntä.</p><details open><summary>Löydetyt luokkamuodot ja ominaisuudet</summary>{inspection.shapes.map((shape:any,i:number)=><div key={i}><code>{shape.iri||'(nimetön muoto)'}</code><p>Kohdeluokat: {shape.targets.join(', ')}</p><ul>{shape.properties.map((p:any,j:number)=><li key={j}>{p.shape||'(nimetön PropertyShape)'} → {p.paths.join(', ')}{p.datatypes?.map((t:any,k:number)=><small key={k}>sh:datatype: {t.value} · {t.termType}{t.datatype&&<> · literaalitermin oma tietotyyppi: {t.datatype}</>}{t.language&&<> · kieli: {t.language}</>}</small>)}{p.owlRanges?.map((t:any,k:number)=><small key={k}>OWL rdfs:range: {t.value} · {t.termType}</small>)}</li>)}</ul></div>)}</details><details><summary>Nimiavaruudet ja riippuvuusviitteet</summary><ul>{inspection.namespaces.map((ns:string)=><li key={ns}><code>{ns}</code></li>)}</ul><ul>{inspection.imports.map((d:any,i:number)=><li key={i}><code>{d.uri}</code> · {d.resolved?'IRI:stä on paikallisia lauseita (ei täydellisyysväitettä)':'ulkoinen / ei noudettu'} · {d.scope}</li>)}</ul></details>
 <HelpLabel>Lähdeprofiilin tunniste<input value={uri} maxLength={2048} onChange={e=>setUri(e.target.value)}/></HelpLabel><HelpLabel>Lähdeprofiilin versio (jos tiedossa)<input maxLength={200} value={version} onChange={e=>setVersion(e.target.value)}/></HelpLabel><p>Lähdeilmoitus on käyttäjän ilmoitus. Tiedostoa ei ole varmennettu Yhteentoimivuusalustalta.</p>
 <button disabled={!uri} onClick={()=>void run<ImportedProfile>({action:'prepare',sources,profileUri:uri,sourceVersion:version||null},value=>{onProfile(value);setSources([]);setInspection(null);setNotice('Profiili liitetty paikalliseen tuotteeseen. Valitse juurimuoto.');})}>Liitä tuotu profiili tuotteeseen</button></>}
 {!!profiles.length&&<HelpLabel>Käytä aiemmin tuotua profiilia<select value={profile?.id||''} onChange={e=>{const next=profiles.find(p=>p.id===e.target.value);if(next)onProfile(next);}}><option value="">Valitse paikallinen profiili</option>{profiles.map(p=><option key={p.id} value={p.id}>{p.profileUri} · {p.sourceVersion||'versio puuttuu'} · {p.sha256}</option>)}</select></HelpLabel>}
 </fieldset>
 {!(profile&&settings)&&feedback}
 {profile&&settings&&<><p>Generoinnin paikallinen snapshot: <code>{profile.profileUri}</code> · {profile.sourceVersion||'versio puuttuu'} · <code>{profile.sha256}</code>. Lähdetiedostot säilyvät kokeilun JSON-viennissä.</p>
 <fieldset disabled={disabled||busy}><legend>Generoinnin esitysvalinnat</legend>
 <HelpLabel>Generoinnin juurimuodon IRI<input value={settings.rootShapeUri} maxLength={2048} onChange={e=>update({rootShapeUri:e.target.value,names:[]})}/></HelpLabel>
 <button onClick={()=>void run<any>({action:'inspect',sources:profile.sources},result=>{setInspection(result);setNotice('Juurimuodon voi valita alla olevasta listasta.');})}>Näytä tuodun profiilin luokkamuodot</button>
 {inspection&&<HelpLabel>Valitse juurimuoto<select value={settings.rootShapeUri} onChange={e=>update({rootShapeUri:e.target.value,names:[]})}><option value="">Valitse yksi juuri</option>{inspection.shapes.filter((s:any)=>s.iri).map((s:any)=><option key={s.iri} value={s.iri}>{s.iri}</option>)}</select></HelpLabel>}
 <button disabled={!settings.rootShapeUri} onClick={()=>{setProposal(null);void run<any>({action:'proposal',profile,settings},result=>{setProposal(result);setFindings(result.findings||[]);setNotice('Generointituen tarkistus läpäisi selainversion rajauksen. Tämä ei ole SHACL-validointi.');});}}>Tarkista tuki ja muodosta mapping-ehdotus</button>
 {feedback}
 {proposal&&<><p>Yhteinen esitys kaikille muodoille; W3C-kenttäpolun alku on /credentialSubject. Tyypit ja määrät tulevat muuttumattomasta SHACLista.</p>{proposal.rows.map(row=><fieldset key={row.mapping.semanticPath.join('|')}><legend>{row.mapping.semanticPath.join(' → ')}</legend><HelpLabel>Kenttänimi {row.mapping.semanticPath.join(' / ')}<input maxLength={100} value={settings.names.find(n=>JSON.stringify(n.semanticPath)===JSON.stringify(row.mapping.semanticPath))?.fieldName??row.name} onChange={e=>update({names:[...settings.names.filter(n=>JSON.stringify(n.semanticPath)!==JSON.stringify(row.mapping.semanticPath)),{semanticPath:row.mapping.semanticPath,fieldName:e.target.value}]})}/></HelpLabel><p>{row.mapping.datatype||row.mapping.classUri} · {row.mapping.minCount}…{row.mapping.maxCount??'∞'} · {row.mapping.fieldPath}</p></fieldset>)}</>}
 <HelpLabel>Mappingin paikallinen versio<input maxLength={100} value={settings.mappingVersion} onChange={e=>update({mappingVersion:e.target.value})}/></HelpLabel>
 <HelpLabel>Suunniteltu HTTPS-julkaisemisen perusosoite<input maxLength={2048} value={settings.publicationBase} placeholder="https://julkaisut.example.org" onChange={e=>update({publicationBase:e.target.value})}/></HelpLabel><p>Osoitteita ei julkaista tai tarkisteta verkosta. Älä käytä demon Pages-osoitetta. Perusosoitteen muuttaminen vaatii uuden paketin.</p>
 <HelpLabel>Synteettinen yhteisen sisällön JSON-esimerkki<textarea rows={6} maxLength={100000} value={settings.exampleContent} onChange={e=>update({exampleContent:e.target.value,synthetic:false})}/></HelpLabel>
 <HelpLabel className="check"><input type="checkbox" checked={settings.acceptRepresentation} onChange={e=>update({acceptRepresentation:e.target.checked})}/>Olen tarkastanut yhteiset kenttänimet ja hyväksyn paketin mapping-ehdotukset</HelpLabel>
 <HelpLabel className="check"><input type="checkbox" checked={settings.acceptFormatPolicies} onChange={e=>update({acceptFormatPolicies:e.target.checked})}/>Olen tarkastanut toimitustapojen vct-, suojaus-, algoritmi-, haltijasidonta- ja paljastamisvalinnat</HelpLabel>
 <HelpLabel className="check"><input type="checkbox" checked={settings.synthetic} onChange={e=>update({synthetic:e.target.checked})}/>Vahvistan JSON-esimerkin synteettiseksi</HelpLabel>
 <p>Täydennä kolmen toimitustavan asetukset tuotteen muokkausnäkymässä. Generointi ei ylikirjoita niitä: muodostetut mappingit tulevat erilliseen paikalliseen pakettiin.</p>
 <button disabled={!proposal||!settings.acceptRepresentation||!settings.acceptFormatPolicies||!settings.synthetic||product.metadata.profileSnapshotId!==profile.id} onClick={()=>void run<LocalPackage>({action:'generate',profile,settings,metadata:product.metadata},value=>{onPackage(value);setNotice('Paikallinen kokeilupaketti muodostettu. Ei julkaistu eikä SHACL-validoitu.');})}>Muodosta paikallinen tekninen paketti</button>
 {product.metadata.profileSnapshotId!==profile.id&&<p>Tuotteen profiiliviite on muuttunut. Valitse generointiin tarkoitettu tuotu profiili uudelleen.</p>}
 </fieldset></>}
 {busy&&<p role="status">Käsitellään paikallisesti Workerissa… <button onClick={()=>controller.current?.abort()}>Keskeytä generointi</button></p>}

 {pkg&&<section aria-label="Paikallinen kokeilupaketti"><h3>Paikallinen kokeilupaketti – ei julkaistu</h3><TopicHelp topic="Paikallinen kokeilupaketti – ei julkaistu"/><p><strong>{stale?'Paketti vanhentunut – muodosta uudelleen':'Paketti vastaa tallennettuja generointisyötteitä'}</strong></p><p>Ei palvelimen riippumatonta hyväksyntää. JSON Schema ja lukittu JSON-LD-prosessointi suoritettu; täydellinen SHACL-validointi ja graafivertailu eivät ole selaimessa ajettuja tarkistuksia. Palautetun kokeilun raportteja ei suoriteta uudelleen automaattisesti.</p><button onClick={()=>downloadLocal(JSON.stringify(pkg),'paikallinen-kuvauspaketti.json')}>Lataa koko paikallinen paketti JSONina</button><ul>{Object.entries(pkg.artifacts).map(([name,artifact])=><li key={name}><button className="text-link" onClick={()=>downloadLocal(artifact.content,name,artifact.mediaType)}>Lataa {name}</button> · {artifact.mediaType}<small>SHA-256 <code>{artifact.sha256}</code></small><details><summary>Tarkastele paikallista artefaktia: {name}</summary><pre>{artifact.content}</pre><p>Suunniteltu osoite (ei julkaistu): <code>{artifact.url}</code></p></details></li>)}</ul></section>}
 </section>;
}
