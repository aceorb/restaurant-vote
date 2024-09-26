from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema

from ..models import Vote
from ..permissions import CanCastVote, CanGetMyVote, CanGetAllVotesResults, CanAddVote, CanChangeVote, CanViewVote, \
    CanDeleteVote
from ..serializers.vote_serializers import VoteSerializer


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer
    permission_classes = [IsAuthenticated]


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
        return Response({}, status=status.HTTP_200_OK)


    @swagger_auto_schema(operation_description="Get the menu voted for the current day by the employee.")
    @action(detail=False, methods=['get'], url_path='my-vote')
    def my_vote(self, request) -> Response:
        return Response({}, status=status.HTTP_200_OK)

    @swagger_auto_schema(operation_description="Get all menus voted by employees for the current day")
    @action(detail=False, methods=['get'], url_path='all-votes-results')
    def all_votes_results(self, request) -> Response:
        return Response({}, status=status.HTTP_200_OK)
