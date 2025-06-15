from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status, views
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response

from projects.models import Project, Discussion, GuidelineVoting
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from projects.serializers import ProjectPolymorphicSerializer


class ProjectList(generics.ListCreateAPIView):
    serializer_class = ProjectPolymorphicSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ["name", "created_at", "created_by", "project_type"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [
                IsAuthenticated,
            ]
        else:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        return Project.objects.filter(role_mappings__user=self.request.user)

    def perform_create(self, serializer):
        project = serializer.save(created_by=self.request.user)
        project.add_admin()

    def delete(self, request, *args, **kwargs):
        delete_ids = request.data["ids"]
        projects = Project.objects.filter(
            role_mappings__user=self.request.user,
            role_mappings__role__name=settings.ROLE_PROJECT_ADMIN,
            pk__in=delete_ids,
        )
        # Todo: I want to use bulk delete.
        # But it causes the constraint error.
        # See https://github.com/django-polymorphic/django-polymorphic/issues/229
        for project in projects:
            project.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ProjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectPolymorphicSerializer
    lookup_url_kwarg = "project_id"
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]


class CloneProject(views.APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        cloned_project = project.clone()
        serializer = ProjectPolymorphicSerializer(cloned_project)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
class ProjectLockView(views.APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=kwargs["project_id"])
        lock_status = request.data.get('locked')
        
        # Validate input
        if not isinstance(lock_status, bool):
            return Response(
                {"detail": "'locked' must be a boolean."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Handle locking logic
        if lock_status and not project.locked:
            
            # Create voting session
            GuidelineVoting.objects.create(
                project=project,
                status='not_started',
                guidelines_snapshot=project.guideline
            )
        elif not lock_status and project.locked:
            # If unlocking, ensure no active voting session exists
            if GuidelineVoting.objects.filter(project=project, status='voting').exists():
                GuidelineVoting.objects.filter(project=project, status='voting').update(status='completed')

        project.locked = lock_status
        project.save()
        return Response({"locked": project.locked})
