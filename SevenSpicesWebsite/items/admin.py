from django.contrib import admin
from .models import Order, MenuItem, OrderItem, Topping, Address, ToppingsCategory, ItemsCategory

admin.site.register(Order)
admin.site.register(MenuItem)
admin.site.register(Topping)
admin.site.register(Address)
admin.site.register(OrderItem)
admin.site.register(ToppingsCategory)
admin.site.register(ItemsCategory)
