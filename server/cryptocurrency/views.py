from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import Currency, CurrencySubscription
from .serializers import (
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
