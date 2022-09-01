from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.conf import settings


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
        TUESDAY = 3, _('sunday')
        WEDNESDAY = 4, _('wednesday')
        EVERY_DAY = -1, _("everyday")

    food = models.ForeignKey(to=Food, on_delete=models.PROTECT, related_name="food_items")
    amount = models.PositiveIntegerField(verbose_name=_("amount"), null=True, blank=True)
    price = models.PositiveIntegerField(verbose_name=_("price"))
    creation_time = models.DateTimeField(auto_now_add=True)
    weekday = models.SmallIntegerField(verbose_name= _("weekday"), choices= dayChoices.choices, default= dayChoices.EVERY_DAY.value)
    
    class Meta:
        ordering = ['-creation_time']

    @property
    def can_be_ordered(self) -> bool:
        if self.amount is not None:
            return self.amount > 0
        return True

    def show_menu(self, weekday):
        pass

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
    time_submited = models.DateTimeField(verbose_name=_("submition time"), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_("modification time"), auto_now=True)
    state = models.SmallIntegerField(verbose_name=_("state"), choices=stateChoices.choices, default=stateChoices.SUBMITED.value)
    last_modifier = models.SmallIntegerField(verbose_name=_("last modifier"), choices=modifierChoices.choices)

    def can_be_ordered(self) -> bool:
        pass #change after redis is added to project

    def can_be_canceled(self) -> bool:
        if self.state != self.stateChoices.SUBMITED.value:
            return False
        # TODO: check time and return True if order can be canceled

    def can_be_served(self) -> bool:
        pass

    def can_be_accepted(self) -> bool:
        pass

    def cancel_order(self, user) -> None:
        if user.is_staff:
            self.last_modifier = self.modifierChoices.ADMIN.value
        else:
            self.last_modifier = self.modifierChoices.USER.value
        self.state = self.stateChoices.CANCELED.value
        self.save()
    
    def accept_order(self) -> None:
        pass
    
    def serve_order(self) -> None:
        pass

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
      