from django.db.models import F, Q
from django.utils.dateformat import DateFormat
from django.utils.dateparse import parse_datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
import datetime

from group.models_party import Party, Membership
from group.models_team import TeamMember
from group.serializers.party import PartySerializer, PartyDetailSerializer, PartyListSerializer, \
    MembershipCreateSerializer, MembershipSerializer
from matzip.handler import request_data_handler
from reviews.models import Review, ReviewImage
from stores.models import Keyword, Category
from ..constants import MembershipStatus
from matzip.utils.datetime_func import today_min, today_max
from matzip.pagination import Pagination


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.get_today_party_list()
    serializer_class = {
        'create': PartySerializer,
        'list': PartyListSerializer,
        'retrieve': PartyDetailSerializer
    }
    permission_classes = [IsAuthenticated]
    pagination_class = Pagination
    pagination_class.page_size = 6

    def get_queryset(self):
        queryset = super(PartyViewSet, self).get_queryset()
        return queryset.objects.get_today_party_list().order_by(F('closed_at').desc(nulls_first=True), '-created_at')

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
        queryset = self.queryset.order_by(F('closed_at').desc(nulls_first=True), '-created_at')
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)

        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = queryset.filter(team=team_member.team).prefetch_related('membership')

        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(keyword__category=category)
        page = self.paginate_queryset(queryset)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['GET'])
    def my_party(self, request, *args, **kwargs):
        queryset = self.queryset
        user = request.user
        team_member = TeamMember.objects.get_my_team_profile(user=user)
        if not team_member:
            return Response({'message': '팀 권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        queryset = queryset.prefetch_related('membership').filter(membership__team_member=team_member)
        serializer = PartyListSerializer(queryset, many=True)
        return Response(serializer.data)

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

        data = request_data_handler(request.data, ['name', 'keyword'],
                                    ['description', 'category', 'use_kakaomap', 'use_team_location'])
        if Party.objects.filter(team=team_member.team, name=data['name'], created_at__range=(today_min, today_max))\
                .first():
            return Response({'message': '파티명이 사용중입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        category = Category.objects.filter(id=data['category']).first()
        keyword = Keyword.objects.hit_keyword(name=data['keyword'], use_kakaomap=data['use_kakaomap'],
                                              use_team_location=data['use_team_location'],
                                              team=team_member.team, category=category)
        data['team'] = team_member.team.id
        data['keyword'] = keyword.id
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        now = datetime.datetime.now()
        membership = Membership(team_member=team_member, party=serializer.instance, date_joined=now)
        membership.save()
        serializer = PartyDetailSerializer(instance=serializer.instance)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def partial_update(self, request, pk=None, *args, **kwargs):
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
            if party.eat:
                return Response({'message': '이미 식사한 메뉴입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            now = datetime.datetime.now()
            party.closed_at = now
            party.keyword.eat_count += 1
            party.eat = True
            party.save()
            party.keyword.save()
            serializer = PartyDetailSerializer(party)
            return Response(data={**serializer.data, 'message': '식사 완료 기록을 생성했습니다.'}, status=status.HTTP_200_OK)
        except Party.DoesNotExist:
            return Response({'message': '오늘의 메뉴를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    # 맛있다 누른 경우
    @action(detail=True, methods=['POST'], parser_classes=[MultiPartParser, FormParser])
    def close_with_review(self, request, pk=None, *args, **kwargs):
        try:
            party = Party.objects.get(pk=pk)
            if party.eat:
                return Response({'message': '이미 식사한 메뉴입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            data = request_data_handler(request.data, None, ['content', 'score'])
            user = request.user
            team_member = TeamMember.objects.get_my_team_profile(user=user)
            review = Review.objects.create(keyword=party.keyword.id, content=data['content'], score=data['score'],
                                           team_member=team_member.id)
            if request.FILES:
                for image in request.FILES.getlist('image'):
                    review_image = ReviewImage.objects.create(review=review.id, image=image)
                    review_image.keyword = party.keyword
                    review_image.save()
                    if not review_image:
                        return Response({'message': '식사 리뷰를 등록할 수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

            serializer = PartyDetailSerializer(party)
            now = datetime.datetime.now()
            party.closed_at = now
            party.keyword.eat_count += 1
            party.eat = True
            party.save()
            party.keyword.save()
            return Response({'message': '식사 리뷰를 등록했습니다.', **serializer.data}, status=status.HTTP_200_OK)
        except Party.DoesNotExist:
            return Response({'message': '오늘의 메뉴를 찾을수 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

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
            if same_membership.status == MembershipStatus.WAITING.value:
                same_membership.status = MembershipStatus.ALLOWED.value
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
    # TODO 여러명 한번에 초대 되게 하기(배열)
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

    @action(detail=True, methods=['POST'])
    def cancel(self, request, pk, *args, **kwargs):
        user = request.user
        try:
            membership = Membership.objects.get(id=pk)
            if membership.invite_member.user.id != user.id:
                return Response({'message': '권한이 없습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.ALLOWED.value:
                return Response({'message': '이미 가입되었습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
            if membership.status == MembershipStatus.WAITING.value:
                membership.delete()
                return Response(data={'message': '파티 초대를 취소했습니다.'}, status=status.HTTP_200_OK)
            return Response({'message': '초대를 취소하지 못했습니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)
        except Membership.DoesNotExist:
            return Response({'message': '존재하지 않는 초대입니다.'}, status=status.HTTP_406_NOT_ACCEPTABLE)

    @action(detail=False, methods=['GET'])
    def my_invite_list(self, request, *args, **kwargs):
        user = request.user
        my_team_profile = TeamMember.objects.get_my_team_profile(user)

        queryset = self.queryset.filter(status=MembershipStatus.WAITING.value)\
            .filter(Q(team_member=my_team_profile.id) | Q(invite_member=my_team_profile.id))\
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
