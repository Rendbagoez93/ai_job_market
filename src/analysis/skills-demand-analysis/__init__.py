"""Skills Demand & Talent Gap Analysis Module.

This module provides comprehensive analysis of:
- Skill demand ranking and trends
- Skill correlation and co-occurrence patterns
- Job-specific skill requirements
- High-value skills identification
- Talent gap analysis
"""

from .skills_demand_analyzer import SkillsDemandAnalyzer, run_skills_demand_analysis

__all__ = ['SkillsDemandAnalyzer', 'run_skills_demand_analysis']
