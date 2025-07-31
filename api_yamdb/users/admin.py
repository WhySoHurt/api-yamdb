from django.contrib import admin

from .models import MyUser

admin.site.empty_value_display = 'Не задано'


@admin.register(MyUser)
class MyUserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'bio',
        'role'
    )
