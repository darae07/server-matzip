from django.contrib import admin
from .models import Company,  Party, Membership, Contract, Vote, Invite

# Register your models here.
admin.site.register(Company)
admin.site.register(Contract)
admin.site.register(Party)
admin.site.register(Membership)
admin.site.register(Vote)
admin.site.register(Invite)
