"""
岗位匹配模块：关键词粗筛 + AI 精排
"""
import json
from typing import List, Dict
from .api_client import call_deepseek_json

def keyword_filter(jobs: List[Dict], profile: Dict, top_n: int = 20) -> List[Dict]:
    """
    第一层：关键词粗筛
    根据学生画像中的技能、求职意向等，筛选相关岗位
    
    Returns:
        粗筛后的岗位列表（最多 top_n 个）
    """
    # 提取学生关键词
    skills = profile.get("skills", [])
    intent = profile.get("job_intent", {})
    target_role = intent.get("target_role", "") if isinstance(intent, dict) else ""
    
    # 构建搜索关键词集合
    keywords = set()
    keywords.update([s.lower() for s in skills])
    if target_role:
        keywords.update(target_role.lower().split())
    
    # 计算岗位匹配分数（基于标签匹配）
    scored_jobs = []
    for job in jobs:
        tags = [t.lower() for t in job.get("tags", [])]
        title = job.get("title", "").lower()
        category = job.get("category", "").lower()
        
        # 计算匹配分数
        score = 0
        for kw in keywords:
            if kw in tags:
                score += 3
            if kw in title:
                score += 5
            if kw in category:
                score += 2
        
        if score > 0 or not keywords:  # 有关键词匹配，或无关键词时全部保留
            job_copy = job.copy()
            job_copy["_keyword_score"] = score
            scored_jobs.append(job_copy)
    
    # 按分数排序，取前 top_n
    scored_jobs.sort(key=lambda x: x["_keyword_score"], reverse=True)
    return scored_jobs[:top_n]


def ai_ranking(jobs: List[Dict], profile_text: str) -> List[Dict]:
    """
    第二层：AI 精排
    使用 AI 对每个岗位进行匹配度评分和理由说明
    
    Returns:
        排序后的岗位列表，每个岗位增加 match_score 和 match_reason 字段
    """
    if not jobs:
        return []
    
    # 构造岗位信息文本（限制数量避免超 token）
    jobs_text = ""
    for i, job in enumerate(jobs[:15]):  # 最多精排 15 个
        jobs_text += f"\n【岗位 {i+1}】\n"
        jobs_text += f"ID: {job['id']}\n"
        jobs_text += f"标题：{job['title']}\n"
        jobs_text += f"公司：{job['company']}\n"
        jobs_text += f"地点：{job['location']}\n"
        jobs_text += f"薪资：{job['salary']}\n"
        jobs_text += f"学历要求：{job['education']}\n"
        jobs_text += f"经验要求：{job['experience']}\n"
        jobs_text += f"技术标签：{', '.join(job['tags'])}\n"
        jobs_text += f"岗位描述：{job['description'][:200]}\n"
    
    system_prompt = """你是一个专业的求职匹配助手。请根据学生画像，对给出的岗位进行匹配度评分和理由说明。

请以 JSON 数组格式返回，每个元素包含：
- id: 岗位 ID（整数）
- match_score: 匹配度评分（0-100 的整数，100 表示完全匹配）
- match_reason: 匹配理由（50-100 字，说明匹配点和潜在不足）
- suggestion: 提升建议（50-100 字，说明如何提升该岗位匹配度）

只返回 JSON 数组，不要有其他文字。"""

    user_prompt = f"学生画像：\n{profile_text}\n\n待匹配岗位：{jobs_text}"
    
    result = call_deepseek_json(system_prompt, user_prompt)
    
    # 将 AI 结果合并回岗位数据
    if isinstance(result, list):
        score_map = {item["id"]: item for item in result if "id" in item}
        for job in jobs:
            if job["id"] in score_map:
                job["match_score"] = score_map[job["id"]].get("match_score", 0)
                job["match_reason"] = score_map[job["id"]].get("match_reason", "")
                job["suggestion"] = score_map[job["id"]].get("suggestion", "")
            else:
                job["match_score"] = 0
                job["match_reason"] = ""
                job["suggestion"] = ""
    else:
        # 如果返回格式不对，给所有岗位默认分数
        for job in jobs:
            job["match_score"] = job.get("_keyword_score", 50)
            job["match_reason"] = ""
            job["suggestion"] = ""
    
    # 按匹配度排序
    jobs.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    
    return jobs


def match_jobs(jobs: List[Dict], profile: Dict, profile_text: str) -> List[Dict]:
    """
    完整匹配流程：关键词粗筛 -> AI 精排
    
    Returns:
        按匹配度排序的岗位列表
    """
    # 第一层：关键词粗筛
    filtered_jobs = keyword_filter(jobs, profile, top_n=15)
    
    # 第二层：AI 精排
    ranked_jobs = ai_ranking(filtered_jobs, profile_text)
    
    return ranked_jobs
