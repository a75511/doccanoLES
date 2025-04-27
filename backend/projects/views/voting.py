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
        # Get the most recent voting session
        return project.voting_sessions.order_by('-created_at').first()

class StartVotingView(generics.UpdateAPIView):  # Changed from CreateUpdateAPIView
    serializer_class = VotingSessionSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get_object(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        # Get the most recent voting session or create a new one
        voting = project.voting_sessions.order_by('-created_at').first()
        if not voting:
            voting = GuidelineVoting.objects.create(
                project=project,
                status='not_started'
            )
        return voting

    def patch(self, request, *args, **kwargs):
        voting = self.get_object()
        discussion = get_object_or_404(Discussion, project=voting.project, is_active=True)
        
        # Update voting session
        voting.current_discussion = discussion
        voting.guidelines_snapshot = voting.project.guideline
        voting.status = 'voting'
        voting.save()
        
        serializer = self.get_serializer(voting)
        return Response(serializer.data, status=status.HTTP_200_OK)

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

class EndVotingView(generics.UpdateAPIView):  # Changed from CreateAPIView
    serializer_class = VotingSessionSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def get_object(self):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        return get_object_or_404(
            GuidelineVoting, 
            project=project, 
            status='voting'
        )

    def patch(self, request, *args, **kwargs):
        voting = self.get_object()
        
        # End current voting
        voting.status = 'completed'
        voting.save_guideline_snapshot()
        voting.save()

        # Close current discussion
        Discussion.objects.filter(project=voting.project, is_active=True).update(is_active=False)
        
        serializer = self.get_serializer(voting)
        return Response(serializer.data)
        
class CreateFollowUpVotingView(generics.CreateAPIView):
    serializer_class = VotingSessionSerializer
    permission_classes = [IsAuthenticated & IsProjectAdmin]

    def create(self, request, *args, **kwargs):
        project = get_object_or_404(Project, pk=self.kwargs['project_id'])
        previous_voting = project.voting_sessions.order_by('-created_at').first()
        
        if not previous_voting or previous_voting.status != 'completed':
            return Response(
                {"detail": "No completed voting session found."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create new discussion
        new_discussion = Discussion.objects.create(
            project=project,
            title="Follow-up Discussion",
            description="Continued discussion for unresolved guidelines",
            is_active=True
        )
        
        # Create new voting session
        voting = GuidelineVoting.objects.create(
            project=project,
            current_discussion=new_discussion,
            previous_voting=previous_voting,
            status='not_started',
            guidelines_snapshot=project.guideline
        )

        return Response(self.get_serializer(voting).data, status=status.HTTP_201_CREATED)