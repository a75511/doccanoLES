from django.apps import apps
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from examples.models import Example, ExampleState, Disagreement
from projects.models import Member, Project
from examples.models import Disagreement
from examples.serializers import DisagreementSerializer
from projects.permissions import IsProjectAdmin, IsProjectStaffAndReadOnly
from xml.dom import ValidationErr

class DisagreementList(generics.ListAPIView):
    serializer_class = DisagreementSerializer
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
    
    def get_queryset(self):
        project_id = self.kwargs['project_id']
        return Disagreement.objects.filter(
            example__project_id=project_id,
            resolved=False
        ).order_by('-created_at')

class DisagreementDetail(generics.RetrieveUpdateAPIView):
    queryset = Disagreement.objects.all()
    serializer_class = DisagreementSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]
    lookup_url_kwarg = 'disagreement_id'
    
    def perform_update(self, serializer):
        serializer.save(resolved=True) 

class DisagreementCompare(APIView):
    permission_classes = [IsAuthenticated & (IsProjectAdmin | IsProjectStaffAndReadOnly)]
    
    def get(self, request, project_id):
        member1_id = request.query_params.get('member1')
        member2_id = request.query_params.get('member2')
        
        if not member1_id or not member2_id:
            return Response(
                {"error": "Both member1 and member2 parameters are required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            project = get_object_or_404(Project, pk=project_id)
            
            # Handle both member IDs and user IDs
            try:
                member1 = get_object_or_404(Member, pk=member1_id, project=project)
                member2 = get_object_or_404(Member, pk=member2_id, project=project)
            except (ValueError, ValidationErr):
                # Fallback to user IDs if member IDs don't work
                member1 = get_object_or_404(Member, user_id=member1_id, project=project)
                member2 = get_object_or_404(Member, user_id=member2_id, project=project)
            
            user1 = member1.user
            user2 = member2.user
            
            # Get all examples both users have annotated
            user1_states = ExampleState.objects.filter(
                confirmed_by=user1,
                example__project=project
            ).select_related('example')
            
            user2_states = ExampleState.objects.filter(
                confirmed_by=user2,
                example__project=project
            ).select_related('example')
            
            # Find common examples
            user1_examples = {state.example_id for state in user1_states}
            user2_examples = {state.example_id for state in user2_states}
            common_examples = user1_examples & user2_examples
            
            # Get all examples data
            all_examples = Example.objects.filter(id__in=common_examples)
            
            conflicts = []
            for example_id in common_examples:
                example = Example.objects.get(pk=example_id)
                user1_state = user1_states.get(example_id=example_id)
                user2_state = user2_states.get(example_id=example_id)
                
                # Get annotations from meta or related annotation models
                user1_annotations = self._get_annotations(user1_state)
                user2_annotations = self._get_annotations(user2_state)
                
                # Compare annotations
                differences = self._find_differences(user1_annotations, user2_annotations)
                
                conflicts.append({
                    "example": {
                        "id": example.id,
                        "text": example.text,
                        "meta": example.meta,
                    },
                    "member1": {
                        "id": member1.id,
                        "user_id": user1.id,
                        "username": user1.username,
                        "annotations": user1_annotations,
                    },
                    "member2": {
                        "id": member2.id,
                        "user_id": user2.id,
                        "username": user2.username,
                        "annotations": user2_annotations,
                    },
                    "differences": differences
                })
            
            return Response({
            "project_id": project.id,
            "project_name": project.name,
            "member1": {
                "id": member1.id,
                "user_id": user1.id,
                "username": user1.username,
            },
            "member2": {
                "id": member2.id,
                "user_id": user2.id,
                "username": user2.username,
            },
            "total_compared": len(common_examples),
            "conflicts": conflicts,
            "examples": [{
                "id": example.id,
                "text": example.text,
                "meta": example.meta,
                "annotation_approver": example.annotations_approved_by.username if example.annotations_approved_by else None,
                "comment_count": example.comment_count,
                "file_url": example.filename.url if example.filename else '',
                "is_confirmed": example.states.filter(confirmed_by__in=[user1, user2]).exists(),
                "filename": example.upload_name,
                "assignments": [{
                    "id": str(assignment.id),
                    "assignee": assignment.assignee.username,
                    "assignee_id": assignment.assignee.id
                } for assignment in example.assignments.all()]
            } for example in all_examples],
            "conflict_count": len([c for c in conflicts if c['differences']]),
        })
            
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_annotations(self, example_state):
        """Extract annotations from example state"""
        # First try to get from meta
        if 'annotations' in example_state.example.meta:
            return example_state.example.meta['annotations']
        
        # If not in meta, try to get from related annotation models
        # You'll need to implement this based on your project type
        annotations = []
        
        # Example for text classification:
        Category = apps.get_model('labels', 'Category')
        categories = Category.objects.filter(
            example=example_state.example,
            user=example_state.confirmed_by
        )
        for cat in categories:
            annotations.append({
                'type': 'category',
                'label': cat.label.text,
                'label_id': cat.label.id,
            })
        
        return annotations
    
    def _annotations_equal(self, annotations1, annotations2):
        """Compare two sets of annotations for equality"""
        # Simple comparison for now - you might need more sophisticated comparison
        # depending on your annotation types
        return annotations1 == annotations2
    
    def _find_differences(self, annotations1, annotations2):
        """Find and highlight differences between two annotation sets"""
        differences = []
        
        # For simple label comparisons
        labels1 = {a.get('label') for a in annotations1 if 'label' in a}
        labels2 = {a.get('label') for a in annotations2 if 'label' in a}
        
        # Find labels only in annotations1
        for label in (labels1 - labels2):
            differences.append({
                'type': 'missing_in_member2',
                'label': label,
                'details': f"Label '{label}' only exists in first annotator's set"
            })
        
        # Find labels only in annotations2
        for label in (labels2 - labels1):
            differences.append({
                'type': 'missing_in_member1',
                'label': label,
                'details': f"Label '{label}' only exists in second annotator's set"
            })
        
        return differences