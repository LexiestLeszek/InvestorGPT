PERPLEXITY_API = ""

import json
import time
from googlesearch import search
from bs4 import BeautifulSoup
import re
import requests
import yfinance as yf
from datetime import date, timedelta
from stockgrader import *
import pandas as pd


################################################################################################
# Helper funcs
################################################################################################
def goog_query_str(company_name):
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    try:
        query = f"{company_name} stock fell after:{yesterday}"
        print(query)
        search_results = search(query, num=2)
        top_links = list(search_results)
        print(top_links)
    except Exception as e:
        print(f"Wiki/Reddit/Yandex/OtvetMail failed: {e}")
        top_links = list("")
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

    user_prompt = f"""What is the company name that has {ticker} stock ticker? Answer only with the company name and nothing else."""
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
        "Authorization": "Bearer " + PERPLEXITY_API
    }
    response = requests.post(url, json=payload, headers=headers)
    
    json_data = response.text
    
    # Parse the JSON data
    parsed_json = json.loads(json_data)

    # Access and print the "content"
    company_name = parsed_json["choices"][0]["message"]["content"]
    
    print(company_name)
    
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
    
    prompt = f"""You are a great financial analyst that takes company news and can interpret how they affect company stocks.
            Read these news carefully:\n
            {context}\n
            Question: Why did company's stock fell? Answer with as many financial details as possible, but keep the answer short.
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

def get_stock_numeric_rating(ticker, csv_file_name):
    # Read the CSV file into a DataFrame
    df = pd.read_csv(csv_file_name)
    
    # Filter the DataFrame to find the row with the given ticker
    filtered_df = df[df['Еickers'] == ticker]
    
    # Extract the "Overall Rating" value for the given ticker
    # Assuming there's only one row for each ticker, and it's the first column
    overall_rating = filtered_df.iloc[0]['Overall Rating']
    
    return overall_rating

# Example usage:
# ticker = 'AAPL'
# csv_file_name = 'stock_ratings.csv'
# print(get_overall_rating(ticker, csv_file_name))

def get_stock_txt_rating(ten_k,ten_q):
    
    # Uses Embeddings + LLMs to ask ~20 questions to company's 10-Ks and 10-Qs and assess its overall health
    
    questions = ""

    for q in questions:
        q = ""

################################################################################################
# Full Step 5: Estimate a chance for a stock to fix the problem 
################################################################################################

# using monte carlo simulation 
#   based on the stock fundamentals
#   reasons why stock fell
#   company's unique advantages
#   company's health compared to competitotrs
#   general market trends

def chance_to_recover(company_name,ticker):
    
    why_fell = why_stock_fell(ticker)
        
    stock_n_rating = get_stock_numeric_rating(ticker, "StockRatings.csv")
    
    stock_txt_rating = get_stock_txt_rating(ticker, "StockRatings.csv")
    
    prompt = f"""You are the greatest and most competent financial analyst that can understand and predict company's future.
        Read this context about the company:\n
        Reason {company_name} stock fell last 24 hours: {why_fell}.\n
        {company_name} overall description: {stock_txt_rating}\n
        {company_name} overall financial rating from world class analytical experts: {stock_n_rating} out of 100.\n
        Question: What is the chance of a company to recover its stock price based on the reason the stock fell, company description, company financial health?
        Answer from a financial expert:
        """
    
    result = llm_call(prompt)
    
    return result

################################################################################################
# Full Step 6: Calculate end value of a company
################################################################################################

# Book value - market cap * probability to fix the problems


def main():
    
    losers_data = get_losers()

    sorted_losers_data = sorted(losers_data, key=lambda x: x[1], reverse=True)
    
    top_3_losers = sorted_losers_data[:3]
    
    # Print the extracted data
    for ticker, percentage_drop in top_3_losers:
        
        company_name = get_company_name(ticker)
        
        answer = chance_to_recover(company_name,ticker)
        
        book_value = get_book_value(ticker)
        
        market_cap = get_market_cap(ticker)
        
        print(f"{company_name} chacnes to recover: ", answer)
        print(f"{company_name} Book value is {book_value}")
        print(f"{company_name} Market Cap is {market_cap}")
        print(f"{company_name} Net value is {book_value - market_cap}")
        
        


















