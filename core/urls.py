from django.urls import path
from core.views import FoodView, MenuView, OrderView, FoodListView


urlpatterns = [
    path('foods/', FoodListView.as_view()),
    path('foods/<food_id>/', FoodView.as_view()),
    path('menu/<day>', MenuView.as_view()),
    path('orders/', OrderView.as_view()),
]