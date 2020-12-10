from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_auth.utils import jwt_encode
from rest_framework.test import APIClient

User = get_user_model()


class ProfileTestCase(TestCase):
    def setUp(self):
        self.email = "profile@user.com"
        self.user = User.objects.create_user(
            self.email, email=self.email, password="pass1", first_name="first", last_name="last"
        )
        self.client = APIClient()
        self.url = reverse("ppast_user_profile")

    def test_get_profile(self):
        token = "JWT %s" % jwt_encode(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=token)
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 200)
        profile = response.json()
        self.assertEqual(profile["username"], self.user.username)
        self.assertEqual(profile["email"], self.user.email)
        self.assertEqual(profile["first_name"], self.user.first_name)
        self.assertEqual(profile["last_name"], self.user.last_name)
        self.assertNotIn("password", profile)
        self.assertNotIn("is_active", profile)

    def test_get_profile_no_auth(self):
        response = self.client.get(self.url, format="json")
        self.assertEqual(response.status_code, 401)

    def test_update_profile(self):
        token = "JWT %s" % jwt_encode(self.user)
        self.client.credentials(HTTP_AUTHORIZATION=token)
        old_pass = self.user.password
        was_staff = self.user.is_staff
        data = {"first_name": "second", "password": "poiu0987)(*&)", "is_staff": True}
        response = self.client.put(self.url, data, format="json")
        profile = response.json()
        user = User.objects.get(email=self.email)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(profile["username"], user.username)
        self.assertEqual(profile["email"], user.email)
        self.assertEqual(profile["first_name"], "second")
        self.assertEqual(profile["last_name"], user.last_name)
        self.assertEqual(profile["is_staff"], user.is_staff)
        # should not update password, admin status
        self.assertEqual(old_pass, user.password)
        self.assertEqual(was_staff, user.is_staff)

    def test_update_profile_no_auth(self):
        data = {"first_name": "third"}
        response = self.client.put(self.url, data, format="json")
        self.assertEqual(response.status_code, 401)
        with self.assertRaises(User.DoesNotExist):
            User.objects.get(first_name="third")
