# Generate secure random secrets for the trading platform
$secrets = @{
    "db_password.txt" = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 32 | ForEach-Object { [char]$_ })
    "jwt_secret.txt" = -join ((65..90) + (97..122) + (48..57) | Get-Random -Count 64 | ForEach-Object { [char]$_ })
    "encryption_key.txt" = [Convert]::ToBase64String((1..32 | ForEach-Object { Get-Random -Min 0 -Max 256 }))
}

Write-Host "Generating secrets in E:\bilal AI\BL_AI\secrets\" -ForegroundColor Green
foreach ($file in $secrets.Keys) {
    $path = "E:\bilal AI\BL_AI\secrets\$file"
    $secrets[$file] | Out-File -FilePath $path -NoNewline -Encoding ASCII
    Write-Host "  Created: $path" -ForegroundColor Cyan
}

Write-Host "`nIMPORTANT: Add your exchange API keys to:" -ForegroundColor Yellow
Write-Host "  secrets/bybit_api_key.txt" -ForegroundColor Yellow
Write-Host "  secrets/bybit_api_secret.txt" -ForegroundColor Yellow
Write-Host "  secrets/binance_api_key.txt" -ForegroundColor Yellow
Write-Host "  secrets/binance_api_secret.txt" -ForegroundColor Yellow
Write-Host "`nThen copy .env.example to .env and fill in remaining values" -ForegroundColor Yellow
