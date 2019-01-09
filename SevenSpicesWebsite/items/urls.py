from django.urls import path
from . import views


app_name = 'orders'

urlpatterns = [
    # path('new/', views.OrderCreateView.as_view(), name = 'new_order'),
    path('new/', views.menu_items_view, name = 'new_order'),
    path('menu/', views.menu_list_view, name = 'menu_list'),
    path('item-detail/<int:pk>', views.menu_item_detail, name = 'item_detail'),
    # path('my-orders/', views.OrderListView.as_view(), name = 'my_orders'),
    path('order-info/', views.new_order_info, name='order_info'),
    path('add-order-info/', views.add_order_info, name='add_order_info'),
    path('customize/<int:pk>/<str:type>/', views.customize_item, name = 'customize_item'),
    path('add-to-order/<int:pk>/<str:type>/<int:order_item_pk>/', views.add_to_order, name = 'add_to_order'),
    path('delete-item/<int:pk>/', views.delete_item, name='delete_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('my-orders/', views.my_orders, name = 'my_orders'),
    path('order-detail/<int:pk>/', views.OrderDetailView.as_view(), name='order_detail')

]
