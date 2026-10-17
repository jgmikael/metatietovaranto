import React,{useEffect,useRef,useState} from 'react';

export type Lifecycle={productId:string;version:string;sequence:number;status:'published'|'deprecated'|'withdrawn';revision:number;etag:string;uri:string;versionContentHash:string;reason:string|null;replacementVersion:string|null;events:{id:string;revision:number;status:string;reason:string;createdAt:string;organizationId:string;replacementVersion:string|null}[]};
export type VersionEntry={version:string;sequence:number;sha256:string;lifecycle:Lifecycle};
export type LifecycleCommand={version:string;status:'deprecated'|'withdrawn';reason:string;replacementVersion:string|null};
export const lifecycleNames:Record<string,string>={published:'Julkaistu',deprecated:'Poistumassa käytöstä',withdrawn:'Poistettu käytöstä'};

export function LifecyclePanel({state,canManage,versions,command}:{state:Lifecycle|null;canManage:boolean;versions:VersionEntry[];command:(body:LifecycleCommand,key:string)=>Promise<void>}){
 const [target,setTarget]=useState<'deprecated'|'withdrawn'>('deprecated'),[reason,setReason]=useState(''),[replacement,setReplacement]=useState(''),[busy,setBusy]=useState(false),[error,setError]=useState('');
 const operation=useRef({scope:'',key:''});
 useEffect(()=>{setTarget(state?.status==='deprecated'?'withdrawn':'deprecated');setReason('');setReplacement('');setError('');},[state?.etag]);
 if(!state)return <section aria-label="Version elinkaari"><p role="alert">Ajantasainen elinkaaritieto puuttuu. Palvelutoiminnot ovat estettyinä; lataa sivu uudelleen.</p></section>;
 async function save(event:React.FormEvent){event.preventDefault();if(!state)return;if(target==='withdrawn'&&!window.confirm('Poistetaanko tämä julkaisuversio käytöstä? Tilamuutosta ei voi perua. Alkuperäinen sisältö ja historia säilyvät.'))return;
  const body:LifecycleCommand={version:state.version,status:target,reason,replacementVersion:target==='deprecated'?(replacement||null):null};
  const scope=JSON.stringify(body)+state.etag;if(operation.current.scope!==scope)operation.current={scope,key:crypto.randomUUID()};
  setBusy(true);setError('');try{await command(body,operation.current.key);}catch(e){setError((e as Error).message);}finally{setBusy(false);}
 }
 return <section aria-label="Version elinkaari"><h2>Version elinkaari</h2>
 {state.status==='withdrawn'?<aside className="error" role="alert"><strong>Versio on poistettu käytöstä.</strong><p>{state.reason}</p><p>Version palvelutoiminnot on estetty. Alkuperäinen metatieto ja historia säilyvät luettavina.</p></aside>:state.status==='deprecated'?<aside className="demo"><strong>Versio on poistumassa käytöstä.</strong><p>{state.reason}</p>{state.replacementVersion&&<p>Korvaava versio: <a href={`#${state.productId}@${state.replacementVersion}`}>{state.replacementVersion}</a></p>}</aside>:<p>Versio on julkaistu. Käytettävyyden ratkaisee kunkin toimitustavan oma saatavuus.</p>}
 <p>Versio {state.version} · {lifecycleNames[state.status]}</p><details><summary>Elinkaarihistoria</summary>{state.events.length?<ol>{state.events.map(item=><li key={item.id}><strong>{lifecycleNames[item.status]}</strong> · {new Date(item.createdAt).toLocaleString('fi-FI')}<p>{item.reason}</p>{item.replacementVersion&&<a href={`#${state.productId}@${item.replacementVersion}`}>Korvaava versio {item.replacementVersion}</a>}</li>)}</ol>:<p>Ei julkaisun jälkeisiä elinkaarimuutoksia.</p>}</details>
 <p><a href={state.uri}>Ajantasainen elinkaaritieto JSONina</a></p>
 {canManage&&state.status!=='withdrawn'&&<form onSubmit={event=>void save(event)}><fieldset disabled={busy}><legend>Julkaisijan elinkaarimuutos</legend><p>Perustelu ja tapahtuma julkaistaan. Muutos ei muokkaa alkuperäistä sisältöä tai sen hyväksyntää.</p><label htmlFor="lifecycle-target">Uusi elinkaaritila</label><select id="lifecycle-target" value={target} onChange={e=>setTarget(e.target.value as 'deprecated'|'withdrawn')}>{state.status==='published'&&<option value="deprecated">Poistumassa käytöstä</option>}<option value="withdrawn">Poistettu käytöstä</option></select>
 <label htmlFor="lifecycle-reason">Julkinen elinkaariperustelu — ei henkilötietoja tai salaisuuksia</label><textarea id="lifecycle-reason" required minLength={10} maxLength={2000} value={reason} onChange={e=>setReason(e.target.value)}/>
 {target==='deprecated'&&<><label htmlFor="lifecycle-replacement">Korvaava julkaisuversio</label><select id="lifecycle-replacement" value={replacement} onChange={e=>setReplacement(e.target.value)}><option value="">Ei korvaavaa versiota — kerro tilanne perustelussa</option>{versions.filter(item=>item.sequence>state.sequence&&item.lifecycle.status!=='withdrawn').map(item=><option key={item.version} value={item.version}>{item.version} · {lifecycleNames[item.lifecycle.status]}</option>)}</select></>}
 <button disabled={reason.trim().length<10}>Tallenna elinkaarimuutos</button></fieldset></form>}
 {busy&&<p role="status">Tallennetaan elinkaaritapahtumaa…</p>}{error&&<p role="alert">{error} Lue ajantasainen tila lataamalla sivu uudelleen.</p>}</section>;
}
