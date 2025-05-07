from rest_framework import generics
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from projects.models import Discussion, DiscussionComment, Member
from projects.serializers import DiscussionSerializer, DiscussionCommentSerializer
from projects.permissions import IsCommentAuthor, IsProjectMember

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