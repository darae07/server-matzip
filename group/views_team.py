from django.db.models import Exists, OuterRef, Prefetch
from django.http import Http404
from rest_framework.decorators import action, api_view, parser_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from common.models import CommonUser
from matzip.handler import request_data_handler
from .constants import InviteStatus
from .models_party import Membership
from .models_team import TeamMember, Team, Invite
from rest_framework import viewsets, status, permissions
from .serializer import TeamSerializer, TeamFindSerializer, TeamListSerializer
from .serializer_team_member import TeamMemberSerializer, TeamMemberCreateSerializer, PartyTeamMemberSerializer
from rest_framework.parsers import MultiPartParser, FormParser


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        membership = TeamMember.objects.filter(user=user.id).values('team')
        queryset = self.queryset.filter(id__in=membership)
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user = request.user
        teams = queryset.prefetch_related(
            Prefetch('members', queryset=TeamMember.objects.filter(user=user.id)))\
            .order_by('-created_at')
        serializer = TeamListSerializer(teams, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['name'])
        if Team.objects.filter(name=data['name']):
            return Response({'message': '이미 사용중인 이름입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TeamSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = TeamSerializer(instance=serializer.instance)
        return Response(data={**serializer.data, 'message': '팀을 생성했습니다.'}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        team = Team.objects.get(pk=pk)
        serializer = self.serializer_class(team, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            team = Team.objects.get(pk=pk)
            team.delete()
            return Response(data={'message': '팀을 삭제했습니다.'}, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response({'message': '팀을 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True)
    def members(self, request, pk=None):
        members = TeamMember.objects.filter(team=pk).order_by('member_name')

        party = self.request.query_params.get('party')
        if party:
            members = members.annotate(
                is_invited_waiting=Exists(Invite.objects.filter(receiver=OuterRef('id'), party=party, status=InviteStatus.WAITING.value)),
                is_party_member=Exists(Membership.objects.filter(party=party, team_member=OuterRef('id')))
            ).order_by('-is_party_member', '-is_invited_waiting', 'member_name')
        page = self.paginate_queryset(members)
        if party:
            serializer = PartyTeamMemberSerializer(page, many=True)
        else:
            serializer = TeamMemberSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(methods=['post'], detail=False)
    def find(self, request):
        code = request.data['code']
        try:
            team = Team.objects.get(join_code=code)
            serializer = TeamFindSerializer(team, many=False)
            return Response(data={**serializer.data, 'message': '인증코드로 팀을 찾았습니다.'})
        except Team.DoesNotExist:
            raise Http404

    @action(detail=True, methods=['POST'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        if request.FILES:
            request.data.image = request.FILES
        try:
            team = Team.objects.get(pk=pk)
        except Team.DoesNotExist:
            return Response({'message': '팀 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = TeamSerializer(team, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        serializer = TeamSerializer(instance=serializer.instance)
        return Response(data={**serializer.data, 'message': '이미지를 등록했습니다.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def delete_image(self, request, pk=None):
        team = Team.objects.get(pk=pk)
        team.image.delete()
        team.save()
        serializer = TeamSerializer(instance=team)
        return Response(data={**serializer.data, 'message': '이미지를 삭제했습니다.'}, status=status.HTTP_200_OK)


class TeamMemberViewSet(viewsets.ModelViewSet):
    queryset = TeamMember.objects.all()
    serializer_class = TeamMemberSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['member_name', 'team'])
        user = request.user
        if TeamMember.objects.filter(user=user.id, team=data['team']):
            return Response({'message': '이미 가입된 유저입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if TeamMember.objects.filter(member_name=data['member_name']):
            return Response({'message': '이미 사용중인 이름입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)

        data['user'] = user.id
        serializer = TeamMemberCreateSerializer(data=data)
        if serializer.is_valid():
            team_member = TeamMember.objects.create(**serializer.validated_data)
            team_member.save()
            serializer = TeamMemberSerializer(instance=team_member)
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

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            member = TeamMember.objects.get(pk=pk)
            member.delete()
            return Response(data={'message': '팀을 탈퇴했습니다.'}, status=status.HTTP_200_OK)
        except TeamMember.DoesNotExist:
            return Response({'message': '가입 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        if request.FILES:
            request.data.image = request.FILES
        try:
            team_member = TeamMember.objects.get(pk=pk)
        except TeamMember.DoesNotExist:
            return Response({'message': '가입 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = TeamMemberSerializer(team_member, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        serializer = TeamMemberSerializer(instance=serializer.instance)
        return Response(data={**serializer.data, 'message': '이미지를 등록했습니다.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def delete_image(self, request, pk=None):
        team_member = TeamMember.objects.get(pk=pk)
        team_member.image.delete()
        team_member.save()
        serializer = TeamMemberSerializer(instance=team_member)
        return Response(data={**serializer.data, 'message': '이미지를 삭제했습니다.'}, status=status.HTTP_200_OK)

