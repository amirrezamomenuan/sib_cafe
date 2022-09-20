from datetime import date

from django.urls import reverse
from django.db.models import Q
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Food, FoodItem

User = get_user_model()

class TestMenuList(APITestCase):
    def setUp(self) -> None:
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
            FoodItem(food=kabab, amount=15, price=150000, weekday=FoodItem.dayChoices.SATURDAY.value),
            FoodItem(food=kabab, amount=10, price=150000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            FoodItem(food=kabab, amount=10, price=150000, weekday=FoodItem.dayChoices.TUESDAY.value),
            FoodItem(food=joojeh, amount=20, price=100000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            FoodItem(food=gordonblue, amount=35, price=35000, weekday=FoodItem.dayChoices.MONDAY.value),
            FoodItem(food=gordonblue, amount=10, price=35000, weekday=FoodItem.dayChoices.TUESDAY.value),
            FoodItem(food=fries, price=10000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(food=soda_can, price=9000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(food=salad, price=20000, weekday=FoodItem.dayChoices.SATURDAY.value),
            FoodItem(food=salad, price=20000, weekday=FoodItem.dayChoices.MONDAY.value),
            FoodItem(food=salad, price=20000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            FoodItem(food=nimroo, amount=15, price=12000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(food=omelette, amount=15, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(food=esspereso, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(food=turkish_cafe, price=15000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(food=hot_chocolate, price=20000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            ]
        )

    
    def test_menu_list_without_limit_offset(self):
        response = self.client.get(reverse('menu'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_menu_list_without_limit_offset_and_with_weekday_given(self):
        query_params = '?weekday=0'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        json_response = response.json().get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 8)

    def test_menu_list_without_limit_offset_and_with_another_weekday_given(self):
        query_params = '?weekday=4'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        json_response = response.json().get('results')
        self.assertEqual(len(json_response), 10)

    def test_menu_list_without_limit_offset_and_with_todays_weekday(self):
        week_day = (date.weekday(date.today()) + 2) % 7
        if week_day in [5, 6]:
            return

        query_params = f'?weekday={week_day}'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        todays_menu_count = FoodItem.objects.filter(Q(weekday= week_day) | Q(weekday = -1)).count()
        json_response = response.json().get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), todays_menu_count)

    def test_menu_list_without_limit_offset_and_with_invalid_weekday(self):
        query_params = '?weekday=6'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        json_response = response.json().get('results')
        self.assertEqual(len(json_response), 0)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_menu_list_with_limit_offset(self):
        query_params = '?weekday=4&limit=5&offset=6'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        json_response = response.json().get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 4)

    def test_menu_list_order_by_highest_price_limit_offset(self):
        query_params = '?weekday=4&limit=10&offset=2&order_by=-price'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        json_response = response.json().get('results')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response[0].get('price'), 20000)
        self.assertEqual(json_response[1].get('price'), 20000)
        self.assertEqual(json_response[2].get('price'), 18000)
        self.assertEqual(json_response[3].get('price'), 18000)
        self.assertEqual(json_response[4].get('price'), 15000)
        self.assertEqual(json_response[5].get('price'), 12000)
        self.assertEqual(json_response[6].get('price'), 10000)
        self.assertEqual(json_response[7].get('price'), 9000)

    def test_menu_list_order_by_lowest_price_limit_offset(self):
        query_params = '?weekday=4&limit=2&offset=7&order_by=price'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        json_response = response.json().get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(json_response[0].get('price'), 20000)
        self.assertEqual(json_response[1].get('price'), 100000)

    def test_menu_list_order_by_highest_rate_limit_offset(self):
        pass

    def test_menu_list_order_by_highest_rate_without_limit_offset(self):
        pass

    def test_menu_list_with_weekday_that_only_has_daily_menu(self):
        query_params = '?weekday=1'
        url = reverse('menu') + query_params
        response = self.client.get(url)
        json_response = response.json().get('results')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(json_response), 6)