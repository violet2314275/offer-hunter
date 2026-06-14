"""
简历诊断模块：对比 JD，输出优化建议
"""
from .api_client import call_deepseek, call_deepseek_json

def diagnose_resume(profile: dict, profile_text: str, job: dict) -> dict:
    """
    对比简历和岗位 JD，输出诊断报告
    
    Returns:
        包含以下字段的字典：
        - match_score: 综合匹配分数（0-100）
        - matched_skills: 已匹配的技能列表
        - missing_skills: 缺失的技能列表
        - experience_gap: 经验差距分析
        - education_match: 学历匹配情况
        - optimization_suggestions: 简历优化建议（列表）
        - resume_edit_suggestions: 具体修改建议（针对每段经历）
        - cover_letter_tips: 求职信/自我介绍建议
    """
    system_prompt = """你是一个专业的简历诊断专家。请对比学生简历和目标岗位 JD，给出详细的诊断报告。

请以 JSON 格式返回，包含以下字段：
- match_score: 综合匹配分数（0-100 的整数）
- matched_skills: 已匹配的技能数组（字符串）
- missing_skills: 缺失的技能数组（字符串）
- experience_gap: 经验差距分析（100字以内）
- education_match: 学历匹配情况（50字以内）
- optimization_suggestions: 简历优化建议数组，每个建议是一段文字
- resume_edit_suggestions: 具体修改建议（针对简历各模块，100字以内）
- cover_letter_tips: 求职信/自我介绍建议（100字以内）

只返回 JSON，不要有其他文字。"""

    job_info = f"""
岗位：{job['title']}
公司：{job['company']}
要求学历：{job['education']}
要求经验：{job['experience']}
技术标签：{', '.join(job['tags'])}
岗位描述：{job['description']}
任职要求：{job['requirements']}
"""
    
    user_prompt = f"学生简历信息：\n{profile_text}\n\n目标岗位信息：\n{job_info}"
    
    return call_deepseek_json(system_prompt, user_prompt)


def generate_optimized_resume_section(profile: dict, job: dict, section: str) -> str:
    """
    针对特定岗位，生成优化后的简历段落
    
    Args:
        section: 要优化的部分，可选值：'skills', 'experiences', 'projects', 'summary'
        
    Returns:
        优化后的文字内容
    """
    section_names = {
        'skills': '技能清单',
        'experiences': '实习/工作经历',
        'projects': '项目经历',
        'summary': '个人总结/自我评价'
    }
    
    system_prompt = f"""你是一个专业的简历优化助手。请根据目标岗位的要求，帮学生优化简历中的「{section_names.get(section, section)}」部分。

优化原则：
1. 突出与目标岗位相关的技能和经验
2. 使用量化数据（如"提升30%"而非"提升了很多"）
3. 使用行业关键词，提高简历筛选通过率
4. 语言简洁专业，避免空话套话
5. 如果没有相关经验，给出合理的学习和替代方案

只返回优化后的内容，不要有其他解释文字。"""
    
    job_info = f"目标岗位：{job['title']}\n技术标签：{', '.join(job['tags'])}\n岗位描述：{job['description']}"
    profile_section = _get_profile_section(profile, section)
    
    user_prompt = f"目标岗位要求：\n{job_info}\n\n学生当前的{section_names.get(section, section)}：\n{profile_section}\n\n请输出优化后的内容："
    
    return call_deepseek(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        temperature=0.4,
        max_tokens=1000,
    )


def _get_profile_section(profile: dict, section: str) -> str:
    """提取学生画像中指定部分的内容"""
    if section == 'skills':
        return "、".join(profile.get('skills', []))
    elif section == 'experiences':
        exps = profile.get('experiences', [])
        return "\n".join([f"{e.get('company', '')} - {e.get('role', '')}：{e.get('description', '')}" for e in exps])
    elif section == 'projects':
        projs = profile.get('projects', [])
        return "\n".join([f"{p.get('name', '')} - {p.get('role', '')}：{p.get('description', '')}" for p in projs])
    elif section == 'summary':
        return profile.get('strengths', '')
    return ""
