from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status


User = get_user_model()

class SignUpTest(TestCase):
    def setUp(self) -> None:
        user = User(first_name = 'nikola', last_name = 'tesla', username = 7777777)
        user.set_password('nikola1943tesla')
        user.save()

    def test_signup_with_correct_username_and_password_and_name(self):
        signup_data = {"first_name": "reza", 'last_name': 'eivazzadeh','username': 3421972, 'password': '1378reza'}
        response = self.client.post(path = reverse('signup'), data = signup_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.json())
        self.assertTrue('refresh' in response.json())

    def test_signup_with_incorrect_username_and_password_and_name(self):
        signup_data = {"first_name": "reza168", 'last_name': 'eivafss23423d2zzadeh','username': 'ffwf51wf68w', 'password': '1'}
        response = self.client.post(path = reverse('signup'), data = signup_data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())

    def test_signup_without_firstname_and_last_name(self):
        signup_data = {'username': 3421972, 'password': '1378reza'}
        response = self.client.post(path = reverse('signup'), data = signup_data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())

    def test_signup_without_username(self):
        signup_data = {"first_name": "reza", 'last_name': 'eivazzadeh','password': '1378reza'}
        response = self.client.post(path = reverse('signup'), data = signup_data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())
    
    def test_signup_without_password(self):
        signup_data = {"first_name": "reza", 'last_name': 'eivazzadeh','username': 3421972}
        response = self.client.post(path = reverse('signup'), data = signup_data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())

    def test_if_user_is_already_signed_up(self):
        signup_data = {"first_name": "reza", 'last_name': 'eivazzadeh','username': 7777777, 'password': '1378reza'}
        response = self.client.post(path = reverse('signup'), data = signup_data)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
