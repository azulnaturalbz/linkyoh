# Generated by Django 2.0.7 on 2018-08-26 16:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkyohapp', '0016_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='rating',
            name='rating',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
