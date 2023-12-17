from django.db import models
from UserApp.models import User

class Transaction(models.Model):
    # Assuming you have a User model for the sender and receiver
    TRANSACTION_TYPES = [
    ('BUY', 'BUY'),
    ('SELL', 'SELL'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_transactions')
    stock = models.CharField(max_length=100)
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    quantity = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)