from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

User = get_user_model()


class RegistrationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.reg_url = reverse("ppast_register_user")

    def test_register_user(self):
        email = "user8@domain.com"
        passwd = "p0iooijlk2@#"
        first = "first"
        last = "last"

        data = {
            "email": email,
            "username": email,
            "password1": passwd,
            "password2": passwd,
            "first_name": first,
            "last_name": last,
        }

        response = self.client.post(self.reg_url, data, format="json")
        resp_json = response.json()
        self.assertEqual(response.status_code, 201)
        user = User.objects.get(email=email)
        self.assertEqual(user.email, email)
        self.assertNotEqual(user.password, passwd)
        self.assertEqual(user.first_name, first)
        self.assertEqual(user.last_name, last)
        self.assertIn("username", resp_json)
        self.assertIn("email", resp_json)
        self.assertIn("first_name", resp_json)
        self.assertIn("last_name", resp_json)
        self.assertNotIn("password", resp_json)
        self.assertNotIn("password1", resp_json)
        self.assertNotIn("password2", resp_json)
        # user should not get activated right after registration
        self.assertFalse(user.is_active)

    def test_register_invalid_pass(self):
        email = "user9@domain.com"
        passwd = "p0iooijlk2@#"
        first = "first"
        last = "last"

        data = {
            "email": email,
            "password1": passwd,
            "password2": "asdb",
            "first_name": first,
            "last_name": last,
        }

        response = self.client.post(self.reg_url, data, format="json")
        self.assertEqual(response.status_code, 400)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(email=email)

    def test_register_dulicate_email(self):
        email = "dupuser@domain.com"
        User.objects.create_user(email, email=email)
        passwd = "p0iooijlk2@#"
        first = "first"
        last = "last"

        data = {
            "username": email,
            "email": email,
            "password1": passwd,
            "password2": passwd,
            "first_name": first,
            "last_name": last,
        }

        response = self.client.post(self.reg_url, data, format="json")
        resp_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", resp_json)
        self.assertEqual(User.objects.filter(email=email).count(), 1)

    def test_register_dulicate_email_case_insensitive(self):
        email = "dupUser1@domain.com"
        User.objects.create_user(email, email=email)
        passwd = "p0iooijlk2@#"
        first = "first"
        last = "last"

        data = {
            "username": email.lower(),
            "email": email.lower(),
            "password1": passwd,
            "password2": passwd,
            "first_name": first,
            "last_name": last,
        }

        response = self.client.post(self.reg_url, data, format="json")
        resp_json = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertIn("email", resp_json)
        self.assertEqual(User.objects.filter(email=email).count(), 1)
