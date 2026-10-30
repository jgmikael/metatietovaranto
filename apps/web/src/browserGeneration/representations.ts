import {type Store,type Term,DataFactory} from 'n3';
import contract from './contract.json';
import {type Tree,canonical} from './model';
import {objects,readCount} from './diagnostics';
const SH='http://www.w3.org/ns/shacl#';const named=DataFactory.namedNode;
export const LANG='http://www.w3.org/1999/02/22-rdf-syntax-ns#langString';
export function referenceClass(graph:Store,prop:Term):Term{
 const classes=objects(graph,prop,SH+'class');
 if(classes.length!==1||classes[0].termType!=='NamedNode'||objects(graph,prop,SH+'node').length||objects(graph,prop,SH+'datatype').length)throw new Error('IRI-viittaus tarvitsee yhden sh:class-IRI:n eikä sh:node- tai sh:datatype-rajoitetta. sh:node vaatii kohteen sisältöä.');
 const kinds=objects(graph,prop,SH+'nodeKind');if(kinds.length&&(kinds.length!==1||kinds[0].termType!=='NamedNode'||kinds[0].value!==SH+'IRI'))throw new Error('IRI-viittaus ei täytä sh:nodeKind-rajoitetta.');
 for(const p of ['targetNode','targetSubjectsOf','targetObjectsOf'])if(graph.getQuads(null,named(SH+p),null,null).length)throw new Error('Muut kohdistukset estävät viittauksen rajatun riittävyystarkistuksen.');
 for(const kind of ['http://www.w3.org/2000/01/rdf-schema#Class','http://www.w3.org/2002/07/owl#Class'])for(const candidate of graph.getSubjects(named('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),named(kind),null))if(graph.getPredicates(candidate,null,null).some(p=>p.value.startsWith(SH))||['NodeShape','PropertyShape'].some(t=>graph.countQuads(candidate,named('http://www.w3.org/1999/02/22-rdf-syntax-ns#type'),named(SH+t),null)))throw new Error('Implisiittinen SHACL-luokkakohdistus vaatii laajemman viittausprofiilin: '+candidate.value);
 const cls=classes[0],annotations=['name','description','order','group','message','severity','defaultValue'];
 if(objects(graph,cls,'http://www.w3.org/2000/01/rdf-schema#subClassOf').length)throw new Error('Kohdeluokan ylaluokkakohdistukset vaativat laajemman viittausprofiilin: '+cls.value);
 for(const shape of graph.getSubjects(named(SH+'targetClass'),cls,null)){
  if(graph.getPredicates(shape,null,null).some(p=>p.value.startsWith(SH)&&![...annotations,'targetClass','property'].includes(p.value.slice(SH.length))))throw new Error('Kohdemuodon rajoitteet vaativat laajemman viittausprofiilin: '+shape.value);
  for(const c of objects(graph,shape,SH+'property')){
   const paths=objects(graph,c,SH+'path');if(paths.length!==1||paths[0].termType!=='NamedNode')throw new Error('Kohdemuodon ominaisuuspolku puuttuu tai on monimutkainen.');
   if(paths[0].value==='http://www.w3.org/1999/02/22-rdf-syntax-ns#type')throw new Error('Kohteen rdf:type on tyypityksen vuoksi läsnä; sen rajoitteet vaativat laajemman viittausprofiilin.');
   if(['minCount','maxCount'].some(p=>objects(graph,c,SH+p).length>1))throw new Error('Kohdemuodon määrärajoite on epäselvä.');
   if(objects(graph,c,SH+'minCount').some(t=>readCount(t,0)!>0))throw new Error('Kohdemuoto vaatii sisältöä; pelkkä IRI ja rdf:type eivät riitä: '+shape.value);
   for(const t of objects(graph,c,SH+'maxCount'))readCount(t);
   if(graph.getPredicates(c,null,null).some(p=>p.value.startsWith(SH)&&![...annotations,'path','datatype','class','node','nodeKind','minCount','maxCount'].includes(p.value.slice(SH.length))))throw new Error('Kohdemuodon muuta sisältöä ei voida todeta valinnaiseksi: '+shape.value);
  }
 }
 return cls;
}
export function referenceNodes(tree:Tree,content:any){
 const nodes=new Map<string,{'@id':string;'@type':string}>();
 function visit(node:Tree,value:any){for(const row of node.fields){if(!(row.name in value))continue;for(const v of row.multi?value[row.name]:[value[row.name]]){if(row.mapping.representation==='iriReference'){
  if(typeof v!=='string'||!new RegExp(contract.representations.iriPattern).test(v)||v===row.mapping.classUri)throw new Error('Viittaus tarvitsee absoluuttisen instanssi-IRI:n; kohdeluokan IRI ei ole instanssin tunniste.');
  nodes.set(canonical([v,row.mapping.classUri]),{'@id':v,'@type':row.mapping.classUri!});
 }else if(row.child)visit(row.child,v);}}}
 visit(tree,content);const compare=(a:string,b:string)=>{const x=Array.from(a,c=>c.codePointAt(0)!),y=Array.from(b,c=>c.codePointAt(0)!);for(let i=0;i<Math.min(x.length,y.length);i++)if(x[i]!==y[i])return x[i]-y[i];return x.length-y.length;};return [...nodes.values()].sort((a,b)=>compare(a['@id'],b['@id'])||compare(a['@type'],b['@type']));
}
