from django.contrib.auth.models import User
from .models import (Order, MenuItem, Address, OrderItem,
                    Topping, ToppingsCategory, ItemsCategory)
from users.models import Profile
from django.views.generic import CreateView, ListView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from items.extras import generate_order_id
from django.http import HttpResponseRedirect
from django.contrib import messages



class MenuListView(ListView):
    model = MenuItem
    template_name = 'items/menu_list.html'

def menu_list_view(request):
    item_list = MenuItem.objects.all()

    context = {'item_list': item_list,
                'item_categories':reversed(ItemsCategory.objects.all()),
                'item_categories_side_nav':reversed(ItemsCategory.objects.all())}

    return render(request, 'items/menu_list.html', context)


def menu_item_detail(request, **kwargs):
    item = MenuItem.objects.filter(id=kwargs.get('pk')).first()

    context = {'item':item}

    return render(request, 'items/item_details.html', context)


@login_required()
def new_order_info(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    order, created = Order.objects.get_or_create(customer=user_profile.user, is_ordered=False)
    if created:
        order.ref_code = generate_order_id()
        order.save()
    context = {'order':order}

    return render(request, 'items/order_info.html', context)


@login_required()
def add_order_info(request):
    street_address = request.POST.get("Street-Address")
    appartment_number = request.POST.get("Apartment-Number")
    postal_code = request.POST.get("Postal-Code")
    order_type = request.POST.get("Order-Type")

    user_profile = get_object_or_404(Profile, user=request.user)

    order = get_user_pending_order(request) # change to get_or_create

    address = Address(street_address=street_address,
                      appartment_number=appartment_number,
                      postal_code=postal_code)

    address_duplicate = Address.objects.filter(street_address=street_address,
                                             appartment_number=appartment_number,
                                             postal_code=postal_code).first()

    if not address_duplicate:
        address.save()
        address.orders.add(order)
        address.customers.add(user_profile)
        address.save()
        user_profile.addresses.add(address)
        order.delivered_to_address = address
    else:
        if not user_profile in address_duplicate.customers.all():
            address_duplicate.customers.add(user_profile)
        if not order in address_duplicate.orders.all():
            address_duplicate.orders.add(order)
        address_duplicate.save()
        order.delivered_to_address = address_duplicate

    order.type = order_type
    order.save()

    return redirect(reverse('orders:new_order'))


# item view
@login_required()
def menu_items_view(request):
    item_list = MenuItem.objects.all()
    user_profile = get_object_or_404(Profile, user=request.user)
    current_order, create = Order.objects.get_or_create(customer=user_profile.user, is_ordered=False) #change to get_user_pending_order()

    # update all item prices if they had toppings added to them
    for order_item in current_order.order_items.all():
        order_item.get_item_price()
        order_item.save()
    current_order.get_order_total()
    current_order.save() # maybe unneccessary line

    context = {'item_list': item_list,
                'current_order':current_order,
                'item_categories':reversed(ItemsCategory.objects.all()),
                'item_categories_side_nav':reversed(ItemsCategory.objects.all())}

    return render(request, 'items/order_create.html', context)




# customize item view
@login_required()
def customize_item(request, **kwargs):
    type = kwargs.get('type')

    order_item = 0

    current_order = get_user_pending_order(request)
    if type == 'add':
        item = MenuItem.objects.filter(id=kwargs.get('pk')).first()
    elif type == 'edit':
        order_item = OrderItem.objects.filter(id=kwargs.get('pk')).first()
        item = order_item.item

    topping_categories = []
    for topping in item.toppings.all():
        if not topping.category in topping_categories:
            topping_categories.append(topping.category)

    context = {'current_order':current_order,
                'topping_categories':topping_categories,
                'toppings':item.toppings.all(),
                'item':item,
                'type':type,
                'order_item':order_item}
    # if order_item:
    # context['order_item'] = order_item

    return render(request, 'items/order_create_toppings.html', context)


# after item has been customized with add-ons/toppings, add it to customers current order
@login_required()
def add_to_order(request, **kwargs):

    # if the request is to edit an item
    if kwargs.get('type') == 'edit':
        # retrieve current order
        order = get_user_pending_order(request)

        # retrieve order_item
        order_item = OrderItem.objects.filter(id=kwargs.get('pk')).first()

        # clear all toppings from order_item
        order_item.toppings.clear()

        # clear item from order
        order.order_items.remove(order_item)
        # order.order_items.delete(order_item)

    # if the request is to add an item
    elif kwargs.get('type') == 'add':
        # retrieving user profile
        user_profile = get_object_or_404(Profile, user=request.user)

        # instantiate Order if this first item being added or get order thats
        #   already instantiated
        order, created = Order.objects.get_or_create(customer=user_profile.user, is_ordered=False) # change to get_user_pending_order()

        if created:
            order.ref_code = generate_order_id()
            order.save()

        # retrieve item from all items
        order_item = OrderItem(item=MenuItem.objects.filter(id=kwargs.get('pk')).first())

    order_item.save()

    # retrive all the inputted toppings for the item and adding it to item toppings
    for category in ToppingsCategory.objects.all():
        category_inputs = request.POST.getlist(category.name)
        print(category_inputs)

        if category.type == 'number':
            for i in range(0, len(category_inputs)):
                if category_inputs[i] and int(category_inputs[i]):
                    topping_input = order_item.item.toppings.filter(category=category)[i].name
                    topping = Topping.objects.filter(name=topping_input).first()
                    order_item.toppings.add(topping)
        else:
            for topping_input in category_inputs:
                topping = Topping.objects.filter(name=topping_input).first()
                order_item.toppings.add(topping)

    order_item.save()

    # retrieving quantity of this item
    order_item_quantity = int(request.POST.get('Item-Quantity'))

    # display success messages
    if kwargs.get('type') == 'add':
        if order_item_quantity > 1:
            messages.success(request, f'{order_item_quantity} {order_item}\'s have been added to your order!')
        else:
            messages.success(request, f'{order_item} has been added to your order!')
    else:
        messages.success(request, f'Changes to your {order_item} have been saved!')


    # adding item_quantity amount of items to order
    while(order_item_quantity):
        # creating new instance of order item for each quantity to add to order
        new_item = OrderItem(item=order_item.item, order_item_order=order)
        new_item.save()
        # copying toppings from order_item to new instance of order item
        for topping in order_item.toppings.all():
            new_item.toppings.add(topping)
        order.order_items.add(new_item)
        order.save()
        order_item_quantity -= 1

    # deleting this extra instance of order item from database.
    order_item.delete()

    return redirect(reverse('orders:new_order'))


@login_required()
def delete_item(request, **kwargs):
    order = get_user_pending_order(request)
    item_to_delete = order.order_items.filter(id=kwargs.get('pk')).first()
    order.order_items.remove(item_to_delete)
    order.save()
    return redirect(reverse('orders:new_order'))


@login_required()
def checkout(request):
    current_order = get_user_pending_order(request)
    # ontario_tax_rate = 0.13
    # current_order.total += current_order.total * ontario_tax_rate
    # current_order.save()
    context = {'current_order':current_order}

    return render(request, 'items/checkout.html', context)


@login_required()
def process_payment(request):
    pass


@login_required()
def update_transaction_records(request):
    # add ordered items to the users profile
    pass


@login_required()
def my_orders(request):
    my_user_profile = Profile.objects.filter(user=request.user).first()
    my_orders = Order.objects.filter(customer=my_user_profile.user)
    # my_user = User.objects.filter(username=request.user.username).first()
    # my_orders = my_user.profile.orders.all()
    context = {
                'my_orders': my_orders,
                }

    return render(request, "items/order_list.html", context)


class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'items/order_details.html'


# HELPER FUNCTION


# get the current order that customer is working on
def get_user_pending_order(request):
    user_profile = get_object_or_404(Profile, user=request.user)
    current_order = Order.objects.filter(customer=user_profile.user, is_ordered=False)
    if current_order.exists():
        return current_order[0]
    return 0


# find length of given queryset
def query_set_len(qSet):
    len = 0
    for item in qSet:
        len += 1
    return len




# ------------------------------------------------------------------------ #


class OrderCreateView(LoginRequiredMixin, CreateView):
    model = Order
    fields = ['items', 'deliver_time', 'pickup_time', 'order_type', 'special_instructions'] #  'pickup_time',
    template_name = 'items/order_create.html'
    # success_url = '/'
    # user = get_user_model ()

    # def get(self, request):
    #     form = NewOrderForm()
    #     items = MenuItem.objects.all()
    #
    #     context = {'form': form, 'items': items}
    #     return render(request, 'orders/order_create.html', context)

    # def post(self, request):
    #     form = NewOrderForm(request.POST)
    #     if form.is_valid():
    #         order = form.save(commit=False)
    #         order.customer = request.user # request.User
    #         order.save()
    #
    #         return redirect('orders:order_purchase') # 'order:order_purchase name'
    #
    #     context = {'form': form, 'items': items}
    #     return render(request, 'orders/order_create.html', context)

    def get_menu_items():
        return [item for item in MenuItem.objects.all()]

    def form_valid(self, form):
        form.instance.customer = self.request.user
        return super().form_valid(form)


# class UserPostListView(LoginRequiredMixin, ListView):
#     model = Order
#     template_name = 'items/order_list.html'  # <app>/<model>_<viewtype>.html
#     context_object_name = 'my_orders'
#     paginate_by = 5
#
#     def get_queryset(self):
#         user = get_object_or_404(User, username=self.kwargs.get('username'))
#         return Order.objects.filter(customer=user)


class OrderListView(LoginRequiredMixin, ListView):
    model = Order

    # template_name = 'items/order_list.html'
    # context_object_name = 'orders'
    # # paginate_by = 5
    #
    # # def get(self, request):
    # #     customer_orders = Order.objects.all().filter(customer=request.user)
    # #     context = {'customer_orders':customer_orders}
    # #     return render(request, 'orders/order_list.html', context)
    #
    # # def get_queryset(self):
    # #     # user = get_object_or_404(User, username=self.kwargs.get('username'))
    # #     return Order.objects.all().order_by('-date_ordered')
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['customer_orders'] = 'HERE'
    #     return context
