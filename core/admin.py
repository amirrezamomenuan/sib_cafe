from django.contrib import admin

from core.models import Food

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    pass