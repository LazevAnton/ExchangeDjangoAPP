# Generated by Django 4.2.1 on 2023-05-14 09:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ExchangeProviders',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('provider_name', models.CharField(max_length=20)),
                ('provider_api_url', models.URLField()),
            ],
        ),
        migrations.CreateModel(
            name='ExchangeRates',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('base_currency', models.CharField(max_length=20)),
                ('currency', models.CharField(max_length=20)),
                ('sale_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('buy_rate', models.DecimalField(decimal_places=2, max_digits=5)),
                ('provider', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='DjangoAPP.exchangeproviders')),
            ],
        ),
    ]
