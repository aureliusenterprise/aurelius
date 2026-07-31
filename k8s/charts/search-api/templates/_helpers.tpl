{{/*
Common helper templates for search-api chart
*/}}

{{- define "search-api.name" -}}
{{- if .Values.nameOverride }}
{{- .Values.nameOverride }}
{{- else }}
{{- .Chart.Name }}
{{- end }}
{{- end }}

{{- define "search-api.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride }}
{{- else }}
{{- printf "%s-%s" .Release.Name (include "search-api.name" .) | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{- define "search-api.labels" -}}
app.kubernetes.io/name: {{ include "search-api.name" . }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{- define "search-api.selectorLabels" -}}
app.kubernetes.io/name: {{ include "search-api.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}
