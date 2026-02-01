# Quick installation script for sentence-transformers
Write-Host "=== Installing sentence-transformers ===" -ForegroundColor Cyan

# Step 1: Create virtual environment if it doesn't exist
Write-Host "`n[1/4] Checking virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path .\venv)) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create virtual environment!" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

# Step 2: Activate venv
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
if (Test-Path .\venv\Scripts\Activate.ps1) {
    & .\venv\Scripts\Activate.ps1
} else {
    Write-Host "Virtual environment activation script not found!" -ForegroundColor Red
    exit 1
}

# Step 3: Upgrade pip and install sentence-transformers
Write-Host "[3/4] Installing sentence-transformers..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet
python -m pip install sentence-transformers

if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install sentence-transformers!" -ForegroundColor Red
    exit 1
}

# Step 4: Verify installation
Write-Host "[4/4] Verifying installation..." -ForegroundColor Yellow
python -c "from sentence_transformers import SentenceTransformer; print('✅ sentence-transformers installed successfully!')"

if ($LASTEXITCODE -ne 0) {
    Write-Host "Verification failed!" -ForegroundColor Red
    exit 1
}

Write-Host "`n=== Installation Complete! ===" -ForegroundColor Green
Write-Host "You can now run: cd apps\backend; python scripts\init_rag_documents.py" -ForegroundColor Green
