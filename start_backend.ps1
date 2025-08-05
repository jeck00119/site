# AOI Backend Starter (PowerShell)
Write-Host "Starting AOI Backend Server..." -ForegroundColor Green
Set-Location "$PSScriptRoot\backend-flask"
if (-not (Test-Path "venv")) {
    Write-Host "Virtual environment not found! Please run setup.py first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
& ".\venv\Scripts\Activate.ps1"
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to activate virtual environment!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
Write-Host "Virtual environment activated" -ForegroundColor Yellow
python main.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "Backend failed to start!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
