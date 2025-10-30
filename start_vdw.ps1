# VDW Orchestrator - Windows PowerShell Start Script

Write-Host "🚀 Starting VDW Orchestrator..." -ForegroundColor Cyan
Write-Host ""

# Check if Redis is installed
$redisInstalled = Get-Command redis-server -ErrorAction SilentlyContinue
if (-not $redisInstalled) {
    Write-Host "❌ Redis is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Redis for Windows:" -ForegroundColor Yellow
    Write-Host "  Option 1: Using Chocolatey - choco install redis-64" -ForegroundColor Yellow
    Write-Host "  Option 2: Download from https://github.com/microsoftarchive/redis/releases" -ForegroundColor Yellow
    Write-Host "  Option 3: Use WSL2 and run Redis in Linux" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Alternative: Use Docker to run Redis:" -ForegroundColor Yellow
    Write-Host "  docker run -d -p 6379:6379 redis:latest" -ForegroundColor Yellow
    Write-Host ""
    exit 1
}

# Check if Redis is running
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -eq "PONG") {
        Write-Host "✅ Redis already running" -ForegroundColor Green
    }
} catch {
    Write-Host "📦 Starting Redis..." -ForegroundColor Yellow
    Start-Process redis-server -WindowStyle Hidden
    Start-Sleep -Seconds 2
    Write-Host "✅ Redis started" -ForegroundColor Green
}

# Check if server is already running on port 8000
$portInUse = Get-NetTCPConnection -LocalPort 8000 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "⚠️  Server already running on port 8000" -ForegroundColor Yellow
    Write-Host "   To restart, run: Stop-Process -Name python -Force; .\start_vdw.ps1" -ForegroundColor Yellow
    exit 1
}

# Start the VDW Orchestrator
Write-Host "🎯 Starting VDW Orchestrator API server..." -ForegroundColor Cyan

# Get the script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Start uvicorn in background
$logFile = "$env:TEMP\vdw_server.log"
Start-Process python -ArgumentList "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000" `
    -RedirectStandardOutput $logFile `
    -RedirectStandardError $logFile `
    -WindowStyle Hidden

Write-Host "⏳ Waiting for server to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 3

# Check if server is running
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ VDW Orchestrator is running!" -ForegroundColor Green
        Write-Host ""
        Write-Host "📊 Server Status:" -ForegroundColor Cyan
        $response.Content | ConvertFrom-Json | ConvertTo-Json
        Write-Host ""
        Write-Host "🔗 API Endpoints:" -ForegroundColor Cyan
        Write-Host "   - Health: http://localhost:8000/" -ForegroundColor White
        Write-Host "   - Docs: http://localhost:8000/docs" -ForegroundColor White
        Write-Host "   - Create Project: POST http://localhost:8000/projects" -ForegroundColor White
        Write-Host ""
        Write-Host "📝 Logs: Get-Content $logFile -Wait" -ForegroundColor Cyan
        Write-Host "🛑 Stop: Stop-Process -Name python -Force" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "🎉 Ready to use with Qwen Desktop!" -ForegroundColor Green
        Write-Host "   Configure MCP: See QWEN_SETUP.md" -ForegroundColor White
    }
} catch {
    Write-Host "❌ Failed to start server" -ForegroundColor Red
    Write-Host "Check logs: Get-Content $logFile" -ForegroundColor Yellow
    exit 1
}
