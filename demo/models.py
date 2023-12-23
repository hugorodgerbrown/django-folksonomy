from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now as tz_now

from folksonomy.models import TagBase


class SkillCategory(models.Model):
    """Used to label skills for filtering and management purposes."""

    name = models.CharField(max_length=100, unique=True)
    created_at = models.DateTimeField(
        default=tz_now, help_text="When this category was created."
    )

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "tag categories"

    def __str__(self) -> str:
        return self.name


class UserSkill(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text="The user who has this skill.",
        related_name="user_skills",
    )
    skill = models.ForeignKey(
        "Skill",
        on_delete=models.CASCADE,
        help_text="The skill that the user has.",
        related_name="user_skills",
    )
    skill_level = models.PositiveSmallIntegerField(
        help_text="The level of skill that the user has.",
        default=1,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When this user skill was created.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When this user skill was last updated.",
    )


class Skill(TagBase):
    """A skill that a user has."""

    categories = models.ManyToManyField(
        SkillCategory,
        blank=True,
        related_name="category_skills",
        help_text="Skill classification categoreis - used for filtering etc.",
    )

    users = models.ManyToManyField(
        User,
        blank=True,
        help_text="Users who have this skill.",
        through=UserSkill,
        related_name="skills",
    )

    class Meta:
        ordering = ["name"]

    def get_category_display(self) -> str:
        """Return all of the categories as a comma-separated string."""
        return ", ".join([category.name for category in self.categories.all()])
