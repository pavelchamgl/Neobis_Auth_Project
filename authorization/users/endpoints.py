import jwt
from django.urls import reverse
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated, AllowAny

from .utils import Util
from .models import User
from authorization import settings
from .serializers import (
    UserEmailSerializer,
    EmailVerificationSerializer,
    UserCreateSerializer,
    UserSetPasswordSerializer,
    ForgotPasswordSerializer,
)


class UserEmailAPIView(APIView):
    serializer_class = UserEmailSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=UserEmailSerializer,
        operation_description="This endpoint set email for user.",
        responses={201: 'Confirm your email by clicking on the link from the email', 400: 'Bad Request'}
    )
    def post(self, request, *args, **kwargs):
        serializer = UserEmailSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            user_data = serializer.data

            user = User.objects.get(email=user_data["email"])
            token = RefreshToken.for_user(user)
            current_site = request.get_host()
            link = reverse("email_verify")
            url = "http://" + current_site + link + "?token=" + str(token.access_token)
            body = "Hi " + " Use the link below to verify your email \n" + url
            data = {
                "email_body": body,
                "to_email": user.email,
                "email_subject": "Verify your email",
            }

            Util.send_email(data)
            return Response(
                {'message': 'Confirm your email by clicking on the link from the email'}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors)


class VerifyEmailAPIView(APIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        query_serializer=EmailVerificationSerializer,
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_QUERY, description='Verification token', type=openapi.TYPE_STRING)
        ],
        operation_description="This endpoint verify email user.",
        responses={200: 'User updated successfully', 400: 'Bad Request', 404: 'Not Found'}
    )
    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response(
                {"error": "Token is not provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=payload["user_id"])
            if not user:
                return Response(
                    {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )
            if not user.is_verified:
                user.is_verified = True
                user.save()
                return Response(
                    {"message": "Successfully activated"}, status=status.HTTP_200_OK
                )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Activation Expired"}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST
            )


class UserUpdateAPIView(APIView):
    permission_classes = (IsAuthenticated,)  # Requires authentication

    @swagger_auto_schema(
        request_body=UserCreateSerializer,
        operation_description="This endpoint set first name, last name and birthday for user.",
        responses={200: 'User updated successfully', 400: 'Bad Request'}
    )
    def put(self, request):
        user = request.user  # Retrieve the authenticated user
        # Initialize the serializer with the user object and request data
        serializer = UserCreateSerializer(user, data=request.data)
        # Validate and update the user data
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSetPasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=EmailVerificationSerializer,
        operation_description="This endpoint set password for user.",
        responses={200: 'User set password successfully', 400: 'Bad Request'}
    )
    def put(self, request):
        user = request.user  # Retrieve the authenticated user
        # Initialize the serializer with the user object and request data
        serializer = UserSetPasswordSerializer(user, data=request.data)
        # Validate and update the user data
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User set password successfully'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResetPasswordAPIView(APIView):
    serializer_class = UserEmailSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=UserEmailSerializer,
        operation_description="This endpoint send email for reset password.",
        responses={200: 'Reset your password by clicking on the link from the email', 400: 'Bad Request'}
    )
    def post(self, request, *args, **kwargs):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = User.objects.get(email=request.data["email"])
        token = RefreshToken.for_user(user)
        current_site = request.get_host()
        link = reverse("reset_password_confirm")
        url = "http://" + current_site + link + "?token=" + str(token.access_token)
        body = "Hi " + " Use the link below to reset your password \n" + url
        data = {
            "email_body": body,
            "to_email": user.email,
            "email_subject": "Reset your password",
        }

        Util.send_email(data)
        return Response(
            {'message': 'Reset your password by clicking on the link from the email'}, status=status.HTTP_200_OK
        )


class ResetPasswordConfirmAPIView(APIView):
    serializer_class = EmailVerificationSerializer
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        query_serializer=EmailVerificationSerializer,
        manual_parameters=[
            openapi.Parameter('token', openapi.IN_QUERY, description='Reset password token', type=openapi.TYPE_STRING)
        ],
        operation_description="This endpoint verify email for reset password.",
        responses={200: 'Successfully link verify.', 400: 'Bad Request', 404: 'Not Found'}
    )
    def get(self, request):
        token = request.GET.get("token")
        if not token:
            return Response(
                {"error": "Token is not provided."}, status=status.HTTP_400_BAD_REQUEST
            )
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
            user = User.objects.get(id=payload["user_id"])
            if not user:
                return Response(
                    {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
                )

            return Response(
                {"message": "Successfully link verify."}, status=status.HTTP_200_OK
            )
        except jwt.ExpiredSignatureError:
            return Response(
                {"error": "Reset password expired."}, status=status.HTTP_400_BAD_REQUEST
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"error": "Invalid token."}, status=status.HTTP_400_BAD_REQUEST
            )
