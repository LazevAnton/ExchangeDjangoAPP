from django.shortcuts import render

from DjangoAPP.services import ExchangePrivate24Service


def index(request):
    privatbank = ExchangePrivate24Service()
    data = privatbank.get_data()
    print(data)
    return render(request, 'index.html')
