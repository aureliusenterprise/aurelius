# Front end container

## current steps of creating

1. create atlas prod

```
npx nx run atlas:build --configuration=standalone

Output location: /workspace/dist/apps/atlas
```

2. copy it to atlas

```
cd backend/m4i-reverse-proxy/atlas/
rm -rf *
cp -r /workspace/dist/apps/atlas/browser/* /workspace/backend/m4i-reverse-proxy/atlas/
cp /workspace/dist/apps/atlas/3rdpartylicenses.txt /workspace/backend/m4i-reverse-proxy/atlas/
```

3. 

# Regi

```

docker build -t aureliusatlas/reverse-proxy:1.0.9.6 .
docker images
docker login --username=aureliusatlas
docker push aureliusatlas/reverse-proxy:1.0.9.6

run
docker run -dit -p 8080:80 reverse_proxy

```

# Change image of an already running deployment

kubectl set image deployment.apps/chart-1728025440-reverse-proxy reverse-proxy=aureliusatlas/reverse-proxy:1.0.9.6 -n demo

REGI

    Image:          aureliusatlas/reverse-proxy:1.0.9.5

kubectl set image deployment.apps/chart-1728025440-reverse-proxy reverse-proxy=wombach/docker-reverse-proxy:1.0.9.4 -n demo
