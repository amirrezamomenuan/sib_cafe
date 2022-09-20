from datetime import date
from unittest import mock

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.conf import settings

from core.models import Food, FoodItem, FoodRate, OrderItem

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
        self.access_token = response.json().get('access')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        user2 = User(first_name = 'reza', last_name = 'eivazzadeh', username = 'eivaz021')
        user2.set_password('eivazindustries')
        user2.save()
        self.user2 = user2

        response = self.client.post(path = reverse('login'), data = {'username':'eivaz021', 'password': "eivazindustries"})
        self.access_token = response.json().get('access')
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        kabab = Food.objects.create(
            id = 1,
            name = 'kabab',
            description = 'kabab koobideh 1 sikh',
            category = Food.foodCategories.LUNCH.value,
        )
        fries = Food.objects.create(
            id = 3,
            name = 'fries',
            description = 'sibzamazni sorkh kardeh',
            category = Food.foodCategories.APPETIZER.value,
        )

        omelette = Food.objects.create(
            id = 4,
            name = 'omelette',
            description = 'omlet ghahvekhoone-ie',
            category = Food.foodCategories.BREAKFAST.value,
        )

        # TODO: bulk create
        kabab_item = FoodItem.objects.create(id = 1, food=kabab, amount=3, price=150000, weekday=FoodItem.dayChoices.SATURDAY.value)
        fries_item = FoodItem.objects.create(id = 3, food=fries, price=10000, weekday=FoodItem.dayChoices.EVERY_DAY.value)
        omelette_item = FoodItem.objects.create(id = 5, food=omelette, amount=15, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value)

        # TODO: bulk create
        OrderItem.objects.create(id = 1, food_item = kabab_item, user= user, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.PAYED.value)
        OrderItem.objects.create(id = 2, food_item = kabab_item, user= user, order_date = date(2022, 9, 18), state = OrderItem.stateChoices.CANCELED.value)
        OrderItem.objects.create(id = 3, food_item = fries_item, user= user2, order_date = date(2022, 7, 4), state = OrderItem.stateChoices.SUBMITED.value)
        OrderItem.objects.create(id = 5, food_item = omelette_item, user= user, order_date = date.today(), state = OrderItem.stateChoices.SUBMITED.value)

        settings.REDIS_CONNECTION.zincrby(name= 'food-rate-total', amount=145, value=3)
        settings.REDIS_CONNECTION.zincrby(name= 'food-rate-total', amount=173, value=1)
        settings.REDIS_CONNECTION.zincrby(name= 'food-rate-total', amount=2000, value=4)

        settings.REDIS_CONNECTION.zincrby(name= 'food-rate-counter', amount=23, value=3)
        settings.REDIS_CONNECTION.zincrby(name= 'food-rate-counter', amount=10, value=1)
        settings.REDIS_CONNECTION.zincrby(name= 'food-rate-counter', amount=450, value=4)
    
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

    def test_rating_for_food_that_does_not_exist(self):
        data = {'food': 485, 'rate':5}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_rating_for_food_that_was_not_ordered_by_this_user(self):
        data = {'food':3, 'rate':4}
        response = self.client.post(path=self.path, data=data)
        redis_food_total = settings.REDIS_CONNECTION.zscore(name= 'food-rate-total', value=3)
        redis_food_count = settings.REDIS_CONNECTION.zscore(name= 'food-rate-counter', value=3)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(145, redis_food_total)
        self.assertEqual(23, redis_food_count)

    @mock.patch('core.models.date')
    def test_rating_with_correct_data(self, mock_date):
        mock_date.today.return_value = date(2022, 9, 17)
        data = {'food':1, 'rate':4}
        response = self.client.post(path=self.path, data=data)
        redis_food_total = settings.REDIS_CONNECTION.zscore(name= 'food-rate-total', value=1)
        redis_food_count = settings.REDIS_CONNECTION.zscore(name= 'food-rate-counter', value=1)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(177, redis_food_total)
        self.assertEqual(11, redis_food_count)

    @mock.patch('core.models.date')
    def test_rating_for_yesterdays_food(self, mock_date):
        mock_date.today.return_value = date(2022, 9, 19)
        data = {'food':1, 'rate':1}
        response = self.client.post(path=self.path, data=data)
        redis_food_total = settings.REDIS_CONNECTION.zscore(name= 'food-rate-total', value=1)
        redis_food_count = settings.REDIS_CONNECTION.zscore(name= 'food-rate-counter', value=1)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(173, redis_food_total)
        self.assertEqual(10, redis_food_count)

    def test_rating_for_food_when_already_rated(self):
        data = {'food':4, 'rate':4}
        response = self.client.post(path=self.path, data=data)
        redis_food_total = settings.REDIS_CONNECTION.zscore(name= 'food-rate-total', value=4)
        redis_food_count = settings.REDIS_CONNECTION.zscore(name= 'food-rate-counter', value=4)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(2004, redis_food_total)
        self.assertEqual(451, redis_food_count)

        data = {'food':4, 'rate':4}
        response = self.client.post(path=self.path, data=data)
        redis_food_total = settings.REDIS_CONNECTION.zscore(name= 'food-rate-total', value=4)
        redis_food_count = settings.REDIS_CONNECTION.zscore(name= 'food-rate-counter', value=4)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(2004, redis_food_total)
        self.assertEqual(451, redis_food_count)

    # def test_rating_for_food_where_order_state_is_canceled(self):
    #     pass
    
    # def test_rating_for_food_where_order_state_is_payed(self):
    #     pass
    
    # def test_rating_for_food_where_order_state_is_served(self):
    #     pass
    