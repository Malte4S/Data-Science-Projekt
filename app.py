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


pg = st.navigation([
    overview,
    q1,
    q2
])

pg.run()