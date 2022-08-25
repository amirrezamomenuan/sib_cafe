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
    image = models.ImageField(verbose_name=_('image'), upload_to ='/uploads/food_images', default='/uploads/food_images/default.jpg')
    creation_time = models.DateTimeField(auto_now_add=True)
    modification_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_food"
        verbose_name = _("food")
        verbose_name_plural = _('foods')
        ordering = ["-creation_time", 'price']
    
    @property
    def rate(self):
        return 5 #TODO: change this to a function that reads data from redis and returns it
    
    @rate.setter
    def rate(self, rate:float) -> None:
        pass #TODO: change this to a function that updates new data to redis
