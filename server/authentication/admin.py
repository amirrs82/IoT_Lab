from django.contrib import admin
from authentication.models import VerificationCode


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    """Admin configuration for VerificationCode model"""
    list_display = ['email', 'username', 'verification_code', 'created_at', 'expires_at']
    list_filter = ['created_at', 'expires_at']
    search_fields = ['email', 'username']
    readonly_fields = ['id', 'created_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'username', 'email')
        }),
        ('Personal Information', {
            'fields': ('first_name', 'last_name', 'password')
        }),
        ('Verification', {
            'fields': ('verification_code', 'expires_at')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
