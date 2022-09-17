from datetime import date, datetime
from time import time

from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings
from django.shortcuts import get_object_or_404

from core.managers import FoodManager, OrderItemManager

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
    
    class Meta:
        ordering = ['-creation_time']

    def __food_weekday_matches_order_date(self, order_date):
        if self.weekday == -1:
            return True
        return self.weekday == (order_date.weekday() + 2) % 7

    def __user_has_ordered_limited_food(self, user, food_item_id, order_date:date):
        return user.user_orders.filter(food_item__id=food_item_id, order_date=order_date).exists()

    def __check_time_limit(self):
        if self.food.category == Food.foodCategories.BREAKFAST.value:
            return datetime.now().hour < settings.BREAKFAST_TIME_LIMIT
        elif self.food.category == Food.foodCategories.LUNCH.value:
            return datetime.now().hour < settings.LUNCH_TIME_LIMIT
        return datetime.now().hour < settings.APPETIZER_TIME_LIMIT

    def __order_time_is_over(self, order_date:date):
        date_difference = (order_date - date.today()).days
        if date_difference >= 7:
            return True

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
        else:
            if date_difference == 0:
                return not self.__check_time_limit()
        return True

    def __user_can_order_limited_food(self, user, food_item_id, order_date):
        if self.__order_time_is_over(order_date):
            return False
        elif not self.__food_weekday_matches_order_date(order_date):
            return False
        return not self.__user_has_ordered_limited_food(user, food_item_id, order_date)

    def __user_can_order_item(self, user, food_item_id, order_date:date) -> bool:
        if self.food.category == Food.foodCategories.APPETIZER.value:
            return not self.__order_time_is_over(order_date)   
        return self.__user_can_order_limited_food(user, food_item_id, order_date)
            
    def __food_is_sold_out(self) -> bool:
        if self.amount is None:
            return False
        try:
            ordered_food_count = settings.REDIS_CONNECTION.get(f'{self.pk}')
            if ordered_food_count is None:
                raise Exception('key for order_item.pk is not provided')
            ordered_food_count = int(ordered_food_count.decode('utf-8'))
            
        except Exception as e:
            today = date.today()
            ordered_food_count = self.food_orders.filter(order_date=today).count()
            try:
                settings.REDIS_CONNECTION.set(name=f'{self.pk}', value=ordered_food_count)
            except:
                pass

        return self.amount <= ordered_food_count
    
    def can_be_ordered(self, user, order_date:date) -> bool:
        user_can_order = self.__user_can_order_item(user, self.pk, order_date)
        if not user_can_order:
            return False
        return user_can_order and not self.__food_is_sold_out()

    def __str__(self) -> str:
        return f"{self.food.name}: {self.price}"


class OrderItem(models.Model):

    class stateChoices(models.IntegerChoices):
        SUBMITED = 0, _('submited')
        SERVED = 1, _('served')
        PAYED = 2, _('payed')
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
    last_modifier = models.SmallIntegerField(verbose_name=_("last modifier"), choices=modifierChoices.choices, default=modifierChoices.ADMIN.value)

    def __todays_order_is_getting_canceled(self) -> bool:
        date_difference = (self.order_date - date.today()).days
        if date_difference == 0:
            return True
        return False

    def __reached_cancel_time_limit(self) -> bool:
        if not self.__todays_order_is_getting_canceled():
            return False
        if self.food_item.food.category == Food.foodCategories.BREAKFAST.value:
            if datetime.now().hour > settings.BREAKFAST_CANCEL_TIME_LIMIT:
                return True
        elif self.food_item.food.category == Food.foodCategories.LUNCH.value:
            if datetime.now().hour > settings.LUNCH_CANCEL_TIME_LIMIT:
                return True
        else:
            if datetime.now().hour > settings.APPETIZER_CANCEL_TIME_LIMIT:
                return True
        return False

    def can_be_canceled(self, user) -> bool:
        if user != self.user:
            return False
        if self.__reached_cancel_time_limit():
            return False
        if self.state != self.stateChoices.SUBMITED.value:
            return False
        return True

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
      