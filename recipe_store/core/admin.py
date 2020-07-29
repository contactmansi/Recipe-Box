from django.contrib import admin
# Here import the built-in userAdmin as BaseUserAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models
from django.utils.translation import gettext as _
# Register your models here.

# Create custome user admin extending Base


class UserAdmin(BaseUserAdmin):
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None,               {'fields': ('email', 'password')}),
        (_('Personal Info'), {'fields': ('name',)}),
        (_('Permissions'),   {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    # Django admin documentation : Add fieldsets which defines the fields u add in the add page
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Tag)
admin.site.register(models.Ingredient)
