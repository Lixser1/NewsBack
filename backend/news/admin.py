from django.contrib import admin

from .models import News


@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ("title", "author_role", "created_at", "updated_at")
    list_filter = ("author_role",)
    search_fields = ("title", "body")
    readonly_fields = ("created_at", "updated_at")
