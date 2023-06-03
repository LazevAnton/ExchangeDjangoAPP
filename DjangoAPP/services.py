import os
from django.db import transaction
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
        privatbank, create = ExchangeProviders.objects.get_or_create(provider_name='PrivatBank',
                                                                     provider_api_url=self.URL_API)
        date = req_data['date']
        for currency in req_data['exchangeRate']:
            if currency['currency'] not in self.CURRENCY:
                continue

            exist = ExchangeRates.objects.filter(
                currency=currency['currency'],
                date_rate=date,
                provider_id=privatbank.id
            ).exists()

            if not exist:
                rates = ExchangeRates(
                    base_currency=baseCurrency,
                    currency=currency['currency'],
                    sale_rate=currency['saleRateNB'],
                    buy_rate=currency['purchaseRate'],
                    date_rate=date,
                    provider_id=privatbank.id
                )
                self.currency_data.append(rates)

    def get_data_thread_pool_executor(self):
        begin_date = datetime(2023, 6, 1).date()
        end_date = datetime.now().date()
        date_range = [begin_date + timedelta(days=i) for i in range((end_date - begin_date).days + 1)]

        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            executor.map(self.get_data, date_range)
        with transaction.atomic():
            ExchangeRates.objects.bulk_create(self.currency_data)


class ExchangeMonoBankService:
    URL_API = 'https://api.monobank.ua/bank/currency'
    CURRENCY = ['USD', 'GBP', 'EUR', 'CHF']

    def get_convert_iso_currency(self, code: int):
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
        baseCurrency = self.get_convert_iso_currency(response[0]['currencyCodeB'])
        monobank, create = ExchangeProviders.objects.get_or_create(provider_name='MonoBank',
                                                                   provider_api_url=self.URL_API)
        currency_data = []
        for data in response:
            if data['currencyCodeA'] == 8 or data['currencyCodeA'] == 51:
                continue
            elif data['rateBuy'] < 2.000 or data['rateSell'] < 2.000:
                continue
            elif self.get_convert_iso_currency(data['currencyCodeA']) not in self.CURRENCY:
                continue
            else:
                exist = ExchangeRates.objects.filter(
                    currency=self.get_convert_iso_currency(data['currencyCodeA']),
                    date_rate=datetime.fromtimestamp(data['date']).strftime("%d.%m.%Y"),
                    provider_id=monobank.id
                ).exists()

                if not exist:
                    rates = ExchangeRates(
                        base_currency=baseCurrency,
                        currency=self.get_convert_iso_currency(data['currencyCodeA']),
                        sale_rate=data['rateBuy'],
                        buy_rate=data['rateSell'],
                        date_rate=datetime.fromtimestamp(data['date']).strftime("%d.%m.%Y"),
                        provider_id=monobank.id
                    )
                    currency_data.append(rates)
        ExchangeRates.objects.bulk_create(currency_data)

