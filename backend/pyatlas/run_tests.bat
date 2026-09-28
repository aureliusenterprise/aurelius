@echo off
rem Runs the pyatlas test-suite inside a throwaway python:3.12 Docker container:
rem   1. in-memory   2. against Elasticsearch on the Windows host (default http://host.docker.internal:9200)
rem Output goes to run_tests.log in this folder.
cd /d "%~dp0"
set LOG=%~dp0run_tests.log
set ES=%PYATLAS_TEST_ES_HOSTS%
if "%ES%"=="" set ES=http://host.docker.internal:9200
echo ==== %DATE% %TIME% > "%LOG%"
docker version --format "docker {{.Server.Version}}" >> "%LOG%" 2>&1
docker run --rm -v "%~dp0..\..:/repo:ro" -e ES=%ES% --add-host host.docker.internal:host-gateway python:3.12-slim sh -c "mkdir -p /w/backend /w/libs/m4i-governance-data-quality/m4i_governance_data_quality/rules && cp -r /repo/backend/pyatlas /w/backend/ && cp -r /repo/backend/m4i-atlas-post-install /w/backend/ && cp -r /repo/libs/m4i-governance-data-quality/m4i_governance_data_quality/rules/definitions /w/libs/m4i-governance-data-quality/m4i_governance_data_quality/rules/ && cd /w/backend/pyatlas && rm -rf .venv && pip install -q --root-user-action=ignore --disable-pip-version-check -e '.[dev]' && echo ==== ELASTICSEARCH $ES && python -c 'import urllib.request,sys;print(urllib.request.urlopen(sys.argv[1],timeout=10).read().decode())' $ES ; echo ==== IN-MEMORY && python -B -m pytest -q -p no:cacheprovider ; echo ==== REAL-ES && PYATLAS_TEST_ES_HOSTS=$ES python -B -m pytest -q -p no:cacheprovider -rf" >> "%LOG%" 2>&1
echo ==== DONE >> "%LOG%"
