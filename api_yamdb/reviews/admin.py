from django.contrib import admin

from .models import YamdbUser

admin.site.empty_value_display = 'Не задано'


@admin.register(YamdbUser)
class YamdbUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role'
    )
