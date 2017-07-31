from django.contrib import admin
from .models import MediaWikiUser
from .mediawiki import (
    get_django_user_from_mediawiki_user,
    get_or_create_django_user_from_mediawiki_user
)


@admin.register(MediaWikiUser)
class MediaWikiUserAdmin(admin.ModelAdmin):
    list_per_page = 20
    list_display = (
        'name', 'real_name', 'email', 'last_accessed', 'registered', 'edit_count', 'linked'
    )
    search_fields = (
        'name', 'real_name', 'email'
    )
    fields = readonly_fields = ('id',)+list_display

    def get_actions(self, request):
        return {'link': (MediaWikiUserAdmin.link, 'link', "Link selected MediaWiki users into django")}

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def link(self, request, queryset):
        users = []
        for user in queryset:
            _, created = get_or_create_django_user_from_mediawiki_user(user)
            if created:
                users.append("'{}'".format(user.name))
        self.message_user(request, "%s successfully linked.".format(', '.join(users)))

    def linked(self, obj):
        return bool(get_django_user_from_mediawiki_user(obj))
    linked.boolean = True
    linked.short_description = 'Linked'
