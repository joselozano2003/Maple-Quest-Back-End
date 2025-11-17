from rest_framework import serializers
from .models import *


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['user_id', 'email', 'password', 'first_name', 'last_name', 'phone_no', 'points', 'created_at']
        extra_kwargs = {
            'user_id': {'read_only': True},
            'password': {'write_only': True},
            'points': {'read_only': True},
            'created_at': {'read_only': True}
        }
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'email', 'first_name', 'last_name', 'phone_no', 'points', 'profile_pic_url', 'created_at']
        read_only_fields = ['user_id', 'points', 'created_at']

class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'

class AchievementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Achievement
        fields = '__all__'

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'
        extra_kwargs = {
            'location_id': {'read_only': True}
        }

class VisitSerializer(serializers.ModelSerializer):
    images = serializers.SerializerMethodField()
    
    class Meta:
        model = Visit
        fields = '__all__'
    
    def get_images(self, obj):
        """Get all images associated with this visit"""
        images = obj.images.all()
        return ImageSerializer(images, many=True).data

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = '__all__'
