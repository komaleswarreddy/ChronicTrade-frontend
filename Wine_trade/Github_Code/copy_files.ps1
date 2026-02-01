# PowerShell script to copy files to GitHubPush structure
# This script preserves directory structure and only copies files

$workspaceRoot = "C:\Users\KomaleswarReddy\Desktop\PROJECT-M\Wine_trade"
$githubPushRoot = "$workspaceRoot\GitHubPush"

# Function to ensure directory exists and copy file
function Copy-FileToStructure {
    param(
        [string]$SourcePath,
        [string]$DestPath
    )
    
    $fullSource = Join-Path $workspaceRoot $SourcePath
    $fullDest = Join-Path $githubPushRoot $DestPath
    
    if (Test-Path $fullSource) {
        $destDir = Split-Path $fullDest -Parent
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -Path $fullSource -Destination $fullDest -Recurse -Force
        Write-Host "Copied: $SourcePath -> $DestPath"
    } else {
        Write-Host "WARNING: Source not found: $fullSource"
    }
}

# Core Foundation Files (00)
Write-Host "`n=== Copying Core Foundation Files ===" -ForegroundColor Green

# Komal - Frontend Core
Copy-FileToStructure "apps\frontend\pages\index.js" "Komal\00_Core_Foundation_Completed\apps\frontend\pages\index.js"
Copy-FileToStructure "apps\frontend\pages\sign-in" "Komal\00_Core_Foundation_Completed\apps\frontend\pages\sign-in"
Copy-FileToStructure "apps\frontend\pages\register" "Komal\00_Core_Foundation_Completed\apps\frontend\pages\register"
Copy-FileToStructure "apps\frontend\pages\_app.js" "Komal\00_Core_Foundation_Completed\apps\frontend\pages\_app.js"
Copy-FileToStructure "apps\frontend\pages\dashboard.js" "Komal\00_Core_Foundation_Completed\apps\frontend\pages\dashboard.js"
Copy-FileToStructure "apps\frontend\components\NavBar.js" "Komal\00_Core_Foundation_Completed\apps\frontend\components\NavBar.js"
Copy-FileToStructure "apps\frontend\components\PortfolioCard.js" "Komal\00_Core_Foundation_Completed\apps\frontend\components\PortfolioCard.js"
Copy-FileToStructure "apps\frontend\components\HoldingsTable.js" "Komal\00_Core_Foundation_Completed\apps\frontend\components\HoldingsTable.js"
Copy-FileToStructure "apps\frontend\components\MarketPulseCard.js" "Komal\00_Core_Foundation_Completed\apps\frontend\components\MarketPulseCard.js"
Copy-FileToStructure "apps\frontend\components\ArbitrageCard.js" "Komal\00_Core_Foundation_Completed\apps\frontend\components\ArbitrageCard.js"
Copy-FileToStructure "apps\frontend\components\AlertCard.js" "Komal\00_Core_Foundation_Completed\apps\frontend\components\AlertCard.js"
Copy-FileToStructure "apps\frontend\components\WatchlistCard.js" "Komal\00_Core_Foundation_Completed\apps\frontend\components\WatchlistCard.js"

# Manikanta - Backend Core
Copy-FileToStructure "apps\backend\auth" "Manikanta\00_Core_Foundation_Completed\apps\backend\auth"
Copy-FileToStructure "apps\backend\main.py" "Manikanta\00_Core_Foundation_Completed\apps\backend\main.py"
Copy-FileToStructure "apps\backend\models\schemas.py" "Manikanta\00_Core_Foundation_Completed\apps\backend\models\schemas.py"

# Yuvraj - Agents Core
Copy-FileToStructure "apps\agents\main.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\main.py"
Copy-FileToStructure "apps\agents\config.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\config.py"
Copy-FileToStructure "apps\agents\schemas.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\schemas.py"
Copy-FileToStructure "apps\agents\nodes\fetch_data.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\nodes\fetch_data.py"
Copy-FileToStructure "apps\agents\nodes\arbitrage_analysis.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\nodes\arbitrage_analysis.py"
Copy-FileToStructure "apps\agents\nodes\risk_evaluation.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\nodes\risk_evaluation.py"
Copy-FileToStructure "apps\agents\nodes\signal_calculation.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\nodes\signal_calculation.py"
Copy-FileToStructure "apps\agents\nodes\predict_price.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\nodes\predict_price.py"
Copy-FileToStructure "apps\agents\nodes\recommend_action.py" "Yuvraj\00_Core_Foundation_Completed\apps\agents\nodes\recommend_action.py"

# Syam - Database Core
Copy-FileToStructure "db\schema.sql" "Syam\00_Core_Foundation_Completed\db\schema.sql"
Copy-FileToStructure "apps\backend\database\init_db.py" "Syam\00_Core_Foundation_Completed\apps\backend\database\init_db.py"
Copy-FileToStructure "apps\backend\database\migrate_demo_user.py" "Syam\00_Core_Foundation_Completed\apps\backend\database\migrate_demo_user.py"
Copy-FileToStructure "apps\backend\database\migrate_holdings_phase8.py" "Syam\00_Core_Foundation_Completed\apps\backend\database\migrate_holdings_phase8.py"
Copy-FileToStructure "apps\backend\database\migrate_phase8_tables.py" "Syam\00_Core_Foundation_Completed\apps\backend\database\migrate_phase8_tables.py"

Write-Host "`n=== Core Foundation Files Complete ===" -ForegroundColor Green
