from django.urls import path
from StocksApp.api.views import *

app_name = 'Stocks'

urlpatterns = [
    path('stock/', StocksView.as_view(), name='stock'),
    path('yahoo-web/', YahooWebView.as_view(), name='yahoo-web'),
    path('yahoo-chart/', YahooChartView.as_view(), name='yahoo-chart'),
    path('optimal/', OptimalPortfolioView.as_view(), name='optimal'),
    path('task-results/<str:task_id>/', TaskResultsView.as_view(), name='task-status'),
]

