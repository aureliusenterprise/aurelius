@echo off
rem Imports sample_data.zip into the Elasticsearch on this machine and checks every entity
rem (tests/test_sample_data.py only). Output goes to run_sample_test.log in this folder.
cd /d "%~dp0"
set LOG=%~dp0run_sample_test.log
set ES=%PYATLAS_TEST_ES_HOSTS%
if "%ES%"=="" set ES=http://host.docker.internal:9200
echo ==== %DATE% %TIME% > "%LOG%"
docker run --rm -v "%~dp0..\..:/repo:ro" -e ES=%ES% --add-host host.docker.internal:host-gateway python:3.12-slim sh -c "mkdir -p /w/backend /w/libs/m4i-governance-data-quality/m4i_governance_data_quality/rules && cp -r /repo/backend/pyatlas /w/backend/ && cp -r /repo/backend/m4i-atlas-post-install /w/backend/ && cp -r /repo/libs/m4i-governance-data-quality/m4i_governance_data_quality/rules/definitions /w/libs/m4i-governance-data-quality/m4i_governance_data_quality/rules/ && cd /w/backend/pyatlas && rm -rf .venv && pip install -q --root-user-action=ignore --disable-pip-version-check -e '.[dev]' && echo ==== REAL-ES $ES && PYATLAS_TEST_ES_HOSTS=$ES python -B -m pytest -q -p no:cacheprovider -rf --durations=5 tests/test_sample_data.py" >> "%LOG%" 2>&1
echo ==== DONE >> "%LOG%"
