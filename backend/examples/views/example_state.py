from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from examples.models import Example, ExampleState
from examples.serializers import ExampleStateSerializer
from projects.models import Project
from projects.permissions import IsProjectMember, IsProjectAdmin


class ExampleStateList(generics.ListCreateAPIView):
    serializer_class = ExampleStateSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    @property
    def can_confirm_per_user(self):
        project = get_object_or_404(Project, pk=self.kwargs["project_id"])
        return not project.collaborative_annotation

    def get_queryset(self):
        queryset = ExampleState.objects.filter(example=self.kwargs["example_id"])
        if self.can_confirm_per_user:
            queryset = queryset.filter(confirmed_by=self.request.user)
        return queryset

    def perform_create(self, serializer):
        queryset = self.get_queryset()
        if queryset.exists():
            queryset.delete()
        else:
            example = get_object_or_404(Example, pk=self.kwargs["example_id"])
            serializer.save(example=example, confirmed_by=self.request.user)

class ResetConfirmation(APIView):
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def post(self, request, *args, **kwargs):
        project_id = self.kwargs["project_id"]
        project = get_object_or_404(Project, pk=project_id)

        ExampleState.objects.filter(example__project=project).delete()

        return Response(
            {"detail": "Confirmation status reset successfully for all examples."},
            status=status.HTTP_200_OK
        )
