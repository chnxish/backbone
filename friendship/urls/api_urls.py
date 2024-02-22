from django.urls import path

from friendship.views import (
    SendFriendRequestView,
    CancelFriendRequestView,
    ShowFriendRequestsView,
    AcceptRejectRequestView,
    SearchUserView,
    ShowFriendsView,
)

urlpatterns = [
    path("send-friend-request/", SendFriendRequestView.as_view(), name="send-friend-request"),
    path("cancel-friend-request/", CancelFriendRequestView.as_view(), name="cancel-friend-request"),
    path("friend-request-list/", ShowFriendRequestsView.as_view(), name="show-friend-requests"),
    path("friend-request-action/", AcceptRejectRequestView.as_view(), name="accept-reject-request"),
    path("search-user/<str:username>", SearchUserView.as_view(), name="search-user"),
    path("friend-list/", ShowFriendsView.as_view(), name="show-friends"),
]