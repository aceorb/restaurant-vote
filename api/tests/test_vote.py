from datetime import timedelta

from django.contrib.auth.models import User
from django.core.management import call_command
from rest_framework.exceptions import ErrorDetail
from rest_framework import status
from django.urls import reverse
from django.utils import timezone

from api.constants import GROUP_NAMES
from api.models import Menu, Restaurant, Vote, Employee
from api.utils import BaseTestCase, create_user_with_group


class VoteViewSetTestCase(BaseTestCase):
    @classmethod
    def setUpTestData(cls):
        call_command('init_groups')
        call_command('seed')

    def setUp(self):
        self.admin_username = 'admin'
        self.admin_passord = 'adminpassword'
        self.test_password = '123qwe!@#QWE'
        # Authenticate User
        self.user = User.objects.get(username='employee1')
        self.api_login('employee1', self.test_password)

        # # Create Employee
        self.employee = Employee.objects.get(user=self.user)

        # Create a sample restaurant
        rest_owner = create_user_with_group(username='rest_owner4', password=self.test_password, group_name=GROUP_NAMES['RESTAURANT_OWNER'])
        restaurant = Restaurant.objects.create(name="Test Restaurant", owner=rest_owner)

        # Create a sample menu
        self.menu = Menu.objects.create(restaurant=restaurant, date=timezone.now().date(), items="Field, Nature, Natural")

        # Create a sample vote
        old_menu = Menu.objects.create(restaurant=restaurant, date=timezone.now().date() - timedelta(days=1), items="Old menu")
        self.vote = Vote.objects.create(employee=self.employee, menu=old_menu, points=1)
    def test_cast_vote_v1(self):
        url = reverse('vote-cast-vote')
        data = {
            'menu_id': self.menu.id
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, {'message': 'Vote cast successfully'})

    def test_cast_vote_v1_validation_already_cast(self):
        Vote.objects.create(employee=self.user.employee, menu=self.menu, points=1)
        url = reverse('vote-cast-vote')
        data = {
            'menu_id': self.menu.id
        }
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'vote': [ErrorDetail(string='You have already cast your vote for this menu.', code='invalid')]})

    def test_cast_vote_v1_validation_menu_id_required(self):
        url = reverse('vote-cast-vote')
        response = self.client.post(url, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'menu_id': [ErrorDetail(string='Menu ID is required.', code='invalid')]})

    def test_cast_vote_v1_validation_no_menu_or_not_available_for_day(self):
        url = reverse('vote-cast-vote')
        data = {
            'menu_id': 5
        }
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'menu_id': [ErrorDetail(string='Menu with ID 5 not found or not available for today.', code='invalid')]})

    def test_cast_vote_v2(self):
        menu1 = Menu.objects.get(restaurant__owner__username='rest_owner1')
        menu2 = Menu.objects.get(restaurant__owner__username='rest_owner2')
        menu3 = Menu.objects.get(restaurant__owner__username='rest_owner3')
        url = reverse('vote-cast-vote')
        data = {
            'top_menus': [
                {'menu_id': menu1.id, 'points': 3},
                {'menu_id': menu2.id, 'points': 2},
                {'menu_id': menu3.id, 'points': 1}
            ]
        }
        headers = {"Accept":"application/json; version=v2"}
        response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_cast_vote_v2_validation_top_menus(self):
        url = reverse('vote-cast-vote')
        data = {
            'top_menus': [
                {'menu_id': 1, 'points': 3},
                {'menu_id': 2, 'points': 2},
            ]
        }
        headers = {"Accept":"application/json; version=v2"}
        response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'top_menus': [ErrorDetail(string='You must provide exactly 3 menus with respective points for version 2.', code='invalid')]})

    def test_cast_vote_v2_validation_points_range(self):
        menu1 = Menu.objects.get(restaurant__owner__username='rest_owner1')
        menu2 = Menu.objects.get(restaurant__owner__username='rest_owner2')
        menu3 = Menu.objects.get(restaurant__owner__username='rest_owner3')
        url = reverse('vote-cast-vote')
        data = {
            'top_menus': [
                {'menu_id': menu1.id, 'points': 3},
                {'menu_id': menu2.id, 'points': 2},
                {'menu_id': menu3.id, 'points': 0},
            ]
        }
        headers = {"Accept":"application/json; version=v2"}
        response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'points': [ErrorDetail(string='Points must be 1, 2, or 3.', code='invalid')]})

    def test_cast_vote_v2_validation_points_unique(self):
        menu1 = Menu.objects.get(restaurant__owner__username='rest_owner1')
        menu2 = Menu.objects.get(restaurant__owner__username='rest_owner2')
        menu3 = Menu.objects.get(restaurant__owner__username='rest_owner3')
        url = reverse('vote-cast-vote')
        data = {
            'top_menus': [
                {'menu_id': menu1.id, 'points': 3},
                {'menu_id': menu2.id, 'points': 2},
                {'menu_id': menu3.id, 'points': 2},
            ]
        }
        headers = {"Accept":"application/json; version=v2"}
        response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'points': [ErrorDetail(string='Points must be unique for each menu.', code='invalid')]})

    def test_cast_vote_v2_validation_menu_ids_unique(self):
        menu1 = Menu.objects.get(restaurant__owner__username='rest_owner1')
        menu2 = Menu.objects.get(restaurant__owner__username='rest_owner2')
        url = reverse('vote-cast-vote')
        data = {
            'top_menus': [
                {'menu_id': menu1.id, 'points': 3},
                {'menu_id': menu1.id, 'points': 2},
                {'menu_id': menu2.id, 'points': 1},
            ]
        }
        headers = {"Accept":"application/json; version=v2"}
        response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'menu_id': [ErrorDetail(string='Menu IDs must be unique.', code='invalid')]})

    def test_cast_vote_v2_validation_already_cast(self):
        menu1 = Menu.objects.get(restaurant__owner__username='rest_owner1')
        menu2 = Menu.objects.get(restaurant__owner__username='rest_owner2')
        menu3 = Menu.objects.get(restaurant__owner__username='rest_owner3')
        Vote.objects.create(employee=self.user.employee, menu=menu1, points=1)
        url = reverse('vote-cast-vote')
        data = {
            'top_menus': [
                {'menu_id': menu1.id, 'points': 3},
                {'menu_id': menu2.id, 'points': 2},
                {'menu_id': menu3.id, 'points': 1}
            ]
        }
        headers = {"Accept":"application/json; version=v2"}
        response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data, {'vote': [ErrorDetail(string=f'You have already cast your vote for this Menu with ID {menu1.id}.', code='invalid')]})

    def test_cast_vote_v2_validation_unsupported_version(self):
        url = reverse('vote-cast-vote')
        data = {
            'top_menus': [
                {'menu_id': 1, 'points': 3},
                {'menu_id': 2, 'points': 2},
                {'menu_id': 3, 'points': 1},
            ]
        }
        headers = {"Accept":"application/json; version=v3"}
        response = self.client.post(url, data, format='json', headers=headers)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(response.data, {'detail': ErrorDetail(string='Invalid version in "Accept" header.', code='not_acceptable')})

    def test_my_vote(self):
        #vote first
        url = reverse('vote-cast-vote')
        data = {
            'menu_id': self.menu.id
        }
        response = self.client.post(url, data, format='json')

        url = reverse('vote-my-vote')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('menu_id', response.data[0])
        self.assertIn('points', response.data[0])

    def test_my_vote_no_vote_found(self):
        url = reverse('vote-my-vote')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {'message': 'No vote found for today'})

    def test_all_votes_results(self):
        #vote first
        url = reverse('vote-cast-vote')
        data = {
            'menu_id': self.menu.id
        }
        response = self.client.post(url, data, format='json')

        self.api_login(self.admin_username, self.admin_passord)
        url = reverse('vote-all-votes-results')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(self.menu.id, response.data)
        self.assertIn('points', response.data[self.menu.id])
        self.assertIn('votes', response.data[self.menu.id])

    def test_all_votes_results_no_votes_found(self):
        self.api_login(self.admin_username, self.admin_passord)
        url = reverse('vote-all-votes-results')
        response = self.client.get(url)
        self.assertEqual(response.data, {'message': 'No votes have been cast for today'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_votes(self):
        self.api_login(self.admin_username, self.admin_passord)
        url = reverse('vote-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_vote(self):
        self.api_login(self.admin_username, self.admin_passord)
        rest_owner = create_user_with_group(username='rest_owner5', password=self.test_password, group_name=GROUP_NAMES['RESTAURANT_OWNER'])
        restaurant = Restaurant.objects.create(name="Test Restaurant", owner=rest_owner)
        old_menu = Menu.objects.create(restaurant=restaurant, date=timezone.now().date() - timedelta(days=1), items="Old menu")
        data = {
            'employee': self.employee.id,
            'menu': old_menu.id,
            'points': 2
        }
        url = reverse('vote-list')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Vote.objects.count(), 2)

    def test_retrieve_vote(self):
        self.api_login(self.admin_username, self.admin_passord)
        url = reverse('vote-detail', args=[self.vote.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['points'], self.vote.points)

    def test_update_vote(self):
        self.api_login(self.admin_username, self.admin_passord)
        url = reverse('vote-detail', args=[self.vote.id])
        data = {'points': 2}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.vote.refresh_from_db()
        self.assertEqual(self.vote.points, 2)

    def test_delete_vote(self):
        self.api_login(self.admin_username, self.admin_passord)
        url = reverse('vote-detail', args=[self.vote.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Vote.objects.count(), 0)