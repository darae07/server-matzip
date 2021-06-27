from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Company, Contract
from rest_framework import viewsets, permissions
from .serializer import CompanySerializer, CompanyMemberSerializer
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