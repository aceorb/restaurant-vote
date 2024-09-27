from rest_framework import serializers

from .restaurant_serializers import RestaurantSerializer
from ..models import Menu


class MenuCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = '__all__'

class MenuUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['date', 'items']

class MenuUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Menu
        fields = ['items']


class MenuSerializer(serializers.ModelSerializer):
    restaurant = RestaurantSerializer(read_only=True)
    class Meta:
        model = Menu
        fields = '__all__'