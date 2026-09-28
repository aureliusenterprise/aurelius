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
import{a as n,j as R}from"./mui-BfQyULi0.js";import{B as F}from"./SideBarTree-BhRV-trs.js";import{u as L,f as V,t as l,i as c,ah as o,v as u,j as w,ab as H}from"./index-BpDEq3xb.js";import"./Router-Bbhl_1y6.js";import"./router-D-5TF13k.js";import"./utils-vGcjcrS1.js";import"./redux-BhQjujQg.js";import"./AddUpdateGlossaryForm-M_do7PtM.js";import"./DetailPageAttributes-GnblffY8.js";import"./EditOutlined-B-2hySUn.js";import"./index-CTgKUtoL.js";import"./ShowMoreView-ByhJWQxk.js";import"./Search-BzH4AsqA.js";import"./EntityStatus-Cmv0MvKm.js";import"./AddCircleOutline-DkL39vz6.js";import"./AssignCategory-CsYLzbX9.js";import"./Refresh-2ij1WC0q.js";const b=({sideBarOpen:S,searchTerm:d})=>{const m=L(),{savedSearchData:i}=V(r=>r.savedSearch),{relationshipSearch:f={}}=H||{},[h,y]=n.useState([]),[T,p]=n.useState(!1);n.useEffect(()=>{p(!0),m(l()),p(!1)},[]);const A=async()=>{p(!0),await m(l()),p(!1)};n.useEffect(()=>{let r=[],t=[{name:"Advanced Search",searchType:"ADVANCED"},{name:"Basic Search",searchType:"BASIC"},...f?[{name:"Relationship Search",searchType:"BASIC_RELATIONSHIP"}]:[]],e=c(i)?o(t,"searchType"):o(i,"searchType");for(let a in e){const C=s=>{if(s=="BASIC")return"Basic Search";if(s=="ADVANCED")return"Advanced Search";if(s=="BASIC_RELATIONSHIP")return"Relationship Search"},E=(s,x)=>!w(s)||c(s.length)?[]:s.map(N=>({name:N.name,children:[],types:"child",parent:x}));let I=C(a),g=c(i)?[]:E(e[a],a);r.push({name:I,children:g,types:"parent",parent:a})}const B=r.map(a=>a.parent);t.forEach(a=>{B.includes(a.searchType)||r.push({name:a.name,children:[],types:"parent",parent:a.searchType})}),y(r)},[i]);const D=n.useMemo(()=>{const r=t=>u(t==null?void 0:t.map(e=>({id:e==null?void 0:e.name,label:e==null?void 0:e.name,children:(e==null?void 0:e.children)!=null?r(e.children.filter(Boolean)):[],types:e==null?void 0:e.types,parent:e==null?void 0:e.parent})),["label"]);return t=>t.map(e=>({id:e.name,label:e.name,children:r(e.children),types:e.types,parent:e.parent}))},[]),v=n.useMemo(()=>u(D(h),["label"]),[h]);return R.jsx(F,{treeData:v,treeName:"CustomFilters",isEmptyServicetype:!0,refreshData:A,sideBarOpen:S,loader:T,searchTerm:d})};export{b as default};
