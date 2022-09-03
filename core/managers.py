from django.db.models import Manager, Q
from django.conf import settings

class FoodItemManager(Manager):
    def show_menu(self, week_day: int):
        return self.filter(Q(weekday= week_day) | Q(weekday = -1))


class FoodManager(Manager):
    page_size = settings.FOOD_PAGE_SIZE
    def get_page(self, page: int):
        return self.all()[(page - 1) * self.page_size : page * self.page_size]