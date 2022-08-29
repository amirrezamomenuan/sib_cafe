from django.db import models
from django.utils.translation import ugettext_lazy as _


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
    food = models.ForeignKey(to=Food, on_delete=models.PROTECT, related_name="food_items")
    amount = models.PositiveIntegerField(verbose_name=_("amount"), null=True)
    price = models.PositiveIntegerField(verbose_name=_("price"))
    creation_time = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(verbose_name=_('is_active'), default= True)
    
    class Meta:
        ordering = ['-creation_time']

    @property
    def can_be_ordered(self) -> bool:
        if self.amount is not None:
            return self.amount > 0
        return True
    
    def save(self, *args, **kwargs) -> None:
        # maybe replace self.__class__ with FoodItem
        self.__class__.objects.filter(food = self.food).update(is_active = False)
        return super().save(*args, **kwargs)

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
    user = models.ForeignKey(to='accounts.user', on_delete=models.PROTECT, related_name='user_orders')
    time_submited = models.DateTimeField(verbose_name=_("submition time"), auto_now_add=True)
    last_modified = models.DateTimeField(verbose_name=_("modification time"), auto_now=True)
    state = models.SmallIntegerField(verbose_name=_("state"), choices=stateChoices.choices, default=stateChoices.SUBMITED.value)
    last_modifier = models.SmallIntegerField(verbose_name=_("last modifier"), choices=modifierChoices.choices)

    def can_be_canceled(self, user) -> bool:
        pass

    def accept_order(self, user) -> None:
        pass

    def serve_order(self, user) -> None:
        pass

    def cancel_order(self, user) -> None:
        pass
