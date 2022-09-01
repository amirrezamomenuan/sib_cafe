from django.urls import path
from core.views import FoodView


urlpatterns = [
    path('<food_id>/', FoodView.as_view()),
]