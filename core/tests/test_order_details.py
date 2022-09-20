from datetime import date

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from core.models import Food, FoodItem, OrderItem

User = get_user_model()

class TestCancelOrder(APITestCase):
    def setUp(self) -> None:
        user = User(first_name = 'elon', last_name = 'musk', username = 'spacexCTO')
        user.set_password('elon1971')
        user.save()
        self.user = user

        user2 = User(first_name = 'reza', last_name = 'eivazzadeh', username = 'EivazIndustriesCTO')
        user2.set_password('robotdaddy1378')
        user2.save()
        self.user2 = user2
        
        response = self.client.post(path = reverse('login'), data = {'username':'spacexCTO', 'password': "elon1971"})
        self.access_token = response.json().get('access')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.post(path = reverse('login'), data = {'username':'EivazIndustriesCTO', 'password': "robotdaddy1378"})
        self.access_token2 = response.json().get('access')
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token2}')

        self.path = reverse('order-detail')
    

        kabab = Food.objects.create(
            name = 'kabab',
            description = 'kabab koobideh 1 sikh',
            category = Food.foodCategories.LUNCH.value,
        )
        omelette = Food.objects.create(
            name = 'omelette',
            description = 'omlet ghahvekhoone-ie',
            category = Food.foodCategories.BREAKFAST.value,
        )


        kabab_item = FoodItem.objects.create(id = 1, food=kabab, amount=3, price=150000, weekday=FoodItem.dayChoices.SATURDAY.value)
        omelette_item = FoodItem.objects.create(id = 5, food=omelette, amount=15, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value)

        OrderItem.objects.create(id = 1, food_item = kabab_item, user= user, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.PAYED.value)
        OrderItem.objects.create(id = 2, food_item = kabab_item, user= user, order_date = date(2022, 9, 18), state = OrderItem.stateChoices.CANCELED.value)
        OrderItem.objects.create(id = 5, food_item = omelette_item, user= user2, order_date = date(2022, 3, 1), state = OrderItem.stateChoices.SUBMITED.value)

    def test_post_method(self):
        response = self.client2.post(path=self.path + '?order_id=5')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_without_providing_authentication_credentials(self):
        client = APIClient()
        response = client.get(path=self.path + '?order_id=5')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_without_providing_order_id(self):
        response = self.client2.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_with_order_id_that_does_not_exist(self):
        response = self.client2.get(path=self.path + '?order_id=1570456045')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_with_correct_id_and_wrong_user(self):
        response = self.client2.get(path=self.path + '?order_id=1')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_with_correct_id_and_correct_user(self):
        response = self.client.get(path=self.path + '?order_id=2')
        self.assertEqual(response.status_code, status.HTTP_200_OK)