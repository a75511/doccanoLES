from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from .models import (
    BoundingBoxProject,
    ImageCaptioningProject,
    ImageClassificationProject,
    IntentDetectionAndSlotFillingProject,
    Member,
    Project,
    SegmentationProject,
    Seq2seqProject,
    SequenceLabelingProject,
    Speech2textProject,
    Tag,
    TextClassificationProject,
    Perspective,
    PerspectiveAttribute,
    PerspectiveAttributeListOption,
    AttributeType,
)


class MemberSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    rolename = serializers.SerializerMethodField()

    @classmethod
    def get_username(cls, instance):
        user = instance.user
        return user.username if user else None

    @classmethod
    def get_rolename(cls, instance):
        role = instance.role
        return role.name if role else None

    class Meta:
        model = Member
        fields = ("id", "user", "role", "username", "rolename")


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            "id",
            "project",
            "text",
        )
        read_only_fields = ("id", "project")

class PerspectiveAttributeListOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = PerspectiveAttributeListOption
        fields = ["id", "value"]

class PerspectiveAttributeSerializer(serializers.ModelSerializer):
    options = PerspectiveAttributeListOptionSerializer(many=True, required=False)

    class Meta:
        model = PerspectiveAttribute
        fields = ["id", "name", "type", "options"]

    def validate(self, data):
        # Se o tipo do atributo for "List", garantir que as opções sejam passadas
        if data.get("type") == AttributeType.LIST and "options" not in data:
            raise serializers.ValidationError("Atributos do tipo 'List' devem ter opções associadas.")
        return data

    def create(self, validated_data):
        options_data = validated_data.pop("options", [])  # Extrai as opções se existirem
        attribute = PerspectiveAttribute.objects.create(**validated_data)

        # Se o atributo for do tipo 'LIST', criar as opções associadas
        if attribute.type == AttributeType.LIST:
            for option_data in options_data:
                PerspectiveAttributeListOption.objects.create(attribute=attribute, **option_data)

        return attribute

class PerspectiveSerializer(serializers.ModelSerializer):
    attributes = PerspectiveAttributeSerializer(many=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Perspective
        fields = ["id", "name", "description", "attributes", "created_at", "created_by"]

    @classmethod
    def get_created_by(cls, instance):
        if instance.created_by:
            return instance.created_by.username
        return None

    def create(self, validated_data):
        attributes_data = validated_data.pop("attributes", [])
        perspective = Perspective.objects.create(
            **validated_data,
            created_by=self.context['request'].user
        )

        for attribute_data in attributes_data:
            options_data = attribute_data.pop("options", [])
            attribute = PerspectiveAttribute.objects.create(perspective=perspective, **attribute_data)

            if attribute.type == AttributeType.LIST:
                for option_data in options_data:
                    PerspectiveAttributeListOption.objects.create(attribute=attribute, **option_data)

        return perspective
    
    def get_projects(self, instance):
        # Return a list of project IDs that use this perspective
        return [project.id for project in instance.projects.all()]

class ProjectSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, required=False)
    author = serializers.SerializerMethodField()
    perspective = PerspectiveSerializer(read_only=True)

    @classmethod
    def get_author(cls, instance):
        if instance.created_by:
            return instance.created_by.username
        return ""

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "guideline",
            "project_type",
            "created_at",
            "updated_at",
            "random_order",
            "author",
            "collaborative_annotation",
            "single_class_classification",
            "allow_member_to_create_label_type",
            "is_text_project",
            "tags",
            "perspective",
        ]
        read_only_fields = (
            "created_at",
            "updated_at",
            "author",
            "is_text_project",
        )

    def create(self, validated_data):
        tags = TagSerializer(data=validated_data.pop("tags", []), many=True)
        project = self.Meta.model.objects.create(**validated_data)
        tags.is_valid()
        tags.save(project=project)
        return project

    def update(self, instance, validated_data):
        # Don't update tags. Please use TagAPI.
        validated_data.pop("tags", None)
        return super().update(instance, validated_data)


class TextClassificationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = TextClassificationProject


class SequenceLabelingProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = SequenceLabelingProject
        fields = ProjectSerializer.Meta.fields + ["allow_overlapping", "grapheme_mode", "use_relation"]


class Seq2seqProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = Seq2seqProject


class IntentDetectionAndSlotFillingProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = IntentDetectionAndSlotFillingProject


class Speech2textProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = Speech2textProject


class ImageClassificationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = ImageClassificationProject


class BoundingBoxProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = BoundingBoxProject


class SegmentationProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = SegmentationProject


class ImageCaptioningProjectSerializer(ProjectSerializer):
    class Meta(ProjectSerializer.Meta):
        model = ImageCaptioningProject


class ProjectPolymorphicSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        Project: ProjectSerializer,
        **{cls.Meta.model: cls for cls in ProjectSerializer.__subclasses__()},
    }
