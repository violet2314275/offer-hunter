"""
Offer 捕手 - Streamlit 主应用
三页面：① 简历上传 & 画像解析  ② 岗位匹配推荐  ③ 简历诊断 & 优化
"""
import sys
import os
import json
import streamlit as st
import pandas as pd

# 将项目根目录加入 path，便于导入 utils
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    call_deepseek,
    test_connection,
    extract_text,
    parse_resume_with_ai,
    format_student_profile,
    match_jobs,
    diagnose_resume,
    generate_optimized_resume_section,
    plot_match_radar,
    plot_jobs_comparison,
    plot_skills_radar,
    plot_salary_distribution,
    plot_match_score_gauge,
)

# ========== 页面配置 ==========
st.set_page_config(
    page_title="Offer 捕手 - AI 求职智能匹配",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ========== 全局样式 ==========
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #0052D9 0%, #7B4FF5 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 2rem;
    }
    .main-header h1 {
        color: white;
        margin: 0;
        font-size: 2rem;
    }
    .main-header p {
        color: rgba(255,255,255,0.85);
        margin: 0.3rem 0 0 0;
    }
    .metric-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-card h3 {
        color: #0052D9;
        font-size: 1.8rem;
        margin: 0;
    }
    .metric-card p {
        color: #666;
        margin: 0.3rem 0 0 0;
        font-size: 0.9rem;
    }
    .job-card {
        background: white;
        padding: 1.2rem;
        border-radius: 10px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        margin-bottom: 1rem;
        border-left: 4px solid #0052D9;
    }
    .job-card.match-high {
        border-left-color: #51CF66;
    }
    .job-card.match-mid {
        border-left-color: #FFA94D;
    }
    .job-card.match-low {
        border-left-color: #FF6B6B;
    }
    .tag {
        display: inline-block;
        background: #F0F4FF;
        color: #0052D9;
        padding: 2px 10px;
        border-radius: 12px;
        font-size: 0.8rem;
        margin: 2px 4px 2px 0;
    }
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #0052D9, #7B4FF5);
    }
    .score-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        color: white;
    }
    .score-high { background: #51CF66; }
    .score-mid { background: #FFA94D; }
    .score-low { background: #FF6B6B; }
    .section-divider {
        height: 3px;
        background: linear-gradient(90deg, #0052D9, #7B4FF5);
        border-radius: 2px;
        margin: 1.5rem 0;
    }
</style>
""", unsafe_allow_html=True)


# ========== 辅助函数 ==========
@st.cache_data
def load_jobs():
    """加载岗位数据（缓存）"""
    import json
    jobs_path = os.path.join(os.path.dirname(__file__), "data", "jobs.json")
    with open(jobs_path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_score_class(score: int) -> str:
    """根据分数返回 CSS 类名"""
    if score >= 70:
        return "high", "score-high"
    elif score >= 40:
        return "mid", "score-mid"
    else:
        return "low", "score-low"


def init_session_state():
    """初始化 session_state"""
    if "profile" not in st.session_state:
        st.session_state.profile = None
    if "profile_text" not in st.session_state:
        st.session_state.profile_text = ""
    if "resume_text" not in st.session_state:
        st.session_state.resume_text = ""
    if "matched_jobs" not in st.session_state:
        st.session_state.matched_jobs = []
    if "selected_job" not in st.session_state:
        st.session_state.selected_job = None
    if "diagnosis" not in st.session_state:
        st.session_state.diagnosis = None
    if "api_tested" not in st.session_state:
        st.session_state.api_tested = False


# ========== 页面 1：简历上传 & 画像解析 ==========
def page_resume():
    st.markdown("## 📄 第一步：上传简历 & 解析画像")
    st.markdown("上传你的简历（支持 PDF / Word / TXT），AI 将自动提取你的技能、经历和求职意向。")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    # 侧边：API 连接测试
    with st.sidebar:
        st.markdown("### 🔧 系统状态")
        if st.button("测试 API 连接", key="test_api"):
            with st.spinner("正在测试..."):
                result = test_connection()
                st.session_state.api_tested = result
                if result:
                    st.success("✅ API 连接正常")
                else:
                    st.error("❌ API 连接失败，请检查 API Key")
        
        if st.session_state.api_tested:
            st.success("✅ API 已连接")
        else:
            st.warning("⚠️ 请先测试 API 连接")
        
        st.markdown("---")
        st.markdown("**API 配置**")
        st.markdown("请在 `.env` 文件中配置 `DEEPSEEK_API_KEY`，或在 Streamlit Cloud 的 `secrets.toml` 中配置。")
    
    # 上传区域
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 上传简历")
        uploaded_file = st.file_uploader(
            "选择简历文件",
            type=["pdf", "docx", "txt"],
            help="支持 PDF、Word（.docx）、纯文本（.txt）格式"
        )
        
        if uploaded_file is not None:
            with st.spinner("正在解析简历内容..."):
                try:
                    resume_text = extract_text(uploaded_file)
                    st.session_state.resume_text = resume_text
                    st.success(f"✅ 成功解析简历，共 {len(resume_text)} 字")
                except Exception as e:
                    st.error(f"❌ 简历解析失败：{e}")
                    return
        
        # 或者手动输入
        st.markdown("**或手动粘贴简历文字**")
        manual_text = st.text_area(
            "粘贴简历内容",
            height=200,
            placeholder="请粘贴你的简历文字内容...",
        )
        if manual_text and not st.session_state.resume_text:
            st.session_state.resume_text = manual_text
        
        # 开始解析按钮
        if st.session_state.resume_text and st.button("🚀 开始 AI 解析", type="primary", use_container_width=True):
            with st.spinner("AI 正在解析简历画像，请稍候（约 10-20 秒）..."):
                try:
                    profile = parse_resume_with_ai(st.session_state.resume_text)
                    st.session_state.profile = profile
                    st.session_state.profile_text = format_student_profile(profile)
                    st.success("✅ 简历画像解析完成！")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ AI 解析失败：{e}")
    
    with col2:
        st.markdown("### 解析结果")
        if st.session_state.profile:
            profile = st.session_state.profile
            
            # 基本信息
            st.markdown(f"**姓名**：{profile.get('name', '未识别')}")
            
            edu = profile.get("education", {})
            if edu:
                st.markdown(f"**教育背景**：{edu.get('school', '')} · {edu.get('major', '')} · {edu.get('degree', '')}")
                if edu.get('graduation_year'):
                    st.markdown(f"**毕业年份**：{edu.get('graduation_year')}")
            
            # 技能
            skills = profile.get("skills", [])
            if skills:
                st.markdown("**技能清单**")
                tags_html = "".join([f'<span class="tag">{s}</span>' for s in skills])
                st.markdown(f'<div style="margin:0.5rem 0">{tags_html}</div>', unsafe_allow_html=True)
            
            # 求职意向
            intent = profile.get("job_intent", {})
            if intent:
                st.markdown("**求职意向**")
                if intent.get("target_role"):
                    st.markdown(f"- 目标岗位：{intent['target_role']}")
                if intent.get("target_city"):
                    st.markdown(f"- 期望城市：{intent['target_city']}")
                if intent.get("expected_salary"):
                    st.markdown(f"- 期望薪资：{intent['expected_salary']}")
            
            # 完整画像
            with st.expander("查看完整画像（用于匹配）"):
                st.text(st.session_state.profile_text)
        else:
            st.info("👆 请先上传简历并点击「开始 AI 解析」")
    
    # 导航按钮
    if st.session_state.profile:
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        if st.button("➡️ 进入岗位匹配", type="primary", use_container_width=True):
            st.session_state.page = "match"
            st.rerun()


# ========== 页面 2：岗位匹配推荐 ==========
def page_match():
    st.markdown("## 🎯 第二步：智能岗位匹配")
    st.markdown("AI 将根据你的简历画像，从岗位库中进行**关键词粗筛 + AI 精排**，推荐最匹配你的岗位。")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ 请先完成简历上传和解析")
        if st.button("⬅️ 返回简历上传"):
            st.session_state.page = "resume"
            st.rerun()
        return
    
    # 匹配按钮
    col_btn, col_info = st.columns([1, 3])
    with col_btn:
        if st.button("🚀 开始智能匹配", type="primary", use_container_width=True):
            with st.spinner("正在进行岗位匹配（关键词粗筛 + AI 精排），请稍候（约 20-40 秒）..."):
                try:
                    jobs = load_jobs()
                    matched = match_jobs(jobs, st.session_state.profile, st.session_state.profile_text)
                    st.session_state.matched_jobs = matched
                    st.success(f"✅ 匹配完成！共找到 {len(matched)} 个推荐岗位")
                    st.balloons()
                except Exception as e:
                    st.error(f"❌ 匹配失败：{e}")
    
    with col_info:
        if st.session_state.matched_jobs:
            st.info(f"共找到 **{len(st.session_state.matched_jobs)}** 个推荐岗位，按匹配度排序")
    
    # 展示匹配结果
    if st.session_state.matched_jobs:
        jobs = st.session_state.matched_jobs
        
        # 统计指标
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            high_match = sum(1 for j in jobs if j.get("match_score", 0) >= 70)
            st.markdown(f'<div class="metric-card"><h3>{high_match}</h3><p>高匹配岗位（≥70分）</p></div>', unsafe_allow_html=True)
        with col2:
            mid_match = sum(1 for j in jobs if 40 <= j.get("match_score", 0) < 70)
            st.markdown(f'<div class="metric-card"><h3>{mid_match}</h3><p>中匹配岗位（40-69分）</p></div>', unsafe_allow_html=True)
        with col3:
            avg_score = int(sum(j.get("match_score", 0) for j in jobs) / len(jobs)) if jobs else 0
            st.markdown(f'<div class="metric-card"><h3>{avg_score}</h3><p>平均匹配度</p></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card"><h3>{len(jobs)}</h3><p>推荐岗位总数</p></div>', unsafe_allow_html=True)
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # 图表
        viz_col1, viz_col2 = st.columns(2)
        with viz_col1:
            fig = plot_jobs_comparison(jobs)
            st.plotly_chart(fig, use_container_width=True)
        with viz_col2:
            fig2 = plot_salary_distribution(jobs)
            st.plotly_chart(fig2, use_container_width=True)
        
        # 岗位列表
        st.markdown("### 📋 推荐岗位列表")
        
        # 筛选
        filter_col1, filter_col2 = st.columns([1, 1])
        with filter_col1:
            min_score = st.slider("最低匹配度", 0, 100, 0)
        with filter_col2:
            categories = ["全部"] + list(set([j.get("category", "") for j in jobs]))
            selected_category = st.selectbox("岗位类别", categories)
        
        # 过滤
        filtered = [j for j in jobs if j.get("match_score", 0) >= min_score]
        if selected_category != "全部":
            filtered = [j for j in filtered if j.get("category") == selected_category]
        
        # 展示岗位卡片
        for job in filtered:
            score = job.get("match_score", 0)
            score_level, badge_class = get_score_class(score)
            card_class = f"match-{score_level}"
            
            with st.container():
                st.markdown(f"""
                <div class="job-card {card_class}">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <div>
                            <h4 style="margin:0;">{job['title']} @ {job['company']}</h4>
                            <p style="color:#666; margin:0.3rem 0;">
                                📍 {job['location']} | 💰 {job['salary']} | 🎓 {job['education']} | 📅 {job['experience']}
                            </p>
                        </div>
                        <div>
                            <span class="score-badge {badge_class}">{score}分</span>
                        </div>
                    </div>
                    <div style="margin:0.5rem 0;">
                        {''.join([f'<span class="tag">{t}</span>' for t in job.get('tags', [])[:6]])}
                    </div>
                    <p style="color:#444; font-size:0.9rem;">{job.get('description', '')[:150]}...</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_a, col_b = st.columns([1, 1])
                with col_a:
                    if st.button(f"📝 查看诊断报告", key=f"diag_{job['id']}", use_container_width=True):
                        st.session_state.selected_job = job
                        st.session_state.page = "diagnosis"
                        st.rerun()
                with col_b:
                    if st.button(f"🔍 查看详情", key=f"detail_{job['id']}", use_container_width=True):
                        st.session_state.selected_job = job
                        st.info(f"**岗位详情**\n\n{job.get('description', '')}\n\n**任职要求**\n\n{job.get('requirements', '')}")
        
        # 导航
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        nav_col1, nav_col2 = st.columns([1, 1])
        with nav_col1:
            if st.button("⬅️ 返回简历上传"):
                st.session_state.page = "resume"
                st.rerun()
        with nav_col2:
            if st.button("➡️ 进入简历诊断", type="primary", use_container_width=True):
                if st.session_state.matched_jobs:
                    st.session_state.selected_job = st.session_state.matched_jobs[0]
                st.session_state.page = "diagnosis"
                st.rerun()


# ========== 页面 3：简历诊断 & 优化 ==========
def page_diagnosis():
    st.markdown("## 📝 第三步：简历诊断 & 优化建议")
    st.markdown("对比你的简历和目标岗位 JD，AI 将输出详细的诊断报告，并给出优化建议。")
    st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
    
    if not st.session_state.profile:
        st.warning("⚠️ 请先完成简历上传和解析")
        return
    
    if not st.session_state.matched_jobs:
        st.warning("⚠️ 请先进行岗位匹配")
        return
    
    # 选择目标岗位
    job_options = {f"{j['title']} @ {j['company']}（{j.get('match_score', 0)}分）": j for j in st.session_state.matched_jobs}
    selected_job_name = st.selectbox(
        "选择目标岗位（用于诊断）",
        list(job_options.keys()),
        index=0,
    )
    selected_job = job_options[selected_job_name]
    st.session_state.selected_job = selected_job
    
    # 显示岗位信息
    with st.expander("查看岗位 JD", expanded=False):
        st.markdown(f"**岗位**：{selected_job['title']}")
        st.markdown(f"**公司**：{selected_job['company']}")
        st.markdown(f"**描述**：{selected_job['description']}")
        st.markdown(f"**要求**：{selected_job['requirements']}")
        st.markdown(f"**标签**：{', '.join(selected_job['tags'])}")
    
    # 开始诊断按钮
    if st.button("🚀 开始 AI 诊断", type="primary", use_container_width=True):
        with st.spinner("AI 正在诊断简历，请稍候（约 20-30 秒）..."):
            try:
                diagnosis = diagnose_resume(
                    st.session_state.profile,
                    st.session_state.profile_text,
                    selected_job
                )
                st.session_state.diagnosis = diagnosis
                st.success("✅ 诊断完成！")
                st.balloons()
            except Exception as e:
                st.error(f"❌ 诊断失败：{e}")
    
    # 展示诊断报告
    if st.session_state.diagnosis:
        diag = st.session_state.diagnosis
        job = st.session_state.selected_job
        
        # 匹配度仪表盘
        score = diag.get("match_score", 0)
        col_gauge, col_info = st.columns([1, 2])
        with col_gauge:
            fig = plot_match_score_gauge(score)
            st.plotly_chart(fig, use_container_width=True)
        with col_info:
            st.markdown(f"### 匹配度：{score} / 100")
            level = "🔥 高度匹配" if score >= 70 else ("⚡ 中等匹配" if score >= 40 else "⚠️ 匹配度较低")
            st.markdown(f"**{level}**")
            st.markdown(f"**学历匹配**：{diag.get('education_match', '')}")
            st.markdown(f"**经验差距**：{diag.get('experience_gap', '')}")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # 技能对比雷达图
        col_radar1, col_radar2 = st.columns([1, 1])
        with col_radar1:
            student_skills = st.session_state.profile.get("skills", [])
            job_tags = job.get("tags", [])
            fig = plot_skills_radar(student_skills, job_tags)
            st.plotly_chart(fig, use_container_width=True)
        with col_radar2:
            st.markdown("### 🔧 技能匹配分析")
            matched = diag.get("matched_skills", [])
            missing = diag.get("missing_skills", [])
            
            if matched:
                st.markdown("**✅ 已匹配技能**")
                st.markdown(", ".join([f"`{s}`" for s in matched]))
            if missing:
                st.markdown("**❌ 缺失技能**")
                st.markdown(", ".join([f"`{s}`" for s in missing]))
                st.markdown("💡 **建议**：在简历中补充这些技能的学习经历或项目经验。")
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # 优化建议
        st.markdown("### 💡 简历优化建议")
        suggestions = diag.get("optimization_suggestions", [])
        for i, sug in enumerate(suggestions, 1):
            st.markdown(f"**{i}.** {sug}")
        
        if diag.get("resume_edit_suggestions"):
            st.markdown("### ✏️ 具体修改建议")
            st.info(diag["resume_edit_suggestions"])
        
        if diag.get("cover_letter_tips"):
            st.markdown("### 📨 求职信/自我介绍建议")
            st.success(diag["cover_letter_tips"])
        
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        
        # 简历优化（针对具体模块）
        st.markdown("### ✏️ AI 简历优化")
        st.markdown("选择你想优化的简历模块，AI 将生成针对该岗位的优化版本。")
        
        optimize_col1, optimize_col2 = st.columns([1, 1])
        with optimize_col1:
            section = st.selectbox(
                "选择优化模块",
                ["skills", "experiences", "projects", "summary"],
                format_func=lambda x: {"skills": "技能清单", "experiences": "实习/工作经历", "projects": "项目经历", "summary": "个人总结"}[x]
            )
        with optimize_col2:
            if st.button("🚀 生成优化内容", use_container_width=True):
                with st.spinner("AI 正在优化简历内容，请稍候..."):
                    try:
                        optimized = generate_optimized_resume_section(
                            st.session_state.profile,
                            job,
                            section
                        )
                        st.session_state.optimized_content = optimized
                        st.success("✅ 优化完成！")
                    except Exception as e:
                        st.error(f"❌ 优化失败：{e}")
        
        if "optimized_content" in st.session_state:
            st.markdown("#### 优化结果（可直接复制到你的简历）")
            st.text_area(
                "优化后的内容",
                value=st.session_state.optimized_content,
                height=300,
                key="optimized_output"
            )
            if st.button("📋 复制到剪贴板", use_container_width=True):
                st.success("内容已显示在上方文本框中，请手动复制")
        
        # 导航
        st.markdown('<div class="section-divider"></div>', unsafe_allow_html=True)
        if st.button("⬅️ 返回岗位匹配", use_container_width=True):
            st.session_state.page = "match"
            st.rerun()


# ========== 主函数 ==========
def main():
    init_session_state()
    
    # 头部
    st.markdown("""
    <div class="main-header">
        <h1>🎯 Offer 捕手</h1>
        <p>AI 求职智能匹配 · 简历诊断优化 · 提升初筛命中率</p>
    </div>
    """, unsafe_allow_html=True)
    
    # 侧边栏导航
    with st.sidebar:
        st.markdown("## 📋 导航")
        page = st.radio(
            "选择页面",
            ["📄 简历上传 & 画像解析", "🎯 智能岗位匹配", "📝 简历诊断 & 优化"],
            key="page_selector"
        )
        
        # 进度条
        st.markdown("---")
        st.markdown("**完成进度**")
        steps = [
            ("简历上传", st.session_state.profile is not None),
            ("岗位匹配", len(st.session_state.matched_jobs) > 0),
            ("简历诊断", st.session_state.diagnosis is not None),
        ]
        for step_name, done in steps:
            icon = "✅" if done else "⬜"
            st.markdown(f"{icon} {step_name}")
        
        st.markdown("---")
        st.markdown("**关于**")
        st.markdown("Offer 捕手 v1.0\n\nAI 驱动的学生求职匹配智能体\n\n技术栈：Streamlit + DeepSeek API")
    
    # 页面路由
    page_map = {
        "📄 简历上传 & 画像解析": "resume",
        "🎯 智能岗位匹配": "match",
        "📝 简历诊断 & 优化": "diagnosis",
    }
    
    # 从 session_state 或 radio 获取当前页面
    current_page = st.session_state.get("page", "resume")
    selected_page = page_map.get(page, "resume")
    
    # 如果 radio 切换了页面，更新 session_state
    if selected_page != current_page:
        st.session_state.page = selected_page
        st.rerun()
    
    current_page = st.session_state.get("page", "resume")
    
    if current_page == "resume":
        page_resume()
    elif current_page == "match":
        page_match()
    elif current_page == "diagnosis":
        page_diagnosis()


if __name__ == "__main__":
    main()
