import datetime

from django.db.models import F, Q
from django.utils import timezone
from drf_spectacular.utils import extend_schema, OpenApiResponse, OpenApiExample, OpenApiParameter
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.viewsets import ViewSet

from authserver.models import User
from friends.models import FriendRequest


class Friendship(ViewSet):
    permission_classes = [IsAuthenticated]

    def update_fields(self, instance, fields: dict):
        for key, value in fields.items():
            setattr(instance, key, value)
        instance.save()

    @extend_schema(
        description="Позволяет получить статус между авторизованным пользователем и переданным username",
        parameters=[OpenApiParameter(name="Authorization", location="header", required=True,
                                     description="Требуется для определения пользователя. В формате: \"Authorization: Token {your token}\""),
                    OpenApiParameter(name="username", location="path",
                                     description="Определяет, статус какого пользователя будет возврщен.")],
        responses={
            200: OpenApiResponse(description="Возвращает одну из констант: nothing, incoming, outcoming, friend"),
            404: OpenApiResponse(description="Пользователь с таким username не найден")
        }

    )
    def get_status(self, request: Request, username: str):
        user = get_object_or_404(User, ~Q(id=request.user.id), username=username)

        if request.user.friends.filter(id=user.id).exists():
            return Response({"status": "friend"})

        friend_request = FriendRequest.objects.filter(Q(to_request=user.id) | Q(from_request=user.id)).first()

        if friend_request:
            substatus = "outcoming" if friend_request.from_request.id == user.id else "incoming"
            return Response({"status": f"{substatus} request"})

        return Response({"status": "nothing"})

    @extend_schema(
        description="Отправляет запрос в друзья переданному username. Если от него уже есть запрос - заявка в друзья будет принята автоматически",
        parameters=[OpenApiParameter(name="Authorization", location="header", required=True,
                                     description="Требуется для определения пользователя. В формате: \"Authorization: Token {your token}\""),
                    OpenApiParameter(name="username", location="path",
                                     description="Определяет, статус какого пользователя будет возврщен.")],
        responses={
            201: OpenApiResponse(description="Возвращается если запрос был отправлен\\автоматически принят"),
            200: OpenApiResponse(description="Возвращается если с запросом возникли проблемыю"),
            404: OpenApiResponse(description="Пользователь с таким username не найден")
        }
    )
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

    @extend_schema(
        description="Позволяет получить все запросы (входящие или исходящие)",
        parameters=[OpenApiParameter(name="Authorization", location="header", required=True,
                                     description="Требуется для определения пользователя. В формате: \"Authorization: Token {your token}\""),
                    OpenApiParameter(name="incoming", location="query",
                                     description="Определяет, какие запросы будут выведены. Если true - то входящие, или исходящие")],
        responses={
            200: OpenApiResponse(description="возвращает массив объектов запросов пользователя с полями id, username, is_accepted")
        }
    )
    def get_all_requests(self, request: Request):
        is_incoming: bool = request.query_params.get("incoming", "false").lower() == "true"

        query_key = "from_request" if is_incoming else "to_request"
        query = {query_key: request.user.id}

        to_requests = FriendRequest.objects.filter(**query, is_accepted=False, answered_on=None)
        return Response(to_requests
                        .annotate(username=F("from_request__username"))
                        .values("id", "username", "is_accepted"))

    @extend_schema(
        description="Позволяет отклонить или принять запрос в друзья, указав его номер в пути",
        parameters=[
            OpenApiParameter(name="Authorization", location="header", required=True,
                             description="Требуется для определения пользователя. В формате: \"Authorization: Token {your token}\""),

            OpenApiParameter(name="request_id", location="path",
                             description="id запроса, на который будет прислан ответ"),
            OpenApiParameter(name="action", location="query",
                             description="Если accept - то принять заявку, если cancel - то отклонить. По-умолчанию - "
                                         "accept")
        ],
        responses={
            200: OpenApiResponse(description="Возвращает OK если ответ успешно сохранен"),
            404: OpenApiResponse(description="Возвращает not found если запрос с таким id не найден")
        }

    )
    def answer_request(self, request: Request, request_id: str):
        is_accept: bool = request.query_params.get("action", "accept").lower() == "accept"  # accept=true - cancel=false
        query = {"is_accepted": is_accept, "answered_on": datetime.datetime.now(tz=timezone.utc)}
        to_request = get_object_or_404(FriendRequest, from_request=request.user, id=request_id, answered_on=None)

        self.update_fields(to_request, query)

        if is_accept:
            request.user.friends.add(to_request.to_request)

        return Response({"status": "ok"})

    @extend_schema(
        description="Возвращает всех друзей по переданному токену",
        parameters=[OpenApiParameter(name="Authorization", location="header", required=True,
                                     description="Требуется для определения пользователя. В формате: \"Authorization: Token {your token}\"")],
        responses={200: OpenApiResponse(
            description="return massive with objects containing users and their ID's",
            examples=[OpenApiExample('[{"id": 1, "username": "dima"}]')]
        )}
    )
    def get_friends(self, request: Request):
        return Response(request.user.friends.values("id", "username"))

    @extend_schema(
        description="Удаляет друга по переданному username.",
        parameters=[OpenApiParameter(name="Authorization", location="header", required=True,
                                     description="Требуется для определения пользователя. В формате: \"Authorization: Token {your token}\""),
                    OpenApiParameter(name="username", location="path",
                                     description="Определяет какой пользователь будет удален из друзей.")],

        responses={
            204: None,
            404: OpenApiResponse(description="Возвращается если друг не найден")
        }
    )
    def remove_friend(self, request: Request, username):
        user = get_object_or_404(User, ~Q(id=request.user.id), username=username)

        request.user.friends.remove(user)
        return Response(status=204)
