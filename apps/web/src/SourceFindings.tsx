import React from 'react';
import type {Finding} from './browserGeneration/model';

export function SourceFindings({findings}:{findings:Finding[]}){
 const categories={sourceError:'Lähdeaineiston virhe',generatorLimit:'Generaattorin tukirajoite',resourceLimit:'Resurssiraja',warning:'Huomio',decisionRequired:'Puuttuva esityspäätös'};
 return <section aria-label="Lähdeprofiilin havainnot"><h3>Lähdeprofiilin havainnot</h3><p>Rajattu generointituen esitarkistus; ei täydellinen SHACL-validointi. Lähdeaineistoa ei ole korjattu tai muutettu.</p>
 {findings.some(f=>f.category==='sourceError')&&<p>Lomakkeen lisäkenttien täyttäminen ei korjaa lähdeprofiilin tietotyyppi- tai ominaisuuspolkumäärityksiä. Korjaa lähde ja tuo uusi Turtle-export.</p>}
 <ol>{findings.map((f,index)=><li key={index}><strong>{f.ruleId} · {categories[f.category||'generatorLimit']}</strong><p>{f.message}</p>
 {f.rootShapeUri&&<p>Juurimuoto: <code>{f.rootShapeUri}</code><br/>Luokkamuoto: <code>{f.nodeShapeUri||'nimetön luokkamuoto (paikallinen käyttöyhteys)'}</code></p>}
 <p>Ominaisuuspolku: {f.ruleId==='PATH_REQUIRED'?'puuttuu':<code>{f.path}</code>}{f.ruleId==='PATH_REQUIRED'&&<><br/>Havaintokohta: <code>{f.path}</code></>}{f.predicate&&<><br/>Predikaatti: <code>{f.predicate}</code></>}</p>
 {f.observed&&<p>Havaittu arvo: <code>{f.observed.value}</code> · RDF-termin tyyppi: {f.observed.termType}{f.observed.datatype&&<> · literaalitermin oma tietotyyppi: <code>{f.observed.datatype}</code></>}{f.observed.language&&<> · kieli: {f.observed.language}</>}{f.expected&&<><br/>Odotettu: {f.expected}</>}</p>}
 {f.owlRanges&&f.owlRanges.length>0&&<p>OWL-arvoalue (rdfs:range), erillinen SHACL-rajoitteesta: {f.owlRanges.map((r,i)=><span key={i}><code>{r.value}</code> · {r.termType}{r.sources?.length?<> · lähdetiedosto: {r.sources.join(', ')}</>:null}{' '}</span>)}</p>}
 {f.propertyShapes&&<ul>{f.propertyShapes.map((p,j)=><li key={j}>Ominaisuusrajoite: {p.uri?<code>{p.uri}</code>:<>nimetön PropertyShape, paikallinen kohta {p.localIndex} (ei pysyvä URI)</>}{p.labels.length>0&&<> · {p.labels.join(' / ')}</>}{p.sources.length>0&&<> · lähdetiedosto: {p.sources.join(', ')}</>}</li>)}</ul>}
 {f.suggestion&&<p>{f.suggestion}</p>}</li>)}</ol></section>;
}
