"""
简历解析模块：从 PDF/Word/文本 中提取学生画像
"""
import pdfplumber
from docx import Document
from io import BytesIO
from .api_client import call_deepseek_json

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """从 PDF 文件中提取文字"""
    text = ""
    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """从 Word 文件中提取文字"""
    doc = Document(BytesIO(file_bytes))
    text = "\n".join([p.text for p in doc.paragraphs if p.text.strip()])
    return text.strip()


def extract_text(uploaded_file) -> str:
    """
    根据文件类型自动选择解析方法
    uploaded_file: Streamlit 上传的文件对象
    """
    file_bytes = uploaded_file.getvalue()
    file_name = uploaded_file.name.lower()
    
    if file_name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif file_name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    elif file_name.endswith(".txt"):
        return file_bytes.decode("utf-8", errors="ignore")
    else:
        raise ValueError(f"不支持的文件格式：{file_name}，请上传 PDF/Word/TXT 文件")


def parse_resume_with_ai(resume_text: str) -> dict:
    """
    使用 AI 从简历文本中提取学生画像
    
    Returns:
        包含学生画像的字典，包括：
        - name: 姓名
        - education: 教育背景（学校、专业、学历、毕业时间）
        - skills: 技能列表
        - experiences: 实习/工作经历列表
        - projects: 项目经历列表
        - strengths: 个人优势
        - job_intent: 求职意向（岗位方向、期望城市、薪资期望）
    """
    system_prompt = """你是一个专业的简历解析助手。请从简历文本中提取结构化信息，并以 JSON 格式返回。

请提取以下字段（如果信息缺失则留空字符串或空数组）：
- name: 姓名
- education: 对象，包含 school（学校）、major（专业）、degree（学历：本科/硕士/博士）、graduation_year（毕业年份）
- skills: 技能数组，每个技能是一个字符串
- experiences: 数组，每个元素包含 company（公司）、role（岗位）、duration（时长）、description（工作描述）
- projects: 数组，每个元素包含 name（项目名称）、role（角色）、description（项目描述）
- strengths: 个人优势（字符串）
- job_intent: 对象，包含 target_role（目标岗位）、target_city（期望城市）、expected_salary（期望薪资）

只返回 JSON，不要有其他文字。"""

    user_prompt = f"请解析以下简历内容：\n\n{resume_text[:4000]}"  # 限制长度避免超 token
    
    return call_deepseek_json(system_prompt, user_prompt)


def format_student_profile(profile: dict) -> str:
    """
    将学生画像格式化为可读文本，用于后续匹配和诊断
    """
    lines = []
    
    if profile.get("name"):
        lines.append(f"姓名：{profile['name']}")
    
    edu = profile.get("education", {})
    if edu:
        edu_str = f"教育背景：{edu.get('school', '')} - {edu.get('major', '')} - {edu.get('degree', '')}"
        if edu.get('graduation_year'):
            edu_str += f"（{edu.get('graduation_year')}年毕业）"
        lines.append(edu_str)
    
    skills = profile.get("skills", [])
    if skills:
        lines.append(f"技能：{', '.join(skills)}")
    
    exps = profile.get("experiences", [])
    if exps:
        lines.append("\n实习/工作经历：")
        for exp in exps:
            lines.append(f"  - {exp.get('company', '')} | {exp.get('role', '')} | {exp.get('duration', '')}")
            if exp.get('description'):
                lines.append(f"    {exp['description']}")
    
    projects = profile.get("projects", [])
    if projects:
        lines.append("\n项目经历：")
        for proj in projects:
            lines.append(f"  - {proj.get('name', '')} | {proj.get('role', '')}")
            if proj.get('description'):
                lines.append(f"    {proj['description']}")
    
    if profile.get("strengths"):
        lines.append(f"\n个人优势：{profile['strengths']}")
    
    intent = profile.get("job_intent", {})
    if intent:
        lines.append("\n求职意向：")
        if intent.get('target_role'):
            lines.append(f"  目标岗位：{intent['target_role']}")
        if intent.get('target_city'):
            lines.append(f"  期望城市：{intent['target_city']}")
        if intent.get('expected_salary'):
            lines.append(f"  期望薪资：{intent['expected_salary']}")
    
    return "\n".join(lines)
