from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.hashers import make_password
from authentication.models import VerificationCode
import random
import string
from datetime import timedelta


def generate_verification_code():
    """Generate a random 8-digit verification code"""
    return ''.join(random.choices(string.digits, k=8))


@api_view(['POST'])
@permission_classes([AllowAny])
def request_verification(request):
    """
    Request verification code for user registration
    
    Creates a verification object with user data and sends verification code via email.
    If verification object with same email exists, it gets deleted and replaced.
    """
    try:
        username = request.data.get('username')
        email = request.data.get('email')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Validate required fields
        if not all([username, email, password, first_name, last_name]):
            return Response(
                {'error': 'Username, email, password, first name, and last name are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if email already exists in User model
        if User.objects.filter(email=email).exists():
            return Response(
                {'error': 'Email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Delete existing verification object with same email if exists
        VerificationCode.objects.filter(email=email).delete()
        
        # Generate verification code
        verification_code = generate_verification_code()
        
        # Set expiration time (15 minutes from now)
        expires_at = timezone.now() + timedelta(minutes=15)
        
        # Create verification object
        verification_obj = VerificationCode.objects.create(
            username=username,
            email=email,
            password=make_password(password),
            first_name=first_name,
            last_name=last_name,
            verification_code=verification_code,
            expires_at=expires_at
        )
        
        # Prepare the email
        subject = 'Your Account Confirmation Code'
        message = f'Hi {username},\n\nThank you for registering. Your confirmation code is: {verification_code}\n\nBest regards.'
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [email]

        # Send the email
        try:
            send_mail(subject, message, from_email, recipient_list)
            return Response({
                'message': 'Verification code sent successfully',
                'email': email
            }, status=status.HTTP_200_OK)
        except Exception as email_error:
            # Delete the verification object if email fails
            verification_obj.delete()
            return Response(
                {'error': f'Failed to send verification email: {str(email_error)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    """
    User registration endpoint with email verification
    
    Validates verification code and creates user account if verification is successful.
    """
    try:
        email = request.data.get('email')
        verification_code = request.data.get('verification_code')
        
        if not all([email, verification_code]):
            return Response(
                {'error': 'Email and verification code are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Find verification object
        try:
            verification_obj = VerificationCode.objects.get(email=email)
        except VerificationCode.DoesNotExist:
            return Response(
                {'error': 'No verification request found for this email'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if verification code matches
        if verification_obj.verification_code != verification_code:
            return Response(
                {'error': 'Invalid verification code'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if verification code has expired
        if timezone.now() > verification_obj.expires_at:
            verification_obj.delete()  # Clean up expired verification
            return Response(
                {'error': 'Verification code has expired. Please request a new one.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if username or email already exists (double check)
        if User.objects.filter(username=verification_obj.username).exists():
            return Response(
                {'error': 'Username already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(email=verification_obj.email).exists():
            return Response(
                {'error': 'Email already exists'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user from verification object
        user = User.objects.create(
            username=verification_obj.username,
            email=verification_obj.email,
            password=verification_obj.password,  # Already hashed
            first_name=verification_obj.first_name,
            last_name=verification_obj.last_name
        )
        
        # Delete verification object after successful registration
        verification_obj.delete()
        
        # Create token for immediate login
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'message': 'User created successfully',
            'token': token.key,
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login endpoint"""
    try:
        username = request.data.get('username')
        password = request.data.get('password')
        
        if not all([username, password]):
            return Response(
                {'error': 'Username and password are required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = authenticate(username=username, password=password)
        
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'user_id': user.id,
                'username': user.username
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
            
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout endpoint"""
    try:
        request.user.auth_token.delete()
        return Response(
            {'message': 'Logout successful'}, 
            status=status.HTTP_200_OK
        )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def profile(request):
    """
    Get or update user profile
    
    Note: Email cannot be changed after registration (enforced at application level).
    Only first_name and last_name can be updated.
    """
    try:
        user = request.user
        
        if request.method == 'GET':
            return Response({
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'date_joined': user.date_joined,
                'is_active': user.is_active
            }, status=status.HTTP_200_OK)
            
        elif request.method == 'PUT':
            # Check if email change is attempted (not allowed)
            if 'email' in request.data and request.data['email'] != user.email:
                return Response(
                    {'error': 'Email cannot be changed'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Update user information (email cannot be changed)
            user.first_name = request.data.get('first_name', user.first_name)
            user.last_name = request.data.get('last_name', user.last_name)
            
            # Validate required fields
            if not user.first_name or not user.last_name:
                return Response(
                    {'error': 'First name and last name are required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user.save()
            
            return Response({
                'message': 'Profile updated successfully',
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name
            }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
