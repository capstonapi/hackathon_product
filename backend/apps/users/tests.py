from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

User = get_user_model()


class AuthTests(APITestCase):
    def test_register_and_login(self):
        resp = self.client.post(
            "/api/auth/register/",
            {"username": "newuser", "password": "Str0ngPassw0rd!23", "email": "new@example.com"},
            format="json",
        )
        self.assertEqual(resp.status_code, 201)
        self.assertIn("token", resp.data)

        login = self.client.post(
            "/api/auth/login/", {"username": "newuser", "password": "Str0ngPassw0rd!23"}, format="json"
        )
        self.assertEqual(login.status_code, 200)
        self.assertIn("token", login.data)

    def test_register_rejects_weak_password(self):
        resp = self.client.post(
            "/api/auth/register/", {"username": "weak", "password": "123", "email": "weak@example.com"}, format="json"
        )
        self.assertEqual(resp.status_code, 400)

    def test_login_invalid_credentials_returns_401(self):
        User.objects.create_user(username="known", password="Str0ngPassw0rd!23")
        resp = self.client.post("/api/auth/login/", {"username": "known", "password": "wrong"}, format="json")
        self.assertEqual(resp.status_code, 401)

    def test_logout_requires_authentication(self):
        resp = self.client.post("/api/auth/logout/")
        self.assertEqual(resp.status_code, 401)

    def test_user_can_delete_own_account(self):
        user = User.objects.create_user(username="erase", password="Str0ngPassw0rd!23")
        self.client.force_authenticate(user=user)
        self.assertEqual(self.client.delete("/api/auth/account/").status_code, 204)
        self.assertFalse(User.objects.filter(username="erase").exists())
