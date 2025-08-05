import uuid
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class Currency(models.Model):
    """Cryptocurrency model to store currency information"""
    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    key = models.CharField(max_length=20, unique=True, help_text="Symbol used to get price from Binance")
    last_price = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True)
    last_day_change = models.FloatField(null=True, blank=True, help_text="Daily change percentage (can be positive or negative)")
    last_price_update = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Currency"
        verbose_name_plural = "Currencies"
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.key})"


class CurrencySubscription(models.Model):
    """Subscription model for users to track currency price changes"""
    
    class StatusChoices(models.TextChoices):
        WAITING = 'waiting', 'Waiting'
        DONE = 'done', 'Done'
        CANCELLED = 'cancelled', 'Cancelled'

    uuid = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='currency_subscriptions')
    currency = models.ForeignKey(Currency, on_delete=models.CASCADE, related_name='subscriptions')
    floor = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, help_text="Alert when price goes below this value")
    ceiling = models.DecimalField(max_digits=20, decimal_places=8, null=True, blank=True, help_text="Alert when price goes above this value")
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.WAITING)
    last_update = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Currency Subscription"
        verbose_name_plural = "Currency Subscriptions"
        ordering = ['-created_at']

    def clean(self):
        """Validate that at least one of floor or ceiling is set"""
        if self.floor is None and self.ceiling is None:
            raise ValidationError("At least one of 'floor' or 'ceiling' must be set.")
        
        if self.floor is not None and self.ceiling is not None:
            if self.floor >= self.ceiling:
                raise ValidationError("Floor price must be less than ceiling price.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} - {self.currency.name} ({self.status})"
