# Generated by Django 2.2.3 on 2025-06-22 16:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkyohapp', '0005_auto_20250622_0923'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='show_qr_code',
            field=models.BooleanField(default=False, help_text='Show QR code on your profile for easy sharing'),
        ),
    ]
