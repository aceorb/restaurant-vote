from django.contrib.auth.models import User
from rest_framework import serializers

from .user_serializers import UserSerializer
from ..models import Restaurant


class RestaurantCreateSerializer(serializers.ModelSerializer):
    owner_id = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), source='owner', write_only=True)

    class Meta:
        model = Restaurant
        fields = ['name', 'owner_id']  # Only include name and owner_id for creation


class RestaurantUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = ['name']


class RestaurantSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    class Meta:
        model = Restaurant
        fields = '__all__'