from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from ..models import Menu
from ..permissions import CanAddMenu, CanChangeMenu, CanViewMenu, CanDeleteMenu, CanUploadMenu, CanGetCurrentDayMenu
from ..serializers.menu_serializers import MenuSerializer


class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    permission_classes = [IsAuthenticated]

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
        return Response({}, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Upload Menu for restaurant each day.")
    @action(detail=False, methods=['post'], url_path='upload-menu')
    def upload_menu(self, request, *args, **kwargs) -> Response:
        return Response({}, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Get the menu for the current day for all restaurants.")
    @action(detail=False, methods=['get'], url_path='current-day-menu')
    def current_day_menu(self, request) -> Response:
        return Response({}, status=status.HTTP_200_OK)
