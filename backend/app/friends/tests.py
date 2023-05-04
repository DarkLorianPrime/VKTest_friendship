import uuid

from rest_framework import status
from rest_framework.test import APITestCase


class FriendsTest(APITestCase):
    domain = "http://127.0.0.1:5006/"

    def setUp(self) -> None:
        data = {"username": "darklorian", "password": "best"}

        data_best = {"username": "bestlorian", "password": "dark"}

        self.client.post(f"{self.domain}registration/", data)
        self.client.post(f"{self.domain}registration/", data_best)

        request = self.client.post(f"{self.domain}token/", data)
        request_2 = self.client.post(f"{self.domain}token/", data_best)

        self.darklorian = {"Authorization": f"Token {request.json()['token']}"}
        self.bestlorian = {"Authorization": f"Token {request_2.json()['token']}"}

    def check_friend(self, need_value: int = 1):
        request_to_incoming = self.client.get(f"{self.domain}friends/", headers=self.bestlorian)
        request_to_incoming_dark = self.client.get(f"{self.domain}friends/", headers=self.darklorian)
        return len(request_to_incoming.json()) == len(request_to_incoming_dark.json()) == need_value

    def send_request(self, header: dict, to: str, need_404: bool = False):
        request = self.client.post(f"{self.domain}friends/request/{to}/", headers=header)
        if not need_404:
            self.assertTrue(request.status_code == status.HTTP_201_CREATED, request.json())
        return request

    def answer_request(self, header: dict, request_id: str, action: str, need_404: bool = False):
        request = self.client.post(f"{self.domain}friends/request/answer/{request_id}/?action={action}", headers=header)
        if not need_404:
            self.assertTrue(request.json()["status"] == "ok")
        return request

    def get_requests(self, header: dict, incoming: bool):
        request = self.client.get(f"{self.domain}friends/requests/?incoming={incoming}", headers=header)

        return request.json(), request.status_code

    def delete_friend(self, header: dict, to: str):
        response = self.client.delete(f"http://127.0.0.1:5006/friends/{to}/remove/", headers=header)
        self.assertTrue(response.status_code == 204)

    def get_status(self, header: dict, to: str, need_status: str):
        request = self.client.get(f"http://127.0.0.1:5006/friends/request/{to}/status", headers=header)
        self.assertTrue(need_status in request.json()["status"])
        return request

    def test_request_friendship(self):
        self.send_request(self.darklorian, "bestlorian")
        request_in, _ = self.get_requests(self.bestlorian, incoming=True)  # входящие
        request_out, _ = self.get_requests(self.darklorian, incoming=False)  # исходящие

        self.assertEquals(len(request_in), 1, request_in)
        self.assertEquals(len(request_out), 1, request_out)

        self.assertTrue(request_out[0]["username"] == request_in[0]["username"] == "bestlorian")

    def test_accept_request_friendship(self):
        self.send_request(self.darklorian, to="bestlorian")

        request_json, request_status = self.get_requests(header=self.bestlorian, incoming=True)

        self.assertEquals(len(request_json), 1, request_json)

        self.answer_request(header=self.bestlorian, request_id=request_json[0]['id'], action="accept")

        request_json, _ = self.get_requests(header=self.bestlorian, incoming=True)
        self.assertTrue(len(request_json) == 0)

        self.assertTrue(self.check_friend())

    def test_cancel_request_friendship(self):
        self.send_request(header=self.darklorian, to="bestlorian")
        request_json, _ = self.get_requests(header=self.bestlorian, incoming=True)
        self.assertEquals(len(request_json), 1, request_json)

        self.answer_request(header=self.bestlorian, request_id=request_json[0]['id'], action="cancel")

        request_json, _ = self.get_requests(header=self.bestlorian, incoming=True)

        self.assertTrue(len(request_json) == 0)
        self.assertTrue(self.check_friend(0))

    def test_not_found_request(self):
        answer = self.answer_request(header=self.bestlorian, need_404=True,
                                     request_id=str(uuid.uuid4()), action="cancel")
        self.assertTrue(answer.status_code == 404)

    def test_auto_accept_friendship(self):
        self.send_request(header=self.darklorian, to="bestlorian")
        self.send_request(header=self.bestlorian, to="darklorian")

        self.assertTrue(self.check_friend())

    def test_self_invite(self):
        request = self.send_request(need_404=True, to="bestlorian", header=self.bestlorian)
        self.assertTrue(request.status_code == status.HTTP_404_NOT_FOUND, request.json())

    def test_remove_friend(self):
        self.send_request(header=self.bestlorian, to="darklorian")
        request_json, _ = self.get_requests(header=self.bestlorian, incoming=False)
        self.answer_request(header=self.darklorian, request_id=request_json[0]["id"], action="accept")

        self.assertTrue(self.check_friend())

        self.delete_friend(header=self.bestlorian, to="darklorian")
        self.assertTrue(self.check_friend(0))

    def test_request_status(self):
        self.get_status(header=self.bestlorian, to="darklorian", need_status="nothing")
        self.send_request(header=self.bestlorian, to="darklorian")
        self.get_status(header=self.bestlorian, to="darklorian", need_status="outcoming")
        self.get_status(header=self.darklorian, to="bestlorian", need_status="incoming")

        request_json, _ = self.get_requests(header=self.darklorian, incoming=True)
        self.answer_request(header=self.darklorian, request_id=request_json[0]["id"], action="accept")

        self.get_status(header=self.darklorian, to="bestlorian", need_status="friend")
