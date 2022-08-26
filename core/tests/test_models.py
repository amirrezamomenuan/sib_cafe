from django.test import TestCase
from django.core.exceptions import MultipleObjectsReturned

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
    
    def test_string_representation(self):
        gheymeh = Food.objects.get(name="gheymeh")
        cesar_salad = Food.objects.get(name= 'cesar salad')
        self.assertEqual("L : gheymeh", f"{gheymeh.category} : {gheymeh.name}")
        self.assertEqual("A : cesar salad", f"{cesar_salad.category} : {cesar_salad.name}")
        

class TestFoodItem(TestCase):
    def setUp(self) -> None:
        koobideh = Food.objects.create(
            name = 'koobideh kabaab',
            description = "meat and fat and onion cooked on fire",
            category = Food.foodCategories.LUNCH,
        )
        fries = Food.objects.create(
            name = 'fries',
            description = "fried potatos and salt",
            category = Food.foodCategories.APPETIZER,
        )
        soda = Food.objects.create(
            name = 'soda',
            category = Food.foodCategories.APPETIZER,
        )
        FoodItem.objects.create(
            food= koobideh,
            price= 1000000,
            amount= 15,
        )
        FoodItem.objects.create(
            food= fries,
            price= 120000,
            amount= 30,
        )
        FoodItem.objects.create(
            food= koobideh,
            price= 1250000,
            amount= 20,
        )
        FoodItem.objects.create(
            food= soda,
            price= 90000,
            amount= 0,
        )

        self.fries = FoodItem.objects.get(food__name = 'fries')
        self.soda = FoodItem.objects.get(food__name = 'soda')
        try:
            self.koobideh = FoodItem.objects.get(food__name = 'koobideh kabaab')
        except MultipleObjectsReturned:
            self.koobideh = FoodItem.objects.filter(food__name = 'koobideh kabaab').first()
    
    def test_amount(self):
        self.assertEqual(self.fries.amount, 30)
        self.assertEqual(self.koobideh.amount, 20)

    def test_price(self):
        # this test is based on the fact that fooditem_manager should return the last item created
        # and deactivate all the previous fooditem objects without deleting them
        self.assertEqual(self.fries.price, 120000)
        self.assertEqual(self.koobideh.price, 1250000)

    def test_food_connection(self):
        koobideh = Food.objects.get(name = 'koobideh kabaab')
        fries = Food.objects.get(name = 'fries')
        self.assertEqual(self.fries.food, fries)
        self.assertEqual(self.koobideh.food, koobideh)

    def test_food_can_be_ordered(self):
        self.assertTrue(self.fries.can_be_ordered)
        self.assertTrue(self.koobideh.can_be_ordered)
        self.assertFalse(self.soda.can_be_ordered)

    def test_string_representation(self):
        self.assertEqual(str(self.fries), "fries: 120000")
        self.assertEqual(str(self.koobideh), 'koobideh kabaab: 1250000')
        self.assertEqual(str(self.soda), 'soda: 90000')
    