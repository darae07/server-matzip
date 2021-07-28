from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views_company import CompanyViewSet, ContractViewSet, InviteViewSet
from .views_party import PartyViewSet, MembershipViewSet

router = routers.DefaultRouter()
router.register(r'company', CompanyViewSet)
router.register(r'party', PartyViewSet)
# router.register(r'vote', VoteViewSet)
router.register(r'membership', MembershipViewSet)
router.register(r'invite', InviteViewSet)
router.register(r'contract', ContractViewSet)

urlpatterns = [
    path('', include(router.urls)),
]