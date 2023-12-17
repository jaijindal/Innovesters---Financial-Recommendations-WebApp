from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from celery.result import AsyncResult
from django.db.models import Sum, Case, When, IntegerField, F
from TransApp.models import Transaction
from StocksApp.api.serializers import YahooSerializer, YahooWebSerializer
from StocksApp.tasks import calculate_portfolio, calculate_playground
import yfinance as yf
import datetime


class StocksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        stocks = Transaction.objects.filter(user=request.user).values('stock').annotate(
            quantity=Sum(
                Case(
                    When(transaction_type='BUY', then=F('quantity')),
                    When(transaction_type='SELL', then=-1 * F('quantity')),
                    default=0,
                    output_field=IntegerField()
                )
            )
        )

        for stock in stocks:
            try:
                close_price = YahooSerializer.get_most_recent_data(stock['stock'])
                stock['Close'] = round(close_price, 2)

                # Get all BUY transactions for the stock
                buy_transactions = Transaction.objects.filter(user=request.user, stock=stock['stock'], transaction_type='BUY').order_by('timestamp')
                # Get all SELL transactions for the stock
                sell_transactions = Transaction.objects.filter(user=request.user, stock=stock['stock'], transaction_type='SELL').order_by('timestamp')

                buy_transactions = [(transaction.price, transaction.quantity) for transaction in buy_transactions]
                sell_transactions = [(transaction.price, transaction.quantity) for transaction in sell_transactions]

                remaining_buy = []
                total_sell = 0

                for buy_price, buy_quantity in buy_transactions:
                    while sell_transactions and buy_quantity > 0:
                        sell_price, sell_quantity = sell_transactions[0]
                        if sell_quantity < buy_quantity:
                            buy_quantity -= sell_quantity
                            total_sell += sell_price * sell_quantity
                            sell_transactions.pop(0)
                        else:
                            total_sell += sell_price * buy_quantity
                            sell_transactions[0] = (sell_price, sell_quantity - buy_quantity)
                            buy_quantity = 0
                    if buy_quantity > 0:
                        remaining_buy.append((buy_price, buy_quantity))

                total_buy = sum(price * quantity for price, quantity in remaining_buy)

                # Calculate the total price for the stock
                stock['Total Price'] = round((total_buy / stock['quantity']), 2) if stock['quantity'] != 0 else 0
                
                # Calculate the current value of the stock
                current_value = stock['Close'] * stock['quantity']

                # Calculate the P/L for the stock
                stock['P/L'] = round(current_value - float(total_buy), 2)

            except ValueError as e:
                stock['Close'] = 'No data found'

        return Response(list(stocks), status=status.HTTP_200_OK)


class YahooWebView(APIView):
    def post(self, request):
        ticker = request.data.get('ticker')
        if not ticker:
            return Response({"error": "No ticker provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            data = YahooWebSerializer.get_stock_data(ticker)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        data = {key.replace('.', ''): value for key, value in data.items()}
        serializer = YahooWebSerializer(data)

        return Response(serializer.data, status=status.HTTP_200_OK)


class YahooChartView(APIView):
    def post(self, request):
        ticker = request.data.get('ticker')
        if not ticker:
            return Response({"error": "No ticker provided"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            today = datetime.date.today().strftime('%Y-%m-%d')
            data = yf.download(ticker, start="2020-01-01", end=today)
            close_prices = data['Close'].tolist()
            dates = data.index.strftime('%Y-%m-%d').tolist()
            chart_data = {"dates": dates, "close_prices": close_prices}

            return Response(chart_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        

class OptimalPortfolioView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        risk = request.user.userprofile.risk
        task = calculate_portfolio.delay(risk)
        return Response({'task_id': str(task.id)}, status=status.HTTP_200_OK)
    
    def post(self, request):
        risk = request.data.get('risk')
        stocks = request.data.get('stocks')
        if risk is None or stocks is None:
            return Response({"error": "Risk and/or stocks not provided"}, status=status.HTTP_400_BAD_REQUEST)
        if len(stocks) < 5:
            return Response({"error": "Minimum of 5 stocks required"}, status=status.HTTP_400_BAD_REQUEST)
        task = calculate_playground.delay(risk, stocks)
        return Response({'task_id': str(task.id)}, status=status.HTTP_200_OK)



class TaskResultsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, task_id):
        task_result = AsyncResult(task_id)
        return Response(task_result.result, status=status.HTTP_200_OK)


