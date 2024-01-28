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
import argostranslate.package
import argostranslate.translate
import os
warnings.filterwarnings("ignore")

llm_api = ""

def llm_inference(system_prompt, user_prompt):
    pplx_key = llm_api
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "pplx-7b-chat",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
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
    answer = parsed_json["choices"][0]["message"]["content"]
    
    #company_name = translate_text(company_name,"ru","en")
    
    print(answer)
    
    return answer

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
        text = ' '.join([p.get_text() for p in soup.find_all('p','<h1>', '<h2>','<span>')])
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
    
    system_prompt = "Given the user request, answer what is the company name in English in user's prompt. Answer only with the company name in English and nothing else, not even a period or comma."

    company_name = llm_inference(system_prompt, query)
    
    print(company_name)
    
    return company_name

def get_stock_ticker(company_name):
    yfinance = "https://query2.finance.yahoo.com/v1/finance/search"
    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'
    params = {"q": company_name, "quotes_count": 1, "country": "United States"}

    res = requests.get(url=yfinance, params=params, headers={'User-Agent': user_agent})
    data = res.json()

    company_ticker = data['quotes'][0]['symbol']
    return company_ticker

def Anazlyze_stock(query):
    #agent.run(query) Outputs Company name, Ticker
    company_name = get_company_name(query)
    ticker=get_stock_ticker(company_name)
    print({"Query":query,"Company_name":company_name,"Ticker":ticker})
    stock_data=get_stock_price(ticker,history=10)
    stock_financials=get_financial_statements(ticker)
    stock_news=get_recent_stock_news(company_name)

    available_information=f"Stock Price: {stock_data}\n\nStock Financials: {stock_financials}\n\nStock News: {stock_news}"
    #available_information=f"Stock Financials: {stock_financials}\n\nStock News: {stock_news}"

    # print("\n\nAnalyzing.....\n")
    
    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
             The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer. Each answer should give an opinion about three things:  company's financial statements, companies stock price dynamic over the period that was analyzed, latest news about the company."
    
    user_prompt = f"Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
            User question: {query} \
            You have the following information available about {company_name}. Write 5-8 bulle tpoints about investment analysis to answer user query, At the end conclude with proper explaination and a certain decision (buy or don't buy) about this company's stock.  : \
            {available_information}. \
            A good rule of thumb that you should use is 'buy rumors and sell news', use that rule when analyzing the stock."
    
    
    answer = llm_inference(system_prompt, user_prompt)
    
    from_code = "en"
    to_code = "ru"
    
    # Download and install Argos Translate package
    argostranslate.package.update_package_index()
    available_packages = argostranslate.package.get_available_packages()
    package_to_install = next(
        filter(
            lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
        )
    )
    argostranslate.package.install_from_path(package_to_install.download())
    
    answer = argostranslate.translate.translate(answer, from_code, to_code)
    
    print(answer)

    return answer
