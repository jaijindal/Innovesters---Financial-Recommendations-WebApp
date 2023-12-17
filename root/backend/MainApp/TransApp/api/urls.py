from django.urls import path
from TransApp.api.views import *

app_name = 'Trans'

urlpatterns = [
    path('transaction/', TransactionView.as_view(), name='transaction'),
]