from django.contrib import admin

from .models import (
    BoundingBoxProject,
    ImageCaptioningProject,
    ImageClassificationProject,
    Member,
    Project,
    SegmentationProject,
    Seq2seqProject,
    SequenceLabelingProject,
    Tag,
    TextClassificationProject,
    Perspective,
    PerspectiveAttribute,
    PerspectiveAttributeListOption,
    Discussion,
    DiscussionComment,
)


class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "user",
        "role",
        "project",
    )
    ordering = ("user",)
    search_fields = ("user__username",)


class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "project_type", "random_order", "collaborative_annotation")
    ordering = ("project_type",)
    search_fields = ("name",)


class TagAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "text",
    )
    ordering = (
        "project",
        "text",
    )
    search_fields = ("text",)

class PerspectiveAdmin(admin.ModelAdmin):
    list_display = ("name", "description")
    search_fields = ("name",)


class PerspectiveAttributeAdmin(admin.ModelAdmin):
    list_display = ("name", "perspective", "type")
    list_filter = ("type",)
    search_fields = ("name", "perspective__name")


class PerspectiveAttributeListOptionAdmin(admin.ModelAdmin):
    list_display = ("attribute", "value")
    search_fields = ("attribute__name", "value")

class DiscussionAdmin(admin.ModelAdmin):
    list_display = ('id', 'project', 'title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'description', 'project__name')
    raw_id_fields = ('project',)
    ordering = ('-created_at',)

class DiscussionCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'discussion', 'member', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('text', 'member__user__username', 'discussion__title')
    raw_id_fields = ('discussion', 'member')
    ordering = ('-created_at',)


admin.site.register(Member, MemberAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(TextClassificationProject, ProjectAdmin)
admin.site.register(SequenceLabelingProject, ProjectAdmin)
admin.site.register(Seq2seqProject, ProjectAdmin)
admin.site.register(BoundingBoxProject, ProjectAdmin)
admin.site.register(SegmentationProject, ProjectAdmin)
admin.site.register(ImageCaptioningProject, ProjectAdmin)
admin.site.register(ImageClassificationProject, ProjectAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Perspective, PerspectiveAdmin)
admin.site.register(PerspectiveAttribute, PerspectiveAttributeAdmin)
admin.site.register(PerspectiveAttributeListOption, PerspectiveAttributeListOptionAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(DiscussionComment, DiscussionCommentAdmin)