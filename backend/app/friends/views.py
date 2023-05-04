import datetime

from django.db.models import F, Q
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

    def get_status(self, request: Request, username: str):
        user = User.objects.filter(~Q(id=request.user.id), username=username).first()
        if user is None:
            return Response({"detail": "user not found"}, status=HTTP_404_NOT_FOUND)

        friendrequest = FriendRequest.objects.filter(Q(to_request=user.id) | Q(from_request=user.id)).first()

        if friendrequest is not None:
            substatus = "outcoming" if friendrequest.from_request.id == user.id else "incoming"

            return Response({"status": f"{substatus} request"})

        elif request.user.friends.filter(id=user.id):
            return Response({"status": "friend"})

        return Response({"status": "nothing"})

    def send_request(self, request: Request, username: str):
        user = User.objects.filter(~Q(id=request.user.id), username=username).first()
        query = {}

        if user is None:
            return Response({"detail": "user not found"}, status=HTTP_404_NOT_FOUND)

        if request.user.friends.filter(id=user.id):
            return Response({"detail": "this user already is your friend"}, status=HTTP_400_BAD_REQUEST)

        if FriendRequest.objects.filter(from_request=user, to_request=request.user).exists():
            return Response({"detail": "request already exists"}, status=HTTP_400_BAD_REQUEST)

        opposite_answers = FriendRequest.objects.filter(from_request=request.user, to_request=user)
        opposite_answer = opposite_answers.first()
        if opposite_answer is not None:
            query = {"is_accepted": True, "answered_on": datetime.datetime.now()}
            opposite_answers.update(**query)
            request.user.friends.add(opposite_answer.to_request)

        FriendRequest.objects.create(from_request=user, to_request=request.user, **query)
        return Response({"status": "ok"}, status=HTTP_201_CREATED)

    def get_all_requests(self, request: Request):
        is_incoming: bool = request.query_params.get("incoming", "null").lower() == "true"
        query = {"to_request": request.user.id}

        if is_incoming:
            query = {"from_request": request.user.id}

        to_requests = FriendRequest.objects.filter(**query, is_accepted=False, answered_on=None)
        return Response(to_requests
                        .annotate(username=F("from_request__username"))
                        .values("id", "username", "is_accepted"))

    def answer_request(self, request: Request, request_id: str):
        is_accept: bool = request.query_params.get("action", "null").lower() == "accept"  # accept=true - cancel=false
        query = {"is_accepted": is_accept, "answered_on": datetime.datetime.now()}

        to_requests = FriendRequest.objects.filter(from_request=request.user, id=request_id, answered_on=None)
        to_request = to_requests.first()

        if to_request:
            to_requests.update(**query)

            if is_accept:
                request.user.friends.add(to_request.to_request)

            return Response({"status": "ok"})

        return Response({"detail": "request_id not found"}, status=HTTP_404_NOT_FOUND)

    def get_friends(self, request: Request):
        return Response(request.user.friends.values("id", "username"))

    def remove_friend(self, request: Request, username):
        removable_friend = request.user.friends.filter(~Q(id=request.user.id), username=username)

        if not removable_friend.exists():
            return Response({"detail": "user not found"}, status=HTTP_404_NOT_FOUND)

        request.user.friends.remove(removable_friend.first())
        return Response({"status": "ok"})
