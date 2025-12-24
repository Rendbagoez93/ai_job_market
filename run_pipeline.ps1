# AI Job Market - Notebook Pipeline Executor
# PowerShell script to run the notebook orchestration pipeline

param(
    [switch]$CheckOnly,
    [switch]$SkipConfirmation,
    [string]$Stage = "all"
)

Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "  AI JOB MARKET - NOTEBOOK PIPELINE" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python first." -ForegroundColor Red
    exit 1
}

# Change to script directory
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptPath

Write-Host "📂 Working directory: $scriptPath" -ForegroundColor Yellow
Write-Host ""

# Check dependencies
if ($CheckOnly) {
    Write-Host "🔍 Checking dependencies only..." -ForegroundColor Yellow
    python run_pipeline.py --check-only
    exit $LASTEXITCODE
}

# Show pipeline stages
Write-Host "📋 Pipeline Stages:" -ForegroundColor Cyan
Write-Host "  1. cleaning.ipynb (Data Cleaning & Enrichment)" -ForegroundColor White
Write-Host "  2. exploration.ipynb (Exploratory Data Analysis)" -ForegroundColor White
Write-Host "  3. salary_intelligence_analysis.ipynb (Salary Analysis)" -ForegroundColor White
Write-Host ""

# Confirmation prompt
if (-not $SkipConfirmation) {
    $response = Read-Host "Execute full pipeline? (y/N)"
    if ($response -ne "y" -and $response -ne "Y") {
        Write-Host "Pipeline execution cancelled." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "🚀 Starting pipeline execution..." -ForegroundColor Green
Write-Host ""

# Run pipeline
python run_pipeline.py

$exitCode = $LASTEXITCODE

Write-Host ""
if ($exitCode -eq 0) {
    Write-Host "✅ Pipeline completed successfully!" -ForegroundColor Green
} else {
    Write-Host "❌ Pipeline failed with errors." -ForegroundColor Red
}

Write-Host ""
Write-Host "📊 Check output/logs/ for execution reports" -ForegroundColor Yellow
Write-Host "📓 Executed notebooks saved to output/executed_notebooks/" -ForegroundColor Yellow
Write-Host ""

exit $exitCode
