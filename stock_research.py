PERPLEXITY_API = ""


import json
from bs4 import BeautifulSoup
import requests
from googlesearch import search
import time
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")
from edgar import *
import datetime
import pandas as pd
import re

def get_recommendation(company_name,book_value,market_value,probability_to_fix_problem_number):
    float_number = float(probability_to_fix_problem_number)
    # Convert to percentage
    prob_float = float_number /  100
    formula = (book_value-market_value) * prob_float
    if formula > 0:
        answ_string = f"You should invest in {company_name}, the company's current value is {formula} whil book value is {book_value}."
        return answ_string
    else:
        answ_string = f"DO NOT invest in {company_name}, the company's current value is {formula} whil book value is {book_value}."
        return False

def get_number(input_string):
    # Find all sequences of digits in the string
    numbers = re.findall(r'\d+', input_string)
    # If there are no numbers, return None
    if not numbers:
        return None
    # Otherwise, return the first number found
    return numbers[0]


def monitor_stock_drop(tickers, lookback_period='1d'):
    """
    Monitors the stock prices of the given tickers and prints a message if any stock drops more than  12% in a day.
    
    Parameters:
    - tickers (list): A list of ticker symbols for the companies to monitor.
    - lookback_period (str): The period to look back for price comparison (default is '1d' for  1 day).
    """
    # Fetch stock data for each ticker
    for ticker in tickers:
        try:
            stock_data = yf.download(ticker, period=lookback_period, interval='1d')
            if not stock_data.empty:
                # Calculate the percentage change in closing price from the previous day
                percentage_change = (stock_data['Close'][0] - stock_data['Close'][1]) / stock_data['Close'][1] *  100
                
                # Check if the percentage change is more than  12%
                if percentage_change >  30:
                    print(f"{ticker} stock has fallen more than  12% in a day.")
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")

# Example usage
top_1000_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "TSLA", "BRK.B", "JNJ", "V", "JPM"]  # Add all  1000 ticker symbols here
monitor_stock_drop(top_1000_tickers)


def llm_inference(system_prompt, user_prompt):
    pplx_key = PERPLEXITY_API
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
    
    try:
        search_results = search(query, num=3, stop=3, pause=2)
        top_links = list(search_results)
        print(f"Search Urls: {top_links}")
        return top_links
    
    except Exception as e:
        print(f"Googlesearch error: {e}")
        url = "https://www.google.com/search?q=" + query
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        search_results = soup.find_all('div', class_='g')
        top_links = []
        for result in search_results[:3]:
            link = result.find('a')
            top_links.append(link['href'])
        print(f"Search Urls: {top_links}")
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

    top3_news=f"Recent News about {company_name}:\n"+news_string
    
    print(top3_news)
    
    return top3_news

# Fetch financial statements from Yahoo Finance

def get_financial_statements(ticker):
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
    
    # Return all three financial statements as strings
    return balance_sheet_str, income_statement_str, cash_flow_statement_str

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
    balance_sheet_str, income_statement_str, cash_flow_statement_str = get_financial_statements(ticker)
    financial_statements_str = f"""
                Stock Balance Sheet: {balance_sheet_str}\n
                Stock Income Statement:{income_statement_str}\n
                Stock Cashflow Statement{cash_flow_statement_str}\n
                """
    book_value = ""
    market_value = ""
    stock_news=get_recent_stock_news(company_name)
    
    stock_drop_percentage = ""
    
    available_information=f"""
    Financial Reports: {financial_statements_str}\n\n
    Recent Stock News: {stock_news}\n\n
    Stock Price history: {stock_data}\n\n
    Company's Stock Price dropped by {stock_drop_percentage} today.
    """

    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer. Each answer should give an opinion about three things:  company's financial statements, companies stock price dynamic over the period that was analyzed, latest news about the company."
    
    user_prompt = f"""You are a risk manager and professional risk analyst. \
            You have the following available information about {company_name}: \n{available_information}.\n
            Question: Based on available information about {company_name}, what was the main reason the stock fell by {stock_drop_percentage} today? \
            Answer:
            """
    
    why_price_dropped = llm_inference(system_prompt, user_prompt)
    
    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer. Each answer should give an opinion about three things:  company's financial statements, companies stock price dynamic over the period that was analyzed, latest news about the company."
    
    user_prompt = f"""You are a risk manager and professional risk analyst. \
            You need to answer the probability question about the company's chances to fix their problem.
            Give the answer strictly as the probabiliy to fix the problem in percentage. Examples: 12 percent, 47 percent, 88 percent.
            You have the following available information about {company_name}: \n{available_information}.\n
            Based on available information about {company_name}, we know the stock price dropped because {why_price_dropped}. \
            Question: what is the percentage chace that the {company_name} will be able to fix the problem in the next year?
            Answer in percentage:
            """
    
    probability_to_fix_problem = llm_inference(system_prompt, user_prompt)
    
    probability_to_fix_problem_number = get_number(probability_to_fix_problem)
    
    recommendation = get_recommendation(company_name,book_value,market_value,probability_to_fix_problem_number)
    
    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer. Each answer should give an opinion about three things:  company's financial statements, companies stock price dynamic over the period that was analyzed, latest news about the company."
    
    user_prompt = f"""Give detailed stock analysis and use the available data to provide concrete investment recommendation in the binary form - invest or not to invest. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
            You have the following information available about {company_name}: {available_information}. \n
            Based on available information about {company_name}, we know the stock price dropped because {why_price_dropped}. \
            Write 5-8 bullet points about investment analysis to answer user query, each bullet point should be whether a positive or negative factor for potential investment. 
            At the end conclude with proper explaination and a certain decision (invest or don't invest) about this company's stock. \
            Also answer how would recent Stock News affect the company and its perspectives. Try to asses how likely is it for the company to fix the problem.
            During your analysis, a good rule of thumb that you should use when assessing the company is 'buy rumors and sell news', use that rule when analyzing the stock. 
            """
    
    answer_analysis = llm_inference(system_prompt, user_prompt)
    
    return recommendation, answer_analysis
