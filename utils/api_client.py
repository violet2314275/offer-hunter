"""
DeepSeek API 封装，含重试机制和错误处理
"""
import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# 从环境变量或Streamlit secrets读取配置
def _get_config(key: str, default: str = "") -> str:
    """优先从环境变量读取，其次从streamlit secrets读取"""
    val = os.getenv(key, "")
    if val:
        return val
    try:
        import streamlit as st
        return st.secrets.get(key, default)
    except Exception:
        return default


API_KEY = _get_config("DEEPSEEK_API_KEY")
BASE_URL = _get_config("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
MODEL = _get_config("DEEPSEEK_MODEL", "deepseek-chat")

# 懒加载 OpenAI 客户端，避免在 Streamlit secrets 准备好之前初始化
_client = None

def _get_client() -> OpenAI:
    """懒加载获取 OpenAI 客户端实例"""
    global _client, API_KEY, BASE_URL
    if _client is None:
        # 重新读取配置（Streamlit secrets 可能此时才就绪）
        API_KEY = _get_config("DEEPSEEK_API_KEY")
        BASE_URL = _get_config("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        MODEL = _get_config("DEEPSEEK_MODEL", "deepseek-chat")
        _client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
    return _client


def call_deepseek(
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3,
    temperature: float = 0.3,
    max_tokens: int = 2000,
) -> str:
    """
    调用 DeepSeek API，含重试机制
    
    Args:
        system_prompt: 系统提示词
        user_prompt: 用户提示词
        max_retries: 最大重试次数
        temperature: 温度参数（0-1，越低越稳定）
        max_tokens: 最大输出 token 数
        
    Returns:
        AI 回复的文本内容
    """
    for attempt in range(max_retries):
        try:
            response = _get_client().chat.completions.create(
                model=MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            error_msg = str(e)
            if attempt < max_retries - 1:
                # 指数退避
                wait_time = 2 ** attempt
                print(f"⚠️ API 调用失败（第 {attempt+1} 次），{wait_time}秒后重试... 错误：{error_msg}")
                time.sleep(wait_time)
            else:
                raise Exception(f"API 调用失败（已重试 {max_retries} 次）：{error_msg}")
    
    return ""


def call_deepseek_json(
    system_prompt: str,
    user_prompt: str,
    max_retries: int = 3,
) -> dict:
    """
    调用 DeepSeek API 并返回 JSON 结果
    
    Returns:
        解析后的 JSON 字典
    """
    response_text = call_deepseek(
        system_prompt=system_prompt,
        user_prompt=user_prompt,
        max_retries=max_retries,
        temperature=0.1,  # JSON 输出需要更稳定的温度
        max_tokens=3000,
    )
    
    # 尝试提取 JSON（处理可能的 markdown 代码块）
    text = response_text.strip()
    if text.startswith("```"):
        # 去掉 markdown 代码块
        lines = text.split("\n")
        lines = [l for l in lines if not l.strip().startswith("```")]
        text = "\n".join(lines).strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # 如果解析失败，尝试提取 JSON 子串
        import re
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group())
            except:
                pass
        raise Exception(f"AI 返回结果无法解析为 JSON：\n{response_text}")


def test_connection() -> bool:
    """测试 API 连接是否正常"""
    try:
        response = call_deepseek(
            system_prompt="你是一个有帮助的助手。",
            user_prompt="请回复'连接正常'三个字。",
            max_retries=1,
            max_tokens=50,
        )
        return len(response) > 0
    except Exception as e:
        print(f"连接测试失败：{e}")
        return False
