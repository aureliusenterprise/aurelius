@echo off
rem Starts Aurelius on pyatlas (reverse proxy + frontend, Keycloak, pyatlas, Elasticsearch, Kibana).
rem The first start builds the images (the frontend build takes several minutes) and writes .env with random
rem secrets (Keycloak admin password, session and proxy secrets, see init-env.ps1); keep .env private.
cd /d "%~dp0"
if not exist .env powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0init-env.ps1" || goto end
docker compose up --build -d || goto end
set KCPW=
for /f "tokens=1,* delims==" %%a in ('findstr /b "KEYCLOAK_ADMIN_PASSWORD=" .env') do set KCPW=%%b
echo.
echo Aurelius Atlas:  http://localhost:9090/aurelius/atlas/
echo Users:           atlas / steward / scientist  (password = user name; change them in the Keycloak console)
echo Keycloak admin:  http://localhost:9090/aurelius/auth/admin/  (admin / %KCPW%, from .env)
echo pyatlas:         http://localhost:9090/aurelius/atlas2/  (the same Keycloak users)
echo Kibana:          http://localhost:9090/aurelius/kibana/  (user atlas)
echo Logs:            docker compose -f "%~dp0docker-compose.yml" logs -f
echo Stop:            docker compose -f "%~dp0docker-compose.yml" down
:end
pause
