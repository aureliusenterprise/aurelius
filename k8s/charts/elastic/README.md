# Elastic

In order to deploy elastic the ``Elastic Cluster on Kubernetes (ECK)`` must be installed on the cluster. To install ECK on the cluster, please follow the instructions provided on https://www.elastic.co/guide/en/cloud-on-k8s/master/k8s-deploy-eck.html

Once ECK is installed on the cluster, the elastic helm charts can be deployed. 
#### This helm chart includes:
- Elasticsearch 9 with persistent volume and security (ECK default; HTTP inside the cluster without TLS)
- Kibana 9 at /<namespace>/kibana, reached through the reverse proxy (a Keycloak login per tenant, a space per
  tenant); Enterprise Search does not exist in 9 (pyatlas serves the frontend's search)

#### What can be changed in the values:
- persistent volume (size, enabled)
- version
- replicaCount


###To access service use the following command:
```commandline
kubectl port-forward service/kibana-kb-http 5601 -n namespace
```
Open the browser to http://localhost:5601/<namespace>/kibana/ (log in as elastic)

#### to get the password to user elastic:
```commandline
kubectl get secret elastic-search-es-elastic-user -o=jsonpath='{.data.elastic}' -n namespace | base64 --decode; echo
```

