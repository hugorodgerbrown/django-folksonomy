from typing import Iterable

from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext as _, gettext_lazy as _lazy

from .models import Tag, TagCategory


@admin.register(TagCategory)
class TagCategoryAdmin(admin.ModelAdmin):
    list_display = ["name", "created_at"]
    readonly_fields = ["created_at"]
    search_fields = ["name"]


class IsSynonymFilter(admin.SimpleListFilter):
    title = _("synonym")
    parameter_name = "parent_tag"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> Iterable[tuple[str, str]]:
        return (
            ("no", _("Is root tag")),
            ("yes", _("Is tag synonym / alias")),
        )

    def queryset(
        self, request: HttpRequest, queryset: models.QuerySet[Tag]
    ) -> models.QuerySet[Tag]:
        if self.value() == "yes":
            return queryset.exclude(parent_tag__isnull=True)
        if self.value() == "no":
            return queryset.filter(parent_tag__isnull=True)
        return queryset


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "is_root_tag",
        "parent_tag",
        "tag_state",
        "categories_",
        "created_at",
    ]
    list_filter = [IsSynonymFilter, "tag_state", "categories"]
    raw_id_fields = ["parent_tag", "categories"]
    readonly_fields = [
        "tag_state",
        "created_at",
        "updated_at",
        "accepted_at",
        "rejected_at",
    ]
    search_fields = ["name", "excerpt"]
    actions = ["accept_tags", "reject_tags"]

    @admin.display(description=_lazy("Tag Categories"))
    def categories_(self, obj: Tag) -> str:
        """Return all of the categories as a comma-separated string."""
        return obj.get_category_display()

    @admin.display(description=_lazy("is root tag (!=alias)"), boolean=True)
    def is_root_tag(self, obj: Tag) -> bool:
        """Return True if this tag is a root tag (i.e. not an alias)."""
        return obj.parent_tag is None

    @admin.action(description=_lazy("Accept selected tag(s)"))
    def accept_tags(self, request: HttpRequest, queryset: models.QuerySet[Tag]) -> None:
        accepted = 0
        for tag in queryset:
            tag.accept()
            accepted += 1
        self.message_user(
            request, _("Accepted {accepted} tags.".format(accepted=accepted))
        )

    @admin.action(description=_lazy("Reject selected tag(s)"))
    def reject_tags(self, request: HttpRequest, queryset: models.QuerySet[Tag]) -> None:
        rejected = 0
        for tag in queryset:
            tag.reject()
            rejected += 1
        self.message_user(request, f"Rejected {rejected} tag(s).")
