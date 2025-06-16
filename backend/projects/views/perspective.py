from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.db import DatabaseError, IntegrityError
from projects.models import MemberAttributeDescription, Perspective, Project, PerspectiveAttribute, PerspectiveAttributeListOption
from projects.serializers import PerspectiveAttributeSerializer, PerspectiveSerializer, ProjectSerializer, PerspectiveAttributeListOptionSerializer
from projects.permissions import IsProjectAdmin, IsAnnotationApprover

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
            self.permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]
        return super().get_permissions()

    def get_queryset(self):
        return Perspective.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        context['project_id'] = self.kwargs.get('project_id')
        return context
    
class PerspectiveDetailView(generics.RetrieveAPIView):
    queryset = Perspective.objects.all()
    serializer_class = PerspectiveSerializer
    lookup_url_kwarg = "perspective_id"
    permission_classes = [IsAuthenticated]

class PerspectiveAttributeListView(generics.ListAPIView):
    serializer_class = PerspectiveAttributeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name']
    ordering_fields = ['name', 'type']
    ordering = ['name']

    def get_queryset(self):
        perspective_id = self.kwargs['perspective_id']
        return PerspectiveAttribute.objects.filter(perspective_id=perspective_id)
    

class CreatePerspectiveView(generics.CreateAPIView):
    serializer_class = PerspectiveSerializer
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]

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
            serializer.context['request'] = request
            perspective = serializer.save()
            
            return Response({
                "message": "Perspective created successfully.",
                "perspective": PerspectiveSerializer(perspective, context={'request': request}).data
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


class PerspectiveAttributeListOptionView(generics.ListCreateAPIView):
    serializer_class = PerspectiveAttributeListOptionSerializer
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]

    def get_queryset(self):
        attribute_id = self.kwargs["attribute_id"]
        return PerspectiveAttributeListOption.objects.filter(attribute_id=attribute_id)

    def perform_create(self, serializer):
        attribute = get_object_or_404(PerspectiveAttribute, id=self.kwargs["attribute_id"])
        serializer.save(attribute=attribute)    

class AssignPerspectiveToProject(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]

    def post(self, request, project_id, perspective_id):
        project = get_object_or_404(Project, id=project_id)
        perspective = get_object_or_404(Perspective, id=perspective_id)

        try:
            #project.delete_annotations() REVIEW: Uncomment if you want to delete existing annotations
            project.perspective = perspective
            project.save()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializer = ProjectSerializer(project)
        return Response({
            "message": "Perspective assigned successfully.",
            "project": serializer.data
        }, status=status.HTTP_200_OK)
    
class AttributeDescriptionsView(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsAnnotationApprover)]

    def get(self, request, project_id):
        try:
            perspective_attributes = request.GET.getlist('attributes', [])
            
            descriptions_data = MemberAttributeDescription.objects.filter(
                attribute__name__in=perspective_attributes,
                attribute__perspective__projects=project_id
            ).values(
                'attribute__name',
                'description'
            ).distinct()
            
            return Response({
                'attribute_descriptions': [
                    {'attribute': d['attribute__name'], 'description': d['description']}
                    for d in descriptions_data
                ]
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

