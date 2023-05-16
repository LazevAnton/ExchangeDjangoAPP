import requests
from datetime import datetime, timedelta

from DjangoAPP.models import ExchangeProviders
from pycountrycodes import currencies


class ExchangePrivate24Service:
    URL_API = 'https://api.privatbank.ua/p24api/exchange_rates'
    CURRENCY = ['USD', 'GBP', 'EUR', 'CHF']

    # PARAMS = {
    #     'date': '03.01.2023'
    # }

    def get_data(self):
        begin_date = datetime(2023, 1, 2).date()
        current_date = datetime.now().date()
        PROVIDER = ExchangeProviders.objects.filter(provider_name='PriVatBank').first()
        if PROVIDER is None:
            PROVIDER = ExchangeProviders(provider_name='PriVatBank', provider_api_url=f'{self.URL_API}')
            PROVIDER.save()
        currency_data = []
        while begin_date <= current_date:
            date_str = begin_date.strftime('%d.%m.%Y')
            params = {'date': date_str}
            req = requests.get(self.URL_API, params=params)
            req_data = req.json()
            baseCurrency = req_data['baseCurrencyLit']
            date = req_data['date']

            for currency in req_data['exchangeRate']:
                if currency['currency'] not in self.CURRENCY:
                    continue
                else:
                    currency_data.append(
                        {
                            'base_currency': baseCurrency,
                            'currency': currency['currency'],
                            'sale_rate': currency['saleRateNB'],
                            'buy_rate': currency['purchaseRateNB'],
                            'date': date
                        }
                    )
            begin_date += timedelta(days=1)
        return currency_data


class ExchangeMonoBankService:
    URL_API = 'https://api.monobank.ua/bank/currency'
    CURRENCY = ['USD', 'GBP', 'EUR', 'CHF']

    def ConvertIsoCurrency(self, code: int):
        number = currencies.get(numeric=str(code))
        return number.alpha_3

    def get_data(self):
        """
        elif data['rateBuy'] < 2.000 or data['rateSell'] < 2.000:
            Монобанк в APi возвращает как я понял разницу между курсом НБУ и курсом самого банка
            посколько эта информация не нужна то ее исключаем из массива, а так убирается все где
            в API банка курсы покупки и продажи равны нулю такое встречается на паре UAH/GBP
            этой парой Монобанк не торгует, а в задаче было сказано получать курс фунта, если данных
            нет то зачем им быть в базе
        """
        req = requests.get(self.URL_API)
        response = req.json()
        baseCurrency = self.ConvertIsoCurrency(response[0]['currencyCodeB'])
        PROVIDER = ExchangeProviders.objects.filter(provider_name='MonoBank').first()
        if PROVIDER is None:
            PROVIDER = ExchangeProviders(provider_name='MonoBank', provider_api_url=f'{self.URL_API}')
            PROVIDER.save()
        currency_data = []
        for data in response:
            if data['currencyCodeA'] == 8 or data['currencyCodeA'] == 51:
                continue
            elif data['rateBuy'] < 2.000 or data['rateSell'] < 2.000:
                continue
            elif self.ConvertIsoCurrency(data['currencyCodeA']) not in self.CURRENCY:
                continue
            else:
                currency_data.append(
                    {
                        'baseCurrency': baseCurrency,
                        'currency': self.ConvertIsoCurrency(data['currencyCodeA']),
                        'rateBuy': data['rateBuy'],
                        'rateSell': data['rateSell']
                    }
                )
        return currency_data
