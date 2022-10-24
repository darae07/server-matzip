from django.contrib import admin
from .models_crew import Vote
from .models_team import Invite, TeamMember, Team
from .models_party import Party, Membership

# Register your models here.
admin.site.register(Party)
admin.site.register(Membership)
admin.site.register(Vote)
admin.site.register(Invite)
admin.site.register(TeamMember)
admin.site.register(Team)
