from django.urls import path
from authentication import views

urlpatterns = [
    path('request-verification/', views.request_verification, name='request_verification'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
]
