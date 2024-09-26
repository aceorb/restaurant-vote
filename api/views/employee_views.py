from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from ..models import Employee
from ..permissions import CanAddEmployee, CanChangeEmployee, CanViewEmployee, CanDeleteEmployee
from ..serializers.employee_serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action in ['create']:
            self.permission_classes.append(CanAddEmployee)
        elif self.action in ['update', 'partial_update']:
            self.permission_classes.append(CanChangeEmployee)
        elif self.action in ['list', 'retrieve']:
            self.permission_classes.append(CanViewEmployee)
        elif self.action in ['destroy']:
            self.permission_classes.append(CanDeleteEmployee)
        return super().get_permissions()

    @swagger_auto_schema(operation_description="Create Employee.")
    def create(self, request, *args, **kwargs) -> Response:
        return Response({}, status=status.HTTP_200_OK)
