from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_auth.utils import jwt_encode
from rest_framework.test import APIClient

User = get_user_model()


class LoginTestCase(TestCase):
    def setUp(self):
        User.objects.create_user("user1", email="user1@domain.com", password="pass1")
        self.client = APIClient()
        self.url = reverse("rest_password_change")

    def test_passwd_change(self):
        user = User.objects.get(email="user1@domain.com")
        data = {
            "old_password": "pass1",
            "new_password1": "adf@#290nkdf",
            "new_password2": "adf@#290nkdf",
        }
        token = "JWT %s" % jwt_encode(user)
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_passwd_change_no_old_pass(self):
        user = User.objects.get(email="user1@domain.com")
        data = {"new_password1": "adf@#290nkdf", "new_password2": "adf@#290nkdf"}
        token = "JWT %s" % jwt_encode(user)
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 400)

    def test_passwd_change_no_token(self):
        data = {"new_password1": "adf@#290nkdf", "new_password2": "adf@#290nkdf"}
        self.client.credentials()
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)

    def test_passwd_invalid_token(self):
        data = {"new_password1": "adf@#290nkdf", "new_password2": "adf@#290nkdf"}
        token = "JWT asdfadfsdfdfd"
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.post(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)
