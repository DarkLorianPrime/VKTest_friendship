import datetime
import pytz

from django.db.models import F, Q
from django.utils import timezone
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.status import HTTP_201_CREATED, HTTP_404_NOT_FOUND, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ModelViewSet

from authserver.models import User
from friends.models import FriendRequest


class Friendship(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def update_fields(self, instance, fields: dict):
        for key, value in fields.items():
            setattr(instance, key, value)
        instance.save()

    def get_status(self, request: Request, username: str):
        user = get_object_or_404(User, ~Q(id=request.user.id), username=username)

        if request.user.friends.filter(id=user.id).exists():
            return Response({"status": "friend"})

        friend_request = FriendRequest.objects.filter(Q(to_request=user.id) | Q(from_request=user.id)).first()

        if friend_request:
            substatus = "outcoming" if friend_request.from_request.id == user.id else "incoming"
            return Response({"status": f"{substatus} request"})

        return Response({"status": "nothing"})

    def send_request(self, request: Request, username: str):
        user = get_object_or_404(User, ~Q(id=request.user.id), username=username)
        query = {}

        if request.user.friends.filter(id=user.id):
            return Response({"detail": "this user already is your friend"}, status=HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_request=user, to_request=request.user).exists():
            return Response({"detail": "request already exists"}, status=HTTP_400_BAD_REQUEST)

        opposite_answer = FriendRequest.objects.filter(from_request=request.user, to_request=user).first()

        if opposite_answer is not None:
            self.update_fields(opposite_answer, query)
            query = {"is_accepted": True, "answered_on": datetime.datetime.now(tz=timezone.utc)}
            request.user.friends.add(opposite_answer.to_request)

        FriendRequest.objects.create(from_request=user, to_request=request.user, **query)
        return Response({"status": "ok"}, status=HTTP_201_CREATED)

    def get_all_requests(self, request: Request):
        is_incoming: bool = request.query_params.get("incoming", "false").lower() == "true"

        query_key = "from_request" if is_incoming else "to_request"
        query = {query_key: request.user.id}

        to_requests = FriendRequest.objects.filter(**query, is_accepted=False, answered_on=None)
        return Response(to_requests
                        .annotate(username=F("from_request__username"))
                        .values("id", "username", "is_accepted"))

    def answer_request(self, request: Request, request_id: str):
        is_accept: bool = request.query_params.get("action", "accept").lower() == "accept"  # accept=true - cancel=false
        query = {"is_accepted": is_accept, "answered_on": datetime.datetime.now(tz=timezone.utc)}

        to_request = FriendRequest.objects.filter(from_request=request.user, id=request_id, answered_on=None).first()

        if to_request is None:
            return Response({"detail": "request_id not found"}, status=HTTP_404_NOT_FOUND)

        self.update_fields(to_request, query)

        if is_accept:
            request.user.friends.add(to_request.to_request)

        return Response({"status": "ok"})

    def get_friends(self, request: Request):
        return Response(request.user.friends.values("id", "username"))

    def remove_friend(self, request: Request, username):
        user = get_object_or_404(User, ~Q(id=request.user.id), username=username)

        request.user.friends.remove(user)
        return Response({"status": "ok"})
