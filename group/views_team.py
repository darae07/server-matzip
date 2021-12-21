from django.http import Http404
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from common.models import CommonUser
from .models import TeamMember, Team
from rest_framework import viewsets, status, permissions
from .serializer import TeamMemberSerializer, TeamSerializer, TeamMemberCreateSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer

    def get_queryset(self):
        user = self.request.user
        print(user)
        membership = TeamMember.objects.filter(user=user.id).values('team')
        queryset = self.queryset.filter(id__in=membership)
        return queryset

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        team = Team.objects.get(pk=pk)
        serializer = self.serializer_class(team, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True)
    def members(self, request, pk=None):
        members = TeamMember.objects.filter(team=pk)
        page = self.paginate_queryset(members)
        if page is not None:
            serializer = TeamMemberSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = TeamMemberSerializer(members, many=True)
        return Response(serializer.data)

    @action(methods=['post'], detail=False)
    def find(self, request):
        code = request.data['code']
        try:
            team = Team.objects.get(join_code=code)
            serializer = self.serializer_class(team, many=False)
            return Response(data={**serializer.data, 'message': '인증코드로 팀을 찾았습니다.'})
        except Team.DoesNotExist:
            raise Http404


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

    def create(self, request, *args, **kwargs):
        data = request.data
        if 'user' not in data:
            return Response({'message': '유저를 입력해야 합니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            user = CommonUser.objects.get(pk=data['user'])
        except CommonUser.DoesNotExist:
            user = None
        if not user:
            return Response({'message': '존재하지 않는 유저입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            same_user = TeamMember.objects.get(user=data['user'], team=data['team'])
        except TeamMember.DoesNotExist:
            same_user = None
        if same_user:
            return Response({'message': '이미 가입된 유저입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        if 'member_name' not in data or data['member_name'] is None:
            return Response({'message': '유저 이름을 입력해주세요.'},
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            member = TeamMember.objects.get(member_name=data['member_name'])
        except TeamMember.DoesNotExist:
            member = None
        if member:
            return Response({'message': '이미 사용중인 이름입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)
        data[user] = user
        serializer = TeamMemberCreateSerializer(data=data)
        if serializer.is_valid():
            team_member = TeamMember.objects.create(**serializer.validated_data)
            team_member.save()
            return Response({**serializer.data, 'message': '팀에 가입되었습니다.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        team_member = TeamMember.objects.get(pk=pk)
        serializer = self.serializer_class(team_member, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['post'])
@permission_classes((permissions.AllowAny,))
@parser_classes([MultiPartParser, FormParser])
def upload_team_member_image(request):
    if request.data['team_member']:
        request.data.team_member = request.data['team_member']
    if request.FILES:
        request.data.image = request.FILES
    team_member = TeamMember.objects.get(pk=request.data.team_member)
    serializer = TeamMemberSerializer(team_member, data=request.data, partial=True)
    serializer.is_valid(raise_exception=True)
    serializer.save(**serializer.validated_data)
    return Response(data=serializer.data, status=status.HTTP_200_OK)


@api_view(['post'])
@permission_classes((permissions.AllowAny,))
def delete_team_member_image(request, pk):
    team_member = TeamMember.objects.get(pk=pk)
    team_member.image.delete()
    team_member.save()
    return Response(data={'id': team_member.id}, status=status.HTTP_200_OK)

