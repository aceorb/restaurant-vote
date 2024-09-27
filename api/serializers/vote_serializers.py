from django.utils import timezone
from rest_framework import serializers

from .employee_serializers import EmployeeSerializer
from .menu_serializers import MenuSerializer
from ..models import Menu, Vote


class VoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = '__all__'


class VoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Vote
        fields = ['points']


class VoteCastSerializer(serializers.ModelSerializer):
    menu_id = serializers.IntegerField(required=False)  # v1
    top_menus = serializers.ListField(child=serializers.DictField(), required=False)  # v2

    class Meta:
        model = Vote
        fields = ['menu_id', 'top_menus']

    def validate(self, data):
        version = self.context['request'].version
        try:
            employee = self.context['request'].user.employee
        except AttributeError:
            raise serializers.ValidationError({'role': 'Attempt to cast a vote as an employee role.'})

        today = timezone.now().date()

        # Validate based on version
        if version == 'v1':
            menu_id = data.get('menu_id')
            if not menu_id:
                raise serializers.ValidationError({'menu_id': 'Menu ID is required.'})

            # Validate menu existence
            try:
                menu = Menu.objects.get(id=menu_id, date=today)
            except Menu.DoesNotExist:
                raise serializers.ValidationError(
                    {'menu_id': f'Menu with ID {menu_id} not found or not available for today.'})

            # Check if the user has already voted
            if Vote.objects.filter(employee=employee, menu=menu).exists():
                raise serializers.ValidationError({'vote': 'You have already cast your vote for this menu.'})

        elif version == 'v2':
            top_menus = data.get('top_menus')

            # Validate that top_menus is a list of exactly 3 items
            if not top_menus or len(top_menus) != 3:
                raise serializers.ValidationError(
                    {'top_menus': 'You must provide exactly 3 menus with respective points for version 2.'})

            # Initialize sets to track unique points and menu_ids
            unique_points = set()
            unique_menu_ids = set()

            # Validate each menu in top_menus
            for menu_vote in top_menus:
                menu_id = menu_vote.get('menu_id')
                points = menu_vote.get('points')

                if points not in [1, 2, 3]:
                    raise serializers.ValidationError({'points': 'Points must be 1, 2, or 3.'})

                if points in unique_points:
                    raise serializers.ValidationError({'points': 'Points must be unique for each menu.'})
                unique_points.add(points)

                if menu_id in unique_menu_ids:
                    raise serializers.ValidationError({'menu_id': 'Menu IDs must be unique.'})
                unique_menu_ids.add(menu_id)

                try:
                    menu = Menu.objects.get(id=menu_id, date=today)
                except Menu.DoesNotExist:
                    raise serializers.ValidationError(
                        {'menu_id': f'Menu with ID {menu_id} not found or not available for today.'})

                if Vote.objects.filter(employee=employee, menu=menu).exists():
                    raise serializers.ValidationError(
                        {'vote': f'You have already cast your vote for this Menu with ID {menu_id}.'})
        else:
            raise serializers.ValidationError({'version': 'Unsupported version.'})
        return data

    def create(self, validated_data):
        employee = self.context['request'].user.employee
        today = timezone.now().date()

        version = self.context['request'].version
        if version == 'v1':
            # Create a single vote
            menu_id = validated_data['menu_id']
            menu = Menu.objects.get(id=menu_id, date=today)
            vote = Vote.objects.create(employee=employee, menu=menu, points=1)
            return vote

        elif version == 'v2':
            # Create votes for each of the top 3 menus
            votes = []
            for menu_vote in validated_data['top_menus']:
                menu_id = menu_vote['menu_id']
                points = menu_vote['points']
                menu = Menu.objects.get(id=menu_id, date=today)
                vote = Vote.objects.create(employee=employee, menu=menu, points=points)
                votes.append(vote)
            return votes


class VoteSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    menu = MenuSerializer(read_only=True)

    class Meta:
        model = Vote
        fields = '__all__'
