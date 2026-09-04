import streamlit as st

overview = st.Page(
    "overview.py",
    title="Overview",
)

q1 = st.Page(
    "research_questions/question_1.py",
    title="Research Question 1",
)

q2 = st.Page(
    "research_questions/question_2.py",
    title="Research Question 2",
)

q3 = st.Page(
    "research_questions/question_3.py",
    title="Research Question 3",
)

q4 = st.Page(
    "research_questions/question_4.py",
    title="Research Question 4",
)

q5 = st.Page(
    "research_questions/question_5.py",
    title="Research Question 5",
)

q6 = st.Page(
    "research_questions/question_6.py",
    title="Research Question 6",
)

pg = st.navigation([
    overview,
    q1,
    q2,
    q3,
    q4,
    q5,
    q6
])

pg.run()