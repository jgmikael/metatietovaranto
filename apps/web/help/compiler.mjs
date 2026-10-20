import {unified} from 'unified';
import remarkParse from 'remark-parse';
import remarkGfm from 'remark-gfm';
export const plain=node=>node.value??(node.children||[]).map(plain).join('');
const allowed=new Set(['root','paragraph','text','heading','strong','emphasis','delete','inlineCode','code','link','list','listItem','table','tableRow','tableCell','blockquote','thematicBreak','break']);
export function safeUrl(url){return typeof url==='string'&&!/[\u0000-\u0020\u007f]/.test(url)&&(!/^[^/?#]*:/.test(url)||/^https?:/i.test(url))&&!url.startsWith('//');}
export function parseMarkdown(source){
 const ast=unified().use(remarkParse).use(remarkGfm).parse(source);
 function clean(node){
  if(node.type==='html'||node.type==='image')return null;
  if(!allowed.has(node.type))throw new Error('Unsupported Markdown node: '+node.type);
  if(node.type==='link'&&!safeUrl(node.url))return {type:'text',value:plain(node)};
  const result={type:node.type};for(const key of ['value','url','title','depth','ordered','start','lang','checked'])if(node[key]!==undefined&&node[key]!==null)result[key]=node[key];
  if(node.children)result.children=node.children.map(clean).filter(Boolean);return result;
 }
 return clean(ast);
}
export function compileHelp(markdown,sections,groups){
 const document=parseMarkdown(markdown),byTitle=new Map(sections.map(([id,title])=>[title,id])),found=new Set(),rows=new Map(),headings=[];let section='';
 function visit(node){
  if(node.type==='heading'){const title=plain(node),id=byTitle.get(title);if(!id)throw new Error('Missing stable heading ID: '+title);if(found.has(id))throw new Error('Duplicate heading: '+id);found.add(id);node.id=id;section=id;headings.push({id,title,depth:node.depth});}
  if(node.type==='table')for(const row of node.children.slice(1)){const key=section+'|'+plain(row.children[0]).trim();if(rows.has(key))throw new Error('Duplicate field row: '+key);rows.set(key,row.children);}
  for(const child of node.children||[])visit(child);
 }
 visit(document);
 for(const [id] of sections)if(!found.has(id))throw new Error('Unused section ID: '+id);
 const fields={};
 for(const [group,[id,labels]] of Object.entries(groups))for(const label of labels){const row=rows.get(id+'|'+label);if(!row)throw new Error('Missing field help: '+id+' / '+label);fields[group+'.'+label]={section:id,label,description:row[1]?.children||[],example:row[2]?.children||[]};}
 return {document,sections:headings,fields};
}
