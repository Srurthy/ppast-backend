from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class LoginTestCase(TestCase):
    def setUp(self):
        User.objects.create_user("user1", email="user1@domain.com", password="pass1")
        self.client = APIClient()
        self.url = reverse("rest_login")

    def test_success_login(self):
        creds = {"email": "user1@domain.com", "password": "pass1"}
        response = self.client.post(self.url, creds, format="json")
        resp_json = response.json()
        self.assertIn("token", resp_json)
        self.assertIn("user", resp_json)
        self.assertIn("is_staff", resp_json.get("user"))
        self.assertNotIn("password", resp_json.get("user"))
        self.assertEqual(response.status_code, 200)

    def test_login_pass_with_space_prefix(self):
        creds = {"email": "user1@domain.com", "password": "  pass1"}
        response = self.client.post(self.url, creds, format="json")
        resp_json = response.json()
        self.assertIn("non_field_errors", resp_json)
        self.assertEqual(response.status_code, 400)

    def test_failed_login(self):
        creds = {"email": "user1@domain.com", "password": "pass"}
        response = self.client.post(self.url, creds, format="json")
        resp_json = response.json()
        self.assertIn("non_field_errors", resp_json)
        self.assertEqual(response.status_code, 400)

    def test_empty_email_validation(self):
        creds = {"email": "", "password": "pass"}
        response = self.client.post(self.url, creds, format="json")
        resp_json = response.json()
        self.assertIn("email", resp_json)
        self.assertEqual(response.status_code, 400)

    def test_empty_password_validation(self):
        creds = {"email": "user1@domain.com", "password": ""}
        response = self.client.post(self.url, creds, format="json")
        resp_json = response.json()
        self.assertIn("password", resp_json)
        self.assertEqual(response.status_code, 400)
