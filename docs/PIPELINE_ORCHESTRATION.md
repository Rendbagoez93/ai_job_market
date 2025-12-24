# Notebook Pipeline Orchestration

Automated execution system for running Jupyter notebooks in a coordinated pipeline.

## Overview

The notebook pipeline orchestrator provides automated, sequential execution of notebooks with:

✅ **Dependency checking** - Validates required tools are installed  
✅ **Error handling** - Graceful failure recovery  
✅ **Progress tracking** - Real-time execution status  
✅ **Execution logging** - Detailed reports and timestamps  
✅ **Checkpoint integration** - Works with CheckpointManager  
✅ **Parameter passing** - Inject variables between notebooks  
✅ **Cross-platform** - Windows, Mac, Linux support  

---

## Quick Start

### Option 1: Python Script (Recommended)

```bash
python run_pipeline.py
```

### Option 2: PowerShell (Windows)

```powershell
.\run_pipeline.ps1
```

### Option 3: Batch File (Windows)

```cmd
run_pipeline.bat
```

### Option 4: Bash Script (Linux/Mac)

```bash
chmod +x run_pipeline.sh
./run_pipeline.sh
```

---

## Pipeline Stages

The default pipeline executes three notebooks in sequence:

| Stage | Notebook | Duration | Description |
|-------|----------|----------|-------------|
| **1** | `cleaning.ipynb` | ~60 min | Data cleaning & enrichment |
| **2** | `exploration.ipynb` | ~30 min | Exploratory data analysis |
| **3** | `salary_intelligence_analysis.ipynb` | ~30 min | Salary intelligence analysis |

**Total estimated time**: ~2 hours

---

## Installation

### Required Dependencies

```bash
# Recommended (full features)
pip install papermill jupyter nbconvert ipykernel

# Minimum (basic features)
pip install jupyter nbconvert
```

### Check Dependencies

```bash
# Using Python script
python run_pipeline.py  # Will check automatically

# Using PowerShell
.\run_pipeline.ps1 -CheckOnly
```

---

## Usage

### Basic Execution

Run the full pipeline with confirmation prompt:

```bash
python run_pipeline.py
```

### Advanced Options

#### Check Dependencies Only

```bash
python run_pipeline.py --check
```

#### Programmatic Usage

```python
from run_pipeline import NotebookOrchestrator, create_default_pipeline

# Initialize orchestrator
orchestrator = NotebookOrchestrator(
    notebooks_dir='notebooks',
    output_dir='output/executed_notebooks',
    log_dir='output/logs'
)

# Check dependencies
deps = orchestrator.check_dependencies()

# Run pipeline
pipeline = create_default_pipeline()
report = orchestrator.run_pipeline(
    pipeline_config=pipeline,
    stop_on_error=True,
    save_report=True
)

# Check results
if report['failed'] == 0:
    print("✅ All notebooks completed successfully!")
else:
    print(f"❌ {report['failed']} notebooks failed")
```

#### Custom Pipeline

```python
from run_pipeline import NotebookOrchestrator

orchestrator = NotebookOrchestrator()

custom_pipeline = [
    {
        'notebook': 'cleaning.ipynb',
        'timeout': 3600,
        'parameters': {'debug_mode': True}
    },
    {
        'notebook': 'exploration.ipynb',
        'timeout': 1800
    }
]

report = orchestrator.run_pipeline(custom_pipeline)
```

---

## Configuration

### Pipeline Configuration File

Edit `config/pipeline.yaml` to customize the pipeline:

```yaml
pipeline:
  name: "AI Job Market Data Pipeline"
  
  settings:
    stop_on_error: true
    default_timeout: 3600
    kernel_name: "python3"
  
  stages:
    - name: "Data Cleaning"
      notebook: "cleaning.ipynb"
      timeout: 3600
      required: true
      
    - name: "Analysis"
      notebook: "exploration.ipynb"
      timeout: 1800
```

### Parameters

Pass parameters to notebooks:

```python
pipeline = [
    {
        'notebook': 'analysis.ipynb',
        'parameters': {
            'date_range': '2024-01-01',
            'sample_size': 1000,
            'debug': False
        }
    }
]
```

Access in notebook:

```python
# Cell with parameters tag
date_range = '2024-01-01'  # Default
sample_size = 1000
debug = False

# Parameters will be injected when running via orchestrator
```

---

## Output

### Executed Notebooks

Saved to `output/executed_notebooks/` with timestamp:

```
output/executed_notebooks/
├── cleaning_executed.ipynb
├── exploration_executed.ipynb
└── salary_intelligence_analysis_executed.ipynb
```

### Execution Logs

JSON reports saved to `output/logs/`:

```
output/logs/
└── pipeline_report_20251224_153045.json
```

**Report Format:**

```json
{
  "pipeline_name": "AI Job Market Data Pipeline",
  "start_time": "2025-12-24T15:30:45",
  "end_time": "2025-12-24T17:45:22",
  "total_duration": 8077.5,
  "total_notebooks": 3,
  "successful": 3,
  "failed": 0,
  "execution_log": [
    {
      "notebook": "cleaning.ipynb",
      "success": true,
      "execution_time": 3542.2,
      "timestamp": "2025-12-24T16:29:27"
    }
  ]
}
```

---

## Execution Flow

```
┌─────────────────────────────────────┐
│  1. Check Dependencies              │
│     - papermill or nbconvert        │
│     - Jupyter kernel                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  2. Load Pipeline Configuration     │
│     - Read notebook list            │
│     - Validate paths                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  3. Execute Notebooks Sequentially  │
│     ┌─────────────────────────┐     │
│     │ cleaning.ipynb          │     │
│     └──────────┬──────────────┘     │
│                ▼                     │
│     ┌─────────────────────────┐     │
│     │ exploration.ipynb       │     │
│     └──────────┬──────────────┘     │
│                ▼                     │
│     ┌─────────────────────────┐     │
│     │ salary_analysis.ipynb   │     │
│     └─────────────────────────┘     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  4. Generate Execution Report       │
│     - Success/failure status        │
│     - Execution times               │
│     - Error messages                │
└─────────────────────────────────────┘
```

---

## Error Handling

### Stop on Error (Default)

Pipeline stops at first failure:

```python
orchestrator.run_pipeline(
    pipeline_config=pipeline,
    stop_on_error=True  # Default
)
```

### Continue on Error

Pipeline continues even if notebooks fail:

```python
orchestrator.run_pipeline(
    pipeline_config=pipeline,
    stop_on_error=False
)
```

### Timeout Handling

Set per-notebook timeouts:

```python
pipeline = [
    {
        'notebook': 'long_running.ipynb',
        'timeout': 7200  # 2 hours
    }
]
```

---

## Integration with Checkpoints

The orchestrator works seamlessly with CheckpointManager:

1. **First Run**: Notebooks create checkpoints as they progress
2. **Pipeline Fails**: Notebooks saved checkpoints up to failure point
3. **Re-run Pipeline**: Notebooks resume from last checkpoint
4. **Result**: Only failed steps re-execute, saving time

**Example:**

```
First Run:
  ✅ cleaning.ipynb → Checkpoint: 01_after_cleaning
  ✅ cleaning.ipynb → Checkpoint: 02_after_skills  
  ❌ cleaning.ipynb → FAILED at tools enrichment

Second Run:
  💾 Loaded checkpoint: 02_after_skills
  ✅ cleaning.ipynb → Resumes from tools enrichment
  ✅ exploration.ipynb
  ✅ salary_analysis.ipynb
```

---

## Troubleshooting

### "Papermill not installed"

**Solution**: Install papermill for best experience:
```bash
pip install papermill
```

Or continue with nbconvert (automatically used as fallback)

### "Jupyter nbconvert not available"

**Solution**: Install Jupyter:
```bash
pip install jupyter nbconvert
```

### "Notebook execution timeout"

**Solutions**:
1. Increase timeout in pipeline config
2. Check for infinite loops in notebook
3. Use checkpoints to resume from last successful step

### "Kernel not found"

**Solution**: Install IPython kernel:
```bash
pip install ipykernel
python -m ipykernel install --user
```

### Execution Fails but Manual Run Works

**Possible causes**:
- Working directory differences
- Environment variables not set
- Interactive input in notebook (e.g., `input()`)

**Solution**: 
- Remove interactive prompts
- Use parameters instead of hardcoded values
- Check notebook paths are relative to project root

---

## Best Practices

### 1. Make Notebooks Non-Interactive

❌ **Avoid:**
```python
response = input("Continue? (y/n): ")
```

✅ **Use:**
```python
# Tagged as parameters cell
auto_continue = True  # Can be overridden by orchestrator
```

### 2. Use Relative Paths

❌ **Avoid:**
```python
df = pd.read_csv('C:/Users/me/data/file.csv')
```

✅ **Use:**
```python
from pathlib import Path
data_path = Path('..') / 'data' / 'file.csv'
df = pd.read_csv(data_path)
```

### 3. Handle Errors Gracefully

```python
try:
    # Your code
    pass
except Exception as e:
    print(f"Error: {e}")
    # Save partial results
    # Don't use exit() or sys.exit() - let orchestrator handle it
```

### 4. Use Checkpoints for Long Processes

```python
from utils.notebook_helpers import get_checkpoint_manager

checkpoint_manager = get_checkpoint_manager()

for step in ['step1', 'step2', 'step3']:
    if checkpoint_manager.checkpoint_exists(step):
        df = checkpoint_manager.load_checkpoint(step)
    else:
        df = process_step(df, step)
        checkpoint_manager.save_checkpoint(df, step)
```

### 5. Log Progress

```python
print(f"Processing {len(df)} records...")
print(f"Step 1/5 complete: {time_elapsed:.1f}s")
```

---

## CI/CD Integration

### GitHub Actions

```yaml
name: Run Data Pipeline

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
  workflow_dispatch:

jobs:
  pipeline:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install papermill jupyter nbconvert
      
      - name: Run pipeline
        run: python run_pipeline.py
      
      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: pipeline-reports
          path: output/logs/
```

### Cron Job (Linux)

```bash
# Run pipeline daily at 2 AM
0 2 * * * cd /path/to/project && /usr/bin/python3 run_pipeline.py >> pipeline.log 2>&1
```

### Task Scheduler (Windows)

1. Open Task Scheduler
2. Create Basic Task
3. Trigger: Daily at 2:00 AM
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `run_pipeline.py`
   - Start in: `C:\path\to\project`

---

## Performance Tips

1. **Use checkpoints** - Avoid re-running expensive operations
2. **Adjust timeouts** - Set realistic timeouts per notebook
3. **Run overnight** - Schedule long pipelines during off-hours
4. **Monitor resources** - Check memory usage for large datasets
5. **Parallelize when possible** - Run independent analyses separately

---

## API Reference

### `NotebookOrchestrator`

```python
NotebookOrchestrator(
    notebooks_dir='notebooks',
    output_dir='output/executed_notebooks',
    log_dir='output/logs'
)
```

**Methods:**
- `execute_notebook(notebook_name, parameters, timeout, kernel_name)`
- `run_pipeline(pipeline_config, stop_on_error, save_report)`
- `check_dependencies()`

### `create_default_pipeline()`

Returns default pipeline configuration for the project.

---

## Examples

See `examples/pipeline_examples.ipynb` for:
- Custom pipeline configurations
- Parameter passing examples
- Error handling patterns
- Integration with external tools

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review execution logs in `output/logs/`
3. Ensure dependencies are installed
4. Check individual notebooks run manually

---

## License

Same as main project.
