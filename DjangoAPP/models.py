from django.db import models


class ExchangeProviders(models.Model):
    provider_name = models.CharField(max_length=20, blank=False)
    provider_api_url = models.URLField(blank=False)


class ExchangeRates(models.Model):
    base_currency = models.CharField(max_length=20)
    currency = models.CharField(max_length=20)
    sale_rate = models.DecimalField(max_digits=10, decimal_places=4)
    buy_rate = models.DecimalField(max_digits=10, decimal_places=4)
    provider = models.ForeignKey(ExchangeProviders, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.base_currency}/{self.currency}'
