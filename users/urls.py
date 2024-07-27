from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    UserRegistrationView,
    UserLoginView,
    UserProfileView,
    PasswordResetRequestView,
    PasswordResetConfirmView
)

urlpatterns = [
    # Регистрация нового пользователя
    path('register/', UserRegistrationView.as_view(), name='register'),

    # Вход пользователя (используя Simple JWT)
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Профиль пользователя
    path('profile/', UserProfileView.as_view(), name='user_profile'),

    # Сброс пароля
    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/confirm/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
]