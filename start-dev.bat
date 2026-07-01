@echo off
setlocal

cd /d "%~dp0"

echo ========================================
echo BiliNote local development startup
echo ========================================
echo.

where node >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Node.js was not found in PATH.
  echo Please install Node.js first.
  pause
  exit /b 1
)

where corepack >nul 2>nul
if errorlevel 1 (
  echo [ERROR] Corepack was not found in PATH.
  echo Please install a recent Node.js version with Corepack.
  pause
  exit /b 1
)

if not exist "backend\.venv\Scripts\python.exe" (
  echo [ERROR] backend\.venv\Scripts\python.exe was not found.
  echo Create the backend virtual environment first:
  echo   cd backend
  echo   python -m venv .venv
  echo   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
  pause
  exit /b 1
)

echo Checking ports 8483 and 3015...
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
  "$ports = 8483,3015; $busy = Get-NetTCPConnection -LocalPort $ports -ErrorAction SilentlyContinue | Select-Object LocalPort,OwningProcess -Unique; if ($busy) { Write-Host '[WARN] These ports are already in use:'; $busy | Format-Table -AutoSize; Write-Host 'Close those processes if startup fails.' }"
echo.

echo Installing frontend dependencies if needed...
pushd "BillNote_frontend"
call corepack pnpm install
if errorlevel 1 (
  echo.
  echo [WARN] pnpm install failed. Trying to approve pending build scripts and reinstall...
  call corepack pnpm approve-builds --all
  call corepack pnpm install
  if errorlevel 1 (
    popd
    echo [ERROR] Frontend dependency installation failed.
    pause
    exit /b 1
  )
)
popd

echo Starting backend on http://localhost:8483 ...
start "BiliNote Backend" cmd /k "cd /d ""%~dp0backend"" && .\.venv\Scripts\python.exe main.py"

echo Starting frontend on http://localhost:3015 ...
start "BiliNote Frontend" cmd /k "cd /d ""%~dp0BillNote_frontend"" && corepack pnpm dev"

echo.
echo Waiting a few seconds before opening the browser...
timeout /t 5 /nobreak >nul
start http://localhost:3015/

echo.
echo Started. Keep the Backend and Frontend windows open while using BiliNote.
pause
