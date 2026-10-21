import {WORKER_LIMIT_MS,type Finding} from './model';
export class BrowserGenerationError extends Error {findings:Finding[];finding:Finding;constructor(finding:Finding,findings?:Finding[]){super(finding.ruleId+' · '+finding.path+': '+finding.message);this.finding=finding;this.findings=findings||[finding];}}
export function runWorker<T=any>(request:unknown,signal?:AbortSignal,timeoutMs=WORKER_LIMIT_MS):Promise<T>{
 return new Promise((resolve,reject)=>{
  if(signal?.aborted){reject(new Error('Toiminto keskeytetty.'));return;}
  const worker=new Worker(new URL('./worker.ts',import.meta.url),{type:'module'});
  const close=()=>{clearTimeout(timer);signal?.removeEventListener('abort',abort);worker.terminate();};
  const abort=()=>{close();reject(new Error('Toiminto keskeytetty. Aineistoa ei muutettu.'));};
  const timer=setTimeout(()=>{close();reject(new Error('Aikaraja 15 s ylittyi. Worker pysäytettiin; aineistoa ei muutettu.'));},timeoutMs);
  signal?.addEventListener('abort',abort,{once:true});
  worker.onerror=()=>{close();reject(new Error('Workerin käynnistys tai suoritus epäonnistui.'));};
  worker.onmessage=event=>{close();if(event.data.ok)resolve(event.data.value);else reject(new BrowserGenerationError(event.data.error,event.data.findings));};
  worker.postMessage(request);
 });
}
