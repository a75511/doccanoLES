from django.contrib import admin

from .models import Comment, Example, Disagreement


class ExampleAdmin(admin.ModelAdmin):
    list_display = ("text", "project", "meta")
    ordering = ("project",)
    search_fields = ("text",)


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "example",
        "text",
        "created_at",
    )
    ordering = (
        "user",
        "created_at",
    )
    search_fields = ("user",)

class DisagreementAdmin(admin.ModelAdmin):
    list_display = ("example", "resolved", "created_at")
    list_filter = ("resolved",)
    search_fields = ("example__text", "users__username")
    raw_id_fields = ("example", "users")  # For performance with large datasets

admin.site.register(Example, ExampleAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Disagreement, DisagreementAdmin)