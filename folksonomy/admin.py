from django.contrib import admin
from django.db import models
from django.http import HttpRequest

from .models import Tag


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "parent_tag",
        "created_at",
        "tag_state",
    ]
    list_filter = ["tag_state"]
    search_fields = ["name", "excerpt"]
    actions = ["accept_tags", "reject_tags"]

    @admin.action(description="Accept selected tags")
    def accept_tags(self, request: HttpRequest, queryset: models.QuerySet[Tag]) -> None:
        accepted = 0
        for tag in queryset:
            tag.accept()
            accepted += 1
        self.message_user(request, f"Accepted {accepted} tags.")

    @admin.action(description="Reject selected tags")
    def reject_tags(self, request: HttpRequest, queryset: models.QuerySet[Tag]) -> None:
        rejected = 0
        for tag in queryset:
            tag.reject()
            rejected += 1
        self.message_user(request, f"Rejected {rejected} tags.")
