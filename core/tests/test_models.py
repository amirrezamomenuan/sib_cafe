from django.test import TestCase
from core.models import Food

class FoodTests(TestCase):
    def setUp(self) -> None:
        Food.objects.create(
            name = 'gheymeh',
            description = "warm food containing meat & rice",
            category = Food.foodCategories.LUNCH,
        )
    
    def test_category(self):
        gheymeh = Food.objects.get(name="gheymeh")
        self.assertEqual(gheymeh.category, 'L')

    def test_2(self):
        pass