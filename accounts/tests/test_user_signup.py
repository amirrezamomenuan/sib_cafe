from django.test import TestCase

from django.contrib.auth import get_user_model
User = get_user_model()

class SignUpTest(TestCase):

    def test_signup_with_correct_username_and_password_and_name(self):
        correct_signup_data = {"first_name": "reza", 'last_name': 'eivazzadeh','username': 3421972, 'password': '1378reza'}
        response = self.client.post(path = '', data = correct_signup_data)
        


    def test_signup_with_incorrect_username_and_password_and_name(self):
        pass

    def test_signup_without_name(self):
        pass

    def test_signup_without_username_and_password(self):
        pass

    def test_if_user_is_already_signed_up(self):
        pass
