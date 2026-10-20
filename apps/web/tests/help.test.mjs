import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {compileHelp,parseMarkdown,safeUrl} from '../help/compiler.mjs';
import {sections,groups} from '../help/config.mjs';
const source=readFileSync(new URL('../../../docs/pages-kayttoohje.md',import.meta.url),'utf8');
test('all pinned sections and field rows have actual explanations',()=>{
 const help=compileHelp(source,sections,groups);
 assert.equal(help.sections.length,sections.length);assert.ok(Object.keys(help.fields).length>100);
 for(const entry of Object.values(help.fields)){assert.ok(entry.description.length);assert.ok(help.sections.some(s=>s.id===entry.section));}
});
test('missing and duplicate sections and field rows fail build',()=>{
 const row=source.split('\n').find(line=>line.startsWith('| Hakusana |'));
 assert.throws(()=>compileHelp(source.replace(row,row+'\n'+row),sections,groups),/Duplicate field row/);
 assert.throws(()=>compileHelp(source,[...sections,['missing','Missing heading']],groups),/Unused section/);
 assert.throws(()=>compileHelp(source+'\n## 0. Julkisen esittelyn selaaminen\n',sections,groups),/Duplicate heading/);
 assert.throws(()=>compileHelp(source,sections,{bad:['tallennus',['Puuttuva kenttä']]}),/Missing field help/);
 assert.throws(()=>compileHelp(source+'\n## Unknown\n',sections,groups),/Missing stable heading/);
});
test('raw HTML, images, event attributes and unsafe links are never renderer nodes',()=>{
 const nodes=parseMarkdown('<script>alert(1)</script>\n\n<img src=x onerror=alert(1)>\n\n[run](javascript:alert) [encoded](java&#x73;cript:alert) ![tracking](https://example.org/x)\n\n```js\nalert(1)\n```');
 const encoded=JSON.stringify(nodes);
 assert.ok(!encoded.includes('"type":"html"'));assert.ok(!encoded.includes('"type":"image"'));assert.ok(!encoded.includes('"url"'));assert.ok(encoded.includes('"type":"code"'));
 for(const url of ['javascript:alert(1)','data:text/html,x','//example.org','https:\n//example.org','JaVaScRiPt:alert'])assert.equal(safeUrl(url),false,url);
 assert.equal(safeUrl('https://example.org'),true);assert.equal(safeUrl('../fixtures/demo.ttl'),true);
});
