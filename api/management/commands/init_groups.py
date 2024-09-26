from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission

from api.constants import GROUP_NAMES


class Command(BaseCommand):
    help = 'Initialize custom groups with permissions'

    def handle(self, *args, **kwargs):
        # Create groups
        admin_group, created = Group.objects.get_or_create(name=GROUP_NAMES['ADMIN'])
        if not created:
            self.stdout.write(self.style.WARNING('Command to initialize custom groups is already run.'))
            return
        restaurant_owner_group, created = Group.objects.get_or_create(name=GROUP_NAMES['RESTAURANT_OWNER'])
        employee_group, created = Group.objects.get_or_create(name=GROUP_NAMES['EMPLOYEE'])

        # Assign permissions custom groups
        admin_permissions = Permission.objects.all()
        restaurant_owner_permissions = Permission.objects.filter(codename__in=[
            'upload_menu'
        ])
        employee_permissions = Permission.objects.filter(codename__in=[
            'get_current_day_menu',
            'cast_vote',
            'get_my_vote',
        ])

        admin_group.permissions.add(*admin_permissions)
        restaurant_owner_group.permissions.add(*restaurant_owner_permissions)
        employee_group.permissions.add(*employee_permissions)

        self.stdout.write(self.style.SUCCESS('Admin, RestaurantOwner, Employee Groups created with permissions'))