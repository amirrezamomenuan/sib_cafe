from django.contrib import admin

from core.models import Food, FoodItem, FoodRate, OrderItem

@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    pass


@admin.register(FoodItem)
class FoodItemAdmin(admin.ModelAdmin):
    def get_queryset(self, request):
        return super().get_queryset(request)
    

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


@admin.register(FoodRate)
class FoodRateLeaderBoard(admin.ModelAdmin):
    pass