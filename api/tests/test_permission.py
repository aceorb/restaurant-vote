from django.core.management import call_command
from rest_framework.exceptions import ErrorDetail
from rest_framework import status
from django.urls import reverse

from api.utils import BaseTestCase


class PermissionTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('init_groups')
        call_command('seed')

    def setUp(self):
        self.test_password = '123qwe!@#QWE'
        self.admin_passwor = 'adminpassword'
    def test_employee_permission(self):
        self.api_login('rest_owner1', self.test_password)

        url = reverse('menu-current-day-menu')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})

        url = reverse('vote-cast-vote')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})

        url = reverse('vote-my-vote')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})


    def test_rest_owner_permission(self):
        self.api_login('employee1', self.test_password)

        url = reverse('menu-upload-menu')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})

    def test_admin_permission(self):
        self.api_login('employee1', self.test_password)

        url = reverse('restaurant-list')
        data = {}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})

        url = reverse('employee-list')
        data = {}
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})

        url = reverse('vote-all-votes-results')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='You do not have permission to perform this action.', code='permission_denied')})