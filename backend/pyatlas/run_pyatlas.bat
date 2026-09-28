@echo off
rem Builds the pyatlas Docker image and runs it against the Elasticsearch on this machine
rem (http://host.docker.internal:9200). sample_data.zip from this folder is imported on the first start.
rem UI: http://localhost:21000  (admin / admin)      Stop: Ctrl+C in this window
cd /d "%~dp0"
set ES=%PYATLAS_ES_HOSTS%
if "%ES%"=="" set ES=http://host.docker.internal:9200
docker build -t pyatlas -f Dockerfile ..\.. || goto end
docker run --rm -it --name pyatlas -p 21000:21000 --add-host host.docker.internal:host-gateway ^
  -e PYATLAS_ES_HOSTS=%ES% -e PYATLAS_IMPORT_ON_START=/import/sample_data.zip -v "%~dp0.:/import:ro" pyatlas
:end
pause
