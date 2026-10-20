import React,{createContext,useContext,useEffect,useId,useRef,useState} from 'react';
import compiled from './generated/help.json';
import markdownUrl from '../../../../docs/pages-kayttoohje.md?url';
import turtleUrl from '../../../../fixtures/semantic-profile-demo.ttl?url';
import reportUrl from '../../../../docs/browser-webcor-report.json?url';
import {pagesMode} from '../dataSource';

type Node={type:string;value?:string;url?:string;title?:string;depth?:number;id?:string;ordered?:boolean;start?:number;children?:Node[]};
type Entry={section:string;label:string;description:Node[];example:Node[]};
const data=compiled as unknown as {document:Node;sections:{id:string;title:string;depth:number}[];fields:Record<string,Entry>};
const Context=createContext<null|{hash:string;open:(section?:string)=>void;back:()=>void}>(null);
export const isHelp=(hash:string)=>hash==='#ohje'||hash.startsWith('#ohje/');
export function HelpProvider({children}:{children:React.ReactNode}){
 const [hash,setHash]=useState(location.hash),previous=useRef(hash),origin=useRef<{hash:string;element:HTMLElement|null;scroll:number}|null>(null);
 const capture=()=>{origin.current={hash:location.hash,element:document.activeElement instanceof HTMLElement?document.activeElement:null,scroll:window.scrollY};};
 useEffect(()=>{const change=()=>{const next=location.hash;if(isHelp(next)&&!isHelp(previous.current)&&!origin.current)origin.current={hash:previous.current,element:document.activeElement as HTMLElement,scroll:window.scrollY};
  if(!isHelp(next)&&isHelp(previous.current)){const saved=origin.current;origin.current=null;if(saved&&next===saved.hash)requestAnimationFrame(()=>{saved.element?.focus({preventScroll:true});window.scrollTo(0,saved.scroll);});}
  previous.current=next;setHash(next);
 };window.addEventListener('hashchange',change);return()=>window.removeEventListener('hashchange',change);},[]);
 return <Context.Provider value={{hash,open:(section='alku')=>{if(!isHelp(location.hash))capture();location.hash='ohje/'+section;},back:()=>{location.hash=origin.current?.hash||'';}}}>{children}</Context.Provider>;
}
export function HelpNavigation(){const help=useContext(Context);return help?<nav className="help-navigation wrap" aria-label="Ohjenavigaatio"><a href="#ohje/alku" onClick={e=>{e.preventDefault();help.open();}}>Käyttöohje</a>{isHelp(help.hash)&&<button type="button" className="secondary" onClick={help.back}>Palaa edelliseen näkymään</button>}</nav>:null;}
function linkUrl(url:string){
 if(/[\u0000-\u0020\u007f]/.test(url)||url.startsWith('//')||(/^[a-z][a-z\d+.-]*:/i.test(url)&&!/^https?:/i.test(url)))return undefined;
 if(url.endsWith('semantic-profile-demo.ttl'))return turtleUrl;
 if(url.endsWith('browser-webcor-report.json'))return reportUrl;
 if(url.startsWith('#'))return url;
 if(!/^https?:/i.test(url))return 'https://github.com/jgmikael/metatietovaranto/blob/main/'+(url.startsWith('../')?url.slice(3):'docs/'+url);
 return url;
}
function Markdown({nodes}:{nodes:Node[]}){return <>{nodes.map((node,i)=>{
 const child=<Markdown nodes={node.children||[]}/>;
 switch(node.type){
 case 'root':return <React.Fragment key={i}>{child}</React.Fragment>;
 case 'text':return <React.Fragment key={i}>{node.value}</React.Fragment>;
 case 'paragraph':return <p key={i}>{child}</p>;
 case 'strong':return <strong key={i}>{child}</strong>;
 case 'emphasis':return <em key={i}>{child}</em>;
 case 'delete':return <del key={i}>{child}</del>;
 case 'inlineCode':return <code key={i}>{node.value}</code>;
 case 'code':return <pre key={i}><code>{node.value}</code></pre>;
 case 'heading':{const Tag=('h'+node.depth) as 'h1'|'h2'|'h3';return <Tag key={i} id={'ohje-'+node.id} tabIndex={-1}>{child}</Tag>;}
 case 'link':{const url=linkUrl(node.url||'');const download=node.url?.endsWith('.ttl')||node.url?.endsWith('browser-webcor-report.json');return url?<a key={i} href={url} download={download?node.url?.split('/').pop():undefined} {...(url.startsWith('https:')?{target:'_blank',rel:'noopener noreferrer'}:{})}>{child}</a>:<React.Fragment key={i}>{child}</React.Fragment>;}
 case 'list':return node.ordered?<ol key={i} start={node.start}>{child}</ol>:<ul key={i}>{child}</ul>;
 case 'listItem':return <li key={i}>{child}</li>;
 case 'table':return <div className="help-table" key={i}><table><thead><tr>{node.children?.[0]?.children?.map((cell,j)=><th key={j}><Markdown nodes={cell.children||[]}/></th>)}</tr></thead><tbody>{node.children?.slice(1).map((row,j)=><tr key={j}>{row.children?.map((cell,k)=><td key={k}><Markdown nodes={cell.children||[]}/></td>)}</tr>)}</tbody></table></div>;
 case 'blockquote':return <blockquote key={i}>{child}</blockquote>;
 case 'thematicBreak':return <hr key={i}/>;
 case 'break':return <br key={i}/>;
 default:return null;
 }
 })}</>;}
export function HelpView(){
 const help=useContext(Context)!;const requested=help.hash.split('/')[1]||'alku',section=data.sections.find(s=>s.id===requested);
 useEffect(()=>{const target=document.getElementById('ohje-'+(section?.id||'alku'));target?.focus({preventScroll:true});target?.scrollIntoView();},[requested]);
 return <main className="wrap help-view"><p>Ohje koskee julkista esittelyä ja selaimen paikallista kokeilua.</p><a href={markdownUrl} download="pages-kayttoohje.md">Lataa käyttöohje Markdownina</a><nav aria-label="Käyttöohjeen sisällysluettelo"><h2>Sisällysluettelo</h2><ul>{data.sections.map(s=><li key={s.id}><a href={'#ohje/'+s.id}>{s.title}</a></li>)}</ul></nav>{!section&&<p role="alert">Ohjeosiota ei löydy. Valitse osio sisällysluettelosta.</p>}<Markdown nodes={[data.document]}/></main>;
}
export function resolveHelp(label:string){
 if(data.fields[label])return label;
 const mapping=label.match(/, kenttä \d+: (.*)$/);if(mapping)return 'mapping.'+mapping[1];
 const wallet=label.match(/: lompakko \d+: (.*)$/);if(wallet)return 'wallet.'+wallet[1];
 const dist=label.match(/^(JSON API|W3C VC|SD-JWT VC) \d+: (.*)$/);
 if(dist){const suffix=dist[2];if(['ES256','ES384','EdDSA'].includes(suffix))return 'distribution.ES256 / ES384 / EdDSA';
  return Object.keys(data.fields).find(key=>!key.startsWith('wallet.')&&key.endsWith('.'+suffix));}
 if(label.startsWith('Kenttänimi '))return 'generation.Kenttänimi [semanttinen polku]';
 return Object.keys(data.fields).find(key=>!key.startsWith('search.')&&key.endsWith('.'+label));
}
const panelId=(id:string)=>id+'-help';
export function helpFieldAttributes(id:string,label:string){return pagesMode&&resolveHelp(label)?{'aria-describedby':panelId(id)}:{};}
function plain(nodes:Node[]):string{return nodes.map(node=>node.value??plain(node.children||[])).join('');}
function Disclosure({entry,id,label}:{entry:Entry;id:string;label:string}){
 const [open,setOpen]=useState(false),help=useContext(Context)!;
 return <><button type="button" className="field-help-button" aria-label={'Ohje: '+label} aria-expanded={open} aria-controls={id} onClick={()=>setOpen(value=>!value)}>Ohje</button><div className="field-help-panel" id={id} hidden={!open}><p>{plain(entry.description)}</p>{entry.example.length>0&&<div className="help-example"><strong>Esimerkki tai toiminta: </strong>{plain(entry.example)}</div>}<a href={'#ohje/'+entry.section} onClick={e=>{e.preventDefault();help.open(entry.section);}}>Lue lisää</a></div></>;
}
export function HelpLabel({children,helpKey,...props}:React.LabelHTMLAttributes<HTMLLabelElement>&{helpKey?:string}){
 const help=useContext(Context),generated=useId();
 if(!help)return <label {...props}>{children}</label>;
 const items=React.Children.toArray(children),control=items.find(item=>React.isValidElement(item)&&['input','textarea','select'].includes(item.type as string)) as React.ReactElement<{id?:string;type?:string;'aria-describedby'?:string}>|undefined;
 const label=items.filter(item=>item!==control).map(item=>typeof item==='string'||typeof item==='number'?String(item):'').join('');
 const entry=data.fields[resolveHelp(helpKey||label)||''];
 const id=props.htmlFor||control?.props.id||'field-'+generated;
 const other=items.filter(item=>item!==control),check=control&&['checkbox','radio'].includes(control.props.type||'');
 return <div className="help-field" data-help-key={resolveHelp(helpKey||label)} data-help-missing={!entry?'true':undefined}><div className="help-field-heading"><label {...props} htmlFor={id}>{check&&React.cloneElement(control,{id,'aria-describedby':panelId(id)})}{other}</label>{entry&&<Disclosure entry={entry} id={panelId(id)} label={label}/>}</div>{control&&!check&&React.cloneElement(control,{id,'aria-describedby':entry?panelId(id):undefined})}</div>;
}
export function TopicHelp({topic}:{topic:string}){const help=useContext(Context),id=useId(),entry=data.fields[resolveHelp(topic)||''];return help&&entry?<div className="topic-help"><span>{entry.label}</span> <Disclosure entry={entry} id={'topic-'+id} label={entry.label}/></div>:null;}
