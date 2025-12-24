@echo off
REM AI Job Market - Notebook Pipeline Executor
REM Windows batch script to run the notebook orchestration pipeline

echo.
echo ======================================================================
echo   AI JOB MARKET - NOTEBOOK PIPELINE
echo ======================================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python first.
    exit /b 1
)

echo Python found
echo.

REM Change to script directory
cd /d "%~dp0"

echo Working directory: %CD%
echo.

REM Show pipeline stages
echo Pipeline Stages:
echo   1. cleaning.ipynb (Data Cleaning ^& Enrichment)
echo   2. exploration.ipynb (Exploratory Data Analysis)
echo   3. salary_intelligence_analysis.ipynb (Salary Analysis)
echo.

REM Run pipeline
echo Starting pipeline execution...
echo.

python run_pipeline.py

if errorlevel 1 (
    echo.
    echo Pipeline failed with errors.
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo Pipeline completed successfully!
    echo.
    echo Check output/logs/ for execution reports
    echo Executed notebooks saved to output/executed_notebooks/
    echo.
    pause
    exit /b 0
)
