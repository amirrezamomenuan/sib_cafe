from django.test import TestCase
from core.models import Food, FoodItem

class FoodTests(TestCase):
    def setUp(self) -> None:
        Food.objects.create(
            name = 'gheymeh',
            description = "warm food containing meat & rice",
            category = Food.foodCategories.LUNCH,
        )
        Food.objects.create(
            name = 'ghoremeh',
            description = "warm food containing meat & rice & sabzi",
            category = Food.foodCategories.LUNCH,
        )
        Food.objects.create(
            name = 'koobideh kabaab',
            description = "meat and fat and onion cooked on fire",
            category = Food.foodCategories.LUNCH,
        )
        Food.objects.create(
            name = 'fries',
            description = "fried potatos and salt",
            category = Food.foodCategories.APPETIZER,
        )
        Food.objects.create(
            name = 'soda',
            category = Food.foodCategories.APPETIZER,
        )
        Food.objects.create(
            name = 'souffle',
            description = "luxury dish for employee of month",
            category = Food.foodCategories.BREAKFAST,
        )
        Food.objects.create(
            name = 'cesar salad',
            description = "salad with extra bs",
            category = Food.foodCategories.APPETIZER,
        )
        Food.objects.create(
            name = 'english breakfast',
            description = "fatty and unhealthy breakfast containing bacon and egs and beans",
            category = Food.foodCategories.BREAKFAST,
        )
    
    def test_category(self):
        gheymeh = Food.objects.get(name="gheymeh")
        ghoremeh = Food.objects.get(name="ghoremeh")
        koobideh = Food.objects.get(name="koobideh kabaab")
        souffle = Food.objects.get(name="souffle")
        soda = Food.objects.get(name="soda")
        fries = Food.objects.get(name="fries")
        english_breakfast = Food.objects.get(name="english breakfast")

        #assertions
        self.assertEqual(gheymeh.category, Food.foodCategories.LUNCH.value)
        self.assertEqual(ghoremeh.category, Food.foodCategories.LUNCH.value)
        self.assertEqual(koobideh.category, Food.foodCategories.LUNCH.value)
        
        self.assertEqual(souffle.category, Food.foodCategories.BREAKFAST.value)
        self.assertEqual(english_breakfast.category, Food.foodCategories.BREAKFAST.value)

        self.assertEqual(soda.category, Food.foodCategories.APPETIZER.value)
        self.assertEqual(fries.category, Food.foodCategories.APPETIZER.value)

    def test_ordering(self):
        foods = Food.objects.all()
        self.assertEqual(foods.first().name, 'english breakfast')
        self.assertEqual(foods.last().name, 'gheymeh')


class TestFoodItem(TestCase):
    def setUp(self) -> None:
        return super().setUp()
    
    def test_amount(self):
        pass

    def test_price(self):
        pass

    def test_food_connection(self):
        pass

    def test_food_can_be_ordered(self):
        pass

    def test_string_representation(self):
        pass
    