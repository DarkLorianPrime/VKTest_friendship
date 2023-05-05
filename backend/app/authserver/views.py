from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework.permissions import AllowAny
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer, ModelSerializer
from rest_framework.status import HTTP_201_CREATED
from rest_framework.viewsets import ModelViewSet

from authserver.serializers import UserSerializer


class Authorization(ModelViewSet):
    permission_classes: list = [AllowAny]
    serializer_class: Serializer = UserSerializer

    @extend_schema(
        description="Регистрирует пользователя с переданным username и паролем.",
    )
    def create(self, request: Request, *args, **kwargs):
        serialized: ModelSerializer = self.get_serializer(data=request.POST)
        serialized.is_valid(raise_exception=True)
        self.perform_create(serialized)

        return Response(serialized.data, status=HTTP_201_CREATED)
