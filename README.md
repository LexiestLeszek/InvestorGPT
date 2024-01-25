### StockBot 📈

A LangChain and LLM-based AI system designed to assist with stock investment by utilizing real-time and historical financial data. As a retail investor without a finance background, understanding complex financial terms can be challenging and time-consuming. To address this issue, we have developed an AI bot that leverages LLM technology to provide investment analysis.

### Data sources

The bot incorporates several tools and functions that retrieve real-time information related to the stock of interest. Key data sources include:
- Company's financial statements;
- Historic stock price data (e.g., 1 month or 1 year, depending on the model's context length);
- Latest company-related news.

These factors provide a comprehensive view of the company's historical performance and current market sentiment. Additional tools can be added as needed.

### LangChain ReAct agent

The response and action agent were initially used for stock analysis, but the results were inconsistent. This approach involves a dynamic thought process during runtime, with actions based on the agent's thoughts. However, it may get stuck in an infinite loop of thoughts and actions, making it unsuitable for complex tasks such as stock analysis. Further improvements can be made by modifying the prompt.


### Example

Input

`Analyze_stock("Is it a good time to invest in Apple Inc.?")`

Formatting

`Query': 'Shall I invest in Apple Inc. right now?', 'Company_name': 'Apple Inc.', 'Ticker': 'AAPL'}`

Analyzing.....

Output:

`
Investment Thesis for Apple Inc.:

1. Strong Financials: Apple Inc. has shown consistent growth in its financials over the past few years. The company has a positive tangible book value, indicating a strong asset base. Additionally, the company has a high invested capital, which suggests a strong financial position.
2. Increasing Stock Price: The stock price of Apple Inc. has been increasing steadily over the past few days. This indicates positive investor sentiment and potential for further growth in the future.
3. High Revenues: Apple Inc. has reported high revenues in its recent quarterly results. This indicates that the company is performing well and has a strong market presence.
4. Positive News Coverage: Apple Inc. has been in the news recently, with multiple articles highlighting the company's performance and prospects. Positive news coverage can attract more investors and potentially drive up the stock price.
5. Technology Sector Outlook: The technology sector in the US is expected to grow in the coming years due to increasing demand for consumer electronics and digital services. Apple Inc., being a major player in the sector, is well-positioned to benefit from this growth. However, it is important to consider the competitive landscape and regulatory environment of the sector before making an investment decision.

Conclusion:
Based on the available data, investing in Apple Inc. right now could be a favorable option. The company has strong financials and a positive stock price trend. Additionally, Apple's high revenues and positive news coverage suggest that the company is performing well and has a strong market presence. However, it is important to conduct further research and analysis to assess the potential risks associated with the technology sector and the company's competitive position.
`

#### Warning - not an investment advice!

This bot is made for educational purposes and is not providing any investment advice. Use it to your own discretion, owner and creator of the bot doesn't hold any responsibility for the results of this bot.
