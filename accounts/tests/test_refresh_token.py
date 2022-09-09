from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status


User = get_user_model()


class TestRefreshToken(TestCase):
    def setUp(self) -> None:
        user = User(first_name = 'reza', last_name = 'eivazzadeh', username = 27111378)
        user.set_password('reza10Hello')
        user.save()

        token_pair_response = self.client.post(path = reverse('login'), data = {'username':27111378, 'password': "reza10Hello"})
        self.refresh_token = token_pair_response.json().get('refresh')
        self.access_token = token_pair_response.json().get('access')
    
    def test_with_correct_refresh_token(self):
        response = self.client.post(path= reverse('refresh_token'), data={"refresh": self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('access' in response.json())

    def test_without_refresh_token(self):
        response = self.client.post(path= reverse('refresh_token'), data={})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_with_invalid_refresh_token(self):
        response = self.client.post(path= reverse('refresh_token'), data={'refresh': 'wrong token'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_rotation_works(self):
        response = self.client.post(path= reverse('refresh_token'), data={"refresh": self.refresh_token})

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue('refresh' in response.json())
        self.assertNotEqual(self.refresh_token, response.json().get('refresh'))
    
    def test_refresh_token_does_not_work_after_blacklisting_previous_refresh_tokens(self):
        # using refresh_token for first time
        response = self.client.post(path= reverse('refresh_token'), data={"refresh": self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # using refresh_token without updating it to the new refresh_token that is returned
        # in previous response
        response = self.client.post(path= reverse('refresh_token'), data={"refresh": self.refresh_token})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
