from typing import Any

from django.db import models
from django.utils.timezone import now as tz_now


class Tag(models.Model):
    class TagState(models.TextChoices):
        PROPOSED = "PROPOSED", "Proposed"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    name = models.CharField(
        max_length=150, unique=True, help_text="The tag value itself."
    )
    excerpt = models.TextField(blank=True, help_text="A short description of the tag.")
    parent_tag = models.ForeignKey(
        "self",
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        help_text="A parent tag for which this acts as a synonym.",
    )
    tag_state = models.CharField(
        max_length=150,
        choices=TagState.choices,
        default=TagState.PROPOSED,
        help_text="The state of this tag.",
    )
    created_at = models.DateTimeField(
        default=tz_now, help_text="When this tag was created."
    )
    updated_at = models.DateTimeField(
        default=tz_now, help_text="When this tag was last updated (at database level)."
    )
    accepted_at = models.DateTimeField(
        blank=True,
        null=True,
        help_text="When this tag was accepted.",
    )
    rejected_at = models.DateTimeField(
        blank=True,
        null=True,
        default=tz_now,
        help_text="When this tag was rejected.",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "tag"
        verbose_name_plural = "tags"

    def __str__(self) -> str:
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
        self.save(update_fields=["tag_state", "accepted_at"])

    def reject(self) -> None:
        self.tag = self.TagState.REJECTED
        self.rejected_at = tz_now()
        self.save(update_fields=["tag_state", "rejected_at"])
