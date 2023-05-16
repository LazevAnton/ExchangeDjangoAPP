import requests
from datetime import datetime, timedelta


class ExchangePrivate24Service:
    URL_API = 'https://api.privatbank.ua/p24api/exchange_rates'
    CURRENCY = ['USD', 'GBP', 'EUR', 'CHF']
    # PARAMS = {
    #     'date': '03.01.2023'
    # }

    def get_data(self):
        begin_date = datetime(2023, 5, 1).date()
        current_date = datetime.now().date()

        currency_date = []
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
                    currency_date.append(
                        {
                            'base_currency': baseCurrency,
                            'currency': currency['currency'],
                            'sale_rate': currency['saleRateNB'],
                            'buy_rate': currency['purchaseRateNB'],
                            'date': date
                        }
                    )
            begin_date += timedelta(days=1)
        return currency_date

# class ExchangeMonoBankService:
#     URL_API = 'https://api.privatbank.ua/p24api/exchange_rates'
#     CURRENCY = ['USD', 'GBP', 'EUR', 'CHF']
#     PARAMS = {
#         'date': '14.05.2023'
#     }
