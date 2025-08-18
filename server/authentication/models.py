from django.db import models
import uuid


class VerificationCode(models.Model):
    """Model to store email verification codes for user registration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)  # Will store hashed password
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    verification_code = models.CharField(max_length=8)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.email} - {self.verification_code}"
