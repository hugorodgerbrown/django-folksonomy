from django.contrib import admin
from django.utils.translation import gettext_lazy as _lazy

from folksonomy.admin import TagAdminBase

from .models import Skill, UserSkill


@admin.register(Skill)
class SkillAdmin(TagAdminBase):
    raw_id_fields = ["users", "categories"]
    search_fields = ["name"]

    @admin.display(description=_lazy("Tag Categories"))
    def categories_(self, obj: Skill) -> str:
        """Return all of the categories as a comma-separated string."""
        return obj.get_category_display()


@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ["user", "skill", "skill_level", "created_at"]
    readonly_fields = ["created_at"]
    raw_id_fields = ["user", "skill"]
    search_fields = ["user__username", "skill__name"]
