@echo off
REM VDW Orchestrator - Windows Batch Start Script

echo.
echo ========================================
echo   VDW Orchestrator - Quick Start
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Redis is installed
redis-cli --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Redis is not installed!
    echo.
    echo Please install Redis:
    echo   - Chocolatey: choco install redis-64
    echo   - Download: https://github.com/microsoftarchive/redis/releases
    echo   - Docker: docker run -d -p 6379:6379 redis:latest
    echo.
    pause
    exit /b 1
)

REM Check if Redis is running
redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo [INFO] Starting Redis...
    start /B redis-server
    timeout /t 2 /nobreak >nul
    echo [OK] Redis started
) else (
    echo [OK] Redis already running
)

REM Check if port 8000 is in use
netstat -ano | findstr :8000 >nul
if not errorlevel 1 (
    echo [WARNING] Port 8000 is already in use!
    echo To stop existing server: taskkill /F /IM python.exe
    pause
    exit /b 1
)

REM Start VDW Orchestrator
echo [INFO] Starting VDW Orchestrator API server...
echo.

start /B python -m uvicorn main:app --host 0.0.0.0 --port 8000 > %TEMP%\vdw_server.log 2>&1

REM Wait for server to start
timeout /t 3 /nobreak >nul

REM Test if server is running
curl -s http://localhost:8000/ >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to start server
    echo Check logs: type %TEMP%\vdw_server.log
    pause
    exit /b 1
)

echo [OK] VDW Orchestrator is running!
echo.
echo ========================================
echo   Server Information
echo ========================================
echo   Health: http://localhost:8000/
echo   Docs:   http://localhost:8000/docs
echo   Logs:   %TEMP%\vdw_server.log
echo.
echo   To stop: taskkill /F /IM python.exe
echo ========================================
echo.
echo Ready to use with Qwen Desktop!
echo See WINDOWS_SETUP.md for Qwen configuration.
echo.
pause
