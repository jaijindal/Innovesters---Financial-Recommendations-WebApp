from rest_framework import serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from UserApp.models import UserProfile
from uuid import uuid4
from os import path

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['phone_number', 'address']

class UserSerializer(serializers.ModelSerializer):
    password1 = serializers.CharField(write_only=True)
    password2 = serializers.CharField(write_only=True)
    userprofile = UserProfileSerializer(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'userprofile']
        extra_kwargs = {
            'username': {
                'validators': [],
            },
        }

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords must match.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists.")
        if User.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("Username already exists.")
        return data

    def create(self, validated_data):
        profile_data = validated_data.pop('userprofile', None)
        password = validated_data.pop('password1')
        password2 = validated_data.pop('password2', None)
        user = User.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        if profile_data is not None:
            UserProfile.objects.create(user=user, risk='MO', **profile_data)
        else:
            UserProfile.objects.create(user=user, risk='MO')
        Token.objects.create(user=user)
        return user
    
class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('image',)

    def save(self, **kwargs):
        upload_file = self.validated_data['image']
        _, extension = path.splitext(upload_file.name)
        random_file_name = f"{uuid4()}{extension}"
        self.validated_data['image'].name = random_file_name
        return super().save(**kwargs)