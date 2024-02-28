PERPLEXITY_API = ""

import json
import time
from bs4 import BeautifulSoup
import re
import requests
import json
import yfinance as yf
import warnings
warnings.filterwarnings("ignore")

def api_return(company_name,book_value,market_value,net_value,prob_int,roi,available_information,recommendation):
    
    data = {
    "company_name": company_name,
    "book_value": book_value,
    "market_value": market_value,
    "net_value": net_value,
    "prob_to_fix": prob_int,
    "roi": roi,
    "available_info": available_information,
    "buy_or_not": recommendation
}

    json_data = json.dumps(data)

    return json_data

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

def get_losers():
    # Step 1: Fetch the HTML content
    url = "https://finance.yahoo.com/losers"
    response = requests.get(url)

    # Step 2: Parse the HTML content
    soup = BeautifulSoup(response.text, 'html.parser')

    # Step 3: Extract the table containing the stock information
    # Assuming the table has a specific class or id, adjust the selector accordingly
    table = soup.find('table', {'class': 'W(100%)'})

    # Step 4: Extract tickers and percentage drop
    data = []
    for row in table.find_all('tr')[1:]: # Skip the header row
        cells = row.find_all('td')
        ticker = cells[0].text.strip()
        percentage_drop = cells[4].text.strip()
        percentage_drop = float(percentage_drop.replace("-", "").replace("%", ""))
        data.append((ticker, percentage_drop))
        
    return data

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

def why_price_dropped(company_name,percentage_drop):
    
    from datetime import datetime

    current_month = datetime.now().month
    current_year = datetime.now().year
    
    user_prompt = f"Why did {company_name} stock price dropped by {percentage_drop} in {current_month} {current_year}?"
    
    pplx_key = PERPLEXITY_API
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-medium-online",
        "temperature": 0,
        "messages": [
            {
            "role": "system",
            "content": "Be precise and concise."
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
    
    print(f"Price of {company_name} dropped because: \n{answer}")
    
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

def get_company_name(ticker):

    user_prompt = f"""
        What is the company name that has {ticker} stock ticker? Answer only with the company name and nothing else."""
    
    pplx_key = PERPLEXITY_API
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
    company_name = parsed_json["choices"][0]["message"]["content"]
    
    print(company_name)
    
    return company_name

def Anazlyze_stock(ticker,percentage_drop):
    company_name = get_company_name(ticker)
    stock_price=get_stock_price(ticker,history=20)
    stock_financials=get_3financial_statements(ticker)
    bad_news=why_price_dropped(company_name,percentage_drop)

    available_information=f"""
            {company_name} Stock Price dynamic for the past 30 days: {stock_price}\n\n
            {company_name} Financials: {stock_financials}\n\n
            {company_name} stock price fell by {percentage_drop} due to {bad_news}.
            """
    
    print(available_information)
    
    system_prompt = f"You are an investment advisory bot that gives detailed ansers about user's question. \
            Give detailed stock analysis and use the available data and provide investment recommendation. \
            The user is fully aware about the investment risk, dont include any kind of warning like 'It is recommended to conduct further research and analysis or consult with a financial advisor before making an investment decision' in the answer. Each answer should give an opinion about three things:  company's financial statements, companies stock price dynamic over the period that was analyzed, latest news about the company."
    
    user_prompt = f"""You are a stock investment analysis expert. 
            {company_name} stock has dropped by {percentage_drop} and you need to estimate the probability of the company being able to fix its problems.
            Use and analyze this information about {company_name}:
            {available_information}\n\n
            Give your precise percentage estimation of how likely will the company successfully fix its problems to return stock price back to all time high.
            Your answer must be only a number of percents and nothing more.
            Examples of acceptable answers: 34%, 55%, 74%.
            Question: What is the probability of the company to fix the reasons that dropped the price and recover its stock price?
            Answer in percentage:
            """
    
    print("##########################################\n")
    
    book_value = 2500 # TODO: add logic (yfinance)
    market_value = 1805 # TODO: add logic (yfinance)
    
    probability_to_fix = llm_inference(system_prompt, user_prompt)
    
    match = re.search(r'(\d+)%', probability_to_fix)
    if match:
        prob_int = int(match.group(1)) 
    
    prob_int = prob_int / 100
    
    print(f"Book Value: {book_value}")
    print(f"Market Cap: {market_value}")
    
    # basically ( book_value - market_value ) * probability to fix

    net_value = book_value - market_value
    print("Net Value: ", net_value)
    print("Probability to fix: ",prob_int)
    
    formula = net_value * prob_int
    formula = round(formula,2)
    
    print("Net Value * Probability to fix the problems: ",formula)
    
    roi = formula/market_value
    roi_round = round(roi,4)
    roi_percentage = roi_round * 100
    roi_percentage_round = round(roi_percentage,1)
    print(f"ROI (NetValue*ProbFix / MarketValue): {roi_percentage_round}%")
    
    if formula > 0:
        print("**Buy ",company_name)
        rec = True
        #result = api_return(company_name,book_value,market_value,net_value,prob_int,roi,available_information,rec)
        #return result
        return True
    else:
        print("**DO NOT BUY ",company_name)
        rec = False
        #result = api_return(company_name,book_value,market_value,net_value,prob_int,roi,available_information,rec)
        #return result
        return False


def main():
    while True:
        losers_data = get_losers()

        # Print the extracted data
        for ticker, percentage_drop in losers_data:
            
            #if percentage_drop > 10:
            #print(f"{ticker}: {percentage_drop}")
        
            #ticker = "MSFT"
            #percentage_drop = "0.39"
            print(ticker)
            print(percentage_drop)
            
            
            rec = Anazlyze_stock(ticker,percentage_drop)
            print(f"Recommendation is: {rec}")
            print("\n##########################################\n\n")

        print("---!Finished checking losers tickets!---")
        time.sleep(3600)

if __name__ == "__main__":
    main()

#TODO
# 1. Add getting Book Value
# 2. Add getting Market Value
