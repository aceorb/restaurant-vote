from django.contrib.auth.models import User
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ..constants import GROUP_NAMES
from ..models import Restaurant
from ..permissions import CanAddRestaurant, CanChangeRestaurant, CanViewRestaurant, CanDeleteRestaurant
from ..serializers.restaurant_serializers import RestaurantSerializer, RestaurantCreateSerializer, \
    RestaurantUpdateSerializer


class RestaurantViewSet(viewsets.ModelViewSet):
    queryset = Restaurant.objects.all()
    serializer_class = RestaurantSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return RestaurantCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return RestaurantUpdateSerializer
        return super().get_serializer_class()

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
        owner_id = request.data.get('owner_id')

        # Check if the owner exists and is part of the "Restaurant" group
        if owner_id:
            try:
                owner = User.objects.get(id=owner_id)  # Get the owner by ID
                if not owner.groups.filter(name=GROUP_NAMES['RESTAURANT_OWNER']).exists():  # Check if in the group
                    return Response(
                        {'error': 'The specified owner is not part of the Restaurant group.'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except User.DoesNotExist:
                return Response(
                    {'error': 'Owner does not exist.'},
                    status=status.HTTP_404_NOT_FOUND
                )

        if Restaurant.objects.filter(owner_id=owner_id).exists():
            return Response(
                {'error': 'Owner already registered Restaurant.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        # If owner is valid and in the group, proceed to create the restaurant
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)