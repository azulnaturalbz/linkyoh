# Generated by Django 2.0.7 on 2018-07-31 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('linkyohapp', '0010_auto_20180730_1544'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='email',
            field=models.CharField(default='1', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='first_name',
            field=models.CharField(default='1', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='gender',
            field=models.CharField(default='1', max_length=8),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='last_name',
            field=models.CharField(default='1', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='link',
            field=models.CharField(default='1', max_length=500),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='locale',
            field=models.CharField(default='1', max_length=128),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='profile',
            name='timezone',
            field=models.CharField(default='1', max_length=64),
            preserve_default=False,
        ),
    ]