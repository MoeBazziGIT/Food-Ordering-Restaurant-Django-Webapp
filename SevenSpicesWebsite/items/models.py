from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
# from users.models import Profile


class ToppingsCategory(models.Model):
    name = models.CharField(max_length=100)
    amount_allowed = models.PositiveIntegerField(blank=True, null=True)
    type = models.CharField(max_length=100)
    description = models.TextField(max_length=100, blank=True, null=True, default='')
    required = models.BooleanField(default=False, blank=True, null=True)


    def __str__(self):
        return self.name


class Topping(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits = 4, decimal_places=2, default=0)
    category = models.ForeignKey(ToppingsCategory, on_delete = models.PROTECT, default=None)
    # this means how many of this TOPPING was added at one time
    # quantity_added = models.PositiveIntegerField(null=True, blank=True)

    # stock = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class ItemsCategory(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    name = models.CharField(max_length=22)
    price = models.DecimalField(max_digits = 4, decimal_places=2)
    category = models.ForeignKey(ItemsCategory, on_delete = models.PROTECT)
    toppings = models.ManyToManyField(Topping, blank=True)
    image = models.ImageField(default=None, upload_to='menu_item_pics', null=True, blank=True)

    # topping_categories = models.ManyToManyField(ToppingsCategory, blank=True, default=None)
    # stock = models.BooleanField(default=True)
    # orders = models.ForeignKey(Order, on_delete=models.PROTECT)
    # total_orders = models.PositiveIntegerField(Order)
    # nickname = models.CharField(max_length=22)

    def __str__(self):
        return self.name


class OrderItem(models.Model):
    item = models.ForeignKey(MenuItem, on_delete=models.SET_NULL, null=True)
    price = models.DecimalField(max_digits = 4, decimal_places=2, default=0)
    order_item_order = models.ForeignKey('items.Order', on_delete=models.CASCADE, null=True)
    toppings = models.ManyToManyField(Topping, blank=True)

    # this means how many of this order_item was added at one time
    # quantity_added = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.item.name


    def get_item_price(self):
        self.price = sum(topping.price for topping in self.toppings.all()) + self.item.price


    def get_all_topping_categories(self):
        categories = []
        for topping in self.toppings.all():
            if not topping.category in categories:
                categories.append(topping.category)
        return categories

class Address(models.Model):
    street_address = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=10)
    appartment_number = models.CharField(max_length=20, blank=True, null=True)
    customers = models.ManyToManyField('users.Profile')
    orders = models.ManyToManyField('items.Order')

    def __str__(self):
        if self.appartment_number:
            return f'{self.street_address} - {self.appartment_number}'
        return f'{self.street_address}'


class Order(models.Model):
    customer = models.ForeignKey(User, on_delete = models.CASCADE)
    date_ordered = models.DateTimeField(default=timezone.now)
    # items = models.ManyToManyField(MenuItem)
    order_items = models.ManyToManyField(OrderItem)
    total = models.DecimalField(max_digits = 6, decimal_places=2, null=True)
    is_ordered = models.BooleanField(default=False)
    ref_code = models.CharField(max_length=15, default = '')
    delivered_to_address = models.ForeignKey(Address, on_delete = models.CASCADE, default='', null=True)
    # address = models.ManyToManyField(Address, default='', null=True)
    # payment_details = models.ForeignKey(Payment, on_delete=models.CASCADE)

    # This is true when food has left restaurant and on its way
    # order_delivered = models.BooleanField(default=False)

    # pickup or delivery
    type = models.CharField(max_length = 12)

    # pickup or delivery
    pickup_time = models.DateTimeField(default=timezone.now)
    deliver_time = models.DateTimeField(default=timezone.now)

    # specific instructions about order provided by customer
    special_instructions = models.TextField(max_length=256, blank=True)

    # the delivery driver for this order
    # driver = models.ForeignKey(OrderDriver, on_delete=models.PROTECT)


    def __str__(self):
        return f'Order #{self.id} - {self.customer.username}'

    # url to redirect to when submitting order form
    def get_absolute_url(self):
        return reverse('orders:order_detail', kwargs={'pk':self.pk})

    # returns the sum of each item price in order and assigns it to self.total
    def get_order_total(self):
        self.total = sum(order_item.price for order_item in self.order_items.all())

    def get_cart_items(self):
        return self.items.all()

    # when order has left restaurant and is on its way
    # def order_delivered(self):
    #     # send notification to customer
    #     self.order_delivered = True

    class Meta():
        ordering = ['-date_ordered']


# class OrderDriver(models.Model):
#     name = models.CharField(max_length=100)
#     id = models.PositiveIntegerField(max_digits=100)
#     order_picked_up_at = models.DateTimeField(default=timezone.now)
