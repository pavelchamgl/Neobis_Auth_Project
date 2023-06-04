import jwt
from django.urls import reverse
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
    UserSetPasswordSerializer
)


class UserEmailAPIView(APIView):
    serializer_class = UserEmailSerializer
    permission_classes = (AllowAny,)

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

    def put(self, request):
        user = request.user  # Retrieve the authenticated user
        # Initialize the serializer with the user object and request data
        serializer = UserCreateSerializer(user, data=request.data)
        # Validate and update the user data
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User updated successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserSetPasswordAPIView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        user = request.user  # Retrieve the authenticated user
        # Initialize the serializer with the user object and request data
        serializer = UserSetPasswordSerializer(user, data=request.data)
        # Validate and update the user data
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'User set password successfully'})
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
