from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from projects.models import Perspective, Project
from projects.serializers import PerspectiveSerializer

class PerspectiveListView(generics.ListAPIView):
    """List all perspectives or the perspective assigned to a project."""

    serializer_class = PerspectiveSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")  # Fields to search against
    ordering_fields = ["name", "created_at"]  # Fields to allow ordering by
    ordering = ["-created_at"]  # Default ordering (most recent first)

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        project_id = self.kwargs.get("project_id")
        project = get_object_or_404(Project, id=project_id)

        # Check if the user wants to see the assigned perspective or all perspectives
        show_assigned = self.request.query_params.get("show_assigned", "false").lower() == "true"

        if show_assigned:
            # Return the assigned perspective (if any)
            if project.perspective:
                return Perspective.objects.filter(id=project.perspective.id)
            else:
                return Perspective.objects.none()  # Return an empty queryset if no perspective is assigned
        else:
            # Return all available perspectives
            return Perspective.objects.all()

        return Response(serialized_perspectives.data)


class AssignPerspectiveToProject(APIView):
    """Vincula uma perspectiva a um projeto."""

    permission_classes = [IsAuthenticated & IsAdminUser]

    def post(self, request, project_id, perspective_id):
        project = get_object_or_404(Project, id=project_id)
        perspective = get_object_or_404(Perspective, id=perspective_id)

        project.perspective = perspective
        project.save()

        return Response({"message": "Perspective assigned successfully."}, status=status.HTTP_200_OK)