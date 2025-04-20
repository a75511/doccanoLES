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
    MemberAttributeDescription,
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

class MemberAttributeDescriptionAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'get_member_username',
        'get_attribute_name',
        'description',
        'created_at'
    )
    list_filter = (
        'attribute__type',
        'created_at',
    )
    search_fields = (
        'member__user__username',
        'attribute__name',
        'description'
    )
    raw_id_fields = ('member', 'attribute')
    list_select_related = ('member__user', 'attribute')

    def get_member_username(self, obj):
        return obj.member.user.username
    get_member_username.short_description = 'Member'
    get_member_username.admin_order_field = 'member__user__username'

    def get_attribute_name(self, obj):
        return f"{obj.attribute.name} ({obj.attribute.type})"
    get_attribute_name.short_description = 'Attribute'
    get_attribute_name.admin_order_field = 'attribute__name'

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('attribute__options')

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
admin.site.register(MemberAttributeDescription, MemberAttributeDescriptionAdmin)
admin.site.register(Discussion, DiscussionAdmin)
admin.site.register(DiscussionComment, DiscussionCommentAdmin)