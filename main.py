import streamlit as st
import os
from PyPDF2 import PdfReader
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from st_copy_to_clipboard import st_copy_to_clipboard

#env에 설정해 놓은 KEY
load_dotenv()

#모델 설정
llm = ChatOpenAI(
    temperature=0.2,
    model_name="gpt-5-mini", 
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

#streamlit: 데이터를 보여주는 것에 초점을 맞춘 데모용 프레임워크(pip install streamlit)
#피그마처럼 빠르게 시각화 해주는데 보기 좋게 해주는 것
#run 코드는 "streamlit run main.py"
st.set_page_config(page_title="Paper-Insight Agent", page_icon="📄", layout="wide")

st.title("📄 Paper-Agent")
st.markdown("### 분석할 논문을 알려주세요")
tab1, tab2 = st.tabs(["논문 제목으로 찾기", "PDF 파일 업로드"])

input_content = ""
source_name = ""

# 사이드바 설정
with st.sidebar:
    st.header("설정")
    level = st.selectbox(
        "용어 해설 수준을 선택하세요",
        ["초등학생 수준", "학부생 수준", "전문가 수준"]
    )
    st.info("수준에 맞게 설명해드립니다.")

with tab1:
    input_title = st.text_input("분석하고 싶은 논문 제목을 입력하세요.", placeholder="예: Attention is All You Need")
    if input_title:
        # 제목만 있을 때는 모델의 지식을 활용하거나 검색 연동(향후 확장)을 전제로 함
        input_content = f"논문 제목: {input_title}"
        source_name = input_title
        
with tab2:
    uploaded_file = st.file_uploader("논문 PDF 파일을 업로드하세요", type=["pdf", "txt"])
    if uploaded_file:
        # 파일 형식 검증 (elif 사용)
        if uploaded_file.name.lower().endswith('.pdf'):
            with st.status("PDF 파싱 중...", expanded=False):
                reader = PdfReader(uploaded_file)
                for page in reader.pages:
                    input_content += page.extract_text()
                source_name = uploaded_file.name
        elif uploaded_file.name.lower().endswith('.txt'):
            input_content = uploaded_file.read().decode("utf-8")
            source_name = uploaded_file.name
        else:
            st.error("지원하지 않는 파일 형식입니다. PDF 또는 TXT 파일만 업로드해주세요.")



    # 분석 버튼
if st.button("논문 심층 분석 시작", type="primary"):
    # 입력 검증
    if not input_content:
        st.warning("논문 제목을 입력하거나 PDF 파일을 업로드해주세요.")
    else:
        with st.spinner("논문의 논리 구조를 파악하고 용어를 정리 중입니다..."):
                
            #프롬프트 설계
            system_template = f"""
            너는 논문을 읽고 핵심을 짚어주는 'AI 연구 파트너'야. 
            사용자가 제공한 논문 텍스트를 바탕으로 다음 구조에 맞춰 리포트를 작성해줘.
            인사말, 맺음말, "추가로 궁금한 게 있으면 물어보라"는 식의 제안은 절대 하지 마.

            [미션]
            1. 제공된 정보가 제목뿐이라면 네가 가진 데이터 중에 해당 제목의 논문을 찾고 총동원해서 요약해줘.
            2. 제공된 정보가 전문 텍스트라면 해당 텍스트를 정밀 분석해줘.
            3. 모든 내용은 '{level}'에 맞춰서 설명해줘.(비유는 하되 실제 개념을 헷갈리게 하는 비유는 제외.)
            4. 어려운 내용은 기존에 있었던 연구와 함께 설명해줘.(ex. Attention is all you need같은 경우는 attention 메커니즘을 이해하지 못하면 안되니, 그 부분 먼저 설명하고 자연스럽게 연결)

            
            [출력형식]
            ## 논문 요약
            ### 사전 지식 및 전문 용어 사전(본문에 등장하는 핵심 용어 중 생소한 단어 5개를 선정), 한 줄 요약, 연구 목적, 주요 방법론, 핵심 실험 결과를 정리.
            -기존 연구에 어떤 문제점이 있었는지와 방법론은 조금 더 자세하게 설명.
            -본문의 핵심수식이나 알고리즘은 방법론에 포함하여 더 자세하고 쉽게 설명.(설명할 때는 반드시 LaTeX 기호(반드시 $$ 또는 $)를 사용하여 가독성을 높여줘)
            
            ## 비판적 시각 및 향후 연구
            ### 이 논문의 한계점이나 제안할 수 있는 후속 연구 방향 제시.
            -논문 주제 방향, 서비스, 프로젝트 위주로 같이 설명해줘.


            모든 답변은 한국어로 작성하고 [미션]은 전부 지키면서 [출력형식]은 마크다운 형식을 지켜줘.
            """

            prompt = ChatPromptTemplate.from_messages([
                ("system", system_template),
                ("user", "입력 데이터: {content}")
            ])

            # 체인 실행
            chain = prompt | llm | StrOutputParser()
            
            analysis_result = chain.invoke({"content": input_content[:20000]})

            # 결과 시각화
            st.divider()
            st.success(f"'{source_name}' 분석 리포트 생성이 완료되었습니다.")
            st.markdown(analysis_result)

            # 결과 다운로드
            st.download_button(
                label="분석 리포트 다운로드 (.md)",
                data=analysis_result,
                file_name=f"Insight_{source_name}.md",
                mime="text/markdown"
            )
            st_copy_to_clipboard(analysis_result, before_text="리포트 전체 복사", after_text="복사 완료")
else:
    st.info("분석을 시작하려면 논문 제목을 입력하거나 PDF 파일을 드래그 앤 드롭 하세요.")
    
