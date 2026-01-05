import streamlit as st
import json
from openai import OpenAI

st.set_page_config(page_title="Chat Wizard 高情商聊天助手", page_icon="🧙", layout="wide", initial_sidebar_state="collapsed")

def has_secrets():
    try:
        return "openai" in st.secrets and "api_key" in st.secrets["openai"] and st.secrets["openai"]["api_key"]
    except Exception:
        return False

def build_prompts(user_text: str, scene: str):
    system_prompt = (
        "你是拥有10年经验的社交沟通专家。你的目标是为用户生成3种不同风格的中文回复。"
        "绝对原则：回复不能只是句号，必须包含钩子或反问，确保话题自然延续，不冷场。"
        "输出严格为JSON，键humor、empathy、curiosity。每条不超过80字，简洁犀利。"
    )
    style_hint = {
        "暧昧/相亲对象": "语气轻松暧昧，适度俏皮，保持分寸。",
        "普通朋友": "自然随和，真诚互动。",
        "领导/同事": "专业礼貌，简洁稳重。",
        "刚认识的陌生人": "友好克制，避免冒犯，逐步深入。"
    }.get(scene, "自然随和，真诚互动。")
    user_prompt = (
        f"场景：{scene}；风格偏好：{style_hint}。对方消息如下：\n"
        f"{user_text}\n"
        "请生成：\n"
        "1) 幽默风趣型：调侃、轻松、带梗；\n"
        "2) 情绪价值型：理解、共情、温柔；\n"
        "3) 好奇反问型：顺着话题挖掘新的点，引导对方多说话；\n"
        "以如下JSON返回：{\"humor\":\"...\",\"empathy\":\"...\",\"curiosity\":\"...\"}"
    )
    return system_prompt, user_prompt

def call_llm(user_text: str, scene: str):
    client = OpenAI(api_key=st.secrets["openai"]["api_key"], base_url=st.secrets["openai"].get("base_url", "https://api.openai.com/v1"))
    model_name = st.secrets["openai"].get("model", "gpt-3.5-turbo")
    system_prompt, user_prompt = build_prompts(user_text, scene)
    resp = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
        temperature=0.7
    )
    content = resp.choices[0].message.content
    try:
        data = json.loads(content)
        humor = str(data.get("humor", "")).strip()
        empathy = str(data.get("empathy", "")).strip()
        curiosity = str(data.get("curiosity", "")).strip()
    except Exception:
        humor = content.strip()
        empathy = content.strip()
        curiosity = content.strip()
    return humor, empathy, curiosity

def main():
    st.title("🧙 Chat Wizard 高情商聊天助手")
    st.caption("把对方的话贴进来，我来给你3种风格的神回复。")

    if not has_secrets():
        with st.sidebar:
            st.error("未检测到 API 密钥。请在云端或本地的 .streamlit/secrets.toml 中配置：")
            st.code('[openai]\napi_key = "sk-..."\nbase_url = "https://api.deepseek.com"\nmodel = "deepseek-chat"')

    scene = st.radio("现在你的聊天对象是谁？", ["暧昧/相亲对象", "普通朋友", "领导/同事", "刚认识的陌生人"], horizontal=True)
    user_text = st.text_area("对方说了什么？", height=200, placeholder="把对方的话粘贴到这里（支持多行）")

    gen = st.button("✨ 帮我生成神回复", type="primary")

    if gen:
        if not user_text.strip():
            st.warning("请输入对方的消息内容。")
            return
        if not has_secrets():
            st.error("未配置 API 密钥，无法生成。请先在 secrets 中添加 openai 配置。")
            return
        with st.spinner("AI 正在思考中，请稍候..."):
            try:
                humor, empathy, curiosity = call_llm(user_text.strip(), scene)
            except Exception as e:
                st.error(f"生成失败：{e}")
                return

        st.success(f"幽默风趣型：{humor}")
        st.code(humor)
        st.info(f"情绪价值型：{empathy}")
        st.code(empathy)
        st.warning(f"好奇反问型：{curiosity}")
        st.code(curiosity)

if __name__ == "__main__":
    main()

