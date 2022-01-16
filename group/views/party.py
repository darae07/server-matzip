from django.db.models import F
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import datetime

from group.models_party import Party
from group.models_team import TeamMember
from group.serializers.party import PartySerializer, PartyDetailSerializer, PartyListSerializer
from matzip.handler import request_data_handler


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.get_today_party_list()
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
        if Party.objects.filter(team=team_member.team, name=data['name']):
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
