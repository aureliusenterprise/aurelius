@echo off
rem Runs the browser journeys (Playwright, in Docker) against the stack in e2e.env.
rem Usage: run_e2e.bat [label]   e.g. run_e2e.bat old  /  run_e2e.bat new
rem Results: results-<label>\ (screenshots, traces), playwright-report\index.html, results.json
cd /d "%~dp0"
if not exist e2e.env (
  echo e2e.env is missing: copy e2e.env.example to e2e.env and fill in the URL and the three users.
  pause
  exit /b 1
)
set LABEL=%1
if "%LABEL%"=="" set LABEL=run
docker run --rm --ipc=host --env-file e2e.env -v "%~dp0.:/e2e" -w /e2e --add-host host.docker.internal:host-gateway ^
  mcr.microsoft.com/playwright:v1.47.2-jammy sh -c "npm install --no-audit --no-fund --loglevel=error && npx playwright test --output=results-%LABEL% ; cp results.json results-%LABEL%.json"
echo.
echo Report: %~dp0playwright-report\index.html   (summary: results-%LABEL%.json)
pause
