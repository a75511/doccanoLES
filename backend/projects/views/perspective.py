from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from projects.models import Perspective, Project
from projects.serializers import PerspectiveSerializer, ProjectSerializer

class PerspectiveListView(generics.ListAPIView):
    serializer_class = PerspectiveSerializer
    filter_backends = (DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter)
    search_fields = ("name", "description")
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [IsAuthenticated & IsAdminUser]
        return super().get_permissions()

    def get_queryset(self):
        return Perspective.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['project_id'] = self.kwargs.get('project_id')
        return context

        return Response(serialized_perspectives.data)


class AssignPerspectiveToProject(APIView):
    permission_classes = [IsAuthenticated & IsAdminUser]

    def post(self, request, project_id, perspective_id):
        project = get_object_or_404(Project, id=project_id)
        perspective = get_object_or_404(Perspective, id=perspective_id)

        project.perspective = perspective
        project.save()

        serializer = ProjectSerializer(project)
        return Response({
            "message": "Perspective assigned successfully.",
            "project": serializer.data
        }, status=status.HTTP_200_OK)