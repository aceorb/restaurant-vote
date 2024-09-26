from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group

from api.constants import GROUP_NAMES
from api.models import Restaurant, Menu, Employee  # Adjust according to your actual models
from faker import Faker
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist

fake = Faker()

class Command(BaseCommand):
    help = 'Seed the database with initial data'

    def handle(self, *args, **kwargs):

        try:
            admin_group = Group.objects.get(name=GROUP_NAMES['ADMIN'])
            restaurant_owner_group = Group.objects.get(name=GROUP_NAMES['RESTAURANT_OWNER'])
            employee_group = Group.objects.get(name=GROUP_NAMES['EMPLOYEE'])
        except ObjectDoesNotExist:
            self.stdout.write(self.style.ERROR('Error: Groups do not exist. run manage.py init_groups first.'))
            return

        if User.objects.filter(username='employee1').exists():
            self.stdout.write(self.style.WARNING('The database has already been seeded.'))
            return

        superuser_password = 'adminpassword'
        fake_password = '123qwe!@#QWE'

        # Create admin user
        user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password=superuser_password,
            first_name='Admin',
            last_name='Admin',
            is_active=True
        )
        user.groups.add(admin_group)

        # Create 3 normal users for employee group
        employee_usernames = ['employee1', 'employee2', 'employee3']
        for username in employee_usernames:
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password=fake_password,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True
            )
            user.groups.add(employee_group)


        # Create 3 users for restaurant owner group
        restaurant_owner_usernames = ['rest_owner1', 'rest_owner2', 'rest_owner3']
        for username in restaurant_owner_usernames:
            user = User.objects.create_user(
                username=username,
                email=fake.email(),
                password=fake_password,
                first_name=fake.first_name(),
                last_name=fake.last_name(),
                is_active=True
            )
            user.groups.add(restaurant_owner_group)

        # Create 3 restaurants
        for owner_username in restaurant_owner_usernames:
            restaurant = Restaurant(
                name=fake.company() + ' Restaurant',
                owner=User.objects.get(username=owner_username)
            )
            restaurant.save()

        # Create 3 employees
        employee_items = ['employee1', 'employee2','employee3']
        for employee_username in employee_items:
            employee = Employee(
                user=User.objects.get(username=employee_username),
                phone=fake.phone_number(),
                position=fake.job()
            )
            employee.save()

        # Create 3 menus for each restaurant
        for owner_username in restaurant_owner_usernames:
            menu = Menu(
                restaurant=Restaurant.objects.get(owner=User.objects.get(username=owner_username)),
                date=timezone.now().date(),
                items= ', '.join([fake.word().capitalize() for _ in range(3)])
            )
            menu.save()
        self.stdout.write(self.style.SUCCESS('Database seeding completed successfully: 1 superuser, 3 restaurant owners, 3 employees, 3 restaurants, and 3 menus have been created.'))