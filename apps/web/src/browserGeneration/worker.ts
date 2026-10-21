/// <reference lib="webworker" />
import {execute,GenerationError} from './engine';
// No imports, loaders or RDF pointers are fetched on behalf of a source file.
self.onmessage=async(event:MessageEvent)=>{
 try{self.postMessage({ok:true,value:await execute(event.data)});}
 catch(e){self.postMessage({ok:false,error:e instanceof GenerationError?e.finding:{ruleId:'GENERATION_ERROR',path:'',message:(e as Error).message},findings:e instanceof GenerationError?e.findings:undefined});}
};
