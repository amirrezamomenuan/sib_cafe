from datetime import date
from unittest import mock

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
        self.refresh_token = response.json().get('refresh')
        self.access_token = response.json().get('access')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        response = self.client.post(path = reverse('login'), data = {'username':'EivazIndustriesCTO', 'password': "robotdaddy1378"})
        self.refresh_token2 = response.json().get('refresh')
        self.access_token2 = response.json().get('access')
        self.client2 = APIClient()
        self.client2.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token2}')

        self.path = reverse('order-cancelation')
    

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


        kabab_item = FoodItem.objects.create(id = 1, food=kabab, amount=3, price=150000, weekday=FoodItem.dayChoices.SATURDAY.value)
        fries_item = FoodItem.objects.create(id = 3, food=fries, price=10000, weekday=FoodItem.dayChoices.EVERY_DAY.value)
        omelette_item = FoodItem.objects.create(id = 5, food=omelette, amount=15, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value)

        o1 = OrderItem.objects.create(id = 1, food_item = kabab_item, user= user, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.PAYED.value)
        o2 = OrderItem.objects.create(id = 2, food_item = kabab_item, user= user, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.CANCELED.value)
        o3 = OrderItem.objects.create(id = 3, food_item = kabab_item, user= user, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.SERVED.value)
        o4 = OrderItem.objects.create(id = 4, food_item = kabab_item, user= user2, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.SUBMITED.value)
        o5 = OrderItem.objects.create(id = 5, food_item = omelette_item, user= user2, order_date = date(2022, 9, 17), state = OrderItem.stateChoices.SUBMITED.value)
        o6 = OrderItem.objects.create(id = 6, food_item = fries_item, user= user, order_date = date(2022, 9, 25), state = OrderItem.stateChoices.SUBMITED.value)

    
    def test_canceling_without_authentication(self):
        client = APIClient()
        response = client.post(path=self.path, data={})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_canceling_with_get_method(self):
        response = self.client.get(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_canceling_order_that_does_not_exist(self):
        response = self.client.post(path=self.path, data={'order_item_id': 15668108740947})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_canceling_order_that_does_not_have_order_item_id(self):
        response = self.client.post(path=self.path)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_canceling_order_that_has_invalid_order_item_id(self):
        response = self.client.post(path=self.path, data={'order_item_id': 'fdgoih lkuh 16587'})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_order_with_payed_status(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 10
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client.post(path=self.path, data={'order_item_id': 1})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_order_with_canceled_status(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 10
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client.post(path=self.path, data={'order_item_id': 2})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_order_with_served_status(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 10
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client.post(path=self.path, data={'order_item_id': 3})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_order_that_doesnot_belong_to_user(self, mock_datetime, mock_date):
         # order belongs to client with user1, not client2 with user2
        mock_datetime.now.return_value.hour = 10
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client2.post(path=self.path, data={'order_item_id': 3})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_lunch_order_after_limited_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 16
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client2.post(path=self.path, data={'order_item_id': 4})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_breakfast_after_limited_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 13
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client2.post(path=self.path, data={'order_item_id': 5})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_lunch_order_after_limited_time_one_day_earlier(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 16
        mock_date.today.return_value = date(2022, 9, 16)
        response = self.client2.post(path=self.path, data={'order_item_id': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_breakfast_after_limited_time_one_day_earlier(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 13
        mock_date.today.return_value = date(2022, 9, 16)
        response = self.client2.post(path=self.path, data={'order_item_id': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_appetizer_after_limited_time_one_day_earlier(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 19
        mock_date.today.return_value = date(2022, 9, 24)
        response = self.client.post(path=self.path, data={'order_item_id': 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_lunch_with_correct_data_and_before_time_limit(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 9
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client2.post(path=self.path, data={'order_item_id': 4})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_breakfast_with_correct_data_and_before_time_limit(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 7
        mock_date.today.return_value = date(2022, 9, 17)
        response = self.client2.post(path=self.path, data={'order_item_id': 5})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_canceling_appetizer_with_correct_data_and_before_time_limit(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 14
        mock_date.today.return_value = date(2022, 9, 25)
        response = self.client.post(path=self.path, data={'order_item_id': 6})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
