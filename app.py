import streamlit as st
from agent import LectureAgent 

Agent = LectureAgent()

st.title("Cinema 4D 콘텐츠 전문가 과정")
st.write("원하는 강의를 선택하고, 퀴즈 풀러가기, 강의 요약 보러가기, 또는 질문하기를 선택하세요.")

st.session_state.lecture_selected = False

selected_lecture = st.selectbox("강의를 선택하세요", options=[False, "1강", "2강", "Redshit_forCinema4d2024"], format_func=lambda x: "강의를 선택하세요" if x is False else x)

if selected_lecture:
    st.session_state.lecture_selected = selected_lecture

if st.session_state.lecture_selected:
    st.write("원하는 작업을 선택하세요:")
    action = st.selectbox("작업 선택", ["퀴즈 풀러가기", "강의 요약 보러가기", "질문하기"])

    if action == "퀴즈 풀러가기":
        st.write("### 퀴즈")
        quiz_output = Agent.get_quiz(st.session_state.lecture_selected)
        st.write(quiz_output)

    elif action == "강의 요약 보러가기":
        st.write("### 강의 요약")
        summary_output = Agent.get_summary(st.session_state.lecture_selected)
        st.write(summary_output)

    elif action == "질문하기":
        st.write("### 질문하기")
        question = st.text_input("궁금한 내용을 입력하세요:")
        if question:
            try:
                filter_output = Agent.query_filter(st.session_state.lecture_selected, question)
                if filter_output.result:
                    chat_output = Agent.get_chat(st.session_state.lecture_selected, question)
                    st.write(chat_output)
                else:
                    st.write("현재 문의해 주신 내용이 학습 데이터에서 찾을 수 없습니다. \n\n 답변을 더 자세하게 내용을 적어주시면 감사하겠습니다.")
            except:
                st.write("현재 문의해 주신 내용이 학습 데이터에서 찾을 수 없습니다. \n\n 답변을 더 자세하게 내용을 적어주시면 감사하겠습니다.")
