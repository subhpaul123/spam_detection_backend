from rest_framework import serializers
from django.contrib.auth import get_user_model, password_validation
from django.core import exceptions as django_exceptions
from .models import Contact, SpamReport

User = get_user_model()

class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})
    password2 = serializers.CharField(write_only=True, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('username', 'phone_number', 'email', 'password', 'password2')
        extra_kwargs = {'username': {'required': True}}

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            phone_number=validated_data['phone_number'],
            email=validated_data.get('email', '')
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(style={'input_type': 'password'})

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'email')
        read_only_fields = ('phone_number',)

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = ['id', 'name', 'phone_number'] 
        read_only_fields = ['id'] 
    def create(self, validated_data):
        return Contact.objects.create(**validated_data)

class SpamReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpamReport
        fields = ('phone_number',)

class SearchResultSerializer(serializers.Serializer):
    name = serializers.CharField()
    phone_number = serializers.CharField()
    spam_likelihood = serializers.FloatField()

class UserDetailSerializer(serializers.ModelSerializer):
    spam_likelihood = serializers.FloatField(read_only=True)
    email = serializers.EmailField(read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'phone_number', 'email', 'spam_likelihood')
        read_only_fields = ('phone_number',)