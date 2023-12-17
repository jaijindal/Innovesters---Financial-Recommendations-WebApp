import requests
from bs4 import BeautifulSoup
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer


def SentimentAnalysis():
    # List of top 50 blue chip stocks (replace with your own list)
    # blue_chip_stocks=["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]
    blue_chip_stocks = [
        "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "JPM", "JNJ", "V", "NVDA", "UNH",
        "PG", "MA", "INTC", "HD", "VZ", "DIS", "ADBE", "CRM", "PYPL", "WMT",
        "BAC", "KO", "PEP", "CVX", "XOM", "CSCO", "ABT", "MRK", "NFLX", "ABBV",
        "T", "WFC", "ABBV", "PM", "MO", "COST", "GOOG", "LMT", "MS", "NKE", "CMCSA",
        "QCOM", "HON", "PYPL", "BLK", "GS", "SBUX", "XOM", "DIS"
    ]

    # Additional news websites
    news_websites = [
        "https://finance.yahoo.com/quote/",
        "https://www.reuters.com/companies/",
    ]

    def get_news_headlines(stock_symbol):
        headlines = []
        for website in news_websites:
            base_url = f"{website}{stock_symbol}"
            page = requests.get(base_url)
            soup = BeautifulSoup(page.text, 'html.parser')
            headlines += soup.find_all("h3")

        return [headline.text for headline in headlines]

    def analyze_sentiment(text):
        analyzer = SentimentIntensityAnalyzer()
        sentiment_scores = analyzer.polarity_scores(text)
        return sentiment_scores['compound']

    def rank_stocks_by_sentiment(stock_symbols):
        stock_sentiments = []
        processed_stocks = set()

        for stock_symbol in stock_symbols:
            if stock_symbol in processed_stocks:
                continue

            headlines = get_news_headlines(stock_symbol)
            sentiment_scores = [analyze_sentiment(headline) for headline in headlines]
            avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
            stock_sentiments.append((stock_symbol, avg_sentiment))
            processed_stocks.add(stock_symbol)

        # Sort stocks by average sentiment score (from most positive to most negative)
        ranked_stocks = sorted(stock_sentiments, key=lambda x: x[1], reverse=True)

        ranked_stocks=ranked_stocks[:10]  # Get the top 10 ranked stocks

        final_stocks=[]
        # Print the top 10 ranked stocks based on sentiment
        for i, (stock_symbol, avg_sentiment) in enumerate(ranked_stocks):
            final_stocks.append(stock_symbol)

        return final_stocks

    top_ranked_stocks = rank_stocks_by_sentiment(blue_chip_stocks)
    return top_ranked_stocks

