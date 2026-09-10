import streamlit as st

overview = st.Page("overview.py", title="Overview")
q1 = st.Page("research_questions/question_1.py", title="Heatwave effect on solar and hydro generation in Spain")
q2 = st.Page("research_questions/question_2.py", title="Research Question 2")
q3 = st.Page("research_questions/question_3.py", title="Research Question 3")
q4 = st.Page("research_questions/question_4.py", title="Research Question 4")
q5 = st.Page("research_questions/question_5.py", title="Research Question 5")
q6 = st.Page("research_questions/question_6.py", title="Research Question 6")

q3_1 = st.Page("research_questions/question_3_1.py", title="└ Interactive Visualizations")
q3_2 = st.Page("research_questions/question_3_2.py", title="└ Analysis of Four Correlations")


pages = [overview, q1, q2, q3, q3_1, q3_2, q4, q5, q6]
pg = st.navigation(pages, position="hidden")

with st.sidebar:
    st.page_link(overview)
    st.page_link(q1)
    st.page_link(q2)
    st.page_link(q3)
    sub_menu = st.empty()
    st.page_link(q4)
    st.page_link(q5)
    st.page_link(q6)

if pg in [q3, q3_1, q3_2]:
    with sub_menu.container():
        st.page_link(q3_1)
        st.page_link(q3_2)

pg.run()
