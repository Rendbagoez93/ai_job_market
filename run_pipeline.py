"""
Notebook Pipeline Orchestrator

Automated execution of Jupyter notebooks in sequence with:
- Dependency checking
- Error handling and reporting
- Progress tracking
- Parameter passing
- Execution logs
- Checkpoint integration
"""

import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
import json
import time


class NotebookOrchestrator:
    """
    Orchestrates execution of multiple notebooks in a pipeline.
    
    Features:
    - Sequential notebook execution
    - Dependency validation
    - Error handling and recovery
    - Execution logging
    - Progress reporting
    - Parameter injection
    - Checkpoint awareness
    """
    
    def __init__(
        self,
        notebooks_dir: Union[str, Path] = 'notebooks',
        output_dir: Union[str, Path] = 'output/executed_notebooks',
        log_dir: Union[str, Path] = 'output/logs'
    ):
        """
        Initialize the orchestrator.
        
        Args:
            notebooks_dir: Directory containing source notebooks
            output_dir: Directory to save executed notebooks
            log_dir: Directory to save execution logs
        """
        self.notebooks_dir = Path(notebooks_dir)
        self.output_dir = Path(output_dir)
        self.log_dir = Path(log_dir)
        
        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.execution_log = []
        self.start_time = None
        self.total_time = 0
    
    def execute_notebook(
        self,
        notebook_name: str,
        parameters: Optional[Dict] = None,
        timeout: int = 3600,
        kernel_name: str = 'python3'
    ) -> Tuple[bool, str, float]:
        """
        Execute a single notebook.
        
        Args:
            notebook_name: Name of the notebook file
            parameters: Optional parameters to inject
            timeout: Execution timeout in seconds
            kernel_name: Jupyter kernel to use
            
        Returns:
            Tuple of (success, message, execution_time)
        """
        notebook_path = self.notebooks_dir / notebook_name
        output_path = self.output_dir / f"{Path(notebook_name).stem}_executed.ipynb"
        
        if not notebook_path.exists():
            return False, f"Notebook not found: {notebook_path}", 0
        
        print(f"\n{'='*70}")
        print(f"📓 Executing: {notebook_name}")
        print(f"{'='*70}")
        
        start_time = time.time()
        
        try:
            # Try using papermill first (preferred method)
            try:
                import papermill as pm
                
                # Execute with papermill
                pm.execute_notebook(
                    str(notebook_path),
                    str(output_path),
                    parameters=parameters or {},
                    kernel_name=kernel_name,
                    progress_bar=True,
                    request_save_on_cell_execute=True
                )
                
                execution_time = time.time() - start_time
                message = f"✅ Completed successfully in {execution_time:.1f}s"
                print(message)
                return True, message, execution_time
                
            except ImportError:
                # Fallback to nbconvert if papermill not available
                print("⚠ Papermill not found, using nbconvert...")
                
                cmd = [
                    sys.executable, '-m', 'jupyter', 'nbconvert',
                    '--to', 'notebook',
                    '--execute',
                    '--ExecutePreprocessor.timeout=3600',
                    '--output', str(output_path.absolute()),
                    str(notebook_path.absolute())
                ]
                
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout
                )
                
                execution_time = time.time() - start_time
                
                if result.returncode == 0:
                    message = f"✅ Completed successfully in {execution_time:.1f}s"
                    print(message)
                    return True, message, execution_time
                else:
                    error_msg = result.stderr or result.stdout
                    message = f"❌ Execution failed: {error_msg[:200]}"
                    print(message)
                    return False, message, execution_time
        
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            message = f"❌ Execution timeout after {timeout}s"
            print(message)
            return False, message, execution_time
            
        except Exception as e:
            execution_time = time.time() - start_time
            message = f"❌ Error: {str(e)}"
            print(message)
            return False, message, execution_time
    
    def run_pipeline(
        self,
        pipeline_config: List[Dict],
        stop_on_error: bool = True,
        save_report: bool = True
    ) -> Dict:
        """
        Execute a pipeline of notebooks.
        
        Args:
            pipeline_config: List of notebook configurations
                Example: [
                    {'notebook': 'cleaning.ipynb', 'timeout': 3600},
                    {'notebook': 'exploration.ipynb', 'parameters': {'var': 'value'}},
                ]
            stop_on_error: Whether to stop pipeline on first error
            save_report: Whether to save execution report
            
        Returns:
            Execution report dictionary
        """
        self.start_time = datetime.now()
        self.execution_log = []
        
        print("\n" + "="*70)
        print("🚀 STARTING NOTEBOOK PIPELINE")
        print("="*70)
        print(f"Pipeline: {len(pipeline_config)} notebook(s)")
        print(f"Start time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Stop on error: {stop_on_error}")
        print("="*70)
        
        total_notebooks = len(pipeline_config)
        successful = 0
        failed = 0
        
        for idx, config in enumerate(pipeline_config, 1):
            notebook_name = config.get('notebook')
            parameters = config.get('parameters', {})
            timeout = config.get('timeout', 3600)
            kernel = config.get('kernel', 'python3')
            
            print(f"\n[{idx}/{total_notebooks}] Processing: {notebook_name}")
            
            success, message, exec_time = self.execute_notebook(
                notebook_name,
                parameters=parameters,
                timeout=timeout,
                kernel_name=kernel
            )
            
            # Log execution
            log_entry = {
                'notebook': notebook_name,
                'success': success,
                'message': message,
                'execution_time': exec_time,
                'timestamp': datetime.now().isoformat(),
                'index': idx
            }
            self.execution_log.append(log_entry)
            
            if success:
                successful += 1
            else:
                failed += 1
                if stop_on_error:
                    print(f"\n⛔ Pipeline stopped due to error in: {notebook_name}")
                    break
        
        # Calculate total time
        end_time = datetime.now()
        self.total_time = (end_time - self.start_time).total_seconds()
        
        # Create report
        report = {
            'pipeline_name': 'AI Job Market Data Pipeline',
            'start_time': self.start_time.isoformat(),
            'end_time': end_time.isoformat(),
            'total_duration': self.total_time,
            'total_notebooks': total_notebooks,
            'successful': successful,
            'failed': failed,
            'stop_on_error': stop_on_error,
            'execution_log': self.execution_log
        }
        
        # Print summary
        self._print_summary(report)
        
        # Save report
        if save_report:
            self._save_report(report)
        
        return report
    
    def _print_summary(self, report: Dict):
        """Print pipeline execution summary."""
        print("\n" + "="*70)
        print("📊 PIPELINE EXECUTION SUMMARY")
        print("="*70)
        print(f"Total notebooks: {report['total_notebooks']}")
        print(f"✅ Successful: {report['successful']}")
        print(f"❌ Failed: {report['failed']}")
        print(f"⏱️  Total time: {report['total_duration']:.1f}s ({report['total_duration']/60:.1f} min)")
        
        print("\nExecution Details:")
        for log in report['execution_log']:
            status = "✅" if log['success'] else "❌"
            print(f"  {status} {log['notebook']:<40} {log['execution_time']:>6.1f}s")
        
        print("="*70)
        
        if report['failed'] == 0:
            print("🎉 All notebooks executed successfully!")
        else:
            print(f"⚠️  {report['failed']} notebook(s) failed")
        
        print("="*70)
    
    def _save_report(self, report: Dict):
        """Save execution report to file."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.log_dir / f"pipeline_report_{timestamp}.json"
        
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📄 Report saved to: {report_file}")
    
    def check_dependencies(self) -> Dict[str, bool]:
        """
        Check if required tools are available.
        
        Returns:
            Dictionary of tool availability
        """
        print("\n" + "="*70)
        print("🔍 CHECKING PIPELINE DEPENDENCIES")
        print("="*70)
        
        dependencies = {}
        
        # Check for papermill
        try:
            import papermill
            dependencies['papermill'] = True
            print("✅ Papermill installed (recommended)")
        except ImportError:
            dependencies['papermill'] = False
            print("⚠️  Papermill not installed (will use nbconvert)")
        
        # Check for nbconvert
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'jupyter', 'nbconvert', '--version'],
                capture_output=True,
                text=True
            )
            dependencies['nbconvert'] = result.returncode == 0
            if dependencies['nbconvert']:
                print("✅ Jupyter nbconvert available")
            else:
                print("❌ Jupyter nbconvert not available")
        except Exception:
            dependencies['nbconvert'] = False
            print("❌ Jupyter nbconvert not available")
        
        # Check for ipykernel
        try:
            import ipykernel
            dependencies['ipykernel'] = True
            print("✅ IPython kernel installed")
        except ImportError:
            dependencies['ipykernel'] = False
            print("⚠️  IPython kernel not installed")
        
        print("="*70)
        
        # Check if pipeline can run
        can_run = dependencies['nbconvert'] or dependencies['papermill']
        
        if can_run:
            print("\n✅ Pipeline can execute notebooks")
            if not dependencies['papermill']:
                print("💡 Tip: Install papermill for better features: pip install papermill")
        else:
            print("\n❌ Cannot execute notebooks - missing required dependencies")
            print("   Install with: pip install papermill jupyter nbconvert")
        
        return dependencies


def create_default_pipeline() -> List[Dict]:
    """
    Create default pipeline configuration for AI Job Market project.
    
    Returns:
        Pipeline configuration
    """
    return [
        {
            'notebook': 'cleaning.ipynb',
            'timeout': 3600,  # 60 minutes
            'description': 'Data cleaning and enrichment'
        },
        {
            'notebook': 'exploration.ipynb',
            'timeout': 1800,  # 30 minutes
            'description': 'Exploratory data analysis'
        },
        {
            'notebook': 'salary_intelligence_analysis.ipynb',
            'timeout': 1800,  # 30 minutes
            'description': 'Salary intelligence analysis'
        }
    ]


def main():
    """Main execution function for running the pipeline."""
    print("\n" + "="*70)
    print("📚 AI JOB MARKET - NOTEBOOK PIPELINE ORCHESTRATOR")
    print("="*70)
    
    # Initialize orchestrator
    orchestrator = NotebookOrchestrator(
        notebooks_dir='notebooks',
        output_dir='output/executed_notebooks',
        log_dir='output/logs'
    )
    
    # Check dependencies
    deps = orchestrator.check_dependencies()
    
    if not (deps.get('nbconvert') or deps.get('papermill')):
        print("\n❌ Cannot run pipeline - missing dependencies")
        print("Install with: pip install papermill jupyter nbconvert")
        return
    
    # Get pipeline configuration
    pipeline = create_default_pipeline()
    
    print("\n📋 Pipeline Configuration:")
    for idx, stage in enumerate(pipeline, 1):
        print(f"  {idx}. {stage['notebook']:<40} (timeout: {stage['timeout']}s)")
        if 'description' in stage:
            print(f"     └─ {stage['description']}")
    
    # Ask for confirmation
    print("\n" + "="*70)
    response = input("Execute pipeline? [y/N]: ").strip().lower()
    
    if response != 'y':
        print("Pipeline execution cancelled.")
        return
    
    # Run pipeline
    report = orchestrator.run_pipeline(
        pipeline_config=pipeline,
        stop_on_error=True,
        save_report=True
    )
    
    # Exit with appropriate code
    exit_code = 0 if report['failed'] == 0 else 1
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
