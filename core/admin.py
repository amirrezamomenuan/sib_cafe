from django.contrib import admin

from core.models import Food, FoodItem

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    pass


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    pass