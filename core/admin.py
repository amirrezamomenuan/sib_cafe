from django.contrib import admin

from core.models import Food, FoodItem

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    pass


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request)