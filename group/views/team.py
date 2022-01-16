from django.db.models import Prefetch, Exists, OuterRef
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.constants import InviteStatus
from group.models_party import Membership
from group.models_team import Team, TeamMember, Invite
from group.serializers.team import TeamSerializer, TeamListSerializer, TeamFindSerializer
from group.serializer_team_member import PartyTeamMemberSerializer, TeamMemberSerializer, TeamMemberCreateSerializer
from matzip.handler import request_data_handler


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        membership = TeamMember.objects.filter(user=user.id).values('team')
        queryset = self.queryset.filter(id__in=membership)
        return queryset

    def retrieve(self, request, pk=None, *args, **kwargs):
        try:
            team = Team.objects.get(pk=pk)
            user = request.user
            has_membership = TeamMember.objects.filter(team=pk, user=user.id)
            if not has_membership:
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            serializer = TeamSerializer(team)
            return Response({'message': '회사 정보를 불러왔습니다.', **serializer.data}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Team.DoesNotExist:
            return Response({'message': '회사를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        user = request.user
        teams = queryset.prefetch_related(
            Prefetch('members', queryset=TeamMember.objects.filter(user=user.id)))\
            .order_by('-created_at')
        serializer = TeamListSerializer(teams, many=True)
        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['name', 'location'])
        if Team.objects.filter(name=data['name']):
            return Response({'message': '이미 사용중인 이름입니다.'}, status=status.HTTP_400_BAD_REQUEST)
        serializer = TeamSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        # 팀 생성후 팀 가입
        serializer = TeamSerializer(instance=serializer.instance)
        return Response(data={**serializer.data, 'message': '회사 생성했습니다.'}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        try:
            team = Team.objects.get(pk=pk)
            serializer = self.serializer_class(team, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(**serializer.validated_data)
            serializer = self.serializer_class(serializer.instance)
            return Response(data={**serializer.data, 'message': '회사 정보를 수정했습니다.'}, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response({'message': '회사를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            team = Team.objects.get(pk=pk)
            team.delete()
            return Response(data={'message': '회사를 삭제했습니다.'}, status=status.HTTP_200_OK)
        except Team.DoesNotExist:
            return Response({'message': '회사를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True)
    def members(self, request, pk=None):
        members = TeamMember.objects.filter(team=pk).order_by('member_name')

        # membership 개발후 수정
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
            return Response(data={**serializer.data, 'message': '인증코드로 회사를 찾았습니다.'})
        except Team.DoesNotExist:
            return Response({'message': '회사를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

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
        my_memberships = TeamMember.objects.filter(user=user.id)
        if my_memberships.filter(team=data['team']):
            return Response({'message': '이미 가입된 유저입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)

        if my_memberships.filter(member_name=data['member_name']):
            return Response({'message': '이미 사용중인 이름입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)

        data['user'] = user.id
        serializer = TeamMemberCreateSerializer(data=data)
        if serializer.is_valid():
            my_memberships.update(is_selected=False)
            team_member = TeamMember.objects.create(**serializer.validated_data)
            team_member.save()
            serializer = TeamMemberSerializer(instance=team_member)
            return Response({**serializer.data, 'message': '회사에 가입되었습니다.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        try:
            team_member = TeamMember.objects.get(pk=pk)
            serializer = self.serializer_class(team_member, data=data, partial=True)
            if serializer.is_valid():
                serializer.save(**serializer.validated_data)
                serializer = self.serializer_class(serializer.instance)
                return Response(data={**serializer.data, 'message': '내 정보를 업데이트 했습니다.'}, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except TeamMember.DoesNotExist:
            return Response({'message': '가입 정보를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            member = TeamMember.objects.get(pk=pk)
            member.delete()
            return Response(data={'message': '회사를 탈퇴했습니다.'}, status=status.HTTP_200_OK)
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