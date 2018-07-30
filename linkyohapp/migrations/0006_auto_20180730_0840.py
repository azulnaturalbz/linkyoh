# Generated by Django 2.0.7 on 2018-07-30 14:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('linkyohapp', '0005_auto_20180730_0704'),
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local', models.CharField(max_length=100)),
                ('description', models.TextField(default='No Description')),
            ],
        ),
        migrations.CreateModel(
            name='LocalType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('local', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('description', models.TextField(blank=True, null=True)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='linkyohapp.Local')),
                ('localType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='linkyohapp.LocalType')),
            ],
        ),
        migrations.CreateModel(
            name='State',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=100)),
                ('description', models.TextField(default='No Description')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='linkyohapp.Country')),
            ],
        ),
        migrations.AddField(
            model_name='local',
            name='state',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='linkyohapp.State'),
        ),
    ]
