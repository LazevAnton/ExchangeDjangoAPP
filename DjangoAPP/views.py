from django.shortcuts import render
from DjangoAPP.services import ExchangePrivate24Service, ExchangeMonoBankService, SendCurrency


def index(request):
    privatbank = ExchangePrivate24Service()
    privatbank.get_data_thread_pool_executor()
    monobank = ExchangeMonoBankService()
    monobank.get_data()
    send_service = SendCurrency()
    send_service.send_custom_email()
    return render(request, 'index.html')
