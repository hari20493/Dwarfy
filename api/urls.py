from django.urls import path
from django.views.decorators.csrf import csrf_exempt

from api.views import shortner, Report, search

urlpatterns = [
    path('shorten/', csrf_exempt(shortner.as_view())),
    path('reports/<slug>', (Report.as_view())),
    path('search/', (search)),
]
