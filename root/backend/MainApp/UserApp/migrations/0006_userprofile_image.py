# Generated by Django 4.2.6 on 2023-11-13 15:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0005_userprofile_last_password_reset_request'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to='profile_images/'),
        ),
    ]