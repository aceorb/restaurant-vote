from django.contrib.auth.models import User, Group
from django.urls import reverse
from rest_framework.test import APITestCase

def create_user_with_group(username, password, group_name):
    user = User.objects.create_user(username=username, password=password)
    group = Group.objects.get(name=group_name)
    user.groups.add(group)
    return user


class BaseTestCase(APITestCase):
    def get_jwt_token(self, username, password):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': username, 'password': password}, format='json')
        return response.data['access']  # Return the access token
    def api_login(self, username, password):
        token = self.get_jwt_token(username, password)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token}')