from django.urls import path
from core.views import CancelOrderView, CreateOrderView, FoodView, MenuItemView, MenuView, OrderDetailView, OrderListView, FoodListView


urlpatterns = [
    # path('foods/', FoodListView.as_view()),
    path('menu/', MenuView.as_view(), name='menu'),# done
    path('menu-item-detail/', MenuItemView.as_view(), name='menu-item-view'),# done
    path('order/submit/', CreateOrderView.as_view(), name='order-submittion'),# done
    path('order/cancel/', CancelOrderView.as_view(), name='order-cancelation'),# done
    path('order/detail/', OrderDetailView.as_view(), name='order-detail'),# done
    path('order/all/', OrderListView.as_view(), name='order-list'),
    path('foods/', FoodView.as_view()),
]