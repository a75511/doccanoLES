from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from projects.models import Discussion, DiscussionComment, Member
from projects.serializers import DiscussionSerializer, DiscussionCommentSerializer
from projects.permissions import IsCommentAuthor, IsProjectMember, IsProjectAdmin
from time import timezone
from django.db import DatabaseError, transaction


class DiscussionSessionViewSet(viewsets.ModelViewSet):
    queryset = Discussion.objects.all()
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated & (IsProjectMember | IsProjectAdmin)]
    
    @action(detail=False, methods=['post'], url_path='start')
    def start_session(self, request, project_id=None):
        if Discussion.objects.filter(project_id=project_id, is_active=True).exists():
            return Response({"error": "An active session already exists"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        discussion = Discussion.objects.create(
            project_id=project_id,
            title="Discussion Session",
            description="Active discussion session"
        )
        return Response(DiscussionSerializer(discussion).data, 
                      status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['post'], url_path='join')
    def join_session(self, request, project_id=None, pk=None):
        discussion = self.get_object()
        member = get_object_or_404(Member, project_id=project_id, user=request.user)
        
        if discussion.participants.filter(id=member.id).exists():
            return Response({"status": "Already joined"}, status=status.HTTP_200_OK)
        
        discussion.participants.add(member)
        return Response({"status": "Session joined"}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['get'], url_path='participation')
    def check_participation(self, request, project_id=None, pk=None):
        discussion = self.get_object()
        member = get_object_or_404(Member, project_id=project_id, user=request.user)
        
        has_joined = discussion.participants.filter(id=member.id).exists()
        return Response({"hasJoined": has_joined}, status=status.HTTP_200_OK)
    
    @action(detail=True, methods=['post'], url_path='close')
    def close_session(self, request, project_id=None, pk=None):
        discussion = self.get_object()
        
        if not discussion.is_active:
            return Response({"error": "Session is already closed"}, 
                           status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Use atomic transaction to ensure data consistency
            with transaction.atomic():
                if discussion.close():
                    cache.delete(f'discussion_{project_id}')
                    cache.delete(f'discussion_comments_{project_id}')
                    return Response({"status": "Session closed"})
                return Response({"error": "Failed to close session"}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except DatabaseError:
            try:
                if discussion.mark_pending_closure():
                    return Response({
                        "warning": "Database offline. Closure will complete when back online",
                        "pending_closure": True
                    }, status=status.HTTP_202_ACCEPTED)
            except Exception as e:
                return Response({"error": f"Failed to mark closure: {str(e)}"}, 
                               status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @action(detail=True, methods=['post'], url_path='cancel-close')
    def cancel_closure(self, request, project_id=None, pk=None):
        discussion = self.get_object()
        try:
            if discussion.cancel_closure():
                return Response({"status": "Closure cancelled"})
            return Response({"error": "No pending closure"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"Failed to cancel closure: {str(e)}"}, 
                           status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class CommentPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'

class ActiveDiscussionDetail(generics.RetrieveAPIView):
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_object(self):
        project_id = self.kwargs['project_id']
        return cache.get_or_set(
            f'discussion_{project_id}',
            lambda: Discussion.objects.get(project_id=project_id, is_active=True),
            300  # Cache for 5 minutes
        )

class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = DiscussionCommentSerializer
    pagination_class = CommentPagination
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_queryset(self):
        return DiscussionComment.objects.filter(
            discussion__project_id=self.kwargs['project_id']
        ).select_related('member__user').order_by('-created_at')

    def perform_create(self, serializer):
        discussion = get_object_or_404(Discussion, project_id=self.kwargs['project_id'], is_active=True)
        member = get_object_or_404(Member, project=discussion.project, user=self.request.user)
        serializer.save(member=member, discussion=discussion)

class CommentDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = DiscussionCommentSerializer
    permission_classes = [IsAuthenticated & IsProjectMember & IsCommentAuthor]

    def get_object(self):
        comment_id = self.kwargs['comment_id']
        return get_object_or_404(DiscussionComment, id=comment_id)