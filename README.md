# InvestorBot: Automated Stock Analysis and Prediction

InvestorBot is an advanced tool designed to automate the process of analyzing and predicting stock market movements. It leverages a range of Python libraries and APIs to gather and analyze data from various sources, providing insights into stock performance, potential reasons for price fluctuations, and predictive analytics to assess the likelihood of stock recovery.

## Features

## Features

stock_data_loader.py:
- **Automated Data Collection**: Collects stock metrics from finance websites using web scraping techniques.
- **Data Cleaning and Analysis**: Processes and cleans the collected data, removing outliers and calculating sector-wise metrics.
- **Sector-wise Performance Metrics**: Calculates median, 10th percentile, 90th percentile, and standard deviation for various financial metrics across different sectors AND industries.
- **Grading System**: Assigns letter grades to stocks based on their fundamentals performance metrics, providing a quick overview of stock health in the form of a rating from 1 to 100.
- **Export Functionality**: Exports the analyzed data, including stock ratings and grades, to a CSV file for further analysis or reporting.

investorbot.py:
- **Top 3 Losers Stock of the Day**: InvestorBot gathers data on stocks that fell today and returns their tickers and percentage drops.
- **Stock Performance Analysis**: InvestorBot gathers data on stocks that have experienced significant drops, identifying the top losers based on percentage drop.
- **Reason for Stock Fall**: By scraping the latest news and financial reports, it provides a detailed analysis of why a particular stock fell, offering insights into the underlying causes.
- **Financial Health Assessment**: Utilizes advanced semantic search and language models to assess the overall financial health of a company, based on its financial reports and market trends.
- **Stock Recovery Prediction**: Employs Monte Carlo simulations and financial analysis to estimate the chances of a stock recovering from its recent performance.
- **End Value Calculation**: Combines book value, market cap, and recovery predictions to estimate the end value of a company.

## Installation

To set up InvestorBot, you will need Python installed on your system. Then, clone the repository and install the required Python packages using pip:

```bash
git clone https://github.com/yourusername/investorbot.git
cd investorbot
pip install -r requirements.txt
```

## Usage

To run InvestorBot, simply execute the `investorbot.py` script:

```bash
python investorbot.py
```

The script will automatically gather data, analyze it, and provide predictions for the top 3 stocks that have experienced significant drops.

## Contributing

Contributions to InvestorBot are welcome. Please feel free to submit issues or pull requests on GitHub.

## License

InvestorBot is open-source software licensed under the MIT License. See the `LICENSE` file for more details.

---

InvestorBot is a powerful tool for investors and financial analysts, providing a comprehensive analysis and predictive modeling for stock market performance. With its ability to gather and analyze data from various sources, it offers valuable insights into stock movements and recovery potential.
