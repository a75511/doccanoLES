from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import DatabaseError, IntegrityError
from projects.models import Perspective, Project, PerspectiveAttribute, PerspectiveAttributeListOption
from projects.serializers import PerspectiveSerializer, ProjectSerializer, PerspectiveAttributeSerializer, PerspectiveAttributeListOptionSerializer

class PerspectiveListView(generics.ListCreateAPIView):
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

class CreatePerspectiveView(generics.CreateAPIView):
    serializer_class = PerspectiveSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def create(self, request, *args, **kwargs):
        try:
            name = request.data.get('name')
            if Perspective.objects.filter(name=name).exists():
                return Response(
                    {
                        "message": "A perspective with this name already exists.",
                        "code": "perspective_exists"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            perspective = serializer.save()
            
            return Response({
                "message": "Perspective created successfully.",
                "perspective": PerspectiveSerializer(perspective).data
            }, status=status.HTTP_201_CREATED)
            
        except DatabaseError:
            return Response(
                {
                    "message": "Database operation failed. Please try again later.",
                    "code": "database_error"
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        except IntegrityError:
            return Response(
                {
                    "message": "Data integrity error occurred. Please check your input.",
                    "code": "integrity_error"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            return Response(
                {
                    "message": "An unexpected error occurred.",
                    "code": "unexpected_error"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def get_queryset(self):
        return Perspective.objects.all()


class PerspectiveAttributeListOptionView(generics.ListCreateAPIView):
    serializer_class = PerspectiveAttributeListOptionSerializer
    permission_classes = [IsAuthenticated & IsAdminUser]

    def get_queryset(self):
        attribute_id = self.kwargs["attribute_id"]
        return PerspectiveAttributeListOption.objects.filter(attribute_id=attribute_id)

    def perform_create(self, serializer):
        attribute = get_object_or_404(PerspectiveAttribute, id=self.kwargs["attribute_id"])
        serializer.save(attribute=attribute)    

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

