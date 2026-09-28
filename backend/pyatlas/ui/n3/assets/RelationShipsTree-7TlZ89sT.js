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
import{a,j as u}from"./mui-BfQyULi0.js";import{u as f,f as h,b7 as i,v as d}from"./index-BpDEq3xb.js";import{B as D}from"./SideBarTree-BhRV-trs.js";import"./redux-BhQjujQg.js";import"./utils-vGcjcrS1.js";import"./Router-Bbhl_1y6.js";import"./router-D-5TF13k.js";import"./AddUpdateGlossaryForm-M_do7PtM.js";import"./DetailPageAttributes-GnblffY8.js";import"./EditOutlined-B-2hySUn.js";import"./index-CTgKUtoL.js";import"./ShowMoreView-ByhJWQxk.js";import"./Search-BzH4AsqA.js";import"./EntityStatus-Cmv0MvKm.js";import"./AddCircleOutline-DkL39vz6.js";import"./AssignCategory-CsYLzbX9.js";import"./Refresh-2ij1WC0q.js";const V=o=>{const{sideBarOpen:p,searchTerm:m}=o,r=f(),{relationships:t,loading:n}=h(e=>e.relationships);a.useEffect(()=>{r(i())},[r]);const s=a.useMemo(()=>t!=null&&t.relationshipDefs?t.relationshipDefs.map(e=>({id:e.name,label:e.name,childrenData:[],guid:e.guid})):[],[t]),c=a.useMemo(()=>d(s,["label"]),[s]),l=async()=>{r(i())};return u.jsx(D,{treeData:c,treeName:"Relationships",refreshData:l,sideBarOpen:p,loader:n,searchTerm:m})};export{V as default};
