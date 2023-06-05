from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .endpoints import UserEmailAPIView, VerifyEmailAPIView, UserUpdateAPIView, UserSetPasswordAPIView, ResetPasswordAPIView, ResetPasswordConfirmAPIView

urlpatterns = [
    path('api/register/email/', UserEmailAPIView.as_view(), name='email'),
    path("api/register/email/verify/", VerifyEmailAPIView.as_view(), name="email_verify"),
    path("api/register/", UserUpdateAPIView.as_view(), name="register"),
    path("api/register/set_password/", UserSetPasswordAPIView.as_view(), name="set_password"),
    path("api/register/reset_password/", ResetPasswordAPIView.as_view(), name="reset_password"),
    path("api/register/reset_password/confirm/", ResetPasswordConfirmAPIView.as_view(), name="reset_password_confirm"),
    path('api/token/', TokenObtainPairView.as_view(), name='jwt_create'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
