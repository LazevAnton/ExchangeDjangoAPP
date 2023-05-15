from django.contrib import admin

from DjangoAPP.models import ExchangeProviders, ExchangeRates

admin.site.register([ExchangeProviders, ExchangeRates])
