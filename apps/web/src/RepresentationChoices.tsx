import {HelpLabel,helpFieldAttributes} from './help/Help';
import React,{useState,useId} from 'react';
type Choices={names:{semanticPath:string[];fieldName:string}[];references?:string[][];languageRepresentation?:'valueLanguage-v1'};
export function RepresentationChoices({value,onChange,disabled=false}:{value:Choices;onChange:(value:Choices)=>void;disabled?:boolean}){
 const id=useId();
 const [path,setPath]=useState(''),[fieldName,setFieldName]=useState('');
 const semanticPath=path.split('\n').map(v=>v.trim()).filter(Boolean);
 return <fieldset disabled={disabled}><legend>Esitysvalinnat ennen mapping-ehdotusta</legend><p>Nämä valinnat ovat käytettävissä myös estyneen ehdotuksen jälkeen. Ne eivät muuta SHACLin tietotyyppejä tai kardinaliteetteja. Tarkista tuki valintojen jälkeen uudelleen.</p>
 <HelpLabel className="check"><input type="checkbox" checked={!!value.languageRepresentation} onChange={e=>{const next={...value};if(e.target.checked)next.languageRepresentation='valueLanguage-v1';else delete next.languageRepresentation;onChange(next);}}/>Hyväksyn kieliarvojen value/language-v1-esityksen</HelpLabel>
 <p>Kieliarvo on esimerkiksi {JSON.stringify({value:'teksti',language:'fi'})}. Tuetaan pienaakkosin 2–3 kirjaimen kieli ja valinnainen kirjoitusjärjestelmä/alue. Kielitietoa ei poisteta eikä oletuskieltä keksitä.</p>
 <HelpLabel htmlFor={id+'-path'}>Esitysvalinnan semanttinen IRI-polku (yksi ominaisuus-IRI rivillä)</HelpLabel><textarea {...helpFieldAttributes(id+'-path','Esitysvalinnan semanttinen IRI-polku (yksi ominaisuus-IRI rivillä)')} id={id+'-path'} value={path} maxLength={17000} onChange={e=>setPath(e.target.value)}/>
 <HelpLabel htmlFor={id+'-name'} helpKey="representation.Tarkastettu tekninen kenttänimi / Lisää tarkastettu kenttänimi">Tarkastettu tekninen kenttänimi</HelpLabel><input {...helpFieldAttributes(id+'-name','representation.Tarkastettu tekninen kenttänimi / Lisää tarkastettu kenttänimi')} id={id+'-name'} value={fieldName} maxLength={100} onChange={e=>setFieldName(e.target.value)}/>
 <button type="button" disabled={!semanticPath.length||semanticPath.length>8||!fieldName} onClick={()=>onChange({...value,names:[...value.names.filter(n=>JSON.stringify(n.semanticPath)!==JSON.stringify(semanticPath)),{semanticPath,fieldName}]})}>Lisää tarkastettu kenttänimi</button>
 <button type="button" disabled={!semanticPath.length||semanticPath.length>8} onClick={()=>onChange({...value,references:[...(value.references||[]).filter(p=>JSON.stringify(p)!==JSON.stringify(semanticPath)),semanticPath]})}>Esitä assosiaatio IRI-viittauksena</button>
 <p>Viittauksen arvo on kohdeolion instanssi-IRI, ei luokka-IRI. Valinta hyväksytään vain, jos lähderajoitteet sallivat pelkän viittauksen ja tyypitetyn kohdesolmun; sh:node tai pakollinen kohdesisältö estää tämän rajatun esityksen. Verkkokohteita ei haeta.</p>
 <ul>{value.names.map((n,i)=><li key={'n'+i}>Kenttänimi: {n.semanticPath.join(' → ')} = {n.fieldName} <button type="button" onClick={()=>onChange({...value,names:value.names.filter((_,j)=>i!==j)})}>Poista nimivalinta {i+1}</button></li>)}{value.references?.map((p,i)=><li key={'r'+i}>IRI-viittaus: {p.join(' → ')} <button type="button" onClick={()=>onChange({...value,references:value.references!.filter((_,j)=>i!==j)})}>Poista viittausvalinta {i+1}</button></li>)}</ul>
 </fieldset>;
}
