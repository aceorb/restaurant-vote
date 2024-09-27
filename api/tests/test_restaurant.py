from django.urls import reverse
from rest_framework import status
from django.core.management import call_command

from ..models import Restaurant
from api.constants import GROUP_NAMES
from ..utils import create_user_with_group, BaseTestCase


class RestaurantViewSetTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('init_groups')

    def setUp(self):
        self.test_password = 'password'
        # Create a user and authenticate them
        create_user_with_group(username='testuser', password=self.test_password, group_name=GROUP_NAMES['ADMIN'])
        self.api_login('testuser', self.test_password)

        # Create a sample restaurant
        rest_owner = create_user_with_group(username='rest_owner', password=self.test_password, group_name=GROUP_NAMES['RESTAURANT_OWNER'])
        self.restaurant = Restaurant.objects.create(name="Test Restaurant", owner=rest_owner)

    def test_list_restaurants(self):
        url = reverse('restaurant-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Restaurant.objects.count(), 1)

    def test_create_restaurant(self):
        rest_owner = create_user_with_group(username='rest_owner2', password=self.test_password, group_name=GROUP_NAMES['RESTAURANT_OWNER'])
        url = reverse('restaurant-list')
        data = {
            'name': 'New Restaurant',
            'owner_id': rest_owner.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Restaurant.objects.count(), 2)

    def test_create_restaurant_failed_group_error(self):
        user = create_user_with_group(username='employee1', password=self.test_password, group_name=GROUP_NAMES['EMPLOYEE'])
        url = reverse('restaurant-list')
        data = {
            'name': 'New Restaurant',
            'owner_id': user.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'The specified owner is not part of the Restaurant group.'})

    def test_create_restaurant_failed_already_registered(self):
        user = create_user_with_group(username='rest_owner2', password=self.test_password, group_name=GROUP_NAMES['RESTAURANT_OWNER'])
        url = reverse('restaurant-list')
        data = {
            'name': 'New Restaurant',
            'owner_id': user.id
        }
        self.client.post(url, data)
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Owner already registered Restaurant.'})

    def test_retrieve_restaurant(self):
        url = reverse('restaurant-detail', args=[self.restaurant.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.restaurant.name)

    def test_update_restaurant(self):
        url = reverse('restaurant-detail', args=[self.restaurant.id])
        data = {'name': 'Updated Restaurant'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.restaurant.refresh_from_db()
        self.assertEqual(self.restaurant.name, 'Updated Restaurant')

    def test_delete_restaurant(self):
        url = reverse('restaurant-detail', args=[self.restaurant.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Restaurant.objects.count(), 0)