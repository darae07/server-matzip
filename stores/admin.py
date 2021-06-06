from django.contrib import admin
from .models import Store
from .models import Dong
from .models import Menu
from .models import Category

# Register your models here.
admin.site.register(Store)
admin.site.register(Dong)
admin.site.register(Menu)
admin.site.register(Category)