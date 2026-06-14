"""
图表可视化模块：雷达图、柱状图、对比图
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np

def plot_match_radar(job_scores: list) -> go.Figure:
    """
    绘制岗位匹配度雷达图
    
    Args:
        job_scores: 包含各维度评分的列表，每个元素为字典：
                   {'dimension': '技能匹配', 'score': 80, 'full_mark': 100}
                   
    维度包括：技能匹配、经验匹配、学历匹配、岗位契合度、发展空间
    """
    if not job_scores:
        # 默认维度
        dimensions = ['技能匹配', '经验匹配', '学历匹配', '岗位契合度', '发展空间']
        scores = [0] * 5
    else:
        dimensions = [s['dimension'] for s in job_scores]
        scores = [s['score'] for s in job_scores]
    
    fig = go.Figure(data=go.Scatterpolar(
        r=scores + [scores[0]],  # 闭合
        theta=dimensions + [dimensions[0]],
        fill='toself',
        line_color='#0052D9',
        fillcolor='rgba(0, 82, 217, 0.2)',
        name='匹配度'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False,
        title="岗位匹配度雷达图",
        height=400,
    )
    
    return fig


def plot_jobs_comparison(jobs: list) -> go.Figure:
    """
    绘制多个岗位的匹配度对比柱状图
    
    Args:
        jobs: 岗位列表，每个岗位包含 title, company, match_score
    """
    if not jobs:
        return go.Figure()
    
    # 取前 10 个岗位
    top_jobs = jobs[:10]
    
    titles = [f"{j['title'][:10]}..." if len(j['title']) > 10 else j['title'] for j in top_jobs]
    scores = [j.get('match_score', 0) for j in top_jobs]
    companies = [j['company'] for j in top_jobs]
    
    # 根据分数设置颜色
    colors = ['#FF6B6B' if s < 40 else '#FFA94D' if s < 70 else '#51CF66' for s in scores]
    
    fig = go.Figure(data=go.Bar(
        x=titles,
        y=scores,
        marker_color=colors,
        text=scores,
        textposition='auto',
        hovertemplate='<b>%{x}</b><br>匹配度：%{y}<br>公司：%{customdata}<extra></extra>',
        customdata=companies,
    ))
    
    fig.update_layout(
        title="岗位匹配度对比（Top 10）",
        xaxis_title="岗位",
        yaxis_title="匹配度评分",
        yaxis=dict(range=[0, 100]),
        height=450,
        showlegend=False,
    )
    
    return fig


def plot_skills_radar(profile_skills: list, job_tags: list) -> go.Figure:
    """
    绘制学生技能与岗位要求的对比雷达图
    
    Args:
        profile_skills: 学生技能列表，如 ['Python', 'SQL', '机器学习']
        job_tags: 岗位要求标签列表，如 ['Python', 'PyTorch', 'NLP', 'LLM']
    """
    # 构建所有技能维度（取并集，最多 8 个）
    all_skills = list(set(profile_skills + job_tags))[:8]
    
    if not all_skills:
        all_skills = ['Python', 'SQL', '机器学习', '深度学习', '数据处理', '可视化']
    
    # 学生技能匹配情况（有该技能=100，没有=0）
    student_scores = [100 if skill in profile_skills else 0 for skill in all_skills]
    
    # 岗位要求重要性（该标签在岗位中=100，不在=0，可扩展为加权）
    job_scores = [100 if skill in job_tags else 0 for skill in all_skills]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=student_scores + [student_scores[0]],
        theta=all_skills + [all_skills[0]],
        fill='toself',
        name='我的技能',
        line_color='#0052D9',
        fillcolor='rgba(0, 82, 217, 0.2)',
    ))
    
    fig.add_trace(go.Scatterpolar(
        r=job_scores + [job_scores[0]],
        theta=all_skills + [all_skills[0]],
        fill='toself',
        name='岗位要求',
        line_color='#7B4FF5',
        fillcolor='rgba(123, 79, 245, 0.2)',
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        title="技能对比：我 vs 岗位要求",
        height=450,
    )
    
    return fig


def plot_salary_distribution(jobs: list) -> go.Figure:
    """
    绘制岗位薪资分布图
    """
    if not jobs:
        return go.Figure()
    
    # 解析薪资（提取最小值）
    salaries = []
    titles = []
    for j in jobs[:15]:
        sal = j.get('salary', '')
        # 简单解析，如 "20-35K·14薪" -> 20
        import re
        match = re.search(r'(\d+)', sal)
        if match:
            salaries.append(int(match.group(1)))
            titles.append(j['title'][:10])
    
    if not salaries:
        return go.Figure()
    
    fig = go.Figure(data=go.Bar(
        x=titles,
        y=salaries,
        marker_color='#7B4FF5',
        text=salaries,
        textposition='auto',
    ))
    
    fig.update_layout(
        title="推荐岗位薪资分布（月薪K）",
        xaxis_title="岗位",
        yaxis_title="月薪（K）",
        height=400,
    )
    
    return fig


def plot_match_score_gauge(score: int) -> go.Figure:
    """
    绘制单个匹配度仪表盘
    """
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "岗位匹配度"},
        delta={'reference': 70, 'position': "top"},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#0052D9"},
            'steps': [
                {'range': [0, 40], 'color': "#FFE0E0"},
                {'range': [40, 70], 'color': "#FFF4E0"},
                {'range': [70, 100], 'color': "#E0FFE0"},
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 70
            }
        }
    ))
    
    fig.update_layout(height=300)
    return fig
