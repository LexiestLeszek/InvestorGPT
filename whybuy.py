PERPLEXITY_API = "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"

import json
import time
from googlesearch import search
from bs4 import BeautifulSoup
import re
import requests
import yfinance as yf
from datetime import date, timedelta
from stock_grader import *
import pandas as pd


################################################################################################
#Helper funcs
################################################################################################
def goog_query_str(ticker):
    today = date.today()
    yesterday = today - timedelta(days=1)
    yesterday = yesterday.strftime('%Y-%m-%d')
    try:
        company_name = get_company_name(ticker) 
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

def why_stock_fell(ticker):
    
    context = goog_query_str(ticker)
    
    prompt = f"""You are a great financial analyst that takes company news and can interpret how they affect company stocks.
            Read these news carefully:\n
            {context}\n
            Question: Why did company's stock fell? Answer with as many financial details as possible, but keep the answer short.
            Answer: 
            """
    
    answer = llm_call(prompt)
    
    return answer


################################################################################################
# Full Step 3: Get 10k and 10q reports and vectorize them
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

def get_stock_rating(ticker, csv_file_name):
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



################################################################################################
# Full Step 5: Estimate a chance for a stock to fix the problem 
################################################################################################

# using monte carlo simulation 
#   based on the stock fundamentals
#   reasons why stock fell
#   company's unique advantages
#   company's health compared to competitotrs
#   general market trends

def probability_to_recover(why_fell,stock_rating):
    
    result = ""
    
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
        
        why_fell = why_stock_fell(ticker)
        
        stock_rating = get_stock_rating(ticker, "StockRatings.csv")
        
        






















### SUmmarizator
'''
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.luhn import LuhnSummarizer


parser = PlaintextParser.from_string(text, Tokenizer("english"))
summarizer = LuhnSummarizer()
summary = summarizer(parser.document, 50) # Summarize the document with 2 sentences

print("SUMMARIZATION:")
for sentence in summary:
    print(sentence)
    
    
    
'''