config = {
    "atlas.server.url": "http://atlas.{{ .Release.Namespace }}.svc.cluster.local:21000/api/atlas",
    "kafka.bootstrap.server.hostname": "kafka.{{ .Release.Namespace }}.svc.cluster.local",
    "kafka.bootstrap.server.port": "9092",
    "kafka.consumer.group.id": "{{ .Release.Namespace }}",
    "atlas.audit.events.topic.name": "ATLAS_ENTITIES",
    "enriched.events.topic.name": "ENRICHED_ENTITIES",
    "determined.events.topic.name": "DETERMINED_CHANGE",
    "sync_elastic.events.topic.name": "SYNC_ELASTIC",
    "exception.events.topic.name": "DEAD_LETTER_BOX",

    "elastic.search.index" : "atlas-dev-audit",
    "elastic.app.search.engine.name" : "atlas-dev",

    "operations.appsearch.engine.name": "atlas-dev",

    "elastic.cloud.username" : "elastic",
    "elastic.cloud.id" : None,
    # "elastic.base.endpoint" : "elastic.{{ .Release.Namespace }}.svc.cluster.local:9200/api/as/v1",
    # "elastic.search.endpoint" : "http://elastic-search-es-http.{{ .Release.Namespace }}.svc.cluster.local:9200",
    # "elastic.enterprise.search.endpoint" : "http://enterprise-search-ent-http.{{ .Release.Namespace }}.svc.cluster.local:3002",
    "elastic.base.endpoint" : "{{ .Values.global.external_hostname }}/{{ .Release.Namespace }}/elastic/api/as/v1",
    "elastic.search.endpoint" : "https://{{ .Values.global.external_hostname }}:443/{{ .Release.Namespace }}/elastic",
    "elastic.enterprise.search.endpoint" : "https://{{ .Values.global.external_hostname }}:443/{{ .Release.Namespace }}/app-search",

    "keycloak.server.url" : "https://{{ .Values.global.external_hostname }}/{{ .Release.Namespace }}/auth/",
    "keycloak.client.id" : "m4i_public",
    "keycloak.realm.name": "m4i",    
}