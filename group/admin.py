from django.contrib import admin
from .models import Company, Contract, Party, Membership

# Register your models here.
admin.site.register(Company)
admin.site.register(Contract)
admin.site.register(Party)
admin.site.register(Membership)