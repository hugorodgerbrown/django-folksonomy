from typing import Any

from django.db import models
from django.utils.timezone import now as tz_now
from django.utils.translation import gettext_lazy as _lazy


class TagBase(models.Model):
    class TagState(models.TextChoices):
        PROPOSED = "PROPOSED", "Proposed"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    name = models.CharField(
        max_length=150, unique=True, help_text=_lazy("The tag value itself.")
    )
    excerpt = models.TextField(
        blank=True, help_text=_lazy("A short description of the tag.")
    )
    is_alias_for = models.ForeignKey(
        "self",
        verbose_name="is an alias for",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text=_lazy(
            "A parent tag for which this acts as an alias.",
        ),
    )
    approval_state = models.CharField(
        max_length=150,
        choices=TagState.choices,
        default=TagState.PROPOSED,
        help_text=_lazy("Whether this has been accepted as a valid tag."),
    )
    created_at = models.DateTimeField(
        default=tz_now, help_text=_lazy("When this tag was created.")
    )
    updated_at = models.DateTimeField(
        default=tz_now,
        help_text=_lazy("When this tag was last updated (at database level)."),
    )
    accepted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_lazy(
            "When this tag was accepted.",
        ),
    )
    rejected_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_lazy(
            "When this tag was rejected.",
        ),
    )

    class Meta:
        abstract = True
        ordering = ["name"]

    def __str__(self) -> str:
        if self.is_alias_for:
            return f"{self.name} (alias for {self.is_alias_for.name})"
        return self.name

    @property
    def is_accepted(self) -> bool:
        return self.tag_state == self.TagState.ACCEPTED

    @property
    def is_proposed(self) -> bool:
        return self.tag_state == self.TagState.PROPOSED

    @property
    def is_rejected(self) -> bool:
        return self.tag_state == self.TagState.REJECTED

    def save(self, **kwargs: Any) -> None:
        self.updated_at = tz_now()
        super().save(**kwargs)

    def accept(self) -> None:
        self.tag_state = self.TagState.ACCEPTED
        self.accepted_at = tz_now()
        self.rejected_at = None
        self.save(update_fields=["tag_state", "accepted_at", "rejected_at"])

    def reject(self) -> None:
        self.tag = self.TagState.REJECTED
        self.rejected_at = tz_now()
        self.accepted_at = None
        self.save(update_fields=["tag_state", "rejected_at", "accepted_at"])
