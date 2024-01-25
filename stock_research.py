import json
import time
from bs4 import BeautifulSoup
import re
import requests
from googlesearch import search
import translators as ts
import json

import yfinance as yf

import warnings
import os
warnings.filterwarnings("ignore")

llm_api = ""

# Fetch stock data from Yahoo Finance
def get_stock_price(ticker,history=5):
    #time.sleep(4) #To avoid rate limit error
    if "." in ticker:
        ticker=ticker.split(".")[0]
    ticker=ticker
    stock = yf.Ticker(ticker)
    df = stock.history(period="1y")
    df=df[["Close","Volume"]]
    df.index=[str(x).split()[0] for x in list(df.index)]
    df.index.rename("Date",inplace=True)
    df=df[-history:]
    # print(df.columns)
    
    return df.to_string()

def get_search_results(company_name):
    query = f"{company_name} news"
    search_results = search(query, num=3, stop=3, pause=2)
    top_links = list(search_results)
    return top_links

def scrape_webpage(url):
    try:
        page = requests.get(url)
        soup = BeautifulSoup(page.content, 'html.parser')
        text = ' '.join([p.get_text() for p in soup.find_all('p')])
        return text
    except Exception as e:
        print(f"Failed to scrape {url}: {e}")
        return None

def get_recent_stock_news(company_name):
    top_links = get_search_results(company_name)
    news=[]
    for link in top_links:
        text = scrape_webpage(link)
        if text:
            news.append(text)
    
    news_string = '\n'.join(news)

    top3_news="Recent News:\n\n"+news_string
    
    print(top3_news)
    
    return top3_news

# Fetch financial statements from Yahoo Finance
def get_financial_statements(ticker):
    # time.sleep(4) #To avoid rate limit error
    if "." in ticker:
        ticker=ticker.split(".")[0]
    else:
        ticker=ticker
    ticker=ticker
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1]>=3:
        balance_sheet=balance_sheet.iloc[:,:3]    # Remove 4th years data
    balance_sheet=balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.to_string()
    return balance_sheet

def get_company_name(query):
    
    pplx_key = llm_api
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "pplx-7b-chat",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": f"Given the user request, what is the company name in English? Answer only with the company name in English and nothing else: {query}?"
            },
            {
                "role": "user",
                "content": query
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + pplx_key
    }
    response = requests.post(url, json=payload, headers=headers)
    
    json_data = response.text
    
    # Parse the JSON data
    parsed_json = json.loads(json_data)

    # Access and print the "content"
    company_name = parsed_json["choices"][0]["message"]["content"]
    
    #company_name = translate_text(company_name,"ru","en")
    
    print(company_name)
    
    return company_name

def get_stock_ticker(company_name):
    yfinance = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    company_code = data['quotes'][0]['symbol']
    return company_code

def Anazlyze_stock(query):
    #agent.run(query) Outputs Company name, Ticker
    company_name = get_company_name(query)
    ticker=get_stock_ticker(query)
    print({"Query":query,"Company_name":company_name,"Ticker":ticker})
    stock_data=get_stock_price(ticker,history=10)
    stock_financials=get_financial_statements(ticker)
    stock_news=get_recent_stock_news(company_name)

    available_information=f"Stock Price: {stock_data}\n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    #available_information=f"Stock Financials: {stock_financials}\n\nStock News: {stock_news}"

    # print("\n\nAnalyzing.....\n")
    
    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
             The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer"
    
    prompt = f"Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
            User question: {query} \
            You have the following information available about {company_name}. Write 5-8 bulle tpoints about investment analysis to answer user query, At the end conclude with proper explaination and a certain decision (buy or don't buy) about this company's stock.  : \
            {available_information}. \
            A good rule of thumb that you should use is 'buy rumors and sell news', use that rule when analyzing the stock."
    
    pplx_key = llm_api
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "mixtral-8x7b-instruct",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + pplx_key
    }
    response = requests.post(url, json=payload, headers=headers)
    
    json_data = response.text
    
    # Parse the JSON data
    parsed_json = json.loads(json_data)

    # Access and print the "content"
    answer_analysis = parsed_json["choices"][0]["message"]["content"]
    
    print(answer_analysis)

    return answer_analysis
