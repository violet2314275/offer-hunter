"""
Offer 捕手 - 工具模块初始化
"""
from .api_client import call_deepseek, call_deepseek_json, test_connection
from .resume_parser import extract_text, parse_resume_with_ai, format_student_profile
from .job_matcher import match_jobs, keyword_filter, ai_ranking
from .resume_advisor import diagnose_resume, generate_optimized_resume_section
from .visualization import (
    plot_match_radar,
    plot_jobs_comparison,
    plot_skills_radar,
    plot_salary_distribution,
    plot_match_score_gauge,
)

__all__ = [
    # API
    'call_deepseek',
    'call_deepseek_json',
    'test_connection',
    # 简历解析
    'extract_text',
    'parse_resume_with_ai',
    'format_student_profile',
    # 岗位匹配
    'match_jobs',
    'keyword_filter',
    'ai_ranking',
    # 简历诊断
    'diagnose_resume',
    'generate_optimized_resume_section',
    # 可视化
    'plot_match_radar',
    'plot_jobs_comparison',
    'plot_skills_radar',
    'plot_salary_distribution',
    'plot_match_score_gauge',
]
