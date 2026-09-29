{{/*
Expand the name of the chart.
*/}}
{{- define "reverse-proxy.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "reverse-proxy.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "reverse-proxy.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "reverse-proxy.labels" -}}
helm.sh/chart: {{ include "reverse-proxy.chart" . }}
{{ include "reverse-proxy.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "reverse-proxy.selectorLabels" -}}
app.kubernetes.io/name: {{ include "reverse-proxy.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}


{{/* Environment of the tenant-sync containers (aurelius-admin proxy sync). */}}
{{- define "reverse-proxy.syncEnv" -}}
- name: AURELIUS_PUBLIC_URL
  value: "https://{{ .Values.global.external_hostname }}"
- name: AURELIUS_NS
  value: {{ .Release.Namespace | quote }}
- name: KEYCLOAK_URL
  value: "http://keycloak:8080/{{ .Release.Namespace }}/auth"
- name: ES_URL
  value: "http://elastic-search-es-http:9200"
# pyatlas' own user: reads the tenant registry (realm client secrets, Kibana keys), nothing else
- name: ES_USERNAME
  value: aurelius_pyatlas
- name: ES_PASSWORD
  valueFrom:
    secretKeyRef: { name: aurelius-secrets, key: pyatlas-es-password }
- name: TENANTS_DIR
  value: /tenants
{{- end }}
