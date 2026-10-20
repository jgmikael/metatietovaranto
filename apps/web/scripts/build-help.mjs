import {readFileSync,mkdirSync,writeFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {compileHelp} from '../help/compiler.mjs';
import {sections,groups} from '../help/config.mjs';
const markdown=readFileSync(new URL('../../../docs/pages-kayttoohje.md',import.meta.url),'utf8');
const output=new URL('../src/help/generated/help.json',import.meta.url);
const json=JSON.stringify(compileHelp(markdown,sections,groups));
if(process.argv.includes('--check')){if(readFileSync(output,'utf8')!==json)throw new Error('Help JSON is stale; run npm run build:help');}
else{mkdirSync(fileURLToPath(new URL('.',output)),{recursive:true});writeFileSync(output,json);}
