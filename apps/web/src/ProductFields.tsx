import React from 'react';
import type {Input,Org} from './types';
import {metadataFields as textFields} from './types';
export {metadataFields} from './types';
type Metadata=Pick<Input,typeof textFields[number][0]|'providerOrganizationId'>;
/** Same basic metadata form in server drafts and local experiments. */
export function ProductMetadataFields<T extends Metadata>({value,onChange,organizations,required=true}:{value:T;onChange:(value:T)=>void;organizations:Org[];required?:boolean}){
 return <><label htmlFor="provider">Tarjoaja</label><select id="provider" required={required} value={value.providerOrganizationId} onChange={e=>onChange({...value,providerOrganizationId:e.target.value})}><option value="">Valitse organisaatio</option>{organizations.map(org=><option key={org.id} value={org.id}>{org.legalName||'(Nimi puuttuu)'} · {org.id}</option>)}</select>{textFields.map(([name,label,max])=><label key={name}>{label}{max>500?<textarea required={required} maxLength={max} value={value[name]} onChange={e=>onChange({...value,[name]:e.target.value})}/>:<input required={required} maxLength={max} value={value[name]} onChange={e=>onChange({...value,[name]:e.target.value})}/>}</label>)}</>;
}
