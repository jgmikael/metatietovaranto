/** Opt-in lexical repair. Never edits the input, infers a type, or fetches an IRI. */
import {Parser,Lexer,DataFactory,Store,type Quad,type Term} from 'n3';
import policy from './repair-policy.json';
import contract from './contract.json';
import {canonical,sha256,bytes,profileBody,FILE_LIMIT,TRIPLE_LIMIT,type SourceFile,type ImportedProfile,type RepairChange,type RepairReport} from './model';
const SH='http://www.w3.org/ns/shacl#',XSD='http://www.w3.org/2001/XMLSchema#';
const named=DataFactory.namedNode;
export class RepairError extends Error {constructor(public code:string,message:string){super(message);}}
function stop(code:string,message:string):never{throw new RepairError(code,message);}
type Token={type:string;value:string;line:number;start:number;end:number;endLine?:number};
type Located={quad:Quad;start:number;end:number;line:number;prefixes:Record<string,string>};
const termKey=(t:Term)=>[t.termType,t.value,...(t.termType==='Literal'?[t.datatype.value,t.language]:[])];
const quadKey=(q:Quad)=>canonical([q.subject,q.predicate,q.object,q.graph].map(termKey));
function parseLocated(file:SourceFile,index:number){
 const offsets=[0];for(let i=0;i<file.content.length;i++){if(file.content[i]==='\r'){if(file.content[i+1]==='\n')i++;offsets.push(i+1);}else if(file.content[i]==='\n')offsets.push(i+1);}
 let literal:Token|null=null,end=0,serial=0,triples=0;
 const located:Located[]=[],prefixes:Record<string,string>=Object.create(null);
 const parser=new Parser({format:'text/turtle',blankNodePrefix:'source-file'+index+'_',factory:{...DataFactory,
  // Separate namespaces for explicit labels and generated nodes; stable across the two parses.
  blankNode:(value?:string)=>DataFactory.blankNode(value??'auto-file'+index+'-'+serial++),
  quad:(s:any,p:any,o:any,g?:any)=>{
   if(++triples>TRIPLE_LIMIT)stop('REPAIR_LIMIT','Korjauksen kolmikkoraja ylittyi.');
   const q=DataFactory.quad(s,p,o,g);
   if(p.value===SH+'datatype'&&o.termType==='Literal'&&literal&&o.value===literal.value){
    const start=offsets[literal.line-1]+literal.start;
    if(!Number.isInteger(start)||end<=start||end>file.content.length)stop('REPAIR_LOCATION','Literalin lähdealuetta ei voitu yksilöidä.');
    located.push({quad:q,start,end,line:literal.line,prefixes:{...prefixes}});
   }
   return q;
  }}});
 // N3 2.13.12's public named token observers are not yet declared in @types/n3.
 const observers={onPrefix:(prefix:string,iri:Term)=>{prefixes[prefix]=iri.value;},onToken:(token:Token)=>{
  if(token.type==='literal'){literal=token;end=offsets[(token.endLine||token.line)-1]+token.end;}
  else if((token.type==='type'||token.type==='typeIRI')&&literal)end=offsets[(token.endLine||token.line)-1]+token.end;
  else if(['IRI','prefixed'].includes(token.type))literal=null;
 },onTokenEnd:(token:Token)=>{if(!['literal','type','typeIRI'].includes(token.type))literal=null;}};
 let quads:Quad[];try{quads=(parser.parse as unknown as (s:string,o:typeof observers)=>Quad[])(file.content,observers);}catch(e){if(e instanceof RepairError)throw e;stop('REPAIR_SYNTAX','Korjaus edellyttää jäsentyvää Turtlea: '+(e as Error).message);}
 if(quads.some(q=>q.graph.termType!=='DefaultGraph'||[q.subject,q.predicate,q.object].some(t=>!['NamedNode','BlankNode','Literal'].includes(t.termType))))stop('REPAIR_PROFILE','Vain Turtle / RDF 1.1 on tuettu.');
 return {quads,located,graph:new Store(quads)};
}
async function checked(sources:SourceFile[]){
 if(!sources.length||sources.length>10||sources.reduce((n,s)=>n+bytes(s.content),0)>FILE_LIMIT)stop('REPAIR_LIMIT','Korjauksen lähderaja on 10 tiedostoa / 256 KiB.');
 for(const file of sources)if(await sha256(file.content)!==file.sha256)stop('SOURCE_HASH','Korjauksen lähdetarkiste ei täsmää: '+file.name);
 const parsed=sources.map(parseLocated);
 if(parsed.reduce((n,p)=>n+p.quads.length,0)>TRIPLE_LIMIT)stop('REPAIR_LIMIT','Korjauksen yhteinen kolmikkoraja 10 000 ylittyi.');
 return parsed;
}
export async function repairProposals(profile:ImportedProfile){
 if(profile.repair)stop('REPAIR_ORIGINAL_REQUIRED','Muodosta uusi korjaus alkuperäisestä profiilista. Korjauksia ei ketjuteta.');
 if(await sha256(canonical(profileBody(profile)))!==profile.sha256)stop('PROFILE_HASH','Alkuperäisen profiilin tarkiste ei täsmää.');
 const parsed=await checked(profile.sources),graph=new Store(parsed.flatMap(p=>p.quads));
 const changes:RepairChange[]=[],skipped:{sourceName:string;line:number;reason:string}[]=[];
 for(const [sourceIndex,item] of parsed.entries())for(const found of item.located){
  const {quad,start,end,line}=found,term=quad.object,file=profile.sources[sourceIndex];
  if(term.termType!=='Literal')continue;
  const before=file.content.slice(start,end);
  const eligible=!term.language&&term.datatype.value===XSD+'string'&&policy.datatypes.includes(term.value)&&/^[A-Za-z][A-Za-z0-9+.-]*:[^\s<>"{}|^`\\]+$/.test(term.value);
  if(!eligible){skipped.push({sourceName:file.name,line,reason:'Tuntematon, kielimerkitty tai korjauslistan ulkopuolinen arvo; ei automaattista korjausta.'});continue;}
  // Token spans may include ^^xsd:string. Refuse to remove comments in that span.
  // Reparse the isolated object, ensuring it identifies precisely this RDF term.
  let isolated:Quad[];try{isolated=new Parser({format:'text/turtle'}).parse(Object.entries(found.prefixes).map(([p,u])=>'@prefix '+p+': <'+u+'> .\n').join('')+'<urn:repair:s> <urn:repair:p> '+before+' .');}catch{stop('REPAIR_LOCATION','Lähdealue ei vastaa yhtä Turtle-objektia.');}
  if(isolated!.length!==1||!isolated![0].object.equals(term)||!['"',"'"].includes(before[0])||new Lexer({comments:true}).tokenize(before).some(t=>t.type==='comment')){
   stop('REPAIR_LOCATION','Lähdealue on epäselvä tai sisältää säilytettävän kommentin. Korjaa tämä kohta käsin.');
  }
  changes.push({id:sourceIndex+':'+start+':'+end,sourceIndex,sourceName:file.name,line,start,end,
   propertyShapeUri:quad.subject.termType==='NamedNode'?quad.subject.value:null,
   nodeShapes:graph.getSubjects(named(SH+'property'),quad.subject,null).filter(t=>t.termType==='NamedNode').map(t=>t.value).sort(),
   paths:graph.getObjects(quad.subject,named(SH+'path'),null).map(t=>t.value).sort(),before,after:'<'+term.value+'>',datatypeIri:term.value,
   limitation:contract.datatypes.some(name=>XSD+name===term.value)?'Vain termikorjaus. Muut generointirajoitteet tarkistetaan erikseen.':'Tietotyypin generointi ei ole tuettu; kielitietoa ei poisteta.'});
 }
 if(changes.length>200)stop('REPAIR_LIMIT','Enintään 200 korjausehdotusta kerralla.');
 if(new Set(changes.map(c=>c.id)).size!==changes.length)stop('REPAIR_LOCATION','Sama lähdealue kohdistui useaan lauseeseen.');
 return {ruleId:policy.ruleId,version:policy.version,changes,skipped};
}
export async function applyRepairs(profile:ImportedProfile,selected:string[]){
 const proposals=await repairProposals(profile);
 if(!selected.length||selected.length>200||new Set(selected).size!==selected.length||selected.some(id=>!proposals.changes.some(c=>c.id===id)))stop('REPAIR_SELECTION','Valitse vain yksilöidyt korjausehdotukset.');
 const changes=proposals.changes.filter(c=>selected.includes(c.id));
 const sources:SourceFile[]=[];
 for(const [index,file] of profile.sources.entries()){
  let content=file.content;
  for(const c of changes.filter(c=>c.sourceIndex===index).sort((a,b)=>b.start-a.start))content=content.slice(0,c.start)+c.after+content.slice(c.end);
  sources.push({...file,content,sha256:await sha256(content)});
 }
 // Stable generated blank nodes preserve structural occurrence identities. Compare full datasets,
 // including multiplicity; this is a constrained edit check, not general RDF isomorphism.
 const before=await checked(profile.sources),after=await checked(sources);
 for(let i=0;i<before.length;i++){
  const selectedLocations=before[i].located.filter(l=>changes.some(c=>c.sourceIndex===i&&c.start===l.start&&c.end===l.end));
  const expected=before[i].quads.map(q=>selectedLocations.some(l=>l.quad===q)?DataFactory.quad(q.subject,q.predicate,named(q.object.value),q.graph):q).map(quadKey).sort();
  if(canonical(expected)!==canonical(after[i].quads.map(quadKey).sort()))stop('REPAIR_GRAPH','Korjattu graafi poikkeaa hyväksytyistä objektimuutoksista.');
 }
 const repair:RepairReport={ruleId:policy.ruleId,version:policy.version,approved:true,originalProfileSha256:profile.sha256,originalSources:profile.sources,correctedSourceHashes:sources.map(s=>s.sha256),changes};
 return {sources,repair};
}
export async function verifyRepair(profile:ImportedProfile){
 if(!profile.repair)return;
 const report=profile.repair;
 if(report.ruleId!==policy.ruleId||report.version!==policy.version||report.approved!==true)stop('REPAIR_REPORT','Tuntematon tai hyväksymätön korjausraportti.');
 const original:ImportedProfile={...profile,sources:report.originalSources,sha256:report.originalProfileSha256};delete original.repair;
 const computed=await applyRepairs(original,report.changes.map(c=>c.id));
 if(canonical(computed)!==canonical({sources:profile.sources,repair:report}))stop('REPAIR_REPORT','Korjausraportti tai aineisto ei vastaa sallittuja hyväksyttyjä muutoksia.');
}
