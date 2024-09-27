from django.core.validators import RegexValidator
from rest_framework import serializers

from .user_serializers import UserSerializer
from ..models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    phone = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )

    class Meta:
        model = Employee
        fields = '__all__'

    def validate_phone(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Phone number is too short.")
        return value

class EmployeeUpdateSerializer(serializers.ModelSerializer):
    phone = serializers.CharField(
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )

    class Meta:
        model = Employee
        fields = ['phone', 'position']

    def validate_phone(self, value):
        if len(value) < 10:
            raise serializers.ValidationError("Phone number is too short.")
        return value
