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


def get_10k(ticker):
    
    curr_year = datetime.datetime.now().year
    
    filings_lists_text = []
    
    set_identity("Michael Mccallum mike.mccalum@indigo.com")
    
    filings = Company(ticker).get_filings(year=range(curr_year-2, curr_year-1))
    
    filings.filter(form=["10-K"])
    
    for i in filings:
        filing = filings[i].text()
        filings_lists_text.append(filing)
        
    filings_string = '.\n'.join(filings_lists_text)
    
    return filings_string

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
    stock_news=get_recent_stock_news(company_name)

    
    available_information=f"""
    Current Stock Price: {stock_data}\n\n
    Financial Reports: {financial_statements_str}\n\n
    Stock News: {stock_news}
    """
    
    '''
    
    available_information=f"""
    Stock Current Price: {stock_data}\n\n
    Stock 10-k filling for the past 4 years: {tenk}\n\n
    Stock News: {stock_news}
    """
    '''
    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer. Each answer should give an opinion about three things:  company's financial statements, companies stock price dynamic over the period that was analyzed, latest news about the company."
    
    user_prompt = f"""Give detailed stock analysis and use the available data to provide concrete investment recommendation in the binary form - invest or not to invest. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer \
            You have the following information available about {company_name}. Write 5-8 bullet points about investment analysis to answer user query, each bullet point should be whether a positive or negative factor for potential investment. At the end conclude with proper explaination and a certain decision (invest or don't invest) about this company's stock. \
            Available information about the company:
            {available_information}. \
            During your analysis, a good rule of thumb that you should use when assessing the company is 'buy rumors and sell news', use that rule when analyzing the stock. 
            User question: {query} \
            """
    
    
    answer = llm_inference(system_prompt, user_prompt)
    
    return answer
