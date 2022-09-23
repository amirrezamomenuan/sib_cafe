from django.urls import reverse
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase

from core.models import Food, FoodRate
from core.utils import LeaderBoardRedisClient


User = get_user_model()

class TestLeaderBoard(APITestCase):
    def setUp(self) -> None:
        self.leaderboard = LeaderBoardRedisClient()
        self.leaderboard.redis_client.flushdb()

        self.path = reverse('leaderboard-view')

        gordonblue = Food.objects.create(
            id = 1,
            name = 'gordonblue',
            description = '350 gram chicken va panir',
            category = Food.foodCategories.LUNCH.value,
        )
        omelette = Food.objects.create(
            id = 2,
            name = 'omelette',
            description = 'omlet ghahvekhoone-ie',
            category = Food.foodCategories.BREAKFAST.value,
        )
        user = User(first_name = 'antony', last_name = 'stark', username = 'ironman')
        user.set_password('starkindustries')
        user.save()

        FoodRate(user=user, food=gordonblue, rate=4).save()
        FoodRate(user=user, food=gordonblue, rate=3).save()
        FoodRate(user=user, food=gordonblue, rate=4).save()
        FoodRate(user=user, food=gordonblue, rate=5).save()
        FoodRate(user=user, food=omelette, rate=2).save()
        FoodRate(user=user, food=omelette, rate=1).save()
        FoodRate(user=user, food=omelette, rate=5).save()
        FoodRate(user=user, food=omelette, rate=5).save()
        self.leaderboard.upgrade_leader_board(food_model=Food)
    
    def test_post_method(self):
        response = self.client.post(path=self.path, data={})
        self.assertEqual(status.HTTP_405_METHOD_NOT_ALLOWED, response.status_code)

    def test_order_rates_count(self):
        response = self.client.get(path=self.path)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)
    
    def test_order_rates_values(self):
        response = self.client.get(path=self.path)
        json_data = response.json()
        self.assertEqual(4, json_data.get('1'))
        self.assertEqual(3.25, json_data.get('2'))

    def test_order_rates_count_with_leaderboard_lazy_loading(self):
        self.leaderboard.redis_client.flushdb()
        response = self.client.get(path=self.path)
        json_data = response.json()
        self.assertEqual(len(json_data), 2)

    def test_order_rates_values_with_leaderboard_lazy_loading(self):
        self.leaderboard.redis_client.flushdb()
        response = self.client.get(path=self.path)
        json_data = response.json()
        self.assertEqual(4, json_data.get('1'))
        self.assertEqual(3.25, json_data.get('2'))
