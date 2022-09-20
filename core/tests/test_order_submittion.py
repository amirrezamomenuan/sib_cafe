from datetime import date
from unittest import mock

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from django.conf import settings

from core.models import Food, FoodItem 

User = get_user_model()


class TestOrderSubmittion(APITestCase):
    def setUp(self) -> None:
        user = User(first_name = 'reza', last_name = 'eivazzadeh', username = 'rezaeivaz')
        user.set_password('reza2000')
        user.save()
        self.user = user
        
        response = self.client.post(path = reverse('login'), data = {'username':'rezaeivaz', 'password': "reza2000"})
        self.access_token = response.json().get('access')
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')

        self.path = reverse('order-submittion')
        
        settings.REDIS_CONNECTION.flushdb()

        kabab = Food.objects.create(
            name = 'kabab',
            description = 'kabab koobideh 1 sikh',
            category = Food.foodCategories.LUNCH.value,
        )
        joojeh = Food.objects.create(
            name = 'joojeh',
            description = 'joojeh kabab 1 sikh',
            category = Food.foodCategories.LUNCH.value,
        )
        gordonblue = Food.objects.create(
            name = 'gordonblue',
            description = '350 gram chicken va panir',
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
        salad = Food.objects.create(
            name = 'salad',
            description = 'lettus salad',
            category = Food.foodCategories.APPETIZER.value,
        )
        nimroo = Food.objects.create(
            name = 'nimroo',
            description = 'nimroo 2 addad egg',
            category = Food.foodCategories.BREAKFAST.value,
        )
        omelette = Food.objects.create(
            name = 'omelette',
            description = 'omlet ghahvekhoone-ie',
            category = Food.foodCategories.BREAKFAST.value,
        )
        esspereso = Food.objects.create(
            name = 'esspereso',
            description = '1 shot',
            category = Food.foodCategories.APPETIZER.value,
        )
        turkish_cafe = Food.objects.create(
            name = 'turkish cafe',
            description = '1 shot',
            category = Food.foodCategories.APPETIZER.value,
        )
        hot_chocolate = Food.objects.create(
            name = 'hot_chocolate',
            description = '1 cup',
            category = Food.foodCategories.APPETIZER.value,
        )

        FoodItem.objects.bulk_create([
            FoodItem(id = 1, food=kabab, amount=3, price=150000, weekday=FoodItem.dayChoices.SATURDAY.value),
            FoodItem(id = 2, food=kabab, amount=2, price=150000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            FoodItem(id = 3, food=kabab, amount=3, price=150000, weekday=FoodItem.dayChoices.TUESDAY.value),
            FoodItem(id = 4, food=joojeh, amount=5, price=100000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            FoodItem(id = 5, food=gordonblue, amount=10, price=35000, weekday=FoodItem.dayChoices.MONDAY.value),
            FoodItem(id = 6, food=gordonblue, amount=1, price=35000, weekday=FoodItem.dayChoices.TUESDAY.value),
            FoodItem(id = 7, food=fries, price=10000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(id = 8, food=soda_can, price=9000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(id = 9, food=salad, price=20000, weekday=FoodItem.dayChoices.SATURDAY.value),
            FoodItem(id = 10, food=salad, price=20000, weekday=FoodItem.dayChoices.MONDAY.value),
            FoodItem(id = 11, food=salad, price=20000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            FoodItem(id = 12, food=nimroo, amount=15, price=12000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(id = 13, food=omelette, amount=15, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(id = 14, food=esspereso, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(id = 15, food=turkish_cafe, price=15000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(id = 16, food=hot_chocolate, price=20000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            ]
        )
    
    def test_without_providing_authentication_token(self):
        client = APIClient()
        data = {"order_item_id":"15"}
        response = client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_method(self):
        response = self.client.get(self.path)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_an_item_that_does_not_exist_on_menu_for_specific_weekday(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 14
        mock_date.today.return_value = date(2022, 9, 8)
        data = {"food_item": 5, "order_date": "2022-09-10"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_breakfast_when_already_ordered_for_a_specific_date(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 7
        mock_date.today.return_value = date(2022, 9, 15)

        data = {"food_item": 13, "order_date": "2022-09-15"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_when_already_ordered_for_a_specific_date(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 14
        mock_date.today.return_value = date(2022, 9, 11)

        data = {"food_item": 3, "order_date": "2022-09-13"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_breakfast_that_is_sold_out(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 7
        mock_date.today.return_value = date(2022, 9, 15)
        settings.REDIS_CONNECTION.set(name=f'12:{date(2022, 9, 15).strftime("%Y/%m/%d")}', value= 15)
    
        data = {"food_item": 12, "order_date": "2022-09-15"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_that_is_sold_out(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 17
        mock_date.today.return_value = date(2022, 9, 11)
        settings.REDIS_CONNECTION.set(name=f'5:{date(2022, 9, 12).strftime("%Y/%m/%d")}', value= 10)

        data = {"food_item": 5, "order_date": "2022-09-12"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_breakfast_after_limited_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 12
        mock_date.today.return_value = date(2022, 9, 12)

        data = {"food_item": 13, "order_date": "2022-09-12"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_after_limited_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 19
        mock_date.today.return_value = date(2022, 9, 13)

        data = {"food_item": 4, "order_date": "2022-09-14"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_on_same_day(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 13
        mock_date.today.return_value = date(2022, 9, 14)

        data = {"food_item": 4, "order_date": "2022-09-14"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_breakfast_for_yesterday_with_correct_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 8
        mock_date.today.return_value = date(2022, 9, 15)

        data = {"food_item": 12, "order_date": "2022-09-14"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_breakfast_for_yesterday_with_incorrect_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 13
        mock_date.today.return_value = date(2022, 9, 15)

        data = {"food_item": 12, "order_date": "2022-09-14"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_for_yesterday_with_correct_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 13
        mock_date.today.return_value = date(2022, 9, 14)

        data = {"food_item": 3, "order_date": "2022-09-13"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_for_yesterday_with_incorrect_time(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 21
        mock_date.today.return_value = date(2022, 9, 14)

        data = {"food_item": 3, "order_date": "2022-09-13"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_for_next_7_days(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 15
        mock_date.today.return_value = date(2022, 9, 14)

        data = {"food_item": 2, "order_date": "2022-09-07"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_oreding_breakfast_for_next_7_days(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 6
        mock_date.today.return_value = date(2022, 9, 14)

        data = {"food_item": 2, "order_date": "2022-09-07"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_appetizer_for_yesterday(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 13
        mock_date.today.return_value = date(2022, 9, 14)

        data = {"food_item": 15, "order_date": "2022-09-13"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_appetizer_for_today_after_time_is_over(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 20
        mock_date.today.return_value = date(2022, 9, 12)

        data = {"food_item": 15, "order_date": "2022-09-12"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_appetizer_with_correct_data(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 16
        mock_date.today.return_value = date(2022, 9, 12)

        data = {"food_item": 15, "order_date": "2022-09-12"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_lunch_for_tomorrow_with_correct_data(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 16
        mock_date.today.return_value = date(2022, 9, 12)

        data = {"food_item": 6, "order_date": "2022-09-13"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_breakfast_for_tomorrow_with_correct_data(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 20
        mock_date.today.return_value = date(2022, 9, 12)

        data = {"food_item": 12, "order_date": "2022-09-13"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @mock.patch('core.models.date')
    @mock.patch('core.models.datetime')
    def test_ordering_breakfast_for_today_with_correct_data(self, mock_datetime, mock_date):
        mock_datetime.now.return_value.hour = 7
        mock_date.today.return_value = date(2022, 9, 13)

        data = {"food_item": 12, "order_date": "2022-09-13"}
        response = self.client.post(path=self.path, data=data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)