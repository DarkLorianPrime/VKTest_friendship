from django.urls import path

from friends import views

urlpatterns = [
    path("request/<str:username>/", views.Friendship.as_view({"post": "send_request"})),
    path("request/<str:username>/status", views.Friendship.as_view({"get": "get_status"})),
    path("<str:username>/remove/", views.Friendship.as_view({"delete": "remove_friend"})),
    path("request/answer/<str:request_id>/", views.Friendship.as_view({"post": "answer_request"})),
    path("requests/", views.Friendship.as_view({"get": "get_all_requests"})),
    path("", views.Friendship.as_view({"get": "get_friends"}))
]