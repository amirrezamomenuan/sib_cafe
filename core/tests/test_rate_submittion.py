from datetime import date

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.conf import settings

from core.models import Food, FoodItem, OrderItem

User = get_user_model()


class TestRateSubmittion(APITestCase):
    def setUp(self) -> None:
        settings.REDIS_CONNECTION.flushdb()

        self.path = reverse('rate-submittion')

        user = User(first_name = 'antony', last_name = 'stark', username = 'ironman')
        user.set_password('starkindustries')
        user.save()
        self.user = user

        response = self.client.post(path = reverse('login'), data = {'username':'ironman', 'password': "starkindustries"})
        self.refresh_token = response.json().get('refresh')
        self.access_token = response.json().get('access')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

    
    def test_without_providing_authentication_credentials(self):
        client = APIClient()
        response = client.post(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_get_method(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_rating_without_sending_data(self):
        data = {}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_for_foood_that_does_not_exist(self):
        pass

    def test_rating_for_foood_that_was_not_ordered_by_this_user(self):
        pass

    def test_rating_for_food_when_already_rated(self):
        pass

    def test_rating_for_yesterdays_food(self):
        pass

    def test_rating_for_food_where_order_state_is_submitted(self):
        pass

    def test_rating_for_food_where_order_state_is_canceled(self):
        pass
    
    def test_rating_for_food_where_order_state_is_payed(self):
        pass
    
    def test_rating_for_food_where_order_state_is_served(self):
        pass
    