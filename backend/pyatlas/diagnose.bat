@echo off
rem Collects information about the docker-compose setup into diagnose.log (for troubleshooting).
cd /d "%~dp0"
set LOG=%~dp0diagnose.log
echo ==== %DATE% %TIME% > "%LOG%"
echo ==== docker compose ps >> "%LOG%"
docker compose ps -a >> "%LOG%" 2>&1
echo ==== images >> "%LOG%"
docker compose images >> "%LOG%" 2>&1
echo ==== elasticsearch indices >> "%LOG%"
docker compose exec -T elasticsearch curl -s "http://localhost:9200/_cat/indices?v&s=index" >> "%LOG%" 2>&1
echo ==== /import in the pyatlas container >> "%LOG%"
docker compose exec -T pyatlas ls -la /import >> "%LOG%" 2>&1
docker compose exec -T pyatlas env >> "%LOG%" 2>&1
echo ==== pyatlas metrics >> "%LOG%"
docker compose exec -T elasticsearch curl -s -u admin:admin http://pyatlas:21000/api/atlas/admin/metrics >> "%LOG%" 2>&1
echo. >> "%LOG%"
echo ==== pyatlas log >> "%LOG%"
docker compose logs --no-color --tail 300 pyatlas >> "%LOG%" 2>&1
echo ==== kibana-setup log >> "%LOG%"
docker compose logs --no-color --tail 100 kibana-setup >> "%LOG%" 2>&1
echo ==== DONE >> "%LOG%"
echo Written to diagnose.log
pause
