import streamlit as st
import tools
from stock_research import Anazlyze_stock

st.title("Робот для анализа Акций")
st.write("Этот бот собирает в реальном времени информацию, связанную с акциями, и анализирует ее с помощью языковой модели")

query = st.text_input('Напишите свой вопрос по поводу конкретной компании:')

Enter=st.button("Enter")
clear=st.button("Clear")

if clear:
    print(clear)
    st.markdown(' ')

if Enter:
    import time
    with st.spinner('Собираю информацию на основе финотчетсности, цены за последний год и последних новостей ...'):
        out=Anazlyze_stock(query)
    st.success('Готово!')
    st.write(out)

# to run:
# $: streamlit run app.py

