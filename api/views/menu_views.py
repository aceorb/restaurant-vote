from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from ..models import Menu, Restaurant
from ..permissions import CanAddMenu, CanChangeMenu, CanViewMenu, CanDeleteMenu, CanUploadMenu, CanGetCurrentDayMenu
from ..serializers.menu_serializers import MenuSerializer, MenuCreateSerializer, MenuUpdateSerializer, \
    MenuUploadSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return MenuCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return MenuUpdateSerializer
        if self.action == 'upload_menu':
            return MenuUploadSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action in ['create']:
            self.permission_classes.append(CanAddMenu)
        elif self.action in ['update', 'partial_update']:
            self.permission_classes.append(CanChangeMenu)
        elif self.action in ['list', 'retrieve']:
            self.permission_classes.append(CanViewMenu)
        elif self.action in ['destroy']:
            self.permission_classes.append(CanDeleteMenu)
        elif self.action in ['upload_menu']:
            self.permission_classes.append(CanUploadMenu)
        elif self.action in ['current_day_menu']:
            self.permission_classes.append(CanGetCurrentDayMenu)
        return super().get_permissions()

    def create(self, request, *args, **kwargs) -> Response:
        restaurant_id = request.data.get('restaurant')
        date = request.data.get('date', timezone.now().date())
        menu_serializer = MenuCreateSerializer(data=request.data)
        if menu_serializer.is_valid():
            if Menu.objects.filter(restaurant_id=restaurant_id, date=date).exists():
                return Response(
                    {'error': 'Menu for this restaurant already exists for the selected day.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return super().create(request, *args, **kwargs)
        else:
            return Response(menu_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description="Upload Menu for restaurant each day.")
    @action(detail=False, methods=['post'], url_path='upload-menu')
    def upload_menu(self, request, *args, **kwargs) -> Response:
        date = request.data.get('date', timezone.now().date())
        menu_serializer = MenuUploadSerializer(data=request.data)
        if menu_serializer.is_valid():
            try:
                restaurant = Restaurant.objects.get(owner_id=request.user.id)
            except Restaurant.DoesNotExist:
                return Response(
                    {'error': 'User\'s Restaurant does not exist.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Menu.objects.filter(restaurant_id=restaurant.id, date=date).exists():
                return Response(
                    {'error': 'Menu for this restaurant already exists for the selected day.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                request.data['restaurant'] = restaurant.id
                menu_upload_serializer = MenuCreateSerializer(data=request.data)
                if menu_upload_serializer.is_valid():
                    menu_upload_serializer.save()
                    return Response(menu_upload_serializer.data, status=status.HTTP_201_CREATED)
                else:
                    return Response(menu_upload_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(menu_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(operation_description="Get the menu for the current day for all restaurants.")
    @action(detail=False, methods=['get'], url_path='current-day-menu')
    def current_day_menu(self, request) -> Response:
        today = timezone.now().date()
        current_day_menus = Menu.objects.filter(date=today)

        if not current_day_menus.exists():
            return Response(
                {'message': 'No menus available for today.'},
                status=status.HTTP_404_NOT_FOUND
            )
        else:
            serializer = MenuSerializer(current_day_menus, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
