from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Company, Contract, Vote, Party, Membership, Invite
from rest_framework import viewsets, permissions, status, generics
from .serializer import CompanySerializer, CompanyMemberSerializer, VoteSerializer, PartySerializer, \
    MembershipSerializer, InviteSerializer
from common.models import CommonUser
from rest_framework.decorators import api_view, permission_classes


# Create your views here.
class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer


class CompanyMemberViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanyMemberSerializer


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def my_company_member(request):
    user_id = request.user.id
    contract = Contract.objects.filter(user_id=user_id).first()
    print(contract)
    if not contract:
        return Response('user`s company is not defined', status=204)
    company_id = contract.company_id
    company = Company.objects.get(pk=company_id)
    serializer = CompanyMemberSerializer(company)
    return Response(serializer.data)


# class MyCompanyMemberView(APIView):
#     def get(self, request):
#         try:
#             user_id = request.user.id
#             contract = Contract.objects.get(user_id=user_id)
#             company = Company.objects.get(contract_id=contract.id)
#             serializer = CompanyMemberSerializer(company)
#             return Response(serializer.data)
#         except Contract.DoseNotExist:
#             return Response('user`s company is not defined')

class VoteViewSet(viewsets.ModelViewSet):
    queryset = Vote.objects.all()
    serializer_class = VoteSerializer


class PartyViewSet(viewsets.ModelViewSet):
    queryset = Party.objects.all()
    serializer_class = PartySerializer


class MembershipViewSet(viewsets.ModelViewSet):
    queryset = Membership.objects.all()
    serializer_class = MembershipSerializer

    def get_queryset(self):
        queryset = Membership.objects.all()
        state = self.request.query_params.get('status')

        if state is not None:
            queryset = queryset.filter(status=state)
            return queryset


class InviteViewSet(viewsets.ModelViewSet):
    queryset = Invite.objects.all()
    serializer_class = InviteSerializer


@api_view(['GET'])
@permission_classes((permissions.AllowAny,))
def my_invite(request):
    user_id = request.user.id
    invite = Invite.objects.filter(receiver=user_id).first()
    if not invite:
        return Response('isn`t exist invitation', status=406)
    serializer = InviteSerializer(invite)
    return Response(serializer.data)


class MyInvitedParty(generics.ListAPIView):
    serializer_class = MembershipSerializer

    def get_queryset(self):
        user = self.request.user
        return Membership.objects.filter(user=user)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def voting(request):
    print(request.method)
    if request.method == 'POST':
        user_id = request.user.id
        membership = Membership.objects.filter(user=user_id, party=request.data['party']).first()
        if not membership:
            return Response('isn`t exist membership', status=406)
        serializer = MembershipSerializer(membership.update(vote=request.data['vote']))
        if serializer.is_valid():
            membership.set_vote(serializer.validated_data['vote'])
            membership.save()
            return Response(serializer.data, status=200)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
