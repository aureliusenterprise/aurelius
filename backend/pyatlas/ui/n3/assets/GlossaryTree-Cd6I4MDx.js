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
import{a as c,j as o}from"./mui-BfQyULi0.js";import{B as w}from"./SideBarTree-BhRV-trs.js";import{u as A,f as M,x,i as y,M as N,N as R,v as I}from"./index-BpDEq3xb.js";import"./Router-Bbhl_1y6.js";import"./router-D-5TF13k.js";import"./utils-vGcjcrS1.js";import"./redux-BhQjujQg.js";import"./AddUpdateGlossaryForm-M_do7PtM.js";import"./DetailPageAttributes-GnblffY8.js";import"./EditOutlined-B-2hySUn.js";import"./index-CTgKUtoL.js";import"./ShowMoreView-ByhJWQxk.js";import"./Search-BzH4AsqA.js";import"./EntityStatus-Cmv0MvKm.js";import"./AddCircleOutline-DkL39vz6.js";import"./AssignCategory-CsYLzbX9.js";import"./Refresh-2ij1WC0q.js";const $=({sideBarOpen:D,searchTerm:S})=>{const m=A(),{glossaryData:d,loading:v}=M(a=>a.glossary),[r,B]=c.useState(!0),[l,E]=c.useState([]);c.useEffect(()=>{m(x())},[]);const O=async()=>{await m(x())};c.useEffect(()=>{let a=[];a=d!=null?d.map(t=>{var s;let e=[];(s=t==null?void 0:t.categories)==null||s.map(i=>{i.parentCategoryGuid!=null&&e.push(i)});const h=i=>y(i.children)?[]:i.children.map(n=>{const f=G=>G?e.map(p=>{if(p.parentCategoryGuid==G)return{name:p.displayText,id:p.displayText,children:f(p.categoryGuid),types:"child",parent:i.parent,cGuid:r?p.termGuid:p.categoryGuid,guid:t.guid}}).filter(Boolean):[];if(n.parentCategoryGuid==null)return{name:n.displayText,id:n.displayText,children:f(n.categoryGuid),types:"child",parent:i.parent,cGuid:r?n.termGuid:n.categoryGuid,guid:t.guid}}).filter(Boolean);let u=t.name,T=h(r?{children:t==null?void 0:t.terms,parent:t.name}:{children:t==null?void 0:t.categories,parent:t.name});return{[u]:{name:u,children:T||[],id:t.guid,types:"parent",parent:u,guid:t.guid}}}):[],E(a)},[d,r]);const k=c.useMemo(()=>{const a=t=>I(t.map(e=>({id:e==null?void 0:e.name,label:e==null?void 0:e.name,children:(e==null?void 0:e.children)!=null?a(e.children.filter(Boolean)):[],types:e==null?void 0:e.types,parent:e==null?void 0:e.parent,guid:e==null?void 0:e.guid,cGuid:e==null?void 0:e.cGuid})),["label"]);return t=>t.map(e=>({id:e[Object.keys(e)[0]].name,label:e[Object.keys(e)[0]].name,children:a(e[Object.keys(e)[0]].children),types:e[Object.keys(e)[0]].types,parent:e[Object.keys(e)[0]].parent,guid:e[Object.keys(e)[0]].guid}))},[r]),C=c.useMemo(()=>y(d)?R():k(N(l)),[r,l]);return o.jsx(w,{treeData:C,treeName:"Glossary",setisEmptyServicetype:B,isEmptyServicetype:r,refreshData:O,sideBarOpen:D,loader:v,searchTerm:S})};export{$ as default};
