from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.response import Response
from .models import TeamMember, Team
from rest_framework import viewsets, status, permissions
from .serializer import TeamMemberSerializer, TeamSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        user = self.request.user
        membership = TeamMember.objects.filter(user=user.id).values('team')
        queryset = self.queryset.filter(id__in=membership)
        return queryset

    @action(detail=True)
    def members(self, request, pk=None):
        members = TeamMember.Objects.filter(team=pk)
        page = self.paginate_queryset(members)
        if page is not None:
            serializer = TeamMemberSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)


@api_view(['post'])
@permission_classes((permissions.AllowAny,))
@parser_classes([MultiPartParser, FormParser])
def upload_team_image(request):
    if request.data['team']:
        request.data.team = request.data['team']
    if request.FILES:
        request.data.image = request.FILES
    team = Team.objects.get(pk=request.data.team)
    serializer = TeamSerializer(team, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(**serializer.validated_data)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['post'])
@permission_classes((permissions.AllowAny,))
def delete_team_image(request, pk):
    team = Team.objects.get(pk=pk)
    team.image.delete()
    team.save()
    return Response(data={'id': team.id}, status=status.HTTP_200_OK)


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        team_member = TeamMember.objects.get(pk=pk)
        serializer = self.serializer_class(team_member, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

