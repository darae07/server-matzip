from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from matzip.handler import request_data_handler
from .models_team import TeamMember
from rest_framework import viewsets, status
from group.serializers.team_member import TeamMemberSerializer, TeamMemberCreateSerializer
from rest_framework.parsers import MultiPartParser, FormParser


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

