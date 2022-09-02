from django.db.models import BaseManager, Q

class FoodItemManager(BaseManager):
    def show_menu(self, week_day: int):
        return self.filter(Q(weekday= week_day) | Q(weekday = -1))