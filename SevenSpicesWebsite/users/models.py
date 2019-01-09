from django.db import models
from django.contrib.auth.models import User
from items.models import Order, Address, OrderItem
from django.db.models.signals import post_save
from django.conf import settings



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    orders = models.ManyToManyField(Order, blank=True)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    addresses = models.ManyToManyField(Address)
    # items_ordered = models.ManyToManyField(OrderItem)

    def __str__(self):
        return f'{self.user.username}\'s Profile'

    # def fav_items(self):
    #     return max(items_ordered.count)


def post_save_profile_create(sender, instance, created, *args, **kwargs):
    if created:
        Profile.objects.get_or_create(user=instance)

    # user_profile, created = Profile.objects.get_or_create(user=instance)
    #
    # if user_profile.stripe_id is None or user_profile.stripe_id == '':
    #     new_stripe_id = stripe.Customer.create(email=instance.email)
    #     user_profile.stripe_id = new_stripe_id['id']
    #     user_profile.save()


post_save.connect(post_save_profile_create, sender=settings.AUTH_USER_MODEL)
