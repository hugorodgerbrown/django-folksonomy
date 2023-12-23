from typing import Iterable

from django.contrib import admin
from django.db import models
from django.http import HttpRequest
from django.utils.translation import gettext as _, gettext_lazy as _lazy

from .models import TagBase


class IsSynonymFilter(admin.SimpleListFilter):
    title = _("synonym / alias")
    parameter_name = "alias"

    def lookups(
        self, request: HttpRequest, model_admin: admin.ModelAdmin
    ) -> Iterable[tuple[str, str]]:
        return (
            ("no", _("Is not an alias")),
            ("yes", _("Is an alias tag")),
        )

    def queryset(
        self, request: HttpRequest, queryset: models.QuerySet[TagBase]
    ) -> models.QuerySet[TagBase]:
        if self.value() == "yes":
            return queryset.exclude(parent_tag__isnull=True)
        if self.value() == "no":
            return queryset.filter(parent_tag__isnull=True)
        return queryset


class TagAdminBase(admin.ModelAdmin):
    list_display = [
        "name",
        "is_root_tag",
        "is_alias_for",
        "approval_state",
        "created_at",
    ]
    list_filter = [IsSynonymFilter, "approval_state"]
    raw_id_fields = ["is_alias_for"]
    readonly_fields = [
        "approval_state",
        "created_at",
        "updated_at",
        "accepted_at",
        "rejected_at",
    ]
    search_fields = ["name", "excerpt"]
    actions = ["accept_tags", "reject_tags"]

    @admin.display(description=_lazy("root tag (i.e. not an alias)"), boolean=True)
    def is_root_tag(self, obj: TagBase) -> bool:
        """Return True if this tag is a root tag (i.e. not an alias)."""
        return obj.is_alias_for is None

    @admin.action(description=_lazy("Accept selected tag(s)"))
    def accept_tags(
        self, request: HttpRequest, queryset: models.QuerySet[TagBase]
    ) -> None:
        accepted = 0
        for tag in queryset:
            tag.accept()
            accepted += 1
        self.message_user(
            request, _("Accepted {accepted} tags.".format(accepted=accepted))
        )

    @admin.action(description=_lazy("Reject selected tag(s)"))
    def reject_tags(
        self, request: HttpRequest, queryset: models.QuerySet[TagBase]
    ) -> None:
        rejected = 0
        for tag in queryset:
            tag.reject()
            rejected += 1
        self.message_user(request, f"Rejected {rejected} tag(s).")
