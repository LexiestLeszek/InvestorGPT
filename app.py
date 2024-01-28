import streamlit as st
import tools
from stock_research import Anazlyze_stock

st.title("Investment Analysis Chatbot")
st.write("This bot analyses investment opportunities based on the available info from the internet and the power of LLM model")

query = st.text_input('Input your investment question about a company or sector:') 

Enter=st.button("Enter")
clear=st.button("Clear")

if clear:
    print(clear)
    st.markdown(' ')

if Enter:
    import time
    with st.spinner('Analyzing stock prices, financial reports and news'):
        out=Anazlyze_stock(query)
    st.success('Done!')
    st.write(out)

# to run: streamlit run app.py