Set-Location c:\Projects\FasalIQ

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  FasalIQ -> Render Deployment" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Stage all changes
Write-Host "`nStaging changes..." -ForegroundColor Yellow
git add .

# Ask for a commit message
$commitMsg = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMsg)) {
    $commitMsg = "chore: deploy to Render"
}

git commit -m $commitMsg

Write-Host "`nPushing to GitHub..." -ForegroundColor Yellow
git push origin main

Write-Host "`n✅ Done! Render will now automatically build and deploy your backend." -ForegroundColor Green
Write-Host "   Monitor progress at: https://dashboard.render.com" -ForegroundColor Cyan
Read-Host "`nPress Enter to close this window"
