from django.urls import path

from .views.member import MemberDetail, MemberList, MyRole
from .views.project import CloneProject, ProjectDetail, ProjectList, ProjectLockView
from .views.tag import TagDetail, TagList
from .views.perspective import PerspectiveListView, PerspectiveDetailView, PerspectiveAttributeListView, CreatePerspectiveView, AssignPerspectiveToProject, AttributeDescriptionsView
from .views.discussion import ActiveDiscussionDetail, CommentDetail, CommentListCreate
from .views.reporting import ReportingView
from .views.voting import VotingSessionView, StartVotingView, SubmitVoteView, EndVotingView

urlpatterns = [
    path(route="projects", view=ProjectList.as_view(), name="project_list"),
    path(route="projects/<int:project_id>", view=ProjectDetail.as_view(), name="project_detail"),
    path(route="projects/<int:project_id>/my-role", view=MyRole.as_view(), name="my_role"),
    path(route="projects/<int:project_id>/tags", view=TagList.as_view(), name="tag_list"),
    path(route="projects/<int:project_id>/tags/<int:tag_id>", view=TagDetail.as_view(), name="tag_detail"),
    path(route="projects/<int:project_id>/members", view=MemberList.as_view(), name="member_list"),
    path(route="projects/<int:project_id>/clone", view=CloneProject.as_view(), name="clone_project"),
    path(route="projects/<int:project_id>/members/<int:member_id>", view=MemberDetail.as_view(), name="member_detail"),
    path(route="projects/<int:project_id>/perspectives", view=PerspectiveListView.as_view(), name="perspective_list"),
    path(route="projects/<int:project_id>/perspectives/<int:perspective_id>", view=PerspectiveDetailView.as_view(), name="perspective_detail"),
    path(route="projects/<int:project_id>/perspectives/<int:perspective_id>/attributes", view=PerspectiveAttributeListView.as_view(), name="perspective_attributes"),
    path(route="projects/<int:project_id>/perspectives/create", view=CreatePerspectiveView.as_view(), name="create_perspective"),
    path(route="projects/<int:project_id>/assign-perspective/<int:perspective_id>", view=AssignPerspectiveToProject.as_view(), name="assign_perspective"),
    path(route="projects/<int:project_id>/attribute-descriptions", view=AttributeDescriptionsView.as_view(), name="attribute_descriptions"),
    path(route="projects/<int:project_id>/discussion", view=ActiveDiscussionDetail.as_view(), name="active_discussion"),
    path(route="projects/<int:project_id>/discussion/comments", view=CommentListCreate.as_view(), name="discussion_comments"),
    path(route="projects/<int:project_id>/discussion/comments/<int:comment_id>", view=CommentDetail.as_view(), name="comment_detail"),
    path(route="projects/<int:project_id>/reporting/disagreements", view=ReportingView.as_view(), name="disagreement_reporting"),
    path(route="projects/<int:project_id>/lock", view=ProjectLockView.as_view(), name="project_lock"),
    path(route='projects/<int:project_id>/voting', view=VotingSessionView.as_view(), name='voting_status'),
    path(route='projects/<int:project_id>/start-voting', view=StartVotingView.as_view(), name='start_voting'),
    path(route='projects/<int:project_id>/vote', view=SubmitVoteView.as_view(), name='submit_vote'),
    path(route='projects/<int:project_id>/end-voting', view=EndVotingView.as_view(), name='end_voting'),
]
