from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..models import Restaurant
from ..permissions import CanAddRestaurant, CanChangeRestaurant, CanViewRestaurant, CanDeleteRestaurant
from ..serializers.restaurant_serializers import RestaurantSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]


    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action in ['create']:
            self.permission_classes.append(CanAddRestaurant)
        elif self.action in ['update', 'partial_update']:
            self.permission_classes.append(CanChangeRestaurant)
        elif self.action in ['list', 'retrieve']:
            self.permission_classes.append(CanViewRestaurant)
        elif self.action in ['destroy']:
            self.permission_classes.append(CanDeleteRestaurant)
        return super().get_permissions()

    @swagger_auto_schema(operation_description="Create restaurant.")
    def create(self, request, *args, **kwargs) -> Response:
        return Response({}, status=status.HTTP_200_OK)