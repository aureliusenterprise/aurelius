@echo off
rem Starts Aurelius on pyatlas (reverse proxy + frontend, Keycloak, pyatlas, Elasticsearch).
rem The first start builds the images (the frontend build takes several minutes).
cd /d "%~dp0"
docker compose up --build -d || goto end
echo.
echo Aurelius Atlas:  http://localhost:8080/aurelius/atlas/
echo Users:           atlas / steward / scientist  (password = user name)
echo Keycloak admin:  http://localhost:8080/aurelius/auth/admin/  (admin / admin)
echo pyatlas:         http://localhost:8080/aurelius/atlas2/
echo Logs:            docker compose -f "%~dp0docker-compose.yml" logs -f
echo Stop:            docker compose -f "%~dp0docker-compose.yml" down
:end
pause
