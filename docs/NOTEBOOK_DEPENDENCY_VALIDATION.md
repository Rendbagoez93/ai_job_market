# Notebook Dependency Validation Implementation

## Overview

Added comprehensive dependency validation to all notebooks in the `notebooks/` directory to ensure proper execution order and prevent runtime errors from missing data files.

## Implementation Date
December 24, 2025

---

## Changes Made

### 1. **cleaning.ipynb** - Data Pipeline Validation

**Location**: After imports (Cell 2-3)

**What it does**:
- ✅ Validates raw data file exists (`data/raw/ai_job_market.csv`)
- ✅ Checks all config files are present (`config/`)
- ✅ Creates output directories if missing (`data/cleaned/`, `data/enriched/`, `data/dictionary/`)
- ✅ Verifies all `src` modules are accessible
- ❌ Raises clear error with action steps if dependencies are missing

**Benefits**:
- Prevents pipeline from starting without required inputs
- Auto-creates output directories
- Clear error messages guide users to fix issues

---

### 2. **exploration.ipynb** - Data Source Validation

**Location**: After imports (Cell 2-3)

**What it does**:
- ✅ Checks for cleaned data (preferred) or raw data
- ✅ Works with both Kaggle and local environments
- ✅ Reports file sizes and availability
- ⚠️ Warns if using raw data instead of cleaned
- ❌ Raises error with setup instructions if no data found

**Benefits**:
- Recommends best data source (cleaned > raw)
- Adapts to available data sources
- Guides users to run cleaning pipeline first

---

### 3. **salary_intelligence_analysis.ipynb** - Enriched Dataset Validation

**Location**: After imports (Cell 2-4)

**What it does**:
- ✅ Validates all 8 enriched datasets exist
- ✅ Distinguishes between critical and optional files
- ✅ Reports file sizes and total data volume
- ✅ Enhanced data loading with better error handling
- ⚠️ Allows partial analysis if only non-critical files missing
- ❌ Blocks execution if critical enriched files missing

**Benefits**:
- Prevents analysis from starting without required enrichments
- Clear visibility into which datasets are available
- Graceful fallback to cleaned data if needed
- Explicit dependency on cleaning.ipynb

---

## Validation Functions

### `validate_dependencies()` - cleaning.ipynb
```python
# Checks:
- Raw data file: data/raw/ai_job_market.csv
- Config files: config/*.yaml
- Output directories writability
- Module imports
```

### `validate_data_sources()` - exploration.ipynb
```python
# Checks:
- Cleaned data (preferred)
- Raw data (fallback)
- Kaggle vs local paths
```

### `validate_enriched_datasets()` - salary_intelligence_analysis.ipynb
```python
# Checks (Critical):
- salary_enriched.csv
- skills_enriched.csv
- tools_enriched.csv
- location_enriched.csv
- experience_enriched.csv

# Checks (Optional):
- employment_enriched.csv
- company_enriched.csv
- date_enriched.csv
```

---

## Error Messages

All validation functions provide **actionable error messages**:

### Example: Missing Raw Data
```
❌ NO DATA SOURCES FOUND!

Expected data locations:
  Kaggle: /kaggle/input/ai-job-market-insights/ai_job_market.csv
  Local:  ../data/raw/ai_job_market.csv

Action required:
  1. If running locally: Ensure 'ai_job_market.csv' is in '../data/raw/'
  2. If on Kaggle: Verify the dataset is attached to your notebook
  3. Run 'cleaning.ipynb' first to generate cleaned data (recommended)
```

### Example: Missing Enriched Data
```
❌ CRITICAL FILES MISSING: 5

Action Required:
  1. Run 'cleaning.ipynb' notebook first to generate enriched datasets
  2. Ensure the cleaning pipeline completed successfully
  3. Verify the output directory structure:
     ../data/enriched/
       - salary_enriched.csv
       - skills_enriched.csv
       ...
```

---

## Execution Order

The validation ensures this dependency chain:

```
1. cleaning.ipynb
   ↓ produces: data/cleaned/*.csv
   ↓ produces: data/enriched/*.csv
   ↓
2. exploration.ipynb (independent)
   ↓ reads: data/cleaned/*.csv OR data/raw/*.csv
   ↓
3. salary_intelligence_analysis.ipynb
   ↓ reads: data/enriched/*.csv (REQUIRED)
```

---

## Testing the Validation

### Test 1: Missing Raw Data
```python
# Remove data/raw/ai_job_market.csv
# Run cleaning.ipynb
# Expected: Clear error message with fix instructions
```

### Test 2: Missing Enriched Data
```python
# Remove data/enriched/*.csv
# Run salary_intelligence_analysis.ipynb
# Expected: Validation fails, guides to run cleaning.ipynb
```

### Test 3: Partial Enriched Data
```python
# Remove only company_enriched.csv (optional)
# Run salary_intelligence_analysis.ipynb
# Expected: Warning but allows execution
```

---

## Benefits Summary

| Before | After |
|--------|-------|
| Confusing runtime errors mid-execution | Clear errors at startup |
| No guidance on missing files | Step-by-step fix instructions |
| Silent failures | Loud validation with status |
| Manual directory creation | Auto-creates output dirs |
| Unknown data availability | Full visibility into sources |
| Unclear dependencies | Explicit pipeline order |

---

## Next Steps

Consider implementing:
1. **Shared Data Loaders** - Centralize loading logic in `src/utils/notebook_helpers.py`
2. **Configuration Files** - Replace hardcoded paths with `config/notebook_paths.yaml`
3. **Notebook Orchestration** - Create `run_pipeline.py` to execute notebooks in order
4. **Checkpointing** - Add progress saving in long-running cleaning steps

---

## Files Modified

- ✅ `notebooks/cleaning.ipynb` - Added cells 2-3 (validation)
- ✅ `notebooks/exploration.ipynb` - Added cells 2-3 (validation)
- ✅ `notebooks/salary_intelligence_analysis.ipynb` - Added cells 2-4 (validation + enhanced loading)

**Total cells added**: 7 new cells across 3 notebooks
**Lines of code added**: ~250 lines of validation logic

---

## Rollback Instructions

If you need to revert these changes:

1. Open each notebook in Jupyter/VS Code
2. Delete the validation cells (look for "Dependency Validation" headers)
3. Notebooks will function as before (but without safety checks)

**Note**: Rolling back removes the safety net - not recommended for production use.
