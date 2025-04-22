from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from projects.models import Project, Discussion, Member
from projects.models import GuidelineVoting, MemberVote
from projects.serializers import VotingSessionSerializer, MemberVoteSerializer
from projects.permissions import IsProjectAdmin, IsProjectMember

class VotingSessionView(generics.RetrieveAPIView):
    serializer_class = VotingSessionSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    def get_object(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return get_object_or_404(GuidelineVoting, project=project)

class StartVotingView(generics.CreateAPIView):
    serializer_class = VotingSessionSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get_object(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        discussion = get_object_or_404(Discussion, project=project, is_active=True)
        voting, _ = GuidelineVoting.objects.get_or_create(project=project)
        voting.current_discussion = discussion
        voting.guidelines_snapshot = project.guideline
        voting.status = 'voting'
        voting.save()
        return voting

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        discussion = get_object_or_404(Discussion, project=project, is_active=True)
        
        voting, created = GuidelineVoting.objects.update_or_create(
            project=project,
            defaults={
                'current_discussion': discussion,
                'guidelines_snapshot': project.guideline,
                'status': 'voting'
            }
        )
        return Response(self.get_serializer(voting).data, status=status.HTTP_201_CREATED)

class SubmitVoteView(generics.CreateAPIView):
    serializer_class = MemberVoteSerializer
    permission_classes = [IsAuthenticated & IsProjectMember]

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        voting = get_object_or_404(GuidelineVoting, project=project, status='voting')
        member = get_object_or_404(Member, user=request.user, project=project)
        
        if MemberVote.objects.filter(voting_session=voting, user=member).exists():
            return Response(
                {"detail": "You have already voted in this session."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(voting_session=voting, user=member)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class EndVotingView(generics.CreateAPIView):
    serializer_class = VotingSessionSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get_object(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        voting = get_object_or_404(GuidelineVoting, project=project, status='voting')
        voting.status = 'completed'
        voting.save()
        return voting
    
    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        voting = get_object_or_404(GuidelineVoting, project=project, status='voting')
        
        # End voting
        voting.status = 'completed'
        voting.save_guideline_snapshot()
        voting.save()

        # Create new discussion if agreement not met
        total_votes = voting.agree_count + voting.disagree_count
        if total_votes > 0 and (voting.agree_count / total_votes) < 0.7:  # 70% threshold
            Discussion.objects.filter(project=project, is_active=True).update(is_active=False)
            new_discussion = Discussion.objects.create(
                project=project,
                title="Follow-up Discussion",
                description="Continued discussion for unresolved guidelines",
                is_active=True
            )
            GuidelineVoting.objects.create(
                project=project,
                current_discussion=new_discussion,
                status='not_started',
                guidelines_snapshot=project.guideline
            )

        return Response(self.get_serializer(voting).data)