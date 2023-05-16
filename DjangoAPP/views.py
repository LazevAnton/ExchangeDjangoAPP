from django.shortcuts import render

from DjangoAPP.models import ExchangeProviders, ExchangeRates
from DjangoAPP.services import ExchangePrivate24Service, ExchangeMonoBankService


def index(request):
    privatbank = ExchangePrivate24Service()
    data = privatbank.get_data()
    privatbank_id = ExchangeProviders.objects.filter(provider_name='PriVatBank').first()
    for all_currencys in data:
        currencys = (
            ExchangeRates.objects.filter(
                currency=all_currencys.get('currency'),
                date_rate=all_currencys.get('date')
            ).first()
        )
        if currencys:
            currencys.currency = all_currencys.get('date'),
            currencys.sale_rate = all_currencys.get('sale_rate')
        else:
            currencys = ExchangeRates(
                base_currency=all_currencys.get('base_currency'),
                currency=all_currencys.get('currency'),
                sale_rate=all_currencys.get('sale_rate'),
                buy_rate=all_currencys.get('buy_rate'),
                date_rate=all_currencys.get('date'),
                provider=privatbank_id
            )
            currencys.save()
    monobank = ExchangeMonoBankService()
    data = monobank.get_data()
    monobank_id = ExchangeProviders.objects.filter(provider_name='MonoBank').first()
    for mono in data:
        currencys = (
            ExchangeRates.objects.filter(
                currency=mono.get('currency'),
                buy_rate=mono.get('rateBuy')
            ).first()
        )
        if currencys:
            currencys.buy_rate = mono.get('rateBuy'),
            currencys.sale_rate = mono.get('rateSell')
        else:
            currencys = ExchangeRates(
                base_currency=mono.get('baseCurrency'),
                currency=mono.get('currency'),
                buy_rate=mono.get('rateBuy'),
                sale_rate=mono.get('rateSell'),
                provider=monobank_id
            )
            currencys.save()
    return render(request, 'index.html')
