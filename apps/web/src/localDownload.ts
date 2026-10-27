export function downloadLocal(content:string,name:string,mediaType='application/json'){
 const url=URL.createObjectURL(new Blob([content],{type:mediaType})),link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);
}
