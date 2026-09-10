import streamlit as st

home = st.Page("other_pages/home.py", title="Home")
q1 = st.Page("research_questions/question_1.py", title="1. Heatwave effect on solar & hydro generation")
q2 = st.Page("research_questions/question_4.py", title="2. Drought and Hydro Energy Production")
q3 = st.Page("research_questions/question_5.py", title="3. Wind Resource & Performance Analysis")
q4 = st.Page("research_questions/question_2.py", title="4. Power Generation & Power Trade Share Volatility")
q5 = st.Page("research_questions/question_6.py", title="5. Bidding Zone Price Volatility")
q6 = st.Page("research_questions/question_3.py", title="6. Northern vs. Southern Europe")
imprint = st.Page("other_pages/imprint.py", title="Imprint")

q6_1 = st.Page("research_questions/question_3_1.py", title="└ Interactive Visualizations")
q6_2 = st.Page("research_questions/question_3_2.py", title="└ Analysis of Four Correlations")


pages = [home, q1, q2, q3, q4, q5, q6, q6_1, q6_2, imprint]
pg = st.navigation(pages, position="hidden")

with st.sidebar:
    st.page_link(home)
    st.page_link(q1)
    st.page_link(q2)
    st.page_link(q3)
    st.page_link(q4)
    st.page_link(q5)
    st.page_link(q6)
    sub_menu = st.empty()
    st.page_link(imprint)

if pg in [q6, q6_1, q6_2]:
    with sub_menu.container():
        st.page_link(q6_1)
        st.page_link(q6_2)

pg.run()
