import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './style.css';

type Element = {name:string; description:string; semanticUri:string};
type Input = {title:string; description:string; provider:string; theme:string; source:string; purpose:string; limitations:string; accessConditions:string; availability:'planned'|'sandbox'; synthetic:true; dataElements:Element[]};
type Product = Input & {id:string; modifiedAt:string};
const empty: Input = {title:'',description:'',provider:'',theme:'',source:'',purpose:'',limitations:'',accessConditions:'Vain synteettiseen demokäyttöön.',availability:'sandbox',synthetic:true,dataElements:[{name:'',description:'',semanticUri:'https://example.org/metatietovaranto/demo/'}]};
const fields: {key: keyof Omit<Input,'availability'|'synthetic'|'dataElements'>; label:string; long?:boolean; max:number}[] = [
 {key:'title',label:'Nimi',max:200},{key:'description',label:'Kuvaus',long:true,max:5000},
 {key:'provider',label:'Tarjoaja',max:200},{key:'theme',label:'Teema',max:100},{key:'source',label:'Synteettinen lähde',max:500},
 {key:'purpose',label:'Käyttötarkoitus',long:true,max:2000},{key:'limitations',label:'Rajaukset — mitä tuote ei todista',long:true,max:2000},
 {key:'accessConditions',label:'Käyttöehdot',long:true,max:2000}];
async function api<T>(path:string, options?:RequestInit):Promise<T> {
 const response=await fetch(path, options);
 if(!response.ok) {
  const body=await response.json().catch(()=>({}));
  const detail=body.detail;
  throw new Error(Array.isArray(detail) ? detail.map((e:{loc:string[];msg:string})=>`${e.loc.slice(1).join('.')}: ${e.msg}`).join('; ') : detail || 'Palveluun ei saada yhteyttä.');
 }
 return response.status===204 ? undefined as T : response.json();
}
function App(){
 const [items,setItems]=useState<Product[]>([]), [total,setTotal]=useState(0), [offset,setOffset]=useState(0);
 const [q,setQ]=useState(''),[theme,setTheme]=useState(''),[provider,setProvider]=useState('');
 const [error,setError]=useState(''),[notice,setNotice]=useState(''),[loading,setLoading]=useState(true);
 const [selected,setSelected]=useState<Product|null>(null),[editing,setEditing]=useState(false),[draft,setDraft]=useState<Input>(empty),[saving,setSaving]=useState(false);
 const params=()=>new URLSearchParams({q,theme,provider,limit:'20',offset:String(offset)});
 async function load(){setLoading(true);setError('');try{const data=await api<{items:Product[];total:number}>(`/api/v1/products?${params()}`);setItems(data.items);setTotal(data.total);}catch(e){setError((e as Error).message);}finally{setLoading(false);}}
 useEffect(()=>{void load();},[offset]);
 useEffect(()=>{
  const open=()=>{const id=location.hash.slice(1);if(!id){setSelected(null);setEditing(false);return;}void api<Product>(`/api/v1/products/${encodeURIComponent(id)}`).then(p=>{setSelected(p);setEditing(false);}).catch(e=>setError(e.message));};
  open();window.addEventListener('hashchange',open);return()=>window.removeEventListener('hashchange',open);
 },[]);
 function edit(product?:Product){setDraft(product ? Object.fromEntries(Object.keys(empty).map(k=>[k,product[k as keyof Input]])) as Input : structuredClone(empty));setEditing(true);setNotice('');setError('');}
 async function save(event:React.FormEvent){event.preventDefault();setSaving(true);setError('');try{
  const p=await api<Product>(selected ? `/api/v1/products/${selected.id}` : '/api/v1/products',{method:selected?'PUT':'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(draft)});
  setSelected(p);setEditing(false);location.hash=p.id;setNotice('Tietotuote tallennettu.');await load();
 }catch(e){setError((e as Error).message);}finally{setSaving(false);}}
 async function remove(){if(!selected||!window.confirm(`Poistetaanko tietotuote ”${selected.title}”?`))return;try{await api(`/api/v1/products/${selected.id}`,{method:'DELETE'});location.hash='';setSelected(null);setEditing(false);setNotice('Tietotuote poistettu.');await load();}catch(e){setError((e as Error).message);}}
 return <><header><div className="wrap"><a className="brand" href="#">Metatietovaranto</a><p>Viranomaisten tietotuotteiden metatietohakemisto</p></div></header><main className="wrap">
 <aside className="demo"><strong>Paikallinen demo · vaihe 1</strong><span>Kaikki esimerkit ovat synteettisiä. Ylläpito on avoin; demossa ei ole kirjautumista tai julkaisuhyväksyntää.</span></aside>
 {error&&<div role="alert" className="error" tabIndex={-1}>{error}</div>}{notice&&<p role="status">{notice}</p>}
 {editing ? <section><h1>{selected?'Muokkaa tietotuotetta':'Lisää tietotuote'}</h1><form onSubmit={save}>
 {fields.map(f=><label key={f.key}>{f.label}{f.long?<textarea required maxLength={f.max} value={draft[f.key]} onChange={e=>setDraft({...draft,[f.key]:e.target.value})}/>:<input required maxLength={f.max} value={draft[f.key]} onChange={e=>setDraft({...draft,[f.key]:e.target.value})}/>}</label>)}
 <label>Saatavuus<select value={draft.availability} onChange={e=>setDraft({...draft,availability:e.target.value as Input['availability']})}><option value="sandbox">Demo / sandbox</option><option value="planned">Suunnitteilla</option></select></label>
 <fieldset><legend>Tietoelementit</legend>{draft.dataElements.map((element,index)=><div className="element" key={index}>{(['name','description','semanticUri'] as const).map((key)=><label key={key}>{key==='name'?'Elementin nimi':key==='description'?'Elementin kuvaus':'Semanttinen URI'}<input required maxLength={key==='description'?500:key==='name'?100:2048} type={key==='semanticUri'?'url':'text'} value={element[key]} onChange={e=>setDraft({...draft,dataElements:draft.dataElements.map((el,i)=>i===index?{...el,[key]:e.target.value}:el)})}/></label>)}{draft.dataElements.length>1&&<button type="button" className="secondary" onClick={()=>setDraft({...draft,dataElements:draft.dataElements.filter((_,i)=>i!==index)})}>Poista elementti {index+1}</button>}</div>)}<button type="button" className="secondary" disabled={draft.dataElements.length>=50} onClick={()=>setDraft({...draft,dataElements:[...draft.dataElements,{name:'',description:'',semanticUri:'https://example.org/metatietovaranto/demo/'}]})}>Lisää tietoelementti</button></fieldset>
 <p>Vahvistan, että kuvaus ja esimerkit ovat synteettisiä.</p><div className="actions"><button disabled={saving}>{saving?'Tallennetaan…':'Tallenna'}</button><button type="button" className="secondary" onClick={()=>{setEditing(false);setError('');}}>Peruuta</button></div></form></section>
 :selected?<article><a href="#">← Takaisin hakuun</a><div className="heading"><h1>{selected.title}</h1><button onClick={()=>edit(selected)}>Muokkaa</button></div><p className="lead">{selected.description}</p><dl>{fields.filter(f=>!['title','description'].includes(f.key)).map(f=><React.Fragment key={f.key}><dt>{f.label}</dt><dd>{selected[f.key]}</dd></React.Fragment>)}<dt>Saatavuus</dt><dd>{selected.availability==='planned'?'Suunnitteilla':'Demo / sandbox'}</dd><dt>Muokattu</dt><dd>{new Date(selected.modifiedAt).toLocaleString('fi-FI')}</dd></dl><h2>Tietoelementit</h2><ul>{selected.dataElements.map((el,i)=><li key={i}><strong>{el.name}</strong> — {el.description}<br/><code>{el.semanticUri}</code></li>)}</ul><h2>Metatietojen vienti</h2><div className="actions"><a href={`/api/v1/products/${selected.id}/export?format=json`}>JSON</a><a href={`/api/v1/products/${selected.id}/export?format=jsonld`}>JSON-LD</a></div><p>JSON-LD käyttää DCAT-termejä ja paikallisia demotermejä. DCAT-AP-vaatimustenmukaisuutta ei ole todennettu.</p><button className="danger" onClick={()=>void remove()}>Poista tietotuote</button></article>
 :<section><div className="heading"><h1>Löydä tietotuote</h1><button onClick={()=>edit()}>Lisää tietotuote</button></div><form className="search" onSubmit={e=>{e.preventDefault();if(offset===0)void load();else setOffset(0);}}><label>Hakusana<input value={q} onChange={e=>setQ(e.target.value)} placeholder="Nimi, kuvaus tai tarjoaja" maxLength={200}/></label><label>Teema<input value={theme} onChange={e=>setTheme(e.target.value)} placeholder="Teeman tarkka nimi" maxLength={100}/></label><label>Tarjoaja<input value={provider} onChange={e=>setProvider(e.target.value)} placeholder="Tarjoajan tarkka nimi" maxLength={200}/></label><button>Hae</button></form><p role="status">{loading?'Haetaan…':`${total} tietotuotetta`}</p><div className="cards">{items.map(p=><article className="card" key={p.id}><span className="tag">{p.theme} · {p.availability==='planned'?'Suunnitteilla':'Demo / sandbox'}</span><h2><a href={`#${p.id}`}>{p.title}</a></h2><p>{p.description}</p><p className="provider">{p.provider}</p></article>)}</div>{!loading&&total===0&&<p>Hakuehdoilla ei löytynyt tietotuotteita.</p>}<div className="actions"><button className="secondary" disabled={offset===0} onClick={()=>setOffset(Math.max(0,offset-20))}>Edellinen</button><button className="secondary" disabled={offset+20>=total} onClick={()=>setOffset(offset+20)}>Seuraava</button></div><p>Koko hakemiston vienti: <a href="/api/v1/catalog/export?format=json">JSON</a> · <a href="/api/v1/catalog/export?format=jsonld">JSON-LD</a></p></section>}
 </main><footer className="wrap">Metatiedot kuvaavat tietotuotteita. Demo ei toimita rekisteritietoja tai myönnä todistuksia.</footer></>;
}
createRoot(document.getElementById('root')!).render(<App/>);
