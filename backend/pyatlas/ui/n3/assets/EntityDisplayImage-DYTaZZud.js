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
import{a as l,j as e,aW as u,z as f}from"./mui-BfQyULi0.js";import{aW as r,aX as j}from"./index-BpDEq3xb.js";const b=({entity:a,width:n,height:g,avatarDisplay:m,isProcess:h})=>{const[c,i]=l.useState(null),[o,x]=l.useState({[a.guid]:!1});return l.useEffect(()=>{(async()=>{let t={...a,isProcess:h},s=r({entityData:t});try{const d=(await j.get(s,{responseType:"blob"})).headers["content-type"];if(d&&d.startsWith("image/")){let p={[t.guid]:s};x(p),i(r({entityData:t}))}else i(r({entityData:t,errorUrl:s}))}catch{i(r({entityData:t,errorUrl:s}))}})()},[]),c!=null?e.jsx("div",{className:"search-result-table-name-col","data-cy":"entityIcon",children:o[a.guid]!==!1?m==null?e.jsx("img",{className:"search-result-table-img",id:a.guid,"data-cy":a.guid,src:o[a.guid],alt:"Entity Icon"}):e.jsx(u,{alt:"entityImg",src:o[a.guid],sx:{width:n,height:g},variant:"square"}):m==null?e.jsx("img",{className:"search-result-table-img",id:a.guid,"data-cy":a.guid,src:c,alt:"Entity Icon"}):e.jsx(u,{alt:"entityImg",src:c,sx:{width:n,height:g}})}):e.jsx("div",{children:e.jsx(f,{variant:"circular",width:22,height:20})})};export{b as D};
