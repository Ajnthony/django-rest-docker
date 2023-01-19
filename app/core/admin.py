"""
django admin page customisation
this seems to be updating/customising the admin page (like frontend)
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# won't be used here but for the future (translation)
from django.utils.translation import gettext_lazy as _
from core import models


class UserAdmin(BaseUserAdmin):
    # define admin pages for users
    ordering = ['id']
    list_display = ['email', 'name']

    # overriding the default fields django offers
    fieldsets = (
        (None, {'fields': ('email', 'password')}),  # title of None
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser',
                )
            }
        ),
        (_('Important dates'), {'fields': ('last_login',)}),
    )

    readonly_fields = ['last_login']

    # simply run the server, go ahead to the admin page
    # and see what happens with the following fields and ones above
    add_fieldsets = (
        (None, {
            'classes': ('wide',),  # this is more like css
            'fields': (
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser'
            )
        }),  # I need to check how tuples work with commas
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
admin.site.register(models.Tag)
