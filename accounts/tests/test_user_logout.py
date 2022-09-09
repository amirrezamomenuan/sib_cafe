from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APITestCase, APIClient

User = get_user_model()

class TestLogOut(APITestCase):
    def setUp(self) -> None:
        user = User(first_name= 'albert', last_name= 'einstin', username= 1234567)
        user.set_password('E=====mc2')
        user.save()

        response = self.client.post(path = reverse('login'), data = {'username':1234567, 'password': "E=====mc2"})
        self.refresh_token = response.json().get('refresh')
        self.access_token = response.json().get('access')
    
    def test_logout_with_authentication_and_correct_data(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = client.post(path = reverse('logout'), data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_205_RESET_CONTENT)
        

    def test_logout_without_authentication_and_correct_data(self):
        client = APIClient()
        response = client.post(path = reverse('logout'), data={'refresh_token': self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_with_authentication_and_incorrect_data(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = client.post(path = reverse('logout'), data={'refresh_token': 'incorect refresh_token g0e6r8g040t8ul8nm40r0ff06we4f0w68e4f'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_logout_without_authentication_and_incorrect_data(self):
        client = APIClient()
        response = client.post(path = reverse('logout'), data={'refresh_token': 'incorect refresh_token g0e6r8g040t8ul8nm40r0ff06we4f0w68e4f'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_logout_with_authentication_and_without_data(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = client.post(path = reverse('logout'))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
