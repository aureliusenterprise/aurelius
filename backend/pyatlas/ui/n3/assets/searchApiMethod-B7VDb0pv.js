/*
 * Licensed to the Apache Software Foundation (ASF) under one or more
 * contributor license agreements.  See the NOTICE file distributed with
 * this work for additional information regarding copyright ownership.
 * The ASF licenses this file to You under the Apache License, Version 2.0
 * (the "License"); you may not use this file except in compliance with
 * the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
import{c as a,bp as s}from"./index-BpDEq3xb.js";const r=e=>{let t=`${a("urlV2")}/search`;return e?`${t}/${e}`:t},f=["type","position"],S=!0,E=100,b=e=>{if(e==null)return;const t=Number(e);if(!(!Number.isFinite(t)||t<0))return t},h=e=>typeof e!="number"||!Number.isFinite(e)||e<=0||e<=1?1:2,p=e=>{const t={limit:e.limit,offset:e.offset,guid:e.guid,sortBy:e.isSorted?"name":void 0,sortOrder:e.isSorted?"ASCENDING":void 0,disableDefaultSorting:!e.isSorted,excludeDeletedEntities:!e.showDeleted,includeSubClassifications:!0,includeSubTypes:!0,includeClassificationAttributes:!0,relation:e.relation,getApproximateCount:e.getApproximateCount};return e.extraAttributes&&e.extraAttributes.length>0&&(t.attributes=e.extraAttributes),t},l=e=>{const t=[];for(const[i,n]of Object.entries(e))if(n!=null){if(i==="attributes"&&Array.isArray(n)){n.forEach(o=>{t.push(`${encodeURIComponent(i)}=${encodeURIComponent(String(o))}`)});continue}if(typeof n=="boolean"){t.push(`${encodeURIComponent(i)}=${encodeURIComponent(n?"true":"false")}`);continue}t.push(`${encodeURIComponent(i)}=${encodeURIComponent(String(n))}`)}return t.join("&")},u=(e,t)=>{const i={method:t=="dsl"?"GET":"POST",...e};return s(r(t||""),i)},T=e=>{const t={method:"POST",...e};return s(r("relations"),t)},A=(e,t)=>{const i={method:"GET",...t};return s(r(e),i)},g=e=>{const t={method:"GET",...e};return s(r("relationship"),t)},I=e=>{const t=l(e.params),i=`${r("relationship")}?${t}`;return s(i,{method:"GET"})},c="__timestamp",d=e=>({typeName:"_ALL_ENTITY_TYPES",excludeDeletedEntities:!0,includeClassificationAttributes:!0,includeSubTypes:!0,includeSubClassifications:e.includeSubClassifications,limit:e.limit,offset:0,tagFilters:null,entityFilters:null,classification:null,termName:null,relationshipFilters:null,attributes:["__timestamp"],sortBy:c,sortOrder:"DESCENDING"}),R=()=>u({data:d({limit:7,includeSubClassifications:!1})},"basic");export{E as D,f as S,A as a,R as b,u as c,h as d,I as e,p as f,T as g,S as h,g as i,b as n};
