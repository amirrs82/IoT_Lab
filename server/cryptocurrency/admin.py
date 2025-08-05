from django.contrib import admin
from .models import Currency, CurrencySubscription


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
    list_display = ['user', 'currency', 'floor', 'ceiling', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'currency']
    search_fields = ['user__username', 'currency__name', 'currency__key']
    readonly_fields = ['uuid', 'created_at', 'last_update']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('uuid', 'user', 'currency')
        }),
        ('Alert Settings', {
            'fields': ('floor', 'ceiling', 'status')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'last_update'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'currency')
