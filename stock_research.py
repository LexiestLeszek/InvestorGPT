PERPLEXITY_API = ""

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

llm_api = PERPLEXITY_API

def llm_inference(system_prompt, user_prompt):
    pplx_key = llm_api
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-medium-chat",
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
    
    print(answer)
    
    return answer

def get_losers():
    url = "https://finance.yahoo.com/losers"
    soup = BeautifulSoup(requests.get(url).text, 'html.parser')
    assets = soup.find_all('a', attrs={"class":"Fw(600)"})
    return assets

def get_recommendation(company_name,book_value,market_value,probability_to_fix_problem_number):
    float_number = float(probability_to_fix_problem_number)
    # Convert to percentage
    prob_float = float_number /  100
    formula = (book_value-market_value) * prob_float
    if formula > 0:
        result = formula / book_value
        result_string = f"Buy {company_name}, its premium / book value is {result}"
        return True, result_string
    else:
        result = formula / book_value
        result_string = f"DO NOT BUY {company_name}, its premium / book value is {result}"
        return False, result_string

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

def why_price_dropped(company_name):
    user_prompt = f"Why did {company_name} stock price dropped?"
    
    pplx_key = llm_api
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-medium-online",
        "temperature": 0,
        "messages": [
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
    
    print(answer)
    
    return answer

def get_3financial_statements(ticker):
    # To avoid rate limit error
    time.sleep(4)
    
    # Ensure ticker is in the correct format
    if "." in ticker:
        ticker = ticker.split(".")[0]
    
    # Fetch the company information using the ticker symbol
    company = yf.Ticker(ticker)
    
    # Fetch and process the balance sheet
    balance_sheet = company.balance_sheet
    if balance_sheet.shape[1] >=  3:
        balance_sheet = balance_sheet.iloc[:, :3]  # Keep only the first three years of data
    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet_str = balance_sheet.to_string()
    
    # Fetch and process the income statement
    income_statement = company.financials
    if income_statement.shape[1] >=  3:
        income_statement = income_statement.iloc[:, :3]  # Keep only the first three years of data
    income_statement = income_statement.dropna(how="any")
    income_statement_str = income_statement.to_string()
    
    # Fetch and process the cash flow statement
    cash_flow_statement = company.cashflow
    if cash_flow_statement.shape[1] >=  3:
        cash_flow_statement = cash_flow_statement.iloc[:, :3]  # Keep only the first three years of data
    cash_flow_statement = cash_flow_statement.dropna(how="any")
    cash_flow_statement_str = cash_flow_statement.to_string()
    
    three_statements = f"""
        Balance Sheet:\n{balance_sheet_str}\n
        Income Statement:\n{income_statement_str}\n
        Cash Flow Statement:\n{cash_flow_statement_str}\n
        """
    return three_statements

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

def Anazlyze_stock(query,percentage_drop):
    #agent.run(query) Outputs Company name, Ticker
    company_name = get_company_name(query)
    ticker=get_stock_ticker(company_name)
    print({"Query":query,"Company_name":company_name,"Ticker":ticker})
    stock_price=get_stock_price(ticker,history=20)
    stock_financials=get_financial_statements(ticker)
    bad_news=why_price_dropped(company_name)
    print(stock_price)

    available_information=f"""
            {company_name} Stock Price for the past 20 days: {stock_price}\n\n
            {company_name} Financials: {stock_financials}\n\n
            {company_name} stock price fell by {percentage_drop} due to {bad_news}."""
    
    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer. Each answer should give an opinion about three things:  company's financial statements, companies stock price dynamic over the period that was analyzed, latest news about the company."
    
    user_prompt = f"""You are a stock investment analysis expert. 
            {company_name} stock has dropped by {percentage_drop} and you need to estimate the probability of the company being able to fix its problems.
            Use and analyze this information about {company_name}:
            {available_information}\n\n
            Your answer must be only a number of percents and nothing more.
            Examples: 34, 55, 74.
            Question: What is the probability of the company to fix the reasons that dropped the price and recover its stock price?
            Answer:
            """
    
    book_value = "1000"
    market_value = "1300"
    
    probability_to_fix = llm_inference(system_prompt, user_prompt)
    
    float_number = float(probability_to_fix)
    # Convert to percentage
    prob_float = float_number /  100
    formula = (book_value-market_value) * prob_float
    if formula > 0:
        result = formula / book_value
        result_string = f"Buy {company_name}, its premium / book value is {result}"
        print(result)
        print(result_string)
        return True
    else:
        result = formula / book_value
        result_string = f"DO NOT BUY {company_name}, its premium / book value is {result}"
        print(result)
        print(result_string)
        return False

losers = get_losers()
print(losers)
