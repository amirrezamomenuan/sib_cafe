from django.urls import path
from core.views import FoodListView


urlpatterns = [
    path('', FoodListView.as_view()),
]