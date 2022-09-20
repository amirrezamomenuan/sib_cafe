from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status


User = get_user_model()

class TestLogin(TestCase):
    def setUp(self) -> None:
        user = User(first_name = 'adolf', last_name = 'Hitler', username = 666666)
        user.set_password('antijewish1')
        user.save()
    
    def test_login_with_correct_username_and_password(self):
        login_data = {'username': 666666, 'password': 'antijewish1'}
        response = self.client.post(path = reverse('login'), data = login_data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.json())
        self.assertTrue('refresh' in response.json())

    def test_login_with_incorrect_username_and_password(self):
        login_data = {'username': 757577, 'password': 'ilovejewish13'}
        response = self.client.post(path = reverse('login'), data = login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())

    def test_login_with_correct_username_and_wrong_password(self):
        login_data = {'username': 666666, 'password': 'ilovejewish13'}
        response = self.client.post(path = reverse('login'), data = login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())

    def test_login_with_incorrect_username_and_correct_password(self):
        login_data = {'username': 757577, 'password': 'antijewish1'}
        response = self.client.post(path = reverse('login'), data = login_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())
    
    def test_loging_without_username_and_password(self):
        login_data = {}
        response = self.client.post(path = reverse('login'), data = login_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse('access' in response.json())
        self.assertFalse('refresh' in response.json())