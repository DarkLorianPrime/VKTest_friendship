from rest_framework import status
from rest_framework.test import APITestCase


class AuthTest(APITestCase):
    def setUp(self) -> None:
        data = {"username": "darklorian",
                "password": "best"}
        self.client.post("http://127.0.0.1:5006/registration/", data)

    def test_empty_create_account(self):
        request = self.client.post("http://127.0.0.1:5006/registration/")
        self.assertEquals(request.status_code, status.HTTP_400_BAD_REQUEST, request.json())

    def test_create_double_account(self):
        data = {"username": "darklorian",
                "password": "best"}
        request = self.client.post("http://127.0.0.1:5006/registration/", data)
        self.assertEquals(request.status_code, status.HTTP_400_BAD_REQUEST, request.json())

    def test_create_account_with_all_params(self):
        data = {"username": "darklorian1",
                "password": "best"}

        request = self.client.post("http://127.0.0.1:5006/registration/", data)
        self.assertEquals(request.status_code, status.HTTP_201_CREATED, request.json())
        self.assertTrue(isinstance(request.json().get("id"), int))

    def test_authorization_with_all_params(self):
        data = {"username": "darklorian",
                "password": "best"}

        request = self.client.post("http://127.0.0.1:5006/token/", data)
        self.assertEquals(request.status_code, status.HTTP_200_OK, request.json())
        self.assertTrue("token" in request.json().keys())

    def test_authorization_with_one_param(self):
        data = {"username": "darklorian"}
        request = self.client.post("http://127.0.0.1:5006/token/", data)
        self.assertEquals(request.status_code, status.HTTP_400_BAD_REQUEST, request.json())
        self.assertTrue(request.json()["password"] == ['This field is required.'])

    def test_create_account_with_one_param(self):
        data = {"username": "darklorian"}
        request = self.client.post("http://127.0.0.1:5006/registration/", data)
        self.assertEquals(request.status_code, status.HTTP_400_BAD_REQUEST, request.json())