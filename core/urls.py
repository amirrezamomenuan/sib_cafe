from django.urls import path
from core.views import CancelOrderView, CreateOrderView, FoodView, MenuItemView, MenuView, ShowOrdersView, FoodListView, ShowOrderView


urlpatterns = [
    # path('foods/', FoodListView.as_view()),
    path('menu/', MenuView.as_view(), name='menu'),# done
    path('menu-item-detail/', MenuItemView.as_view(), name='menu-item-view'),# done
    path('order/submit', CreateOrderView.as_view(), name='order-submittion'),# done
    path('order/cancel', CancelOrderView.as_view(), name='order-cancelation'),# done
    path('order/<int:order_id>', ShowOrderView.as_view()),
    path('foods/', FoodView.as_view()),
]