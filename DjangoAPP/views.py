from django.shortcuts import render
from DjangoAPP.models import ExchangeProviders, ExchangeRates
from DjangoAPP.services import ExchangePrivate24Service, ExchangeMonoBankService, SendCurrency


def index(request):
    privatbank = ExchangePrivate24Service()
    data = privatbank.get_data_thread_pool_executor()
    privatbank_id, create = ExchangeProviders.objects.get_or_create(provider_name='PriVatBank',
                                                                    provider_api_url=privatbank.URL_API)
    for all_currencys in data:
        currencys = (
            ExchangeRates.objects.filter(
                currency=all_currencys.get('currency'),
                date_rate=all_currencys.get('date'),
                provider=privatbank_id.id
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
    monobank_id, create = ExchangeProviders.objects.get_or_create(provider_name='MonoBank',
                                                                  provider_api_url=monobank.URL_API)
    for mono in data:
        currencys = (
            ExchangeRates.objects.filter(
                currency=mono.get('currency'),
                buy_rate=mono.get('rateBuy'),
                provider=monobank_id.id
            ).first()
        )
        if currencys:
            currencys.buy_rate = mono.get('currency'),
            currencys.sale_rate = mono.get('date_rate')
        else:
            currencys = ExchangeRates(
                base_currency=mono.get('baseCurrency'),
                currency=mono.get('currency'),
                buy_rate=mono.get('rateBuy'),
                sale_rate=mono.get('rateSell'),
                date_rate=mono.get('date_rate'),
                provider=monobank_id
            )
            currencys.save()

    send_service = SendCurrency()
    send_service.send_custom_email()
    return render(request, 'index.html')
