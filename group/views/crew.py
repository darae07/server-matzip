import datetime

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.models_crew import Crew, CrewMembership
from group.models_team import TeamMember
from group.serializers.crew import CrewListSerializer, CrewDetailSerializer, CrewSerializer
from matzip.handler import request_data_handler


class CrewViewSet(viewsets.ModelViewSet):
    queryset = Crew.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = self.queryset.filter(team=team_member.team.id).order_by('id')
        page = self.paginate_queryset(queryset)
        serializer = CrewListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        crew = get_object_or_404(self.queryset, pk=pk)
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        serializer = CrewDetailSerializer(crew)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data = request_data_handler(request.data, ['name'], ['title'])
        if Crew.objects.filter(team=team_member.team.id, name=data['name']).first():
            return Response({'message': '크루명이 사용중입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data['team'] = team_member.team.id

        serializer = CrewSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        now = datetime.datetime.now()
        membership = CrewMembership(team_member=team_member, crew=serializer.instance, date_joined=now)
        membership.save()
        serializer = CrewDetailSerializer(instance=serializer.instance)
        return Response({'message': '크루를 생성했습니다.', **serializer.data}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data
        try:
            crew = Crew.objects.get(pk=pk)
            serializer = CrewSerializer(instance=crew, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(data={'message': '크루가 업데이트 되었습니다.', **serializer.data}, status=status.HTTP_200_OK)
        except Crew.DoesNotExist:
            return Response({'message': '크루를 찾을 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['GET'])
    def my_crew(self, request):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        my_crew_membership_list = CrewMembership.objects.filter(team_member=team_member).values('crew')
        queryset = self.queryset.filter(team=team_member.team.id, id__in=my_crew_membership_list)
        my_crew = queryset.first()
        if my_crew:
            serializer = CrewDetailSerializer(my_crew)
            return Response({'message': '나의 크루를 불러왔습니다.', **serializer.data}, status=status.HTTP_200_OK)
        return Response({'message': '나의 크루를 찾을 수 없습니다.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'], parser_classes=[MultiPartParser, FormParser])
    def upload_image(self, request, pk=None):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            crew = Crew.objects.get(id=pk)
            my_crew_membership_list = CrewMembership.objects.filter(team_member=team_member).values('crew')
            if not my_crew_membership_list.filter(crew=pk).first():
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Crew.DoesNotExist:
            return Response({'message': '크루를 찾을 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        if request.FILES:
            request.data.image = request.FILES
        serializer = CrewSerializer(crew, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        serializer = CrewDetailSerializer(instance=serializer.instance)
        return Response({'message': '크루 이미지를 등록했습니다.', **serializer.data}, status=status.HTTP_200_OK)
