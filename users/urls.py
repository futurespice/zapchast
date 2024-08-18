from django.urls import path
from .views import (
    UserRegistrationInitView,
    UserRegistrationVerifyView,
    UserLoginView,
    PasswordResetRequestView,
    PasswordResetConfirmView,
    UserProfileView
)

urlpatterns = [
    path('register/', UserRegistrationInitView.as_view(), name='register_init'),
    path('verify/', UserRegistrationVerifyView.as_view(), name='register_verify'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('profile/', UserProfileView.as_view(), name='user_profile'),
]