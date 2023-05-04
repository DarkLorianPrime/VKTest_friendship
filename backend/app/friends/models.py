import uuid
from django.conf import settings
from django.contrib.auth.models import User

from django.db import models


class FriendRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    to_request = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   related_name="friend_to_request")
    from_request = models.ForeignKey(to=settings.AUTH_USER_MODEL,
                                     on_delete=models.CASCADE,
                                     related_name="friend_from_request")
    is_accepted = models.BooleanField(default=False)
    answered_on = models.DateTimeField(null=True)

