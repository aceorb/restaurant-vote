from django.contrib.auth.models import Group
from django.core.exceptions import ObjectDoesNotExist
from drf_yasg.utils import swagger_auto_schema
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated

from ..constants import GROUP_NAMES
from ..models import Employee
from ..permissions import CanAddEmployee, CanChangeEmployee, CanViewEmployee, CanDeleteEmployee
from ..serializers.employee_serializers import EmployeeSerializer, EmployeeUpdateSerializer
from ..serializers.user_serializers import UserSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update']:
            return EmployeeUpdateSerializer
        return super().get_serializer_class()

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
        # Step 1: Create the user
        user_data = request.data.pop('user')  # User data comes from the request
        user_serializer = UserSerializer(data=user_data)

        if user_serializer.is_valid():
            user = user_serializer.save()  # Save the user

            # Step 2: Add the user to the "employee" group
            try:
                employee_group = Group.objects.get(name=GROUP_NAMES['EMPLOYEE'])
                user.groups.add(employee_group)
            except ObjectDoesNotExist:
                # Delete the user if the employee creation fails
                user.delete()
                return Response({'error': 'The Employee group does not exist. Please ensure the group is created before assigning users.'}, status=status.HTTP_400_BAD_REQUEST)

            # Step 3: Create the employee with the newly created user
            employee_data = request.data

            employee_serializer = self.get_serializer(data=employee_data)

            if employee_serializer.is_valid():
                employee_serializer.save(user=user)
                return Response(employee_serializer.data, status=status.HTTP_201_CREATED)
            else:
                # Delete the user if the employee creation fails
                user.delete()
                return Response(employee_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
