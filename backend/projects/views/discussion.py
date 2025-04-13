from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from projects.models import Discussion, DiscussionComment, Member, Project
from projects.serializers import DiscussionSerializer, DiscussionCommentSerializer
from projects.permissions import IsProjectMember, IsProjectAdmin

class ActiveDiscussionDetail(generics.RetrieveAPIView):
    serializer_class = DiscussionSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_object(self):
        project_id = self.kwargs['project_id']
        return get_object_or_404(Discussion, project_id=project_id, is_active=True)

class CommentListCreate(generics.ListCreateAPIView):
    serializer_class = DiscussionCommentSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_queryset(self):
        discussion = get_object_or_404(Discussion, project_id=self.kwargs['project_id'], is_active=True)
        return DiscussionComment.objects.filter(discussion=discussion)

    def perform_create(self, serializer):
        discussion = get_object_or_404(Discussion, project_id=self.kwargs['project_id'], is_active=True)
        member = get_object_or_404(Member, project=discussion.project, user=self.request.user)
        serializer.save(member=member, discussion=discussion)