from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from django.contrib.auth.password_validation import validate_password

from .models import User


class UserEmailSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["email"]


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=555)

    class Meta:
        model = User
        fields = ["token"]


class UserCreateSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False)
    last_name = serializers.CharField(required=False)
    birth_date = serializers.DateField(required=False)
    # Add any other fields you want to update

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.birth_date = validated_data.get('birth_date', instance.birth_date)
        # Update any other fields as needed
        instance.save()
        return instance


class UserSetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data['password'])
        instance.save()
        return instance
