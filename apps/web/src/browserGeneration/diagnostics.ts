/** Bounded read-only checks. They do not repair RDF or implement SHACL validation. */
import {type Store,type Term,DataFactory} from 'n3';
import contract from './contract.json';
import {type Finding,DEPTH_LIMIT,FIELD_LIMIT} from './model';
const SH='http://www.w3.org/ns/shacl#',XSD='http://www.w3.org/2001/XMLSchema#',OWL='http://www.w3.org/2002/07/owl#';
const named=DataFactory.namedNode;
// Match Python/code-point ordering, including supplementary-plane source IRIs.
function compare(left:string,right:string){const a=Array.from(left,v=>v.codePointAt(0)!),b=Array.from(right,v=>v.codePointAt(0)!);for(let i=0;i<Math.min(a.length,b.length);i++)if(a[i]!==b[i])return a[i]-b[i];return a.length-b.length;}
export const objects=(g:Store,s:Term,p:string)=>g.getObjects(s,named(p),null);
const sourceLocations=new WeakMap<Store,Map<string,Set<string>>>();
const key=(t:Term)=>t.termType+':'+t.value;
export function recordSource(g:Store,s:Term,name:string){let map=sourceLocations.get(g);if(!map){map=new Map();sourceLocations.set(g,map);}const names=map.get(key(s))||new Set<string>();names.add(name);map.set(key(s),names);}
/** Diagnostic DTO only. Generation always reparses the original source terms. */
export const termInfo=(t:Term)=>({value:t.value,termType:t.termType,...(t.termType==='Literal'?{datatype:t.datatype.value,language:t.language}:{})});
export const rangeInfo=(g:Store,path:Term)=>objects(g,path,contract.rangePolicy.range).map(t=>({...termInfo(t),sources:[...(sourceLocations.get(g)?.get(key(path))||[])].sort()}));
function datatypeSuggestion(value:string){return /^[A-Za-z][A-Za-z0-9+.-]*:[^\s<>"{}|^`\\]+$/.test(value)?'sh:datatype <'+value+'> .':'Anna sh:datatype-arvoksi tarkoitetun konkreettisen tietotyypin IRI.';}
export const sourcesFor=(g:Store,s:Term)=>[...(sourceLocations.get(g)?.get(key(s))||[])].sort();
export class CountError extends Error{constructor(public code:string,message:string){super(message);}}
export function readCount(term:Term|undefined,defaultValue:number|null=null):number|null{
 if(!term)return defaultValue;
 const name=term.termType==='Literal'&&term.datatype.value.startsWith(XSD)?term.datatype.value.slice(XSD.length):'';
 const types=contract.countTypes as Record<string,(string|null)[]>;
 if(term.termType!=='Literal'||!Object.hasOwn(types,name))throw new CountError('CARDINALITY_TERM','Määrärajoite tarvitsee XSD-kokonaislukuliteraalin (esimerkiksi xsd:int tai xsd:integer), ei merkkijonoa tai muuta RDF-termiä.');
 const lexical=term.value.replace(/^[ \t\r\n]+|[ \t\r\n]+$/g,'');
 if(!/^[+-]?[0-9]+$/.test(lexical))throw new CountError('CARDINALITY_LEXICAL','Virheellinen kokonaisluvun kirjoitusasu; desimaaliosaa tai eksponenttia ei hyväksytä.');
 const value=BigInt(lexical),[low,high]=types[name];
 if(low!==null&&value<BigInt(low)||high!==null&&value>BigInt(high))throw new CountError('CARDINALITY_VALUE','Arvo ei kuulu ilmoitetun '+name+'-tietotyypin arvoavaruuteen.');
 if(value<0n)throw new CountError('CARDINALITY_VALUE','sh:minCount ja sh:maxCount eivät saa olla negatiivisia.');
 if(value>BigInt(contract.countLimit))throw new CountError('CARDINALITY_LIMIT','Kelvollinen kokonaisluku ylittää generaattorin resurssirajan 10 000.');
 return Number(value); // Conversion only after exact bounded comparisons.
}
export function groupProperties(g:Store,shape:Term){
 const groups=new Map<string,Term[]>();
 for(const prop of objects(g,shape,SH+'property')){const paths=objects(g,prop,SH+'path');const id=paths.length===1&&paths[0].termType==='NamedNode'?key(paths[0]):key(prop);const list=groups.get(id)||[];list.push(prop);groups.set(id,list);}
 return [...groups.values()].map(group=>group.sort((a,b)=>compare(a.value,b.value))).sort((a,b)=>{const x=objects(g,a[0],SH+'path')[0]?.value||'',y=objects(g,b[0],SH+'path')[0]?.value||'';return compare(x,y);});
}
export function propertyValues(g:Store,group:Term[],predicate:string){const result:Term[]=[];for(const prop of group)for(const value of objects(g,prop,predicate))if(!result.some(t=>t.equals(value)))result.push(value);return result;}
export function propertyLocator(shape:Term,prop:Term,path:string){return {nodeShapeUri:shape.termType==='NamedNode'?shape.value:null,propertyPath:path,propertyShapeUri:prop.termType==='NamedNode'?prop.value:null};}
export function preflight(g:Store,root:Term,choices:{references?:string[][];languageRepresentation?:string}={}):Finding[]{
 const findings:Finding[]=[],seen=new Set<string>();let fields=0,truncated=false;
 function add(ruleId:string,message:string,shape:Term,group:Term[],predicate:string,path:string,extra:Partial<Finding>={}){
  if(findings.length>=200){truncated=true;return;}
  findings.push({ruleId,message,path,category:'sourceError',rootShapeUri:root.value,nodeShapeUri:shape.termType==='NamedNode'?shape.value:null,predicate,
   propertyShapes:group.map((prop,index)=>({uri:prop.termType==='NamedNode'?prop.value:null,kind:prop.termType==='NamedNode'?'iri':'blankNode',localIndex:index+1,labels:[...objects(g,prop,SH+'name'),...objects(g,prop,'http://www.w3.org/2000/01/rdf-schema#label')].filter(t=>t.termType==='Literal').map(t=>t.value).sort(),sources:[...(sourceLocations.get(g)?.get(key(prop))||[])].sort()})),...extra});
 }
 function visit(shape:Term,depth:number,semantic:string[]=[]){
  if(depth>DEPTH_LIMIT||seen.has(key(shape)))return;seen.add(key(shape));
  for(const group of groupProperties(g,shape)){
   if(++fields>FIELD_LIMIT){add('FIELD_LIMIT','Esitarkistuksen kenttäraja 200 ylittyi; raportti on rajattu.',shape,group,SH+'property',root.value,{category:'resourceLimit'});return;}
   const groupStart=findings.length,paths=objects(g,group[0],SH+'path'),path=paths[0]?.termType==='NamedNode'?paths[0].value:root.value;
   const isReference=choices.references?.some(p=>JSON.stringify(p)===JSON.stringify([...semantic,path]));
   if(!paths.length)add('PATH_REQUIRED','sh:path puuttuu. Sisältöominaisuutta ei päätellä nimestä tai ylaluokkaviitteestä; korjaa lähdeprofiili.',shape,group,SH+'path',group[0].termType==='NamedNode'?group[0].value:root.value);
   const lows:number[]=[],highs:number[]=[];let numericError=false;
   for(const prop of group){
    for(const predicate of ['minCount','maxCount']){
     const terms=objects(g,prop,SH+predicate);
     if(terms.length>1){numericError=true;add('CARDINALITY_TERM','Yhdellä ominaisuusrajoitteella saa olla yksi sh:'+predicate+'-arvo.',shape,[prop],SH+predicate,path);continue;}
     if(terms.length)try{const value=readCount(terms[0])!;(predicate==='minCount'?lows:highs).push(value);}catch(e){numericError=true;const error=e as CountError;add(error.code,error.message,shape,[prop],SH+predicate,path,{category:error.code==='CARDINALITY_LIMIT'?'resourceLimit':'sourceError',observed:{value:terms[0].value,termType:terms[0].termType,datatype:terms[0].termType==='Literal'?terms[0].datatype.value:undefined},expected:'XSD-kokonaislukuliteraali, arvo 0–10 000'});}
    }
    const datatypes=objects(g,prop,SH+'datatype'),kinds=objects(g,prop,SH+'nodeKind');
    const owlRanges=paths[0]?.termType==='NamedNode'?rangeInfo(g,paths[0]):[];
    const detail=(term:Term)=>({observed:termInfo(term),owlRanges});
    for(const term of datatypes){
     if(term.termType!=='NamedNode')add('DATATYPE_TERM','sh:datatype tarvitsee IRI:n. URI:n näköinen merkkijono on literaali eikä tietotyypin IRI.'+(term.value===contract.rangePolicy.literal?' Lainattu rdfs:Literal ei määritä konkreettista tyyppiä; älä oleta xsd:stringiä.':''),shape,[prop],SH+'datatype',path,{...detail(term),expected:'IRI',suggestion:datatypeSuggestion(term.value)+' Korjaa lähdeprofiili tai exportin tuottaminen ja tuo uusi Turtle-export. Lähdettä ei muuteta automaattisesti.'});
     else if(term.value===contract.rangePolicy.literal)add('DATATYPE_REPRESENTATION_REQUIRED','Konkreettinen literaalin esitysratkaisu puuttuu. sh:datatype rdfs:Literal ei tarkoita mitä tahansa literaalia; tyyppiä ei oleteta merkkijonoksi.',shape,[prop],SH+'datatype',path,{...detail(term),category:'generatorLimit'});
     else if(term.value==='http://www.w3.org/1999/02/22-rdf-syntax-ns#langString'&&choices.languageRepresentation!==contract.representations.languageProfile)add('LANGUAGE_REPRESENTATION_REQUIRED','Hyväksy value/language-v1-kieliesitys ennen ehdotusta. Lähteen kielitietoa ei poisteta.',shape,[prop],SH+'datatype',path,{...detail(term),category:'decisionRequired'});
     else if(term.value!=='http://www.w3.org/1999/02/22-rdf-syntax-ns#langString'&&!contract.datatypes.some(name=>term.value===XSD+name))add('DATATYPE_UNSUPPORTED','Kelvollinen tietotyyppi-IRI ei kuulu generointiprofiiliin. Kielimerkittyjä arvoja ei muuteta merkkijonoiksi eikä kielitietoa poisteta: '+term.value,shape,[prop],SH+'datatype',path,{...detail(term),category:'generatorLimit'});
     else for(const range of owlRanges){
      const r=objects(g,paths[0],contract.rangePolicy.range).find(t=>t.termType===range.termType&&t.value===range.value)!,disjoint=contract.rangePolicy.disjoint;
      const conflict=g.countQuads(term,named(disjoint),r,null)>0||g.countQuads(r,named(disjoint),term,null)>0;
      const ruleId=conflict?'OWL_SHACL_CONFLICT':range.termType==='NamedNode'&&range.value===term.value?'OWL_RANGE_COMPATIBLE':range.termType==='NamedNode'&&range.value===contract.rangePolicy.literal?'OWL_RANGE_REFINEMENT':'OWL_RANGE_UNASSESSED';
      const messages={OWL_SHACL_CONFLICT:'Lukitussa aineistossa on eksplisiittinen owl:disjointWith SHACL-tietotyypin ja OWL-arvoalueen välillä.',OWL_RANGE_COMPATIBLE:'SHACL-tietotyyppi ja paikallinen OWL-arvoalue ovat samat.',OWL_RANGE_REFINEMENT:'OWL:n rdfs:Literal sallii SHACLin konkreettisen literaalityypin tarkennuksen.',OWL_RANGE_UNASSESSED:'Rajattu tarkistus ei ratkaise tämän OWL-arvoalueen yhteensopivuutta. Eri IRI ei yksin todista ristiriitaa; OWL-päättelyä ei suoritettu.'};
      add(ruleId,messages[ruleId],shape,[prop],SH+'datatype',path,{observed:termInfo(term),owlRanges:[range],category:conflict?'sourceError':'warning'});
     }
    }
    for(const kind of kinds){
     if(!datatypes.length&&kind.termType==='NamedNode'&&kind.value===SH+'Literal')add('DATATYPE_REPRESENTATION_REQUIRED','sh:nodeKind sh:Literal jättää konkreettisen tietotyypin ja esitysratkaisun avoimeksi; tyyppiä ei oleteta merkkijonoksi.',shape,[prop],SH+'nodeKind',path,{...detail(kind),category:'generatorLimit'});
     else if(!isReference&&(kind.termType!=='NamedNode'||kind.value!==SH+'Literal'))add('NODE_KIND_UNSUPPORTED','Vain konkreettista literaalityyppiä täydentävä sh:nodeKind sh:Literal on tuettu.',shape,[prop],SH+'nodeKind',path,{...detail(kind),category:'generatorLimit'});
    }
   }
   if(!numericError&&Math.max(0,...lows)>Math.min(Infinity,...highs))add('CARDINALITY_CONFLICT','Samalle polulle kohdistuvien määrärajoitteiden leikkaus on tyhjä: maxCount on minCountia pienempi.',shape,group,SH+'maxCount',path);
   if(group.length>1){
    if(path===OWL+'topObjectProperty')add('SEMANTIC_TOP_PROPERTY','Useat ominaisuusrajoitteet käyttävät owl:topObjectProperty-polkua. Generaattori ei voi päätellä niistä eri sisältöominaisuuksia. Määrittele tarkoitetut semanttiset ominaisuudet lähdemallissa. Tämä on mapping-este, ei itsessään RDF-/SHACL-syntaksivirhe.',shape,group,SH+'path',path,{category:'generatorLimit'});
    else if(group.some(p=>p.termType!=='NamedNode')||!propertyValues(g,group,SH+'datatype').length||['datatype','class','node'].some(p=>propertyValues(g,group,SH+p).length>1))add('PROPERTY_CONSTRAINT_UNSUPPORTED','Saman polun rajoitteiden yhdistäminen vaatii yksiselitteiset nimetyt PropertyShapet ja yhden tuetun literaalityypin. SHACL voi silti olla kelvollinen; tämä on generaattorin tukirajoite.',shape,group,SH+'path',path,{category:'generatorLimit'});
    else if(!findings.slice(groupStart).some(f=>f.category!=='warning'))add('PROPERTY_CONSTRAINT_INTERSECTION','Saman ominaisuuspolun yhteensopivat nimetyt rajoitteet käsitellään yhtenä kenttänä; määrärajoitteista käytetään leikkausta ja alkuperäiset rajoiteviitteet säilytetään.',shape,group,SH+'path',path,{category:'warning'});
   }
   if(!isReference)for(const node of propertyValues(g,group,SH+'node'))visit(node,depth+1,[...semantic,path]);
   if(!isReference&&!propertyValues(g,group,SH+'node').length)for(const cls of propertyValues(g,group,SH+'class')){const candidates=g.getSubjects(named(SH+'targetClass'),cls,null);if(candidates.length===1)visit(candidates[0],depth+1,[...semantic,path]);}
  }
 }
 visit(root,0);if(truncated)findings[findings.length-1]={ruleId:'DIAGNOSTIC_LIMIT',path:root.value,message:'Raportin 200 havainnon raja ylittyi. Korjaa ilmoitetut kohdat ja tarkista uudelleen; pakettia ei muodosteta rajatusta raportista.',category:'resourceLimit',rootShapeUri:root.value};return findings;
}
