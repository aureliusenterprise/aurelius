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
import{j as t,q as m,aD as p}from"./mui-BfQyULi0.js";import{a as u,d,i as x}from"./Router-Bbhl_1y6.js";import{i as a,j as f,ap as e}from"./index-BpDEq3xb.js";const c=r=>{if(a(r))return"Type Details";const n=r==null?void 0:r.category,s=r==null?void 0:r.name;return n!=null&&s!=null&&e[String(n)]?`${e[String(n)]} Type Details: ${String(s)}`:s!=null?`Type Details: ${String(s)}`:"Type Details"},D=({open:r,onClose:n,detailObject:s,maxWidth:l="md"})=>t.jsx(u,{open:r,onClose:n,title:c(s),footer:!1,button1Handler:void 0,button2Handler:void 0,maxWidth:l,children:t.jsx(d,{variant:"outlined",children:a(s)?"No Record Found":Object.entries(s).sort(([i],[o])=>i.localeCompare(o)).map(([i,o])=>t.jsxs("div",{children:[t.jsxs(m,{direction:"row",spacing:4,marginBottom:1,marginTop:1,children:[t.jsx("div",{className:"text-truncate-flex text-left fw-600",children:`${i} ${f(o)?`(${o.length})`:""}`}),t.jsx("div",{className:"text-truncate-flex text-left",children:x(o,void 0,void 0,void 0,"properties")})]}),t.jsx(p,{})]},i))})});export{D as T};
