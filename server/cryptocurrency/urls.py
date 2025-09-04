from django.urls import path
from cryptocurrency.views import (
    CurrencyListAPIView,
    CurrencyRetrieveAPIView,
    CurrencySubscriptionListAPIView,
    CurrencySubscriptionCreateAPIView,
    CurrencySubscriptionCancelAPIView,
    analyze_coin_turtle,
    analyze_coin_fvg,
)

app_name = 'cryptocurrency'

urlpatterns = [
    # Currency endpoints
    path('currencies/', CurrencyListAPIView.as_view(), name='currency-list'),
    path('currencies/<uuid:uuid>/', CurrencyRetrieveAPIView.as_view(), name='currency-detail'),
    
    # Currency subscription endpoints
    path('subscriptions/', CurrencySubscriptionListAPIView.as_view(), name='subscription-list'),
    path('subscriptions/create/', CurrencySubscriptionCreateAPIView.as_view(), name='subscription-create'),
    path('subscriptions/<uuid:uuid>/cancel/', CurrencySubscriptionCancelAPIView.as_view(), name='subscription-cancel'),
    path('analyze/turtle/', analyze_coin_turtle, name='analyze_coin_turtle'),
    path('analyze/fvg/', analyze_coin_fvg, name='analyze_coin_fvg'),
]
