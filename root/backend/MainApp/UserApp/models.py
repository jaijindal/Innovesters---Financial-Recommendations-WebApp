from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    RISK_CHOICES = [
        ('HR', 'High Risk High Reward'),
        ('MO', 'Most Optimized (Recommended)'),
        ('LR', 'Low Risk Decent Returns'),
    ]

    INVESTMENT_CHOICES = [
        ('RP', 'Retirement Planning'),
        ('CI', 'Counter Inflation'),
        ('SI', 'Side Income'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='profile_images/', default='default.jpg')
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=100, null=True, blank=True)
    last_password_reset_request = models.DateTimeField(null=True, blank=True)

    risk = models.CharField(
        max_length=2,
        choices=RISK_CHOICES,
        default='MO',
    )

    investment = models.CharField(
        max_length=2,
        choices=INVESTMENT_CHOICES,
        null=True,
    )