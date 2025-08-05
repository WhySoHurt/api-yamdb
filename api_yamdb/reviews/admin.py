from django.contrib import admin

from .models import YamdbUser, Category, Genre, Title, Review, Comment

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


@admin.register(Category, Genre)
class NameSlugAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Title)
class TitleAdmin(admin.ModelAdmin):
    list_display = ('name', 'year', 'category')
    list_filter = ('year', 'category')
    search_fields = ('name',)
    filter_horizontal = ('genre',)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('author', 'title', 'score', 'pub_date')
    list_filter = ('score', 'pub_date', 'title')
    search_fields = ('text', 'author__username', 'title__name')
    readonly_fields = ('pub_date',)
    raw_id_fields = ('author', 'title')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'review', 'text', 'pub_date')
    list_filter = ('pub_date', 'author')
    search_fields = ('text', 'author__username', 'review__text')
    readonly_fields = ('pub_date',)
    raw_id_fields = ('author', 'review')
