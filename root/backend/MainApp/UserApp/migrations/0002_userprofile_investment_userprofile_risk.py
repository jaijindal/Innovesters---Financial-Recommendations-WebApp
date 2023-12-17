# Generated by Django 4.2.6 on 2023-11-05 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='investment',
            field=models.CharField(choices=[('RP', 'Retirement Planning'), ('CI', 'Counter Inflation'), ('SI', 'Side Income')], default='RP', max_length=2),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='risk',
            field=models.CharField(choices=[('HR', 'High Risk High Reward'), ('MO', 'Most Optimized (Recommended)'), ('LR', 'Low Risk Decent Returns')], default='MO', max_length=2),
        ),
    ]