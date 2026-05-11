# PowerShell script to fix frontend installation issues
# Run this script as Administrator: Right-click -> Run with PowerShell

Write-Host "Fixing frontend installation..." -ForegroundColor Green

# Navigate to frontend directory
$frontendPath = Join-Path $PSScriptRoot "frontend"
Set-Location $frontendPath

Write-Host "Current directory: $frontendPath" -ForegroundColor Yellow

# Force remove node_modules (multiple attempts if needed)
Write-Host "Cleaning node_modules..." -ForegroundColor Yellow
if (Test-Path "node_modules") {
    try {
        Remove-Item -Recurse -Force node_modules -ErrorAction Stop
        Write-Host "node_modules removed successfully" -ForegroundColor Green
    } catch {
        Write-Host "Warning: Could not fully remove node_modules. Some files may be locked by OneDrive." -ForegroundColor Red
        Write-Host "Try pausing OneDrive sync temporarily, then run this script again." -ForegroundColor Yellow
    }
}

# Remove lock files
Write-Host "Cleaning lock files..." -ForegroundColor Yellow
Remove-Item -Force package-lock.json -ErrorAction SilentlyContinue
Remove-Item -Force yarn.lock -ErrorAction SilentlyContinue
Remove-Item -Force pnpm-lock.yaml -ErrorAction SilentlyContinue

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

if ($LASTEXITCODE -eq 0) {
    Write-Host "`nInstallation successful! You can now run 'npm run dev'" -ForegroundColor Green
} else {
    Write-Host "`nInstallation failed. Common solutions:" -ForegroundColor Red
    Write-Host "1. Pause OneDrive sync for this folder" -ForegroundColor Yellow
    Write-Host "2. Move project outside OneDrive folder" -ForegroundColor Yellow
    Write-Host "3. Run PowerShell as Administrator" -ForegroundColor Yellow
}
