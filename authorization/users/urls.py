from drf_yasg import openapi
from rest_framework import permissions
from django.urls import path, re_path
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .endpoints import UserEmailAPIView, VerifyEmailAPIView, UserUpdateAPIView, UserSetPasswordAPIView, ResetPasswordAPIView, ResetPasswordConfirmAPIView


schema_view = get_schema_view(
   openapi.Info(
      title="Neobis authorization API",
      default_version='v1',
      description="Description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)


urlpatterns = [
    path('api/register/email/', UserEmailAPIView.as_view(), name='email'),
    path("api/register/email/verify/", VerifyEmailAPIView.as_view(), name="email_verify"),
    path("api/register/", UserUpdateAPIView.as_view(), name="register"),
    path("api/register/set_password/", UserSetPasswordAPIView.as_view(), name="set_password"),
    path("api/register/reset_password/", ResetPasswordAPIView.as_view(), name="reset_password"),
    path("api/register/reset_password/confirm/", ResetPasswordConfirmAPIView.as_view(), name="reset_password_confirm"),
    path('api/token/', TokenObtainPairView.as_view(), name='jwt_create'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    re_path(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]
