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
import{a,j as D}from"./mui-BfQyULi0.js";import{u as l,f as M,aI as o,i as B,v as h,N as x}from"./index-BpDEq3xb.js";import{B as E}from"./SideBarTree-BhRV-trs.js";import"./redux-BhQjujQg.js";import"./utils-vGcjcrS1.js";import"./Router-Bbhl_1y6.js";import"./router-D-5TF13k.js";import"./AddUpdateGlossaryForm-M_do7PtM.js";import"./DetailPageAttributes-GnblffY8.js";import"./EditOutlined-B-2hySUn.js";import"./index-CTgKUtoL.js";import"./ShowMoreView-ByhJWQxk.js";import"./Search-BzH4AsqA.js";import"./EntityStatus-Cmv0MvKm.js";import"./AddCircleOutline-DkL39vz6.js";import"./AssignCategory-CsYLzbX9.js";import"./Refresh-2ij1WC0q.js";const C=m=>{const{sideBarOpen:p,searchTerm:n}=m,i=l(),[e,u]=a.useState([]),{businessMetaData:t,loading:c}=M(s=>s.businessMetaData);a.useEffect(()=>{i(o())},[]),a.useEffect(()=>{if((t==null?void 0:t.businessMetadataDefs)!=null){const s=t.businessMetadataDefs.map(r=>({id:r.name,label:r.name,childrenData:[],guid:r.guid}));u(s)}},[t]);const d=async()=>{await i(o())},f=a.useMemo(()=>B(e)?x():h(e,["label"]),[e]);return D.jsx(E,{treeData:f,treeName:"Business MetaData",refreshData:d,sideBarOpen:p,loader:c,searchTerm:n})};export{C as default};
