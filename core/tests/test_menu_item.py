from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Food, FoodItem

User = get_user_model()


class TestMenuItemDetail(APITestCase):
    def setUp(self) -> None:
        self.url = reverse('menu-item-view')

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

        FoodItem.objects.bulk_create([
            FoodItem(id=100, food=kabab, amount=15, price=150000, weekday=FoodItem.dayChoices.SATURDAY.value),
            FoodItem(id=101, food=joojeh, amount=20, price=100000, weekday=FoodItem.dayChoices.WEDNESDAY.value),
            FoodItem(id=102, food=gordonblue, amount=10, price=35000, weekday=FoodItem.dayChoices.TUESDAY.value),
            FoodItem(id=103, food=omelette, amount=15, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            FoodItem(id=104, food=esspereso, price=18000, weekday=FoodItem.dayChoices.EVERY_DAY.value),
            ]
        )

    def test_without_providing_fooditem_id(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_fooditem_with_wrong_fooditem_id(self):
        url = self.url + '?menu_item_id=13543626757'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_post_method(self):
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_fooditem_id(self):
        url = self.url + '?menu_item_id=100'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('id'), 100)

    def test_fooditem_name(self):
        url = self.url + '?menu_item_id=101'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('food').get('name'), 'joojeh')

    def test_fooditem_price(self):
        url = self.url + '?menu_item_id=102'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('price'), 35000)

    def test_fooditem_amount(self):
        url = self.url + '?menu_item_id=103'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('amount'), 15)
    
    def test_fooditem_amount_is_null(self):
        url = self.url + '?menu_item_id=104'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('amount'), None)

    def test_fooditem_category(self):
        url = self.url + '?menu_item_id=104'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('food').get('category'), Food.foodCategories.APPETIZER.value)

    def test_fooditem_description(self):
        url = self.url + '?menu_item_id=104'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('food').get('description'), '1 shot')
