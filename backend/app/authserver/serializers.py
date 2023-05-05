from rest_framework.authtoken.models import Token
from rest_framework.serializers import ModelSerializer

from authserver.models import User


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "date_joined", "username", "password"]
        extra_kwargs = {"password": {"write_only": True}, "date_joined": {"read_only": True}}

    def create(self, validated_data):
        user = User(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        Token.objects.create(user=user)
        return user
