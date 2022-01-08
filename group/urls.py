from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views_invite import InviteViewSet
from .views_party import PartyViewSet, MembershipViewSet, VoteViewSet, TagViewSet
from .views_team import TeamMemberViewSet, TeamViewSet
router = routers.DefaultRouter()
router.register(r'party', PartyViewSet)
router.register(r'vote', VoteViewSet)
router.register(r'membership', MembershipViewSet)
router.register(r'invite', InviteViewSet)
router.register(r'team', TeamViewSet)
router.register(r'member', TeamMemberViewSet)
router.register(r'tag', TagViewSet)

urlpatterns = [
    path('', include(router.urls))
]
