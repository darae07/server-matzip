import datetime

from django.db.models import Q, F, Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from group.constants import MembershipStatus
from group.models_crew import Crew, CrewMembership, Lunch, Vote
from group.models_team import TeamMember
from group.serializers.crew import CrewListSerializer, CrewDetailSerializer, CrewSerializer, \
    CrewMembershipSerializer, CrewMembershipCreateSerializer, LunchSerializer, LunchListSerializer, VoteSerializer, \
    VoteListSerializer
from matzip.handler import request_data_handler
from stores.models import Category, Keyword


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
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        crew = self.queryset.filter(id=pk) \
            .prefetch_related(Prefetch('lunches', Lunch.objects.get_today_lunch_list())).first()
        if crew:
            serializer = CrewDetailSerializer(crew)
            return Response(serializer.data)
        return Response({'message': '크루를 찾을 수 없습니다.'}, status=status.HTTP_404_NOT_FOUND)

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
        queryset = self.queryset.filter(team=team_member.team.id, id__in=my_crew_membership_list).order_by('created_at')
        page = self.paginate_queryset(queryset)
        serializer = CrewDetailSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

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
        serializer = CrewSerializer(instance=serializer.instance)
        return Response({'message': '크루 이미지를 등록했습니다.', **serializer.data}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['POST'])
    def delete_image(self, request, pk=None):
        try:
            crew = Crew.objects.get(id=pk)
        except Crew.DoesNotExist:
            return Response({'message': '크루를 찾을 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        crew.image.delete()
        crew.save()
        serializer = CrewSerializer(instance=crew)
        return Response({'message': '크루 이미지를 삭제했습니다.', **serializer.data}, status=status.HTTP_200_OK)


class CrewMembershipViewSet(viewsets.ModelViewSet):
    queryset = CrewMembership.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        queryset = self.queryset
        page = self.paginate_queryset(queryset)
        serializer = CrewMembershipSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        membership = get_object_or_404(self.queryset, pk=pk)
        serializer = CrewSerializer(membership)
        return Response(serializer.data)

    @action(detail=False, methods=['POST'])
    def join(self, request, *args, **kwargs):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data = request_data_handler(request.data, ['crew'], ['invite_reason'])

        same_membership = CrewMembership.objects.filter(team_member=team_member.id, crew=data['crew']).first()
        now = datetime.datetime.now()
        if same_membership:
            if same_membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입한 크루입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if same_membership.status == MembershipStatus.WAITING.value:
                same_membership.status = MembershipStatus.ALLOWED.value
                same_membership.date_joined = now
                same_membership.save()
                serializer = CrewMembershipSerializer(same_membership)
            else:
                return Response({'message': '가입할 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data['team_member'] = team_member.id
            data['date_joined'] = now
            serializer = CrewMembershipCreateSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = CrewMembershipSerializer(serializer.instance)
        return Response({'message': '크루에 가입했습니다.', **serializer.data}, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['POST'])
    # TODO 여러명 한번에 초대 되게 하기(배열)
    def invite(self, request):
        user = request.user
        data = request_data_handler(request.data, ['crew', 'receiver'], ['invite_reason'])
        team_member_id = data['receiver']
        team_member = TeamMember.objects.filter(id=team_member_id).first()
        if not team_member:
            return Response({'message': '존재하지 않는 회원입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        invite_member = TeamMember.objects.get_my_team_profile(user=user)
        if not invite_member:
            return Response({'message': '초대 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        crew = Crew.objects.filter(id=data['crew']).first()
        if not crew:
            return Response({'message': '존재하지 않는 크루입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        same_membership = CrewMembership.objects.filter(team_member=team_member_id, crew=data['crew']).first()
        if same_membership:
            if same_membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입한 크루입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if same_membership.status == MembershipStatus.WAITING.value:
                return Response({'message': '이미 초대한 크루입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data['team_member'] = team_member_id
        data['invite_member'] = invite_member.id
        data['status'] = MembershipStatus.WAITING.value
        data.pop('receiver')
        serializer = CrewMembershipCreateSerializer(data=data)

        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = CrewMembershipSerializer(serializer.instance)
        return Response(data={**serializer.data, 'message': '크루에 초대했습니다.'}, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['POST'])
    def accept(self, request, pk=None):
        user = request.user
        try:
            membership = CrewMembership.objects.get(id=pk)
            if membership.team_member.user.id != user.id:
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입되었습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.WAITING.value:
                membership.status = MembershipStatus.ALLOWED.value
                membership.save()
                serializer = CrewMembershipSerializer(membership)
                return Response({'message': '크루에 가입했습니다.', **serializer.data}, status=status.HTTP_200_OK)
        except CrewMembership.DoesNotExist:
            return Response({'message': '존재하지 않는 초대입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def refuse(self, request, pk=None):
        user = request.user
        try:
            membership = CrewMembership.objects.get(id=pk)
            if membership.team_member.user.id != user.id:
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입되었습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.WAITING.value:
                membership.status = MembershipStatus.DENIED.value
                membership.save()
                serializer = CrewMembershipSerializer(membership)
                return Response({'message': '크루 초대를 거절했습니다.', **serializer.data}, status=status.HTTP_200_OK)
            return Response({'message': '초대를 거절하지 못했습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except CrewMembership.DoesNotExist:
            return Response({'message': '존재하지 않는 초대입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['GET'])
    def my_invite_list(self, request):
        user = request.user
        my_team_profile = TeamMember.objects.get_my_team_profile(user)

        queryset = self.queryset.filter(status=MembershipStatus.WAITING.value)\
            .filter(Q(team_member=my_team_profile.id) | Q(invite_member=my_team_profile.id))\
            .order_by(F('invite_member').desc(nulls_first=True), '-created_at')
        page = self.paginate_queryset(queryset)
        serializer = CrewMembershipSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            membership = CrewMembership.objects.get(pk=pk)
            membership.delete()
            return Response({'message': '크루에서 탈퇴했습니다.'}, status=status.HTTP_200_OK)
        except CrewMembership.DoesNotExist:
            return Response({'message': '크루 가입 이력이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def partial_update(self, request, pk=None, *args, **kwargs):
        data = request.data

        instance = CrewMembership.objects.get(pk=pk)
        serializer = CrewMembershipCreateSerializer(instance, data=data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(**serializer.validated_data)
        serializer = CrewMembershipSerializer(serializer.instance)
        return Response({'message': '크루 멤버쉽을 업데이트 했습니다.', **serializer.data}, status=status.HTTP_200_OK)


class LunchViewSet(viewsets.ModelViewSet):
    queryset = Lunch.objects.get_today_lunch_list()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        data = request_data_handler(request.data, ['crew', 'keyword'], ['title', 'category'])
        category = Category.objects.filter(id=data['category']).first()
        keyword = Keyword.objects.hit_keyword(name=data['keyword'], team=team_member.team, category=category)
        same_lunch = self.queryset.filter(crew=data['crew'], keyword=keyword).first()
        if same_lunch:
            return Response({'message': '이미 있는 메뉴입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data['keyword'] = keyword.id
        serializer = LunchSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = LunchListSerializer(serializer.instance)
        return Response({'message': '점심을 생성했습니다.', **serializer.data})

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.queryset)
        serializer = LunchListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def partial_update(self, request, pk=None, *args, **kwargs):
        data = request.data
        try:
            lunch = Lunch.objects.get(pk=pk)
            serializer = LunchSerializer(instance=lunch, data=data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            serializer = LunchListSerializer(serializer.instance)
            return Response(data={**serializer.data, 'message': '점심이 업데이트 되었습니다.'}, status=status.HTTP_200_OK)
        except Lunch.DoesNotExist:
            return Response({'message': '점심을 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=True, methods=['POST'])
    def close(self, request, pk=None):
        try:
            lunch = Lunch.objects.get(pk=pk)
            if lunch.eat:
                return Response({'message': '이미 먹은 메뉴입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            lunch.keyword.eat_count += 1
            lunch.eat = True
            lunch.save()
            lunch.keyword.save()
            serializer = LunchListSerializer(lunch)
            return Response({'message': '점심을 먹었습니다.', **serializer.data}, status=status.HTTP_200_OK)
        except Lunch.DoesNotExist:
            return Response({'message': '점심을 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            lunch = Lunch.objects.get(pk=pk)
            lunch.delete()
            return Response({'message': '점심을 삭제했습니다.'}, status=status.HTTP_200_OK)
        except Lunch.DoesNotExist:
            return Response({'message': '점심을 찾을 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)


class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    permission_classes = [IsAuthenticated]

    def list(self, request, *args, **kwargs):
        page = self.paginate_queryset(self.queryset)
        serializer = VoteListSerializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    def retrieve(self, request, pk=None, *args, **kwargs):
        vote = get_object_or_404(self.queryset, pk=pk)
        serializer = VoteListSerializer(vote)
        return Response({'message': '투표를 불러왔습니다.', **serializer.data}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['lunch'])
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        same_vote = Vote.objects.filter(lunch=data['lunch'], team_member=team_member).first()
        if same_vote:
            return Response({'message': '이미 투표했습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data['team_member'] = team_member.id
        serializer = VoteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = VoteListSerializer(serializer.instance)
        return Response({'message': '성공적으로 투표했습니다.', **serializer.data}, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None, *args, **kwargs):
        try:
            vote = Vote.objects.get(pk=pk)
            vote.delete()
            return Response({'message': '성공적으로 투표를 철회했습니다.'}, status=status.HTTP_200_OK)
        except Vote.DoesNotExist:
            return Response({'message': '투표 이력이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)