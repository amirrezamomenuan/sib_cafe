from django.urls import path
from core.views import FoodView, MenuView, ShowOrdersView, FoodListView


urlpatterns = [
    path('foods/', FoodListView.as_view()),
    path('foods/<food_id>/', FoodView.as_view()),
    path('menu/', MenuView.as_view()),
    path('orders/', ShowOrdersView.as_view()),
]