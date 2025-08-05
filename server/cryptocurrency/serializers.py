from rest_framework import serializers
from .models import Currency, CurrencySubscription


class CurrencySerializer(serializers.ModelSerializer):
    """Serializer for Currency model"""
    
    class Meta:
        model = Currency
        fields = [
            'uuid', 'name', 'key', 'last_price', 
            'last_day_change', 'last_price_update', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['uuid', 'created_at', 'updated_at']


class CurrencySubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for CurrencySubscription model"""
    currency_name = serializers.CharField(source='currency.name', read_only=True)
    currency_key = serializers.CharField(source='currency.key', read_only=True)
    user_username = serializers.CharField(source='user.username', read_only=True)
    
    class Meta:
        model = CurrencySubscription
        fields = [
            'uuid', 'user', 'currency', 'currency_name', 'currency_key',
            'user_username', 'floor', 'ceiling', 'status', 
            'last_update', 'created_at'
        ]
        read_only_fields = ['uuid', 'user', 'last_update', 'created_at', 'user_username']

    def validate(self, data):
        """Validate that at least one of floor or ceiling is set"""
        floor = data.get('floor')
        ceiling = data.get('ceiling')
        
        if floor is None and ceiling is None:
            raise serializers.ValidationError(
                "At least one of 'floor' or 'ceiling' must be set."
            )
        
        if floor is not None and ceiling is not None:
            if floor >= ceiling:
                raise serializers.ValidationError(
                    "Floor price must be less than ceiling price."
                )
        
        return data


class CurrencySubscriptionCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating CurrencySubscription"""
    
    class Meta:
        model = CurrencySubscription
        fields = ['currency', 'floor', 'ceiling']

    def validate(self, data):
        """Validate that at least one of floor or ceiling is set"""
        floor = data.get('floor')
        ceiling = data.get('ceiling')
        
        if floor is None and ceiling is None:
            raise serializers.ValidationError(
                "At least one of 'floor' or 'ceiling' must be set."
            )
        
        if floor is not None and ceiling is not None:
            if floor >= ceiling:
                raise serializers.ValidationError(
                    "Floor price must be less than ceiling price."
                )
        
        return data

    def create(self, validated_data):
        """Create subscription with current user"""
        user = self.context['request'].user
        validated_data['user'] = user
        return super().create(validated_data)
