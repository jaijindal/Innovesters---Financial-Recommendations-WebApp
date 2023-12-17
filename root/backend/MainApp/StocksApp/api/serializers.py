import yfinance as yf
import matplotlib.pyplot as plt
import requests
from bs4 import BeautifulSoup
from rest_framework import serializers

class YahooSerializer(serializers.Serializer):
    Close = serializers.FloatField()

    @staticmethod
    def get_most_recent_data(stock_ticker):
        stock = yf.Ticker(stock_ticker)
        intraday_data = stock.history(period="1d", interval="1m")

        if intraday_data.empty:
            raise ValueError(f"No data found for ticker: {stock_ticker}")

        return intraday_data['Close'].tail(1).iloc[0]

class NewsArticleSerializer(serializers.Serializer):
    index = serializers.IntegerField()
    headline = serializers.CharField()
    href = serializers.CharField()

class YahooWebSerializer(serializers.Serializer):
    Previous_Close = serializers.CharField(source='Previous Close')
    Open = serializers.CharField()
    Bid = serializers.CharField()
    Ask = serializers.CharField()
    Days_Range = serializers.CharField(source="Day's Range")
    Week52_Range = serializers.CharField(source='52 Week Range')
    Volume = serializers.CharField()
    Avg_Volume = serializers.CharField(source='Avg Volume')
    Market_Cap = serializers.CharField(source='Market Cap')
    Beta_5Y_Monthly = serializers.CharField(source='Beta (5Y Monthly)')
    PE_Ratio_TTM = serializers.CharField(source='PE Ratio (TTM)')
    EPS_TTM = serializers.CharField(source='EPS (TTM)')
    Earnings_Date = serializers.CharField(source='Earnings Date')
    Forward_Dividend_Yield = serializers.CharField(source='Forward Dividend & Yield')
    Ex_Dividend_Date = serializers.CharField(source='Ex-Dividend Date')
    Target_Est_1y = serializers.CharField(source='1y Target Est')
    news_articles_data = NewsArticleSerializer(many=True)

    @staticmethod
    def get_stock_data(ticker):
        url = f"https://finance.yahoo.com/quote/{ticker}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            

            news_section = soup.find('div', id='mrt-node-quoteNewsStream-0-Stream')
            news_articles_data = []

            if news_section:
                news_articles = news_section.find_all('li', class_='js-stream-content Pos(r)')
                for index, article in enumerate(news_articles[:3], start=1):
                    headline = article.find('h3').text.strip()
                    href = "https://finance.yahoo.com" + article.find('a')['href'] if article.find('a') else None
                    news_articles_data.append({
                    "index": index,
                    "headline": headline,
                    "href": href
                })
                


            data_fields = {
                "Previous Close": None,
                "Open": None,
                "Bid": None,
                "Ask": None,
                "Day's Range": None,
                "52 Week Range": None,
                "Volume": None,
                "Avg. Volume": None,
                "Market Cap": None,
                "Beta (5Y Monthly)": None,
                "PE Ratio (TTM)": None,
                "EPS (TTM)": None,
                "Earnings Date": None,
                "Forward Dividend & Yield": None,
                "Ex-Dividend Date": None,
                "1y Target Est": None,
                "news_articles_data": news_articles_data

            }

            for key in data_fields:
                field_label = soup.find("td", string=key)
                if field_label:
                    field_value = field_label.find_next("td")
                    if field_value:
                        data_fields[key] = field_value.text.strip()

      
            return data_fields
        else:
            return {"error": "Failed to retrieve the page. Status code: " + str(response.status_code)}
        

