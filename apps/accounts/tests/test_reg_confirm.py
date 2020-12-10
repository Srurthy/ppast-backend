from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

User = get_user_model()


class RegistrationConfirmationTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.reg_cnf_url = reverse("ppast_confirm_registration")

    def test_confirm_registration(self):
        email = "newuser@domain.com"
        user = User.objects.create_user(email, email, is_active=False)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        data = {"uid": uid, "token": token}
        response = self.client.post(self.reg_cnf_url, data, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertTrue(User.objects.get(email=email).is_active)

    def test_confirm_reg_invalid_token(self):
        email = "newuser1@domain.com"
        user = User.objects.create_user(email, email, is_active=False)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        data = {"uid": uid, "token": "invalid token"}
        response = self.client.post(self.reg_cnf_url, data, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.get(email=email).is_active)
