import abc
import uuid
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.db.models import Manager
from polymorphic.models import PolymorphicModel
from django.apps import apps

from roles.models import Role


class ProjectType(models.TextChoices):
    DOCUMENT_CLASSIFICATION = "DocumentClassification"
    SEQUENCE_LABELING = "SequenceLabeling"
    SEQ2SEQ = "Seq2seq"
    INTENT_DETECTION_AND_SLOT_FILLING = "IntentDetectionAndSlotFilling"
    SPEECH2TEXT = "Speech2text"
    IMAGE_CLASSIFICATION = "ImageClassification"
    BOUNDING_BOX = "BoundingBox"
    SEGMENTATION = "Segmentation"
    IMAGE_CAPTIONING = "ImageCaptioning"

class Perspective(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True, help_text="Descrição geral da perspectiva.")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_perspectives"
    )

    def __str__(self):
        return self.name


class AttributeType(models.TextChoices):
    TEXT = "text", "Text"
    NUMBER = "number", "Number"
    BOOLEAN = "boolean", "Boolean"
    LIST = "list", "List"


class PerspectiveAttribute(models.Model):
    perspective = models.ForeignKey(Perspective, on_delete=models.CASCADE, related_name="attributes")
    name = models.CharField(max_length=255, help_text="Nome do atributo (ex.: idade, sexo, localização).")
    type = models.CharField(max_length=10, choices=AttributeType.choices, default=AttributeType.TEXT)

    class Meta:
        unique_together = ("perspective", "name", "type")

    def __str__(self):
        return f"{self.name} ({self.type})"

class PerspectiveAttributeListOption(models.Model):
    attribute = models.ForeignKey(PerspectiveAttribute, on_delete=models.CASCADE, related_name="options")
    value = models.CharField(max_length=255, help_text="Opção disponível para um atributo do tipo 'List'.")

    def __str__(self):
        return f"{self.attribute.name} - {self.value}"

class Project(PolymorphicModel):
    name = models.CharField(max_length=100)
    description = models.TextField(default="")
    guideline = models.TextField(default="", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
    )
    project_type = models.CharField(max_length=30, choices=ProjectType.choices)
    random_order = models.BooleanField(default=False)
    collaborative_annotation = models.BooleanField(default=False)
    single_class_classification = models.BooleanField(default=False)
    allow_member_to_create_label_type = models.BooleanField(default=False)
    perspective = models.ForeignKey(
        Perspective,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects"
    )
    locked = models.BooleanField(default=False)

    def add_admin(self):
        admin_role = Role.objects.get(name=settings.ROLE_PROJECT_ADMIN)
        Member.objects.create(
            project=self,
            user=self.created_by,
            role=admin_role,
        )

    @property
    @abc.abstractmethod
    def is_text_project(self) -> bool:
        return False

    def clone(self) -> "Project":
        """Clone the project.
        See https://docs.djangoproject.com/en/4.2/topics/db/queries/#copying-model-instances

        Returns:
            The cloned project.
        """
        project = Project.objects.get(pk=self.pk)
        project.pk = None
        project.id = None
        project._state.adding = True
        project.save()

        def bulk_clone(queryset: models.QuerySet, field_initializers: Optional[Dict[Any, Any]] = None):
            """Clone the queryset.

            Args:
                queryset: The queryset to clone.
                field_initializers: The field initializers.
            """
            if field_initializers is None:
                field_initializers = {}
            items = []
            for item in queryset:
                item.id = None
                item.pk = None
                for field, value_or_callable in field_initializers.items():
                    if callable(value_or_callable):
                        value_or_callable = value_or_callable()
                    setattr(item, field, value_or_callable)
                item.project = project
                item._state.adding = True
                items.append(item)
            queryset.model.objects.bulk_create(items)

        bulk_clone(self.role_mappings.all())
        bulk_clone(self.tags.all())

        # clone examples
        bulk_clone(self.examples.all(), field_initializers={"uuid": uuid.uuid4})

        # clone label types
        bulk_clone(self.categorytype_set.all())
        bulk_clone(self.spantype_set.all())
        bulk_clone(self.relationtype_set.all())

        return project
    
    def delete_annotations(self):
        """
        Delete all annotations (categories, spans, text labels, relations, bounding boxes, segmentations)
        associated with this project.
        """
        Category = apps.get_model('labels', 'Category')
        Span = apps.get_model('labels', 'Span')
        TextLabel = apps.get_model('labels', 'TextLabel')
        Relation = apps.get_model('labels', 'Relation')
        BoundingBox = apps.get_model('labels', 'BoundingBox')
        Segmentation = apps.get_model('labels', 'Segmentation')
        Category.objects.filter(example__project=self).delete()
        Span.objects.filter(example__project=self).delete()
        TextLabel.objects.filter(example__project=self).delete()
        Relation.objects.filter(example__project=self).delete()
        BoundingBox.objects.filter(example__project=self).delete()
        Segmentation.objects.filter(example__project=self).delete()

    def __str__(self):
        return self.name


class TextClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class SequenceLabelingProject(Project):
    allow_overlapping = models.BooleanField(default=False)
    grapheme_mode = models.BooleanField(default=False)
    use_relation = models.BooleanField(default=False)

    @property
    def is_text_project(self) -> bool:
        return True


class Seq2seqProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class IntentDetectionAndSlotFillingProject(Project):
    @property
    def is_text_project(self) -> bool:
        return True


class Speech2textProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageClassificationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class BoundingBoxProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class SegmentationProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class ImageCaptioningProject(Project):
    @property
    def is_text_project(self) -> bool:
        return False


class Tag(models.Model):
    text = models.TextField()
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="tags")

    def __str__(self):
        return self.text


class MemberManager(Manager):
    def can_update(self, project: int, member_id: int, new_role: str) -> bool:
        """The project needs at least 1 admin.

        Args:
            project: The project id.
            member_id: The member id.
            new_role: The new role name.

        Returns:
            Whether the mapping can be updated or not.
        """
        queryset = self.filter(project=project, role__name=settings.ROLE_PROJECT_ADMIN)
        if queryset.count() > 1:
            return True
        else:
            admin = queryset.first()
            # we can change the role except for the only admin.
            return admin.id != member_id or new_role == settings.ROLE_PROJECT_ADMIN

    def has_role(self, project_id: int, user: User, role_name: str):
        return self.filter(project=project_id, user=user, role__name=role_name).exists()


class Member(models.Model):
    user = models.ForeignKey(to=User, on_delete=models.CASCADE, related_name="role_mappings")
    project = models.ForeignKey(to=Project, on_delete=models.CASCADE, related_name="role_mappings")
    role = models.ForeignKey(to=Role, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = MemberManager()

    def clean(self):
        members = self.__class__.objects.exclude(id=self.id)
        if members.filter(user=self.user, project=self.project).exists():
            message = "This user is already assigned to a role in this project."
            raise ValidationError(message)

    def is_admin(self):
        return self.role.name == settings.ROLE_PROJECT_ADMIN

    @property
    def username(self):
        return self.user.username

    class Meta:
        unique_together = ("user", "project")

class MemberAttributeDescription(models.Model):
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name="attribute_descriptions")
    attribute = models.ForeignKey(PerspectiveAttribute, on_delete=models.CASCADE)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("member", "attribute")

    def clean(self):
        if self.attribute.type == AttributeType.LIST:
            valid_options = [option.value for option in self.attribute.options.all()]
            if self.description not in valid_options:
                raise ValidationError(f"Value must be one of: {', '.join(valid_options)}")
        elif self.attribute.type == AttributeType.NUMBER:
            if not self.description.isdigit():
                raise ValidationError("Value must be a number")
        elif self.attribute.type == AttributeType.BOOLEAN:
            if self.description.lower() not in ["true", "false"]:
                raise ValidationError("Value must be 'true' or 'false'")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, kwargs)

class Discussion(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='discussions')
    title = models.CharField(max_length=255, default="Annotation Guidelines Discussion")
    description = models.TextField(default="Discuss annotation guidelines and resolve disagreements")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    participants = models.ManyToManyField(
        Member,
        related_name='discussion_participants',
        blank=True
    )
    
    # Track closure attempt when offline
    pending_closure = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'is_active'],
                condition=models.Q(is_active=True),
                name='unique_active_discussion'
            )
        ]
    def close(self):
        """Close the discussion session"""
        if not self.is_active:
            return False
        
        self.is_active = False
        self.finished_at = timezone.now()
        self.save()
        return True

    def mark_pending_closure(self):
        """Mark for closure when offline"""
        self.pending_closure = True
        self.save()
        return True

    def cancel_closure(self):
        """Cancel pending closure"""
        if self.pending_closure:
            self.pending_closure = False
            self.save()
            return True
        return False

class DiscussionComment(models.Model):
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    temp_id = models.BigIntegerField(null=True, blank=True)
    is_synced = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['temp_id']),
            models.Index(fields=['is_synced'])
        ]

class GuidelineVoting(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='voting_sessions')  # Changed from OneToOne
    current_discussion = models.ForeignKey(Discussion, on_delete=models.SET_NULL, null=True, blank=True)
    previous_voting = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)  # For history tracking
    status = models.CharField(
        max_length=20,
        choices=(
            ('not_started', 'Not Started'),
            ('voting', 'Voting'),
            ('completed', 'Completed')
        ),
        default='not_started'
    )
    guidelines_snapshot = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)  # Add creation date

    class Meta:
        ordering = ['-created_at']  # Newest first

    def save_guideline_snapshot(self):
        """Save current project guideline as snapshot when voting ends"""
        self.guidelines_snapshot = self.project.guideline
        self.save()

class MemberVote(models.Model):
    voting_session = models.ForeignKey(GuidelineVoting, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(Member, on_delete=models.CASCADE)
    agrees = models.BooleanField()
    voted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('voting_session', 'user')
