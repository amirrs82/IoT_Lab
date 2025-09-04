from datetime import datetime
from io import BytesIO

from django.http import HttpResponse
from matplotlib.pyplot import savefig
from rest_framework import generics, status
from rest_framework.decorators import permission_classes, api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from cryptocurrency.models import Currency, CurrencySubscription
from cryptocurrency.scripts import detect_fvg, detect_turtle_soup, get_historical_price_data, plot_ict_chart, \
    get_candles, get_time_format
from cryptocurrency.serializers import (
    CurrencySerializer,
    CurrencySubscriptionSerializer,
    CurrencySubscriptionCreateSerializer
)


class CurrencyListAPIView(generics.ListAPIView):
    """API view to list all currencies"""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]


class CurrencyRetrieveAPIView(generics.RetrieveAPIView):
    """API view to retrieve a specific currency by UUID"""
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'


class CurrencySubscriptionListAPIView(generics.ListAPIView):
    """API view to list current user's currency subscriptions"""
    serializer_class = CurrencySubscriptionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return CurrencySubscription.objects.filter(
            user=self.request.user
        ).select_related('currency', 'user')


class CurrencySubscriptionCreateAPIView(generics.CreateAPIView):
    """API view to create a new currency subscription"""
    serializer_class = CurrencySubscriptionCreateSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        subscription = serializer.save()

        # Return the created subscription with full details
        response_serializer = CurrencySubscriptionSerializer(subscription)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CurrencySubscriptionCancelAPIView(generics.UpdateAPIView):
    """API view to cancel a currency subscription"""
    serializer_class = CurrencySubscriptionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'uuid'

    def get_queryset(self):
        return CurrencySubscription.objects.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        subscription = self.get_object()

        # Only allow cancelling if status is 'waiting'
        if subscription.status != CurrencySubscription.StatusChoices.WAITING:
            return Response(
                {'error': 'Only waiting subscriptions can be cancelled'},
                status=status.HTTP_400_BAD_REQUEST
            )

        subscription.status = CurrencySubscription.StatusChoices.CANCELLED
        subscription.save()

        serializer = self.get_serializer(subscription)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_coin_turtle(request):
    coin_obj = Currency.objects.get(uuid=request.data['coin_id'])
    coin = coin_obj.key
    duration = request.data['duration']
    step = request.data['step']
    end_time = int(datetime.now().timestamp())
    start_time = end_time - duration

    raw = get_historical_price_data(coin, start_time, end_time, step)
    candles = get_candles(raw)

    format = get_time_format(duration)
    turtle = detect_turtle_soup(candles)
    plt = plot_ict_chart(candles, format, turtle)

    # Convert plot to image and return as response
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type="image/png")


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyze_coin_fvg(request):
    coin_obj = Currency.objects.get(uuid=request.data['coin_id'])
    coin = coin_obj.key
    duration = request.data['duration']
    step = request.data['step']
    end_time = int(datetime.now().timestamp())
    start_time = end_time - duration

    raw = get_historical_price_data(coin, start_time, end_time, step)
    candles = get_candles(raw)

    format = get_time_format(duration)
    fvg = detect_fvg(candles)
    plt = plot_ict_chart(candles, format, fvg)

    # Convert plot to image and return as response
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type="image/png")


