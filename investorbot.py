PERPLEXITY_API = ""

import json
import time
from googlesearch import search
from bs4 import BeautifulSoup
import re
import requests
import yfinance as yf
from datetime import date, timedelta
#from stock_data_loader import *
import pandas as pd
import warnings
warnings.filterwarnings("ignore")


################################################################################################
# Helper funcs
################################################################################################
def goog_query_str(company_name):
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    query = f"{company_name} stock dropped after:{yesterday}"
    print(query)
    try:
        search_results = search(query,num_results=5,advanced=True)
        top_links = []
        for sr in search_results:
            if f"{company_name}" in sr.title or f"{company_name}" in sr.description:
                top_links.append(sr.url)
        top_links = list(search_results)
        #print(top_links)
    except Exception as e:
        print(f"Google1 failed: {e}")
        
    scraped_texts = []
    for link in top_links:
        print(link)
        try:
            page = requests.get(link)
            soup = BeautifulSoup(page.content, 'html.parser')
            text = ' '.join([p.get_text() for p in soup.find_all('p')])
        except Exception as e:
            print(f"Failed to scrape the link: {link}\nError: {e}")
        scraped_texts.append(text)

    all_scraped_text = '.\n'.join(scraped_texts)
    
    return all_scraped_text

def get_company_name(ticker):

    user_prompt = f"""
            Answer only with the company name and nothing else.
            Do not answer anything except company name, no commas, periods, punctuation or explanation.
            Answer only with the company name.
            Question: What is the company name that has {ticker} stock ticker? 
            Company name:
            """
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-small-online",
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
        "Authorization": "Bearer " + PERPLEXITY_API
    }
    response = requests.post(url, json=payload, headers=headers)
    
    json_data = response.text
    parsed_json = json.loads(json_data)
    company_name = parsed_json["choices"][0]["message"]["content"]
    
    return company_name

def llm_call(prompt):
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-medium-chat",
        "temperature": 0,
        "messages": [
            {
                "role": "system",
                "content": "Be precise and concise."
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
        "Authorization": "Bearer " + PERPLEXITY_API
    }
    response = requests.post(url, json=payload, headers=headers)
    json_data = response.text
    parsed_json = json.loads(json_data)
    answer = parsed_json["choices"][0]["message"]["content"]
    
    return answer

################################################################################################
# Full Step 1 is this func: get losers ticker and percentage drop
################################################################################################
def get_losers():
    try:
        url = "https://finance.yahoo.com/losers"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'W(100%)'})
        data = []
        for row in table.find_all('tr')[1:]: 
            cells = row.find_all('td')
            ticker = cells[0].text.strip()
            percentage_drop = cells[4].text.strip()
            percentage_drop = float(percentage_drop.replace("-", "").replace("%", ""))
            data.append((ticker, percentage_drop))
            return data
    except Exception as e:
        url = "https://stockanalysis.com/markets/losers/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'main-table'})
        data = []
        for row in table.find_all('tr')[1:]: 
            cells = row.find_all('td')
            ticker = cells[1].text.strip()
            percentage_drop = cells[3].text.strip()
            percentage_drop = float(percentage_drop.replace("-", "").replace("%", ""))
            data.append((ticker, percentage_drop))
            #data.append(ticker)
            return data
        
    
################################################################################################
# Full Step 2 is this func: get top 2 google results for "{ticker} stock fell"
################################################################################################

def why_stock_fell(company_name):
    
    context = goog_query_str(company_name)
    
    prompt = f"""
            Context: {context}\n
            Question: Based on the Context, answer with bullet points and give detailed analysis the precise reasons why {company_name} stock price dropped. Why did {company_name} stock price fell? 
            Answer: 
            """
    
    answer = llm_call(prompt)
    
    return answer

################################################################################################
# Full Step 3: Get 10k and 10q reports and vectorize them (rag pipeline)
################################################################################################

# Download 10-Ks and 10-Qs
# Vectorize them
# Ask 20+ questions to them using semantic search + LLM
# summarize the answer into coherent and not so long text


################################################################################################
# Full Step 4: Analyze fundamentals
################################################################################################

# Use some kind of a tool to download and analyze 3 Financial Reports
# Get their main metrics and ratios
# Compare them to competitors

def get_book_value(ticker):
    if "." in ticker:
        ticker = ticker.split(".")[0]
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    # getting book value
    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.iloc[:, :1] 
    total_assets = balance_sheet.loc["Total Assets"][0]
    total_liabilities = balance_sheet.loc["Total Liabilities Net Minority Interest"][0]
    #print("Total Assets in dollars: ",total_assets)
    #print("Total Liabilities Net Minority Interest in dollars: ",total_liabilities)
    book_value = total_assets - total_liabilities
    return book_value

def get_market_cap(ticker):
    if "." in ticker:
        ticker = ticker.split(".")[0]
    company = yf.Ticker(ticker)
    balance_sheet = company.balance_sheet
    # getting book value
    balance_sheet = balance_sheet.dropna(how="any")
    balance_sheet = balance_sheet.iloc[:, :1] 
    market_cap = balance_sheet.loc["Total Capitalization"][0]
    #print("Total Capitalization in dollars as of latest balance sheet: ",market_cap)
    return market_cap

def get_net_value(ticker):

    book_value = get_book_value(ticker)
    market_cap = get_market_cap(ticker)
    net_value = book_value - market_cap
    return net_value
    
def get_stock_numeric_rating(ticker, csv_file_name):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_name)
    
    # Filter the DataFrame to find the row with the given ticker
    filtered_df = df[df['Ticker'] == ticker]
    
    # Extract the "Overall Rating" value for the given ticker
    # Assuming there's only one row for each ticker, and it's the first column
    overall_rating = filtered_df.iloc[0]['Overall Rating']
    
    return overall_rating

#def get_stock_txt_rating(ten_k,ten_q):
def get_stock_txt_rating(company_name):    
    # Uses Embeddings + LLMs to ask ~20 questions to company's 10-Ks and 10-Qs and assess its overall health
    
    prompt = f"What is overall financial health of {company_name}?"
    
    url = "https://api.perplexity.ai/chat/completions"
    payload = {
        "model": "sonar-small-online",
        "temperature": 0,
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "Authorization": "Bearer " + PERPLEXITY_API
    }
    response = requests.post(url, json=payload, headers=headers)
    
    json_data = response.text
    parsed_json = json.loads(json_data)
    answer = parsed_json["choices"][0]["message"]["content"]
    return answer

################################################################################################
# Full Step 5: Estimate a chance for a stock to fix the problem 
################################################################################################

# using monte carlo simulation and bayes rule
#   based on the stock fundamentals
#   reasons why stock fell
#   company's unique advantages
#   company's health compared to competitotrs
#   general market trends

# General idea: 
# 1. Probability of recovering stock price due to health of fundamentals (0-1) 
# p(H) = probability to recover stock price from bad news (general case)
# p(E) = probability of a company having an E financial health (health is the value from 0 to 1)
# P(E|H) = probability of a company to have an E financial health after recovering stock price from bad news
# General formula :
###       P(H|E) = ( P(E|H) * P(H) ) / P(E)
#
# 2. Probability of recovering stock price due to how bad are the news 
# 3. average?

# NOT USED NOT USED
'''
def chance_to_recover(company_name,ticker):
    
    why_fell = why_stock_fell(ticker)
        
    stock_n_rating = get_stock_numeric_rating(ticker, "StockRatings.csv")
    print(f"{company_name} Overall Financial score: {stock_n_rating}")
    
    stock_txt_rating = get_stock_txt_rating(company_name)
    print(f"{company_name} Overall Financial health: {stock_txt_rating}")
    
    prompt = f"""You are the greatest and most competent financial analyst that can understand and predict company's future.
        Read this context about the company:\n
        Reason {company_name} stock fell last 24 hours: {why_fell}.\n
        {company_name} overall description: {stock_txt_rating}\n
        {company_name} overall financial rating from world class analytical experts: {stock_n_rating} out of 100.\n
        Question: What is the chance of a company to recover its stock price based on the reason the stock fell, company description, company financial health?
        Answer from a financial expert:
        """
    
    result = llm_call(prompt)
    print(f"{company_name} chances to recover stock price: {result}")
    
    return result
'''
################################################################################################
# Full Step 6: Calculate end value of a company
################################################################################################


def main():
    
    losers_data = get_losers()
    print("losers gathered")

    sorted_losers_data = sorted(losers_data, key=lambda x: x[1], reverse=True)
    
    top_3_losers = sorted_losers_data[:3]
    
    # Print the extracted data
    for ticker, percentage_drop in top_3_losers:
        print("###########################################################################\n")
        
        company_name = get_company_name(ticker)
        print(f"{company_name} ({ticker}) -{percentage_drop}%")
        
        why_fell = why_stock_fell(company_name)
        print(f"{company_name} Stock drop reasons: {why_fell}")
        net_value = get_net_value(ticker)
        print(f"{company_name} Net Value (Book - MarketCap): {net_value}")
        stock_n_rating = get_stock_numeric_rating(ticker, "StockRatings.csv")
        print(f"{company_name} Overall Funamental Financials health score: {stock_n_rating}")
        stock_txt_rating = get_stock_txt_rating(company_name)
        #print(f"{company_name} Overall Financial health: {stock_txt_rating}")
        
        prompt = f"""You are the greatest and most competent financial analyst that can understand and predict company's future.
            Read this context about the company:\n
            Reason {company_name} stock fell last 24 hours: {why_fell}.\n
            {company_name} overall description: {stock_txt_rating}\n
            {company_name} overall financial rating from world class analytical experts: {stock_n_rating} out of 100.\n
            Question: What is the chance of a company to recover its stock price based on the reason the stock fell, company description, company financial health?
            Answer from a financial expert:
            """
        
        answer = llm_call(prompt)
        print(f"{company_name} chances to recover: {answer}\n")
        
if __name__ == "__main__":
    main()
