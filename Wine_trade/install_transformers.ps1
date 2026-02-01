# Install sentence-transformers using uv for faster installation
Write-Host "Installing uv package manager..." -ForegroundColor Cyan
pip install uv

Write-Host "`nActivating virtual environment..." -ForegroundColor Cyan
.\venv\Scripts\Activate.ps1

Write-Host "`nInstalling sentence-transformers with uv (this will be fast!)..." -ForegroundColor Cyan
uv pip install sentence-transformers

Write-Host "`nVerifying installation..." -ForegroundColor Cyan
python -c "from sentence_transformers import SentenceTransformer; print('✅ sentence-transformers installed successfully!')"

Write-Host "`n✅ Installation complete! You can now run the RAG initialization script." -ForegroundColor Green
