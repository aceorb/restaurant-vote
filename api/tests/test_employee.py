from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework import status
from django.urls import reverse

from api.constants import GROUP_NAMES
from api.models import Employee
from api.utils import BaseTestCase, create_user_with_group


class EmployeeViewSetTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('init_groups')

    def setUp(self):
        self.test_password = '123qwe!@#QWE'
        # Create a user and authenticate them
        create_user_with_group(username='testuser', password=self.test_password, group_name=GROUP_NAMES['ADMIN'])
        self.api_login('testuser', self.test_password)

        # Create a user and authenticate them
        self.user = User.objects.create_user(username='employee4', password=self.test_password)

        # Create an employee
        self.employee = Employee.objects.create(user=self.user, phone="1234567890", position="Developer")

    def test_list_employees(self):
        url = reverse('employee-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_employee(self):
        url = reverse('employee-list')
        user_data = {
            'username': 'newuser',
            'password': self.test_password,
            'email': 'newuser@example.com'
        }
        data = {
            'user': user_data,
            'phone': '0987654321',
            'position': 'Developer'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 2)

    def test_retrieve_employee(self):
        url = reverse('employee-detail', args=[self.employee.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['phone'], self.employee.phone)

    def test_update_employee(self):
        url = reverse('employee-detail', args=[self.employee.id])
        data = {'phone': '1111111111', 'position': 'Software Developer'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.phone, '1111111111')

    def test_delete_employee(self):
        url = reverse('employee-detail', args=[self.employee.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 0)