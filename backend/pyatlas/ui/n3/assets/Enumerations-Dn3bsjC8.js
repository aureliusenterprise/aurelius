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
import{a as B,j as g,q as N}from"./mui-BfQyULi0.js";import{u as P,f as R,i as p,bs as $,B as t,bt as k,a9 as q,s as F}from"./index-BpDEq3xb.js";import{E as I}from"./EnumCreateUpdate-BCUtJq4F.js";import{u as U}from"./Router-Bbhl_1y6.js";import"./redux-BhQjujQg.js";import"./utils-vGcjcrS1.js";import"./router-D-5TF13k.js";const M=()=>{const x=P(),{enumObj:i}=R(c=>c.enum),{enumDefs:r}=(i==null?void 0:i.data)||{},{control:D,handleSubmit:S,watch:v,setValue:b,reset:d,formState:{isDirty:j,isSubmitting:C}}=U(),s=B.useRef(null),T=async c=>{let w={...c},m=!1,f=!1;const{enumType:u="",enumValues:h=[]}=w||{},a=p(h)?[]:h.map(e=>e.value);let n=[];const E=p(r)?{}:r==null?void 0:r.find(e=>e.name===u),{elementDefs:A=[]}=E||{};if(p(E))f=!0;else{let e=A||[];e.length===a.length?e.forEach(l=>{a.includes(l.value)||(m=!0)}):m=!0}let o=[];a==null||a.forEach((e,l)=>{o==null||o.push({ordinal:l+1,value:e})}),n==null||n.push({name:u,elementDefs:o});let y={enumDefs:n};try{f?(await $(y),t.dismiss(s.current),s.current=t.success(`Enumeration ${u} 
           added
             successfully`)):m?(await k(y),t.dismiss(s.current),s.current=t.success(`Enumeration ${u} updated
             successfully`)):(t.dismiss(s.current),s.current=t.success("No updated values")),d({enumType:"",enumValues:[]}),x(q())}catch(e){F(e,s)}};return g.jsx(N,{gap:2,paddingTop:"2rem",paddingBottom:"2rem",children:g.jsx(I,{control:D,handleSubmit:S,setValue:b,reset:d,watch:v,isSubmitting:C,onSubmit:T,isDirty:j})})};export{M as default};
