@echo off
rem Starts Aurelius on pyatlas for several tenants (reverse proxy + frontend, Keycloak, pyatlas, Elasticsearch,
rem Kibana, log shipper). The first start builds the images (the frontend build takes several minutes); init-env.ps1
rem writes random secrets to .env (and adds new ones to an existing .env); keep .env private.
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0init-env.ps1" || goto end
docker compose up --build -d || goto end
set KCPW=
for /f "tokens=1,* delims==" %%a in ('findstr /b "KEYCLOAK_ADMIN_PASSWORD=" .env') do set KCPW=%%b
set OPPW=
for /f "tokens=1,* delims==" %%a in ('findstr /b "AURELIUS_OPERATOR_PASSWORD=" .env') do set OPPW=%%b
echo.
echo Tenant m4i:      http://localhost:9090/aurelius/m4i/atlas/   (old address /aurelius/atlas/ redirects)
echo Users of m4i:    atlas / steward / scientist  (password = user name; change them in the Keycloak console)
echo Kibana of m4i:   http://localhost:9090/aurelius/m4i/kibana/  (user atlas)
echo pyatlas of m4i:  http://localhost:9090/aurelius/m4i/atlas2/  (the same users)
echo New tenant:      docker compose -f "%~dp0docker-compose.yml" run --rm aurelius-admin tenant create acme --name ACME --admin-user anna
echo Operators:       http://localhost:9090/aurelius/platform/kibana/  (operator / %OPPW%, all tenants)
echo Keycloak admin:  http://localhost:9090/aurelius/auth/admin/  (admin / %KCPW%, from .env)
echo Logs:            docker compose -f "%~dp0docker-compose.yml" logs -f
echo Stop:            docker compose -f "%~dp0docker-compose.yml" down
:end
pause
