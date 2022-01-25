from django.urls import path
from django.conf.urls import include
from rest_framework import routers
from .views_invite import InviteViewSet
from .views_party import VoteViewSet, TagViewSet
from .views.team import TeamViewSet, TeamMemberViewSet
from .views.party import PartyViewSet, MembershipViewSet
from .views.crew import CrewViewSet, CrewMembershipViewSet

router = routers.DefaultRouter()
router.register(r'party', PartyViewSet)
router.register(r'vote', VoteViewSet)
router.register(r'party_membership', MembershipViewSet)
router.register(r'invite', InviteViewSet)
router.register(r'team', TeamViewSet)
router.register(r'member', TeamMemberViewSet)
router.register(r'tag', TagViewSet)
router.register(r'crew', CrewViewSet)
router.register(r'crew_membership', CrewMembershipViewSet)

urlpatterns = [
    path('', include(router.urls))
]
