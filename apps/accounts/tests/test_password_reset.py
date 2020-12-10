from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

User = get_user_model()


class LoginTestCase(TestCase):
    def setUp(self):
        User.objects.create_user("user1", email="user1@domain.com", password="pass1")
        self.client = APIClient()
        self.reset_url = reverse("rest_password_reset")
        self.reset_cnf_url = reverse("rest_password_reset_confirm")

    def test_pass_reset(self):
        data = {"email": "user1@domain.com"}
        response = self.client.post(self.reset_url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_pass_reset_invalid_user(self):
        """
        Returns success message though actual email is not sent
        """
        data = {"email": "user2@domain.com"}
        response = self.client.post(self.reset_url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_pass_reset_confirm(self):
        user = User.objects.get(username="user1")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        newpass = "p@ssw0rds3cre"
        data = {"uid": uid, "token": token, "new_password1": newpass, "new_password2": newpass}

        response = self.client.post(self.reset_cnf_url, data, format="json")
        self.assertEqual(response.status_code, 200)

    def test_pass_reset_confirm_invalid_token(self):
        user = User.objects.get(username="user1")
        token = "invalid-token"
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        newpass = "p@ssw0rds3cre"
        data = {"uid": uid, "token": token, "new_password1": newpass, "new_password2": newpass}

        response = self.client.post(self.reset_cnf_url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("token", response.json())

    def test_pass_reset_confirm_invalid_uid(self):
        user = User.objects.get(username="user1")
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk + 1))
        newpass = "p@ssw0rds3cre"
        data = {"uid": uid, "token": token, "new_password1": newpass, "new_password2": newpass}

        response = self.client.post(self.reset_cnf_url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("uid", response.json())
