from django.db.models import F, Q
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import datetime

from group.models_party import Party, Membership
from group.models_team import TeamMember
from group.serializers.party import PartySerializer, PartyDetailSerializer, PartyListSerializer, \
    MembershipCreateSerializer, MembershipSerializer
from matzip.handler import request_data_handler
from ..constants import MembershipStatus


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.get_today_party_list()
    # queryset = Party.objects.all()
    serializer_class = {
        'create': PartySerializer,
        'list': PartyListSerializer,
        'retrieve': PartyDetailSerializer
    }
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset.order_by(F('closed_at').desc(nulls_first=True), '-created_at')
        return queryset

    def get_serializer_context(self):
        context = super(PartyViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return self.serializer_class['create']
        if self.action == 'retrieve':
            return self.serializer_class['retrieve']
        return self.serializer_class['list']

    def list(self, request, *args, **kwargs):
        queryset = self.queryset.order_by('id')
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)

        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = queryset.filter(team=team_member.team)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        party = get_object_or_404(self.queryset, pk=pk)
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = self.get_serializer(party)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data = request_data_handler(request.data, ['name'], ['description'])
        if Party.objects.filter(team=team_member.team, name=data['name']).first():
            return Response({'message': '파티명이 사용중입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data['team'] = team_member.team.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(instance=serializer.instance)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            party = Party.objects.get(pk=pk)
            if 'date' in data:
                data['date'] = parse_datetime(data['date'])
            serializer = self.get_serializer(instance=party, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data={**serializer.data, 'message': '파티가 업데이트 되었습니다.'}, status=status.HTTP_200_OK)
        except Party.DoesNotExist:
            return Response({'message': '파티를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def close(self, request, pk=None):
        try:
            party = Party.objects.get(pk=pk)
            now = datetime.datetime.now()
            party.closed_at = now
            party.save()
            serializer = PartySerializer(party)
            return Response(data={**serializer.data, 'message': '파티가 종료되었습니다.'}, status=status.HTTP_200_OK)
        except Party.DoesNotExist:
            return Response({'message': '파티를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            party = Party.objects.get(pk=pk)
            party.delete()
            return Response(data={'message': '파티를 삭제했습니다.'}, status=status.HTTP_200_OK)
        except Party.DoesNotExist:
            return Response({'message': '파티를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipCreateSerializer
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        page = self.paginate_queryset(queryset)
        serializer = MembershipSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        membership = get_object_or_404(self.queryset, pk=pk)
        serializer = MembershipSerializer(membership)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def join(self, request, *args, **kwargs):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data = request_data_handler(request.data, ['party'], ['invite_reason'])

        same_membership = Membership.objects.filter(team_member=team_member.id, party=data['party']).first()
        now = datetime.datetime.now()
        if same_membership:
            if same_membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입한 파티입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if same_membership.status == MembershipStatus.WAITING:
                same_membership.status = MembershipStatus.ALLOWED
                same_membership.date_joined = now
                same_membership.save()
                serializer = MembershipSerializer(same_membership)
            else:
                return Response({'message': '가입할 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data['team_member'] = team_member.id
            data['date_joined'] = now
            serializer = MembershipCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = MembershipSerializer(serializer.instance)
        return Response(data={**serializer.data, 'message': '파티에 가입했습니다.'}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    def invite(self, request, *args, **kwargs):
        user = request.user
        data = request_data_handler(request.data, ['party', 'receiver'], ['invite_reason'])
        team_member_id = data['receiver']
        team_member = TeamMember.objects.filter(id=team_member_id).first()
        if not team_member:
            return Response({'message': '존재하지 않는 회원입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        invite_member = TeamMember.objects.get_my_team_profile(user=user)
        if not invite_member:
            return Response({'message': '초대 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        party = Party.objects.filter(id=data['party']).first()
        if not party:
            return Response({'message': '존재하지 않는 파티입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        same_membership = Membership.objects.filter(team_member=team_member_id, party=data['party']).first()
        if same_membership:
            same_membership = same_membership
            if same_membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입한 파티입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if same_membership.status == MembershipStatus.WAITING.value:
                return Response({'message': '이미 초대한 파티입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data['team_member'] = team_member_id
        data['invite_member'] = invite_member.id
        data['status'] = MembershipStatus.WAITING.value
        data.pop('receiver')
        serializer = MembershipCreateSerializer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = MembershipSerializer(serializer.instance)
        return Response(data={**serializer.data, 'message': '파티에 초대했습니다.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def accept(self, request, pk=None, *args, **kwargs):
        user = request.user
        try:
            membership = Membership.objects.get(id=pk)
            if membership.team_member.user.id != user.id:
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입되었습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.WAITING.value:
                membership.status = MembershipStatus.ALLOWED.value
                membership.save()
                serializer = MembershipSerializer(membership)
                return Response(data={**serializer.data, 'message': '파티에 가입했습니다.'}, status=status.HTTP_200_OK)
            return Response({'message': '파티에 가입할 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Membership.DoesNotExist:
            return Response({'message': '존재하지 않는 초대입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def refuse(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            membership = Membership.objects.get(id=pk)
            if membership.team_member.user.id != user.id:
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입되었습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.WAITING.value:
                membership.status = MembershipStatus.DENIED.value
                membership.save()
                serializer = MembershipSerializer(membership)
                return Response(data={**serializer.data, 'message': '파티 초대를 거절했습니다.'}, status=status.HTTP_200_OK)
            return Response({'message': '초대를 거절하지 못했습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Membership.DoesNotExist:
            return Response({'message': '존재하지 않는 초대입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['GET'])
    def my_invite_list(self, request, *args, **kwargs):
        user = request.user
        my_team_profile = TeamMember.objects.get_my_team_profile(user)

        queryset = self.queryset.filter(status=MembershipStatus.WAITING.value).filter(Q(team_member=my_team_profile.id) | Q(invite_member=my_team_profile.id))\
            .order_by(F('invite_member').desc(nulls_first=True), '-created_at')
        page = self.paginate_queryset(queryset)
        serializer = MembershipSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            membership = Membership.objects.get(pk=pk)
            membership.delete()
            return Response({'message': '파티에서 탈퇴했습니다.'}, status=status.HTTP_200_OK)
        except Membership.DoesNotExist:
            return Response({'message': '파티 가입 이력이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def create(self, request, *args, **kwargs):
        data = request.data
        party = data['party']
        user = data['user']

        same_membership = Membership.objects.filter(team_member__user=user, party=party).first()
        if same_membership:
            return Response({'message': 'the same membership exists'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        serializer = MembershipCreateSerializer(data=data)

        if serializer.is_valid():
            membership = Membership.objects.create(**serializer.validated_data)
            membership.save()
            return Response({'id': membership.pk}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data

        instance = Membership.objects.get(pk=pk)
        serializer = MembershipCreateSerializer(instance, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
