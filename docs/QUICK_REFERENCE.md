# Quick Reference: Notebook Modularity Improvements

## 🎯 What Changed?

We improved notebook modularity with:
1. ✅ **Dependency validation** - Explicit checks before execution
2. ✅ **Centralized data loading** - No more duplicate code
3. ✅ **Checkpointing** - Resume long-running processes

---

## 📚 Quick Start Examples

### Load Data (Any Notebook)

```python
from utils.notebook_helpers import get_data_loader

# Initialize
data_loader = get_data_loader()

# Auto-load with fallback
df, data_type = data_loader.load_data_auto(prefer='cleaned', fallback=True)

# Or load specific type
df = data_loader.load_raw_data()
df = data_loader.load_cleaned_data()
df = data_loader.load_enriched_data()  # Auto-merges all enriched files
```

### Use Checkpoints (Long Processes)

```python
from utils.notebook_helpers import get_checkpoint_manager

checkpoint_manager = get_checkpoint_manager()

# Check and resume
if checkpoint_manager.checkpoint_exists('my_step'):
    df = checkpoint_manager.load_checkpoint('my_step')
else:
    # Do work
    df = expensive_operation(df)
    # Save checkpoint
    checkpoint_manager.save_checkpoint(df, 'my_step')

# View all checkpoints
checkpoints = checkpoint_manager.list_checkpoints()

# Clear when done
checkpoint_manager.clear_all_checkpoints()
```

---

## 📋 Notebook Execution Order

```
1. cleaning.ipynb          ← Run first (creates enriched data)
   ↓
2. exploration.ipynb       ← Independent (can run anytime)
   ↓
3. salary_intelligence_analysis.ipynb  ← Requires enriched data
```

---

## 🔍 Where to Find Things

| What | Where |
|------|-------|
| Centralized loader code | `src/utils/notebook_helpers.py` |
| Checkpoint storage | `data/checkpoints/` |
| Implementation docs | `docs/CENTRALIZED_LOADING_CHECKPOINTING.md` |
| Validation docs | `docs/NOTEBOOK_DEPENDENCY_VALIDATION.md` |

---

## 🐛 Troubleshooting

### "FileNotFoundError: Raw data file not found"
→ Run dependency validation cell or download data to `data/raw/`

### "Missing enriched files"
→ Run `cleaning.ipynb` first to generate enriched datasets

### "Checkpoint not found"
→ Normal on first run. Checkpoints are created automatically.

### Want to start fresh?
```python
checkpoint_manager.clear_all_checkpoints()
```

---

## 📊 Benefits at a Glance

| Feature | Before | After | Improvement |
|---------|--------|-------|-------------|
| **Code Duplication** | 70 lines | 6 lines | 91% reduction |
| **Error Messages** | Unclear | Actionable | ✅ Better UX |
| **Resume Failed Runs** | ❌ Not possible | ✅ Checkpoint-based | Time savings |
| **Environment Detection** | Manual | Automatic | ✅ Kaggle + Local |
| **Data Loading** | Per-notebook | Centralized | ✅ Maintainable |

---

## 🎓 Learn More

- Full implementation: [CENTRALIZED_LOADING_CHECKPOINTING.md](CENTRALIZED_LOADING_CHECKPOINTING.md)
- Validation details: [NOTEBOOK_DEPENDENCY_VALIDATION.md](NOTEBOOK_DEPENDENCY_VALIDATION.md)
- Module source: [src/utils/notebook_helpers.py](../src/utils/notebook_helpers.py)

---

## ✨ Key Takeaways

1. **Always run validation cells first** - They'll catch missing dependencies
2. **Use centralized loader** - Consistent across all notebooks
3. **Checkpoints save time** - Resume instead of re-run
4. **Clear checkpoints when done** - Free up disk space
5. **Run cleaning.ipynb first** - Required for enriched data

**Questions?** Check the full documentation linked above!
