from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from ..models import Vote
from ..permissions import CanCastVote, CanGetMyVote, CanGetAllVotesResults, CanAddVote, CanChangeVote, CanViewVote, \
    CanDeleteVote
from ..serializers.vote_serializers import VoteSerializer, VoteCreateSerializer, VoteUpdateSerializer, \
    VoteCastSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return VoteCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return VoteUpdateSerializer
        elif self.action == 'cast_vote':
            return VoteCastSerializer
        return super().get_serializer_class()

    def get_permissions(self):
        self.permission_classes = [IsAuthenticated]
        if self.action in ['create']:
            self.permission_classes.append(CanAddVote)
        elif self.action in ['update', 'partial_update']:
            self.permission_classes.append(CanChangeVote)
        elif self.action in ['list', 'retrieve']:
            self.permission_classes.append(CanViewVote)
        elif self.action in ['destroy']:
            self.permission_classes.append(CanDeleteVote)
        elif self.action in ['cast_vote']:
            self.permission_classes.append(CanCastVote)
        elif self.action in ['my_vote']:
            self.permission_classes.append(CanGetMyVote)
        elif self.action in ['all_votes_results']:
            self.permission_classes.append(CanGetAllVotesResults)
        return super().get_permissions()

    @swagger_auto_schema(operation_description="Cast vote to current day's menus.")
    @action(detail=False, methods=['post'], url_path='cast-vote')
    def cast_vote(self, request) -> Response:
        serializer = VoteCastSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Vote cast successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    @swagger_auto_schema(operation_description="Get the menu voted for the current day by the employee.")
    @action(detail=False, methods=['get'], url_path='my-vote')
    def my_vote(self, request) -> Response:
        employee = request.user.employee
        today = timezone.now().date()

        # Filter votes for the current day
        votes = Vote.objects.filter(employee=employee, menu__date=today)

        if votes.exists():
            results = [{'menu_id': vote.menu.id, 'points': vote.points} for vote in votes]
            return Response(results, status=200)
        else:
            return Response({'message': 'No vote found for today'}, status=200)

    @swagger_auto_schema(operation_description="Get all menus voted by employees for the current day")
    @action(detail=False, methods=['get'], url_path='all-votes-results')
    def all_votes_results(self, request) -> Response:
        today = timezone.now().date()
        votes = Vote.objects.filter(menu__date=today)

        if not votes.exists():
            return Response({'message': 'No votes have been cast for today'}, status=200)

        results: dict[int, dict] = {}
        for vote in votes:
            menu_id: int = vote.menu.id
            if menu_id not in results:
                results[menu_id] = {
                    'menu_id': menu_id,
                    'points': 0,
                    'votes': []
                }
            results[menu_id]['points'] += vote.points
            results[menu_id]['votes'].append({
                'employee_id': vote.employee.id,
                'points': vote.points
            })

        return Response(results, status=200)
