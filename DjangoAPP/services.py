import os

import requests
from datetime import datetime, timedelta

from DjangoAPP.models import ExchangeProviders, ExchangeRates
from pycountrycodes import currencies
import pandas as pd
import concurrent.futures
import requests
from datetime import datetime, timedelta

from django.core.mail import EmailMessage
from django.conf import settings


class SendCurrency:
    def send_custom_email(self):
        current_rate = self.get_current_rate()
        df = pd.DataFrame.from_dict(current_rate)
        today = datetime.today().strftime('%d-%m-%Y')
        file = f'{today}.csv'
        file_path = os.path.join(settings.BASE_DIR, file)
        df.to_csv(file_path, index=False)

        email = EmailMessage(
            subject=f'Курс валют на {today}',
            body='Приветствую! Файл во вложении.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=['lazev.anton@gmail.com'],
        )
        email.attach_file(file_path)
        email.send()
        os.remove(file_path)

    def get_current_rate(self):
        current_rate = []
        today = datetime.today().strftime('%d.%m.%Y')
        data = ExchangeRates.objects.filter(date_rate=today).all()
        for ex in data:
            base_currency = ex.base_currency
            currency = ex.currency
            sale = ex.sale_rate
            buy = ex.buy_rate
            date = ex.date_rate
            provider = ex.provider.provider_name
            current_rate.append(
                {
                    'Bank': provider,
                    'BaseCurrency': base_currency,
                    'Currency': currency,
                    'Sale': str(sale),
                    'Buy': str(buy),
                    'Date': date
                }
            )
        return current_rate


class ExchangePrivate24Service:
    URL_API = 'https://api.privatbank.ua/p24api/exchange_rates'
    CURRENCY = ['USD', 'GBP', 'EUR', 'CHF']

    def __init__(self):
        self.currency_data = []

    def get_data(self, date):
        date_str = date.strftime('%d.%m.%Y')
        params = {'date': date_str}
        req = requests.get(self.URL_API, params=params)
        req_data = req.json()
        baseCurrency = req_data['baseCurrencyLit']
        date = req_data['date']

        for currency in req_data['exchangeRate']:
            if currency['currency'] not in self.CURRENCY:
                continue
            else:
                self.currency_data.append(
                    {
                        'base_currency': baseCurrency,
                        'currency': currency['currency'],
                        'sale_rate': currency['saleRateNB'],
                        'buy_rate': currency['purchaseRate'],
                        'date': date
                    }
                )

    def get_data_ThreadPoolExecutor(self):
        begin_date = datetime(2023, 5, 1).date()
        end_date = datetime.now().date()
        date_range = [begin_date + timedelta(days=i) for i in range((end_date - begin_date).days + 1)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.get_data, date_range)
        return self.currency_data


# class ExchangePrivate24Service:
#     URL_API = 'https://api.privatbank.ua/p24api/exchange_rates'
#     CURRENCY = ['USD', 'GBP', 'EUR', 'CHF']
#
#
#     def get_data(self):
#         begin_date = datetime(2023, 1, 2).date()
#         current_date = datetime.now().date()
#         PROVIDER = ExchangeProviders.objects.filter(provider_name='PriVatBank').first()
#         if PROVIDER is None:
#             PROVIDER = ExchangeProviders(provider_name='PriVatBank', provider_api_url=f'{self.URL_API}')
#             PROVIDER.save()
#         currency_data = []
#         while begin_date <= current_date:
#             date_str = begin_date.strftime('%d.%m.%Y')
#             params = {'date': date_str}
#             req = requests.get(self.URL_API, params=params)
#             req_data = req.json()
#             baseCurrency = req_data['baseCurrencyLit']
#             date = req_data['date']
#
#             for currency in req_data['exchangeRate']:
#                 if currency['currency'] not in self.CURRENCY:
#                     continue
#                 else:
#                     currency_data.append(
#                         {
#                             'base_currency': baseCurrency,
#                             'currency': currency['currency'],
#                             'sale_rate': currency['saleRateNB'],
#                             'buy_rate': currency['purchaseRate'],
#                             'date': date
#                         }
#                     )
#             begin_date += timedelta(days=1)
#         return currency_data
#
#
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
            поскольку эта информация не нужна то ее исключаем из массива, а так же убираеться все где
            в API банка курсы покупки и продажи равны нулю, такое встречается на паре UAH/GBP
            этой парой Монобанк не торгует, а в задаче было сказано получать курс фунта, если данных
            нет то зачем им быть в базе?😎
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
                        'rateSell': data['rateSell'],
                        'date_rate': datetime.fromtimestamp(data['date']).strftime("%d.%m.%Y")
                    }
                )
        return currency_data
