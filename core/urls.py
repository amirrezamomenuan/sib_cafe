from django.urls import path
from core.views import CancelOrderView, CreateOrderView, FoodRateView, MenuItemView, MenuView, OrderDetailView, OrderListView


urlpatterns = [
    path('menu/', MenuView.as_view(), name='menu'),
    path('menu-item-detail/', MenuItemView.as_view(), name='menu-item-view'),
    path('order/submit/', CreateOrderView.as_view(), name='order-submittion'),
    path('order/cancel/', CancelOrderView.as_view(), name='order-cancelation'),
    path('order/detail/', OrderDetailView.as_view(), name='order-detail'),
    path('order/all/', OrderListView.as_view(), name='order-list'),
    path('rate/', FoodRateView.as_view(), name='rate-submittion'),
]