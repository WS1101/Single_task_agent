import streamlit as st
import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

# Streamlit UI 설정
st.set_page_config(page_title="NetShield Agent", page_icon="🛡️")
st.title("🛡️ NetShield: 네트워크 보안 분석 에이전트")
st.info("로그를 입력하면 Llama-3.1이 즉시 분석하여 대응 방안을 제시합니다.")

# 모델 초기화
llm = ChatGroq(
    temperature=0,
    model_name="llama-3.1-8b-instant",
    groq_api_key=os.getenv("GROQ_API_KEY")
)

# 분석 로직
user_input = st.text_area("네트워크 로그 또는 상황을 입력하세요:", placeholder="예: Multiple failed SSH login attempts...")

if st.button("분석 시작"):
    if user_input:
        with st.spinner("Grok(LPU)이 분석 중입니다..."):
            prompt = ChatPromptTemplate.from_messages([
                ("system", "너는 네트워크 보안 전문가야. 상황분석, 위험등급, 권장조치를 한국어로 정리해줘."),
                ("user", "{input}")
            ])
            chain = prompt | llm
            response = chain.invoke({"input": user_input})
            st.markdown("### 🔍 분석 결과")
            st.write(response.content)
    else:
        st.warning("분석할 내용을 입력해주세요.")
