{{/*
Common values of the Aurelius chart.
*/}}
{{- define "aurelius.ns" -}}
{{ .Release.Namespace }}
{{- end }}

{{- define "aurelius.publicUrl" -}}
https://{{ .Values.global.external_hostname }}
{{- end }}

{{- define "aurelius.image" -}}
{{ .Values.global.imageRegistry }}/{{ .name }}:{{ .Values.global.version }}
{{- end }}

{{- define "aurelius.labels" -}}
app.kubernetes.io/part-of: aurelius
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/*
Environment of the tenant administration (aurelius-init job, aurelius-admin pod).
*/}}
{{- define "aurelius.adminEnv" -}}
- name: AURELIUS_PUBLIC_URL
  value: {{ include "aurelius.publicUrl" . | quote }}
- name: AURELIUS_NS
  value: {{ include "aurelius.ns" . | quote }}
- name: KEYCLOAK_URL
  value: "http://keycloak:8080/{{ include "aurelius.ns" . }}/auth"
- name: KEYCLOAK_ADMIN
  valueFrom:
    secretKeyRef: { name: keycloak-secret, key: admin-username }
- name: KEYCLOAK_ADMIN_PASSWORD
  valueFrom:
    secretKeyRef: { name: keycloak-secret, key: admin-password }
- name: KEYCLOAK_THEME
  value: m4i
- name: ES_URL
  value: "http://elastic-search-es-http:9200"
- name: ES_USERNAME
  value: elastic
- name: ES_PASSWORD
  valueFrom:
    secretKeyRef: { name: elastic-search-es-elastic-user, key: elastic }
- name: KIBANA_URL
  value: "http://kibana-kb-http:5601/{{ include "aurelius.ns" . }}/kibana"
- name: PYATLAS_ES_PASSWORD
  valueFrom:
    secretKeyRef: { name: aurelius-secrets, key: pyatlas-es-password }
- name: FILEBEAT_PASSWORD
  valueFrom:
    secretKeyRef: { name: aurelius-secrets, key: filebeat-password }
- name: AURELIUS_OPERATOR_PASSWORD
  valueFrom:
    secretKeyRef: { name: aurelius-secrets, key: operator-password }
- name: LOG_RETENTION_DAYS
  value: {{ .Values.logRetentionDays | quote }}
- name: TENANTS_DIR
  value: /tmp/tenants
{{- end }}
