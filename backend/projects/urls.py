from django.urls import path

from .views.member import MemberDetail, MemberList, MyRole
from .views.project import CloneProject, ProjectDetail, ProjectList, ProjectLockView
from .views.tag import TagDetail, TagList
from .views.perspective import PerspectiveListView, PerspectiveDetailView, PerspectiveAttributeListView, CreatePerspectiveView, AssignPerspectiveToProject
from .views.discussion import ActiveDiscussionDetail, CommentDetail, CommentListCreate
from .views.reporting import disagreement_statistics

urlpatterns = [
    path(route="projects", view=ProjectList.as_view(), name="project_list"),
    path(route="projects/<int:project_id>", view=ProjectDetail.as_view(), name="project_detail"),
    path(route="projects/<int:project_id>/my-role", view=MyRole.as_view(), name="my_role"),
    path(route="projects/<int:project_id>/tags", view=TagList.as_view(), name="tag_list"),
    path(route="projects/<int:project_id>/tags/<int:tag_id>", view=TagDetail.as_view(), name="tag_detail"),
    path(route="projects/<int:project_id>/members", view=MemberList.as_view(), name="member_list"),
    path(route="projects/<int:project_id>/clone", view=CloneProject.as_view(), name="clone_project"),
    path(route="projects/<int:project_id>/members/<int:member_id>", view=MemberDetail.as_view(), name="member_detail"),
    path("projects/<int:project_id>/perspectives", PerspectiveListView.as_view(), name="perspective_list"),
    path("projects/<int:project_id>/perspectives/<int:perspective_id>", PerspectiveDetailView.as_view(), name="perspective_detail"),
    path("projects/<int:project_id>/perspectives/<int:perspective_id>/attributes", PerspectiveAttributeListView.as_view(), name="perspective_attributes"),
    path("projects/<int:project_id>/perspectives/create", CreatePerspectiveView.as_view(), name="create_perspective"),
    path("projects/<int:project_id>/assign-perspective/<int:perspective_id>", AssignPerspectiveToProject.as_view(), name="assign_perspective"),
    path("projects/<int:project_id>/discussion", ActiveDiscussionDetail.as_view(), name="active_discussion"),
    path("projects/<int:project_id>/discussion/comments", CommentListCreate.as_view(), name="discussion_comments"),
    path("projects/<int:project_id>/discussion/comments/<int:comment_id>", CommentDetail.as_view(), name="comment_detail"),
    path("projects/<int:project_id>/lock", ProjectLockView.as_view(), name="project_lock"),
    path("projects/<int:project_id>/reporting/disagreements-statistics", disagreement_statistics, name="disagreement_reporting"),
]
