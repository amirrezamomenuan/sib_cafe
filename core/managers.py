# from calendar import weekday as _weekday
from datetime import date, timedelta
from django.db.models import Manager, Q
from django.conf import settings

class FoodItemManager(Manager):
    page_size = settings.MENU_PAGE_SIZE

    def show_menu(self, week_day: int):
        # TODO: update to ASYNC after adding redis to the project
        # since fitem.can_be_ordered will triger a redis call
        return [fitem for fitem in self.filter(Q(weekday= week_day) | Q(weekday = -1)) if fitem.can_be_ordered]

    def get_page(self, queryset, page: int):
        return queryset[(page - 1) * self.page_size : page * self.page_size]

class FoodManager(Manager):
    page_size = settings.FOOD_PAGE_SIZE
    def get_page(self, page: int):
        return self.all()[(page - 1) * self.page_size : page * self.page_size]