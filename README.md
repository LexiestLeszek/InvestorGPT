# InvestorGPT: Automated Stock Analysis and Prediction

InvestorGPT is an AI agent that analyzes the stock that dropped in its price recently and calculates chance for the company to recover the stock price back.

InvestorGPT is an advanced tool designed to automate the process of analyzing and predicting stock market movements. It leverages a range of Python libraries and APIs to gather and analyze data from various sources, providing insights into stock performance, potential reasons for price fluctuations, and predictive analytics to assess the likelihood of stock recovery.

## Features

stock_data_loader.py:
- **Automated Data Collection**: Collects stock metrics from finance websites using web scraping techniques.
- **Data Cleaning and Analysis**: Processes and cleans the collected data, removing outliers and calculating sector-wise metrics.
- **Sector-wise Performance Metrics**: Calculates median, 10th percentile, 90th percentile, and standard deviation for various financial metrics across different sectors AND industries.
- **Grading System**: Assigns letter grades to stocks based on their fundamentals performance metrics, providing a quick overview of stock health in the form of a rating from 1 to 100.
- **Export Functionality**: Exports the analyzed data, including stock ratings and grades, to a CSV file for further analysis or reporting.

InvestorGPT.py:
- **Top 3 Losers Stock of the Day**: InvestorGPT gathers data on stocks that fell today and returns their tickers and percentage drops.
- **Stock Performance Analysis**: InvestorGPT gathers data on stocks that have experienced significant drops, identifying the top losers based on percentage drop.
- **Reason for Stock Fall**: By scraping the latest news and financial reports, it provides a detailed analysis of why a particular stock fell, offering insights into the underlying causes.
- **Financial Health Assessment**: Utilizes advanced semantic search and language models to assess the overall financial health of a company, based on its financial reports and market trends.
- **Stock Recovery Prediction**: Employs Monte Carlo simulations and financial analysis to estimate the chances of a stock recovering from its recent performance.
- **End Value Calculation**: Combines book value, market cap, and recovery predictions to estimate the end value of a company.

## Installation

To set up InvestorGPT, you will need Python installed on your system. Then, clone the repository and install the required Python packages using pip:

```bash
git clone https://github.com/LexiestLeszek/InvestorGPT.git
cd InvestorGPT
pip install -r requirements.txt
```

## Usage

To run InvestorGPT, simply execute the `InvestorGPT.py` script:

```bash
python InvestorGPT.py
```

The script will automatically gather data, analyze it, and provide predictions for the top 3 stocks that have experienced significant drops.

## Grading System

The grading system used in this program is based on the normal distribution of values for a certain metric for a specified sector. For example, if I want to grade the Net Margin of a stock in the Technology sector, I look at the net margins of all the stocks in the technology sector and grade the stock's net margin based on its percentile in the distribution of values.

The grading system utilized in the program takes the standard deviation of the set of values after removing outliers and divides that number by 3, which is represented by the 'Change' value shown in the figure, equaling 4.68. This is the value that is used to grade each metric for each stock.

After all the metrics in each category of valuation, profitability, growth, and price performance are graded, the grades are then converted to numbers and then the average of the values is computed. To get the overall rating of a stock, these numerical ratings for each category are added together and multiplied to get a score out of 100.

For metrics where a lower value is considered better, such as P/E ratios, the algorithm will use the 10th percentile as the basis for grading. So if a stock in the Technology sector has a P/E ratio of 10 and that is in the 10th percentile of all P/E ratios for Technology stocks, it will be rated A+.

## Contributing

Contributions to InvestorGPT are welcome. Please feel free to submit issues or pull requests on GitHub.

## License

InvestorGPT is open-source software licensed under the MIT License. See the `LICENSE` file for more details.

---

## Not a Financial Advice

InvestorGPT is a powerful tool for investors and financial analysts, providing a comprehensive analysis and predictive modeling for stock market performance. With its ability to gather and analyze data from various sources, it offers valuable insights into stock movements and recovery potential. The tool is made for educational purposes and might provide wrong results. You should use its analysis and recommendations to your own discretion.
