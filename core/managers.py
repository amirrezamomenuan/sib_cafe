from django.db.models import Manager, Q

class FoodItemManager(Manager):
    def show_menu(self, week_day: int):
        return self.filter(Q(weekday= week_day) | Q(weekday = -1))