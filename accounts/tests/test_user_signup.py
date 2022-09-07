from django.test import TestCase

from accounts.models import User


class SignUpTest(TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_signup_with_correct_username_and_password_and_name(self):
        pass

    def test_signup_with_incorrect_username_and_password_and_name(self):
        pass

    def test_signup_without_name(self):
        pass

    def test_signup_without_username_and_password(self):
        pass