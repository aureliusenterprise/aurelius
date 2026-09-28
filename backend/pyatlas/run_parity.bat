@echo off
rem Runs a parity check (python -m parity ...) in a throwaway Python container; reports go to parity-reports\.
rem Examples:
rem   run_parity.bat rules --repo-defaults
rem   run_parity.bat store --zip /aurelius-data/sample_data.zip --right http://host.docker.internal:21100 --right-user admin --right-password admin
rem   run_parity.bat indices --left file:/aurelius-data/atlas-dev.json --right es:http://host.docker.internal:9201#atlas_search
rem Credentials can be put in parity.env next to this file (PARITY_LEFT_TOKEN=..., PARITY_RIGHT_USER=..., ...).
cd /d "%~dp0"
if not exist parity-reports mkdir parity-reports
set ENVFILE=
if exist parity.env set ENVFILE=--env-file parity.env
docker run --rm %ENVFILE% -e PYTHONDONTWRITEBYTECODE=1 -v "%~dp0.:/src:ro" -v "%~dp0parity-reports:/reports" ^
  -v "%~dp0..\m4i-atlas-post-install\data:/aurelius-data:ro" -v "%~dp0..\..\libs:/repo-libs:ro" ^
  -e PARITY_AURELIUS_DATA=/aurelius-data ^
  -e PARITY_RULES_DIR=/repo-libs/m4i-governance-data-quality/m4i_governance_data_quality/rules/definitions ^
  --add-host host.docker.internal:host-gateway -w /src python:3.12-slim python -m parity --out-dir /reports %*
echo Reports: %~dp0parity-reports
