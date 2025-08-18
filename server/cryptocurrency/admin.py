from django.contrib import admin
from django import forms
from cryptocurrency.models import Currency, CurrencySubscription


class CurrencySubscriptionAdminForm(forms.ModelForm):
    """Custom form for CurrencySubscription admin with enhanced help text"""
    
    class Meta:
        model = CurrencySubscription
        fields = '__all__'
        help_texts = {
            'floor': 'Alert when price drops below this value. Cannot be set if ceiling is set.',
            'ceiling': 'Alert when price rises above this value. Cannot be set if floor is set.',
            'status': 'WAITING: subscription is active and monitoring price. DONE: alert has been sent. CANCELLED: subscription was cancelled.',
        }
    
    def clean(self):
        cleaned_data = super().clean()
        floor = cleaned_data.get('floor')
        ceiling = cleaned_data.get('ceiling')
        
        if floor is None and ceiling is None:
            raise forms.ValidationError("Exactly one of 'floor' or 'ceiling' must be set.")
        
        if floor is not None and ceiling is not None:
            raise forms.ValidationError("Cannot set both 'floor' and 'ceiling'. Choose only one.")
        
        return cleaned_data


@admin.register(Currency)
class CurrencyAdmin(admin.ModelAdmin):
    """Admin configuration for Currency model"""
    list_display = ['name', 'key', 'last_price', 'last_day_change', 'last_price_update', 'created_at']
    list_filter = ['created_at', 'last_price_update']
    search_fields = ['name', 'key']
    readonly_fields = ['uuid', 'created_at', 'updated_at']
    ordering = ['name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'name', 'key')
        }),
        ('Price Information', {
            'fields': ('last_price', 'last_day_change', 'last_price_update')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CurrencySubscription)
class CurrencySubscriptionAdmin(admin.ModelAdmin):
    """Admin configuration for CurrencySubscription model"""
    form = CurrencySubscriptionAdminForm
    list_display = ['user', 'currency', 'get_threshold_type', 'get_threshold_value', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'currency']
    search_fields = ['user__username', 'currency__name', 'currency__key']
    readonly_fields = ['uuid', 'created_at', 'last_update']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'user', 'currency')
        }),
        ('Alert Settings', {
            'fields': ('floor', 'ceiling', 'status'),
            'description': 'Set exactly ONE threshold: either floor OR ceiling (not both). '
                          'Floor: alerts when price drops below this value. '
                          'Ceiling: alerts when price rises above this value.'
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_update'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'currency')
    
    def get_threshold_type(self, obj):
        """Display the type of threshold set"""
        if obj.floor is not None:
            return "Floor"
        elif obj.ceiling is not None:
            return "Ceiling"
        return "None"
    get_threshold_type.short_description = "Threshold Type"
    
    def get_threshold_value(self, obj):
        """Display the threshold value"""
        if obj.floor is not None:
            return f"${obj.floor}"
        elif obj.ceiling is not None:
            return f"${obj.ceiling}"
        return "No threshold set"
    get_threshold_value.short_description = "Threshold Value"
