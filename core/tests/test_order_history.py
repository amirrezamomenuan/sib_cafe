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

        self.path = reverse('order-list')
    

        kabab = Food.objects.create(
            name = 'kabab',
            description = 'kabab koobideh 1 sikh',
            category = Food.foodCategories.LUNCH.value,
        )
        soda_can = Food.objects.create(
            name = 'soda_can',
            description = '330 ml canned soda',
            category = Food.foodCategories.APPETIZER.value,
        )
        fries = Food.objects.create(
            name = 'fries',
            description = 'sibzamazni sorkh kardeh',
            category = Food.foodCategories.APPETIZER.value,
        )

        omelette = Food.objects.create(
            name = 'omelette',
            description = 'omlet ghahvekhoone-ie',
            category = Food.foodCategories.BREAKFAST.value,
        )

        # TODO: bulk create
        kabab_item = FoodItem.objects.create(id = 1, food=kabab, amount=3, price=150000, weekday=FoodItem.dayChoices.SATURDAY.value)
        fries_item = FoodItem.objects.create(id = 3, food=fries, price=10000, weekday=FoodItem.dayChoices.EVERY_DAY.value)
        omelette_item = FoodItem.objects.create(id = 5, food=omelette, amount=15, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value)
        soda_item = FoodItem.objects.create(id = 6, food=soda_can, price=12000, weekday=FoodItem.dayChoices.EVERY_DAY.value)
        
        # TODO: bulk create
        OrderItem.objects.create(id = 1, food_item = kabab_item, user= user, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.PAYED.value)
        OrderItem.objects.create(id = 2, food_item = kabab_item, user= user, order_date = date(2022, 9, 18), state = OrderItem.stateChoices.CANCELED.value)
        OrderItem.objects.create(id = 3, food_item = omelette_item, user= user, order_date = date(2022, 8, 22), state = OrderItem.stateChoices.SERVED.value)
        OrderItem.objects.create(id = 4, food_item = kabab_item, user= user2, order_date = date(2022, 9, 14), state = OrderItem.stateChoices.SUBMITED.value)
        OrderItem.objects.create(id = 5, food_item = omelette_item, user= user2, order_date = date(2022, 3, 1), state = OrderItem.stateChoices.SUBMITED.value)
        OrderItem.objects.create(id = 6, food_item = fries_item, user= user, order_date = date(2022, 3, 29), state = OrderItem.stateChoices.SUBMITED.value)
        OrderItem.objects.create(id = 7, food_item = soda_item, user= user, order_date = date(2022, 12, 27), state = OrderItem.stateChoices.SUBMITED.value)
        OrderItem.objects.create(id = 8, food_item = soda_item, user= user, order_date = date(2022, 11, 29), state = OrderItem.stateChoices.PAYED.value)
        OrderItem.objects.create(id = 9, food_item = fries_item, user= user, order_date = date(2021, 2, 2), state = OrderItem.stateChoices.SUBMITED.value)
        OrderItem.objects.create(id = 10, food_item = kabab_item, user= user, order_date = date(2022, 7, 19), state = OrderItem.stateChoices.SERVED.value)

    def test_without_providing_authentication_credentials(self):
        client = APIClient()
        response = client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_method(self):
        response = self.client.post(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_without_limit_offset(self):
        path = self.path
        response = self.client.get(path=path)
        json_response = response.json().get('results')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 8)
        self.assertEqual(json_response[0].get('order_date'), '2022-12-27')
        self.assertEqual(json_response[1].get('order_date'), '2022-11-29')
        self.assertEqual(json_response[2].get('order_date'), '2022-09-18')
        self.assertEqual(json_response[6].get('order_date'), '2022-03-29')
        self.assertEqual(json_response[7].get('order_date'), '2021-02-02')

    def test_with_limit_and_without_offset(self):
        path = self.path + '?limit=3'
        response = self.client.get(path=path)
        json_response = response.json().get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 3)
        self.assertEqual(json_response[0].get('order_date'), '2022-12-27')
        self.assertEqual(json_response[1].get('order_date'), '2022-11-29')
        self.assertEqual(json_response[2].get('order_date'), '2022-09-18')

    def test_without_limit_and_with_offset(self):
        path = self.path + '?offset=4'
        response = self.client.get(path=path)
        json_response = response.json().get('results')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 4)
        self.assertEqual(json_response[0].get('order_date'), '2022-08-22')
        self.assertEqual(json_response[1].get('order_date'), '2022-07-19')
        self.assertEqual(json_response[2].get('order_date'), '2022-03-29')
        self.assertEqual(json_response[3].get('order_date'), '2021-02-02')
    
    def test_with_limit_and_offset(self):
        path = self.path + '?limit=3&offset=7'
        response = self.client.get(path=path)
        json_response = response.json().get('results')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0].get('order_date'), '2021-02-02')


    def test_with_invalid_limit_and_offset(self):
        path = self.path + '?limit=2763&offset=3846331'
        response = self.client.get(path=path)
        json_response = response.json().get('results')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 0)
    
    def test_client2_price_with_limit_and_offset(self):
        path = self.path + '?limit=5&offset=1'
        response = self.client2.get(path=path)
        json_response = response.json().get('results')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 1)
        self.assertEqual(json_response[0].get('food_item').get('price'), 18000)
