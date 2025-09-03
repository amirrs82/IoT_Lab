from datetime import time, datetime
from io import BytesIO

from django.http import HttpResponse
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from matplotlib.pyplot import tight_layout, xticks, savefig, subplots
from cryptocurrency.models import Currency, CurrencySubscription
from cryptocurrency.scripts import get_historical_price_data, detect_structure_breaks, detect_turtle_soup, detect_ote
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
def analyze_coin(request):
    coin = Currency.objects.get(uuid=request.data['coin_id'])
    duration = request.data['duration']
    step = request.data['step']
    end_time = int(datetime.now().timestamp())
    start_time = end_time - duration

    print("\nFetching historical data...")
    raw = get_historical_price_data(coin, start_time, end_time, step)
    if "error" in raw:
        print("Error fetching price data:", raw["error"])
        return

    candles = [
        {"timestamp": itm["start_time"], "open": itm["open"], "high": itm["max"],
         "low": itm["min"], "close": itm["close"]}
        for itm in raw if all(v is not None for v in [itm["open"], itm["close"], itm["min"], itm["max"]])
    ]
    times = [c["timestamp"] / 1000 for c in candles]  # Convert timestamps to seconds
    close_prices = [c["close"] for c in candles]
    if not candles:
        print("No valid candle data found.")
        return

    print(f"Processed {len(candles)} candles.")

    structure = detect_structure_breaks(candles)

    # Detect Turtle Soup signals
    turtle_soup_signals = detect_turtle_soup(candles)

    # Detect OTE zones
    ote_zones = detect_ote(candles, structure)

    # Create the plot
    fig, ax = subplots(figsize=(10, 6))

    # Plot the closing prices
    ax.plot(times, close_prices, label="Close Price", color='blue')

    # Plot Turtle Soup Signals
    for signal in turtle_soup_signals:
        if signal["type"] == "bullish_turtle_soup":
            ax.scatter(times[signal["index"]], candles[signal["index"]]["close"], color='green',
                       label='Bullish Turtle Soup', zorder=5)
        elif signal["type"] == "bearish_turtle_soup":
            ax.scatter(times[signal["index"]], candles[signal["index"]]["close"], color='red',
                       label='Bearish Turtle Soup', zorder=5)

    # Plot OTE Zones
    for zone in ote_zones:
        if zone["type"] == "bullish_ote":
            ax.axvline(x=times[zone["index"]], color='green', linestyle='--', label='Bullish OTE Entry')
        elif zone["type"] == "bearish_ote":
            ax.axvline(x=times[zone["index"]], color='red', linestyle='--', label='Bearish OTE Entry')

    # Labeling
    ax.set_xlabel("Time")
    ax.set_ylabel("Price (USD)")
    ax.set_title("Bitcoin Price with Turtle Soup and OTE Signals")
    ax.legend(loc='best')

    # Rotate x-axis labels to avoid overlap
    xticks(rotation=45)
    tight_layout()

    # Convert plot to image and return as response
    buf = BytesIO()
    savefig(buf, format='png')
    buf.seek(0)
    return HttpResponse(buf, content_type="image/png")
