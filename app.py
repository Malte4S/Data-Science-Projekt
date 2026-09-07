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
    title="Research Question 3 - Introduction",
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
# Subpages for RQ 3
q3_1 = st.Page("research_questions/question_3_1.py", title="└ Interactive Visualizations")
q3_2 = st.Page("research_questions/question_3_2.py", title="└ Analysis of four Correlations")

pg = st.navigation([overview,q1,q2,q3,q3_1,q3_2,q4,q5,q6])

if pg in [q3, q3_1, q3_2]:
    pg = st.navigation([overview,q1,q2,q3,q3_1,q3_2,q4,q5,q6])
else:
    pg = st.navigation([overview,q1,q2,q3,q4,q5,q6])

pg.run()
