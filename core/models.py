from datetime import date, datetime
from time import time

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.shortcuts import get_object_or_404

from core.managers import FoodItemManager, FoodManager, OrderItemManager

class Food(models.Model):

    class foodCategories(models.TextChoices):
        BREAKFAST = "B", _('breakfast')
        LUNCH = "L", _('lunch')
        APPETIZER = "A", _('appetizer')

    name = models.CharField(verbose_name= _("name"), max_length =50)
    description = models.TextField(verbose_name=_('descriptions'), null=True, blank= True, max_length=300)
    category = models.CharField(_('category'), max_length=1, choices=foodCategories.choices)
    image = models.ImageField(verbose_name=_('image'), upload_to ='uploads/food_images', default='uploads/food_images/default.jpg')
    creation_time = models.DateTimeField(auto_now_add=True)
    modification_time = models.DateTimeField(auto_now=True)
    objects = FoodManager()

    class Meta:
        db_table = "core_food"
        verbose_name = _("food")
        verbose_name_plural = _('foods')
        ordering = ["-creation_time",]
    
    @property
    def rate(self):
        return 5 #TODO: change this to a function that reads data from redis and returns it
       
    @rate.setter
    def rate(self) -> None:
        pass #TODO: change this to a function that updates new data to redis

    def __str__(self) -> str:
        return f"{self.category} : {self.name}"


class FoodItem(models.Model):

    class dayChoices(models.IntegerChoices):
        SATURDAY = 0 , _('saturday')
        SUNDAY = 1, _('sunday')
        MONDAY = 2, _('monday')
        TUESDAY = 3, _('tuesday')
        WEDNESDAY = 4, _('wednesday')
        EVERY_DAY = -1, _("everyday")

    food = models.ForeignKey(to=Food, on_delete=models.PROTECT, related_name="food_items")
    amount = models.PositiveIntegerField(verbose_name=_("amount"), null=True, blank=True)
    price = models.PositiveIntegerField(verbose_name=_("price"))
    creation_time = models.DateField(null=True, blank=True)
    weekday = models.SmallIntegerField(verbose_name= _("weekday"), choices= dayChoices.choices, default= dayChoices.EVERY_DAY.value)
    objects = FoodItemManager()
    
    class Meta:
        ordering = ['-creation_time']

    def __food_weekday_matches_order_date(self, order_date):
        if self.weekday == -1:
            print('daily food can be ordered')
            return True
        print(f"\nweekday for order_date is {(order_date.weekday() + 2) % 7}, self.weekday is {self.weekday}")
        return self.weekday == (order_date.weekday() + 2) % 7

    def __user_has_ordered_limited_food(self, user, food_item_id, order_date:date):
        print("\nchecking if user has ordered this food\n")
        return user.user_orders.filter(food_item__id=food_item_id, order_date=order_date).exists()

    def __user_can_order_breakfast(self, user, food_item_id, order_date:date) -> bool:
        if datetime.now().hour >= settings.BREAKFAST_TIME_LIMIT:
            print("\nout of breakfast time limit\n")
            return False
        elif date.today() < order_date:
            print(order_date)
            print("\nout of breakfast date\n")
            return False
        elif not self.__food_weekday_matches_order_date(order_date):
            print('food_item doesnot match weekday')
            return False
        return not self.__user_has_ordered_limited_food(user, food_item_id, order_date)
    
    def __user_can_order_lunch(self, user, food_item_id, order_date:date):
        print('\n', datetime.now().hour, "is woooooooooooooooooorking\n")
        if datetime.now().hour >= settings.LUNCH_TIME_LIMIT:
            print("\nout of lunch time limiit\n")
            return False
        elif date.today() <= order_date:
            print(order_date, ' ++++++ ', date.today())
            print("\nout of lunch date\n")
            return False
        elif not self.__food_weekday_matches_order_date(order_date):
            print('food_item doesnot match weekday')
            return False
        return not self.__user_has_ordered_limited_food(user, food_item_id, order_date)
    
    def __check_time_limit(self):
        if self.food.category == Food.foodCategories.BREAKFAST.value:
            return datetime.now().hour < settings.BREAKFAST_TIME_LIMIT
        elif self.food.category == Food.foodCategories.LUNCH.value:
            return datetime.now().hour < settings.LUNCH_TIME_LIMIT

    def __order_time_is_over(self, order_date:date):
        date_difference = (order_date - date.today()).days
        print(f"\ndate difference is : {date_difference}\n")
        print('order date for current request is: ', order_date, 'todays date is : ', date.today())

        if self.food.category == Food.foodCategories.BREAKFAST.value:
            if date_difference == 0:
                return not self.__check_time_limit()
            elif date_difference > 0:
                return False
        elif self.food.category == Food.foodCategories.LUNCH.value:
            if date_difference == 1:
                return not self.__check_time_limit()
            elif date_difference > 1:
                return False
        return True

    def __user_can_order_limited_food(self, user, food_item_id, order_date):
        print('\n', datetime.now().hour, "is woooooooooooooooooorking\n")
        if self.__order_time_is_over(order_date):
            print("\nout of order time limit\n")
            return False
        elif not self.__food_weekday_matches_order_date(order_date):
            print('food_item doesnot match weekday')
            return False
        return not self.__user_has_ordered_limited_food(user, food_item_id, order_date)

    def __user_can_order_item(self, user, food_item_id, order_date:date) -> bool:
        if self.food.category == Food.foodCategories.APPETIZER.value:
            print("\nordering a breakfast\n")
            return True    
        return self.__user_can_order_limited_food(user, food_item_id, order_date)
            
    def __food_is_sold_out(self) -> bool:
        print("checking redis in here")
        s_time = time()
        try:
            ordered_food_count = settings.REDIS_CONNECTION.get(f'{self.pk}')
            if ordered_food_count is None:
                print('no data is available in redis for key: ', self.pk)
                raise Exception('key for order_item.pk is not provided')
            ordered_food_count = int(ordered_food_count.decode('utf-8'))
            print('redis is working fine and the food_count is: ', ordered_food_count)
        except Exception as e:
            print("\n hitted 11111111  first 111111111 exception in redis\n")
            print(f'first error message is {e}')
            today = date.today()
            ordered_food_count = self.food_orders.filter(order_date=today).count()
            try:
                settings.REDIS_CONNECTION.set(name=f'{self.pk}', value=ordered_food_count)
                print('added new value to redis: ', ordered_food_count)
            except:
                print("\n hitted 22222222222222222 exception in redis\n")
                print("failed to add new value to redis")

        print('checking redis completed')
        print(self.amount, " -------- ", ordered_food_count)
        print(f'\n took {time() - s_time} to complete redis query\n')
        if self.amount == ordered_food_count:
            print('======food is sold out======')
        return self.amount <= ordered_food_count
    
    def can_be_ordered(self, user, order_date:date) -> bool:
        user_can_order = self.__user_can_order_item(user, self.pk, order_date)
        print("\nuser can order food: ", user_can_order)
        sold_out = self.__food_is_sold_out()
        return user_can_order and not sold_out

    def __str__(self) -> str:
        return f"{self.food.name}: {self.price}"


class OrderItem(models.Model):

    class stateChoices(models.IntegerChoices):
        SUBMITED = 0, _('submited')
        ACCEPTED = 1, _('accepted')
        SERVED = 2, _('served')
        CANCELED = -1, _('canceled')
    
    class modifierChoices(models.IntegerChoices):
        ADMIN = 0, _("admin")
        USER = 1, _('user')

    food_item = models.ForeignKey(to= FoodItem, on_delete=models.PROTECT, related_name="food_orders")
    user = models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='user_orders')
    order_date = models.DateField(verbose_name='oreder date')
    time_submited = models.DateTimeField(verbose_name=_("submition time"), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_("modification time"), auto_now=True)
    state = models.SmallIntegerField(verbose_name=_("state"), choices=stateChoices.choices, default=stateChoices.SUBMITED.value)
    last_modifier = models.SmallIntegerField(verbose_name=_("last modifier"), choices=modifierChoices.choices)
    objects = OrderItemManager()

    def cancel_order(self, user) -> None:
        if user.is_staff:
            self.last_modifier = self.modifierChoices.ADMIN.value
        else:
            self.last_modifier = self.modifierChoices.USER.value
        self.state = self.stateChoices.CANCELED.value
        self.save()
    
    def __str__(self) -> str:
        return f"{self.food_item.food.name}"


class FoodRate(models.Model):
    
    class rateChoices(models.IntegerChoices):
        VERY_BAD = 1, _('very bad')
        BAD = 2, _('bad')
        AVERAGE = 3, _('average')
        GOOD = 4, _('good')
        VERY_GOOD = 5, _('very good')
    
    user = models.ForeignKey(to = settings.AUTH_USER_MODEL, null=True, on_delete= models.SET_NULL)
    food = models.ForeignKey(to= Food, on_delete= models.CASCADE)
    date_rated = models.DateField(verbose_name=_("date rated"), auto_now_add=True)
    rate = models.PositiveSmallIntegerField(verbose_name=_("rate"), choices=rateChoices.choices)

    class Meta:
        ordering = ['-date_rated',]
        unique_together = ['user', 'food', 'date_rated', ]
        verbose_name = _("rate")
        verbose_name_plural = _('food rates')
      