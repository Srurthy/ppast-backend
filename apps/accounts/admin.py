from django.contrib import admin

# Register your models here.
from .models import User, EnterpriseMemberProfile, UserType

admin.site.register(User)
admin.site.register(EnterpriseMemberProfile)
admin.site.register(UserType)