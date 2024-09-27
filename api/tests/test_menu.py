from datetime import timedelta

from django.core.management import call_command
from django.urls import reverse
from rest_framework import status
from django.utils import timezone

from ..constants import GROUP_NAMES
from ..models import Menu, Restaurant

from ..utils import BaseTestCase, create_user_with_group


class MenuViewSetTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('init_groups')
        call_command('seed')

    def setUp(self):
        self.admin_password = 'adminpassword'
        self.test_password = '123qwe!@#QWE'
        # Authenticate admin User
        self.api_login('admin', self.admin_password)

        # Create a restaurant for the menu
        self.restaurant = Restaurant.objects.get(owner__username='rest_owner1')
        # Create sample menu for today
        self.menu = Menu.objects.create(restaurant=self.restaurant, date=timezone.now().date() - timedelta(days=1), items='Sample Menu')

    def test_create_menu(self):
        url = reverse('menu-list')
        data = {
            'restaurant': Restaurant.objects.get(owner__username='rest_owner2').id,
            'date': timezone.now().date() + timedelta(days=1),
            'items': 'New Menu'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Menu.objects.last().items, 'New Menu')

    def test_upload_menu(self):
        self.api_login('rest_owner2', self.test_password)

        url = reverse('menu-upload-menu')
        data = {
            'date': timezone.now().date() + timedelta(days=1),
            'items': 'New Menu'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Menu.objects.last().items, 'New Menu')

    def test_upload_menu_failed_restaurant_not_exist(self):
        create_user_with_group(username='rest_owner4', password=self.test_password, group_name=GROUP_NAMES['RESTAURANT_OWNER'])
        self.api_login('rest_owner4', self.test_password)

        url = reverse('menu-upload-menu')
        data = {
            'date': timezone.now().date() + timedelta(days=1),
            'items': 'New Menu'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': "User's Restaurant does not exist."})

    def test_upload_menu_failed_menu_duplicate(self):
        self.api_login('rest_owner2', self.test_password)

        url = reverse('menu-upload-menu')
        data = {
            'date': timezone.now().date(),
            'items': 'New Menu'
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'error': 'Menu for this restaurant already exists for the selected day.'})

    def test_current_day_menu_success(self):
        self.api_login('employee1', self.test_password)

        url = reverse('menu-current-day-menu')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 3)
#
    def test_current_day_menu_no_menu(self):
        Menu.objects.all().delete()  # Remove all menus
        url = reverse('menu-current-day-menu')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['message'], 'No menus available for today.')

    def test_retrieve_menu(self):
        url = reverse('menu-detail', args=[self.menu.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['items'], self.menu.items)

    def test_update_menu(self):
        url = reverse('menu-detail', args=[self.menu.id])
        data = {
            'items': 'Updated Menu Description'
        }
        response = self.client.put(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Menu.objects.get(id=self.menu.id).items, 'Updated Menu Description')

    def test_delete_menu(self):
        self.assertEqual(Menu.objects.count(), 4)
        url = reverse('menu-detail', args=[self.menu.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Menu.objects.count(), 3)
