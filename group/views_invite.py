# invite -> 파티 초대로 변경
# r - 나의 초대 목록
# c - 파티 - 유저 동일한 항목은 유일해야함
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from matzip.handler import request_data_handler
from .models_party import Party
from .models_team import Invite, TeamMember
from rest_framework import viewsets, status
from .serializer import InviteSerializer, InviteCreateSerializer
from .serializers.party import MembershipCreateSerializer
from django.db.models import Q
from .constants import InviteStatus


# 파티 초대 기능
class InviteViewSet(viewsets.ModelViewSet):
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = self.queryset.filter(receiver__user=user, status=InviteStatus.WAITING.value)\
            .order_by('-date_invited')
        return queryset

    def create(self, request, *args, **kwargs):
        data = request_data_handler(request.data, ['receiver', 'party'])

        same_invite = Invite.objects.filter(Q(receiver=data['receiver']) & Q(party=data['party']))
        if same_invite:
            return Response({'message': '이미 초대된 회원입니다.'},
                            status=status.HTTP_400_BAD_REQUEST)

        try:
            party = Party.objects.get(id=data['party'])
        except Party.DoesNotExist:
            return Response({'message': '파티를 찾을 수 없습니다.'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        try:
            sender = TeamMember.objects.get(team=party.team.id, user=request.user.id)
        except TeamMember.DoesNotExist:
            return Response({'message': '팀 멤버가 아닙니다.'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)

        data['party_id'] = party.id
        data['sender'] = sender.id
        serializer = InviteCreateSerializer(data=data)
        if serializer.is_valid():
            invite = Invite.objects.create(**serializer.validated_data)
            invite.save()
            serializer = InviteCreateSerializer(instance=invite)
            return Response({**serializer.data, 'message': '초대했습니다.'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        instance = self.get_object()
        if instance.status == InviteStatus.ACCEPTED.value:
            return Response({'message': '이미 승인된 초대입니다.'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        membership = MembershipCreateSerializer(data={'team_member': instance.receiver.id, 'party': instance.party.id})
        if membership.is_valid():
            membership.save()
            instance.status = InviteStatus.ACCEPTED.value
            instance.save()
            return Response(membership.data, status=status.HTTP_200_OK)
        return Response(membership.errors, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, pk, *args, **kwargs):
        data = request.data
        invite = Invite.objects.get(pk=pk)
        serializer = self.serializer_class(invite, data=data, partial=True)
        if serializer.is_valid():
            serializer.save(**serializer.validated_data)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk, *args, **kwargs):
        try:
            invite = Invite.objects.get(pk=pk)
        except Invite.DoesNotExist:
            return Response({'message': '초대를 찾을수 없습니다.'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        invite.delete()
        return Response({'message': '초대를 거절했습니다.'},
                        status=status.HTTP_200_OK)

