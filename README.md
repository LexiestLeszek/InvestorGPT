# InvestorBot 📈

A LangChain and LLM-based agent designed to assist with stock investment by utilizing real-time and historical financial data. As a retail investor without a finance background, understanding complex financial terms can be challenging and time-consuming. To address this issue, we have developed an AI bot that leverages LLM technology to provide investment analysis.

# Data sources

The agent incorporates several tools and functions that retrieve real-time information related to the stock of interest. Key data sources include:
- Company's financial statements;
- Historic stock price data (e.g., 1 month or 1 year, depending on the model's context length);
- Latest company-related news.

These factors provide a comprehensive view of the company's historical performance and current market sentiment. Additional tools can be added as needed.

# TODO:

## Non-market value 
1. **Book Value**:
   - **Explanation**: Book value is the value of a company's assets minus its liabilities as reported on the balance sheet. It represents the net worth of a company based on historical costs.
   - **Formula**: Book Value = Total Assets - Total Liabilities

2. **Discounted Cash Flow (DCF) Analysis**:
   - **Explanation**: DCF estimates the present value of a company based on its expected future cash flows. It considers the time value of money, risk, and growth potential.
   - **Formula**: DCF = CF1 / (1+r)^1 + CF2 / (1+r)^2 + ... + CFn / (1+r)^n

3. **Earnings Multiplier**:
   - **Explanation**: The earnings multiplier, or P/E ratio, compares a company's stock price to its earnings per share, indicating how much investors are willing to pay for each dollar of earnings.
   - **Formula**: Earnings Multiplier = Stock Price / Earnings Per Share

4. **Present Value of a Growing Perpetuity Formula**:
   - **Explanation**: This formula calculates the present value of an infinite series of cash flows growing at a constant rate, providing an estimate of the total value.
   - **Formula**: PV = C / (r-g)

## Market Value 
1. **Market Capitalization**:
   - **Explanation**: Market cap is the total market value of a company's outstanding shares. It reflects what the market values the company at.
   - **Formula**: Market Cap = Share Price x Total Shares Outstanding

2. **Enterprise Value**:
   - **Explanation**: Enterprise value is a comprehensive measure of a company's total value, including debt and equity. It provides a more accurate picture of a company's worth.
   - **Formula**: Enterprise Value = Market Cap + Total Debt - Cash and Cash Equivalents

**TODO**: 

Implement "HedgeFund advisorBot": If the company's Non-market value is less than its Market Value (price per stock x # of stocks) - the company is undervalued. If company's stock dropped due to bad news or sudden problems - calculate the probability of the company to be able to fix the problem and buy based on this risk if the return is positive.

### Formula for determing whether to buy or not the company: 
If company is undervalued (Market Value < Book value), then formula on when to buy it:

`(Market Value - Book Value) * probability of fixing the problem
AND
Price / Earnings is lower than the benchmark`

If the number is positive - Buy, If the number is negative - don't buy.
If you bought, sell when Book Value = Market Value.

## Task 1: Implement calculation of the book and market value of a company
## Task 2: Overall algo looks lke this:
1) bot monitors stocks (for a given set of companies based on some kind of a hardcoded threshold) and triggers when some particular company's stock falls 10% or more (30% or more? 50% or more?)
2) Bot then assesses its book value
3) Bot assesses why company's stock has fallen - analyzed the news
4) Bot asseses probability of a company to deal with bad news and fix what's broken
5) Bot calculated company book value, company market value and probability to fix the problem (using Poker logic)
6) If company is undervalued and there is a positive ROI given the probability to fix the problems, bot provides a telegram recommendation to buy this company's stock.

# Not a financial or investment advice!

This program is made for educational purposes and doesn't provide investment or financial (or any other) advice. Please use it to your own discretion and risks.
