# InvestorBot

InvestorBot is a FastAPI-based application designed to provide investment analysis and recommendations for stocks experiencing significant drops in value. The application leverages data from Yahoo Finance, financial statements, and uses AI-driven inference to assess the likelihood of a company's recovery and provide investment recommendations.

## Features

- **API Integration**: Utilizes Perplexity AI for natural language processing to generate human-like responses and investment recommendations.
- **Stock Analysis**: Analyzes stocks that have seen significant drops in value.
- **Financial Statement Analysis**: Fetches and analyzes the balance sheet, income statement, and cash flow statement for the analyzed stocks.
- **AI-Driven Inference**: Uses AI to predict the probability of a company fixing its issues and recovering its stock price.
- **Investment Recommendation**: Based on the analysis, provides a recommendation on whether to buy or not.

## Getting Started

### Prerequisites

- Python 3.7+
- FastAPI
- Uvicorn
- BeautifulSoup
- Requests
- yfinance
- bs4

### Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/investorbot.git
cd investorbot
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

### Running the Application

To run the application, use the following command:

```bash
uvicorn app:app --reload
```

This will start the server at `http://0.0.0.0:8001`.

## API Endpoints

### `GET /api/getinvestinfo`

Returns investment information for stocks that have seen significant drops in value.

### Example Usage

```http
GET /api/getinvestinfo
```

### Response

A JSON response containing the investment analysis and recommendation for the analyzed stocks.


## Key Functions

- `get_losers()`: Fetches a list of stocks that have shown significant drops in value.
- `get_stock_price(ticker, history=5)`: Retrieves the historical stock prices for a given ticker symbol.
- `get_3financial_statements(ticker)`: Fetches the balance sheet, income statement, and cash flow statement for a company.
- `why_price_dropped(company_name, percentage_drop)`: Uses Perplexity AI to determine the reasons behind a stock price drop.
- `Anazlyze_stock(ticker, percentage_drop)`: Analyzes a stock, generates investment recommendations, and returns a JSON object with the analysis results.

## Contributing

Contributions are welcome! Please read the [Contribution Guidelines](CONTRIBUTING.md) before submitting any pull requests.

## Future Enhancements

- **Book Value and Market Value Fetching**: Implement logic to fetch the book value and market value of companies for a more comprehensive analysis.
- **Expanded Financial Statement Analysis**: Enhance the analysis of financial statements to include more detailed insights.
- **Integration with Other Financial APIs**: Consider integrating with other financial data providers for a broader range of analysis.
- **User Interface**: Develop a user-friendly interface for easier access to the tool's functionalities.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contact

For any questions or suggestions, please open an issue on GitHub or contact the project maintainers.

## Acknowledgments

- [Yahoo Finance](https://finance.yahoo.com/) for providing financial data.
- [Perplexity AI](https://perplexity.ai/) for the AI-driven inference service.
- [yfinance](https://pypi.org/project/yfinance/) for fetching financial data from Yahoo Finance.
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) for web scraping to fetch financial data.
- [FastAPI](https://fastapi.tiangolo.com/) for building the web API.
