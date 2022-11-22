from datetime import datetime, date

from django.db import models
from django.forms import CharField, IntegerField
from djangoProject import settings
from django.utils import translation


# Create your models here.



class Branch(models.Model):
    name = models.CharField(max_length=200)
    branch_number = models.CharField(max_length=50, blank=True, null=True)
    delivery_price = models.IntegerField(default=0)
    telegram_group_id = models.CharField(max_length=200, blank=True, null=True)
    telegram_group_name = models.CharField(max_length=200, blank=True, null=True)
    telegraph_link = models.CharField(max_length=200, blank=True, null=True)
    color_for_statistics = models.CharField(max_length=200, blank=True, null=True)
    total_for_statistics = models.CharField(max_length=200, blank=True, null=True)
    data_for_statistics = models.TextField(blank=True, null=True)
    # label_for_statistics = models.TextField(blank=True, null=True)


    def __str__(self):
        return self.name




class BotUsers(models.Model):
    user_id = models.CharField(max_length=15)
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    firstname = models.CharField(max_length=25, blank=True, default="new user")
    surname = models.CharField(max_length=25, blank=True)
    phone = models.CharField(max_length=25, blank=True)
    lang = models.CharField(max_length=2, blank=True)
    user_step = models.CharField(max_length=25, blank=True)
    user_feedback = models.CharField(max_length=100, blank=True)
    orqaga_step = models.CharField(max_length=10000, blank=True, default='')
    tem_address_name = models.CharField(max_length=255, blank=True, default='')
    birthday = models.CharField(max_length=10, default='')
    firebase_quary_id = models.CharField(max_length=100, default='')
    delivery_type = models.CharField(max_length=100, default='')
    delivery_price = models.IntegerField(default=0)
    cashback_price = models.IntegerField(default=0)

    def __str__(self):
        return f'{self.firstname} {self.surname}'


class Catagory(models.Model):
    title_uz = models.CharField(max_length=255)
    title_ru = models.CharField(max_length=255)


class MenuCatagory(models.Model):
    branch = models.ForeignKey(Branch, on_delete=models.CASCADE, null=True, blank=True)
    menu_title = models.CharField(max_length=255, default='', blank=True, null=True)
    menu_catagoriya_nomi = models.CharField(max_length=255)

    def __str__(self):
        return self.menu_catagoriya_nomi


class Ovqatlar(models.Model):
    turi = models.ForeignKey(MenuCatagory, on_delete=models.CASCADE)
    parent = models.ForeignKey('Ovqatlar', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    narxi = models.CharField(max_length=255, blank=True, default=0)
    gramm = models.FloatField(default=0)
    step = models.IntegerField(default=0)
    paket_narxi = models.IntegerField(default=0)
    working = models.BooleanField(default=True)
    image = models.ImageField(blank=True, default='default.jpg')
    tarkibi = models.TextField(blank=True, default='')

    def __str__(self):
        return self.name


class JoinedGroup(models.Model):
    group_name = models.CharField(max_length=255, default='')
    group_chat_id = models.IntegerField(default=0)


    def __str__(self):
        return self.group_name


class AddToCart(models.Model):
    food_obj = models.ForeignKey(Ovqatlar, on_delete=models.CASCADE, null=True, blank=True)
    user_id = models.CharField(max_length=25)
    product_id = models.CharField(max_length=255)
    price = models.IntegerField(default=0)
    count = models.IntegerField(default=0)
    name = models.CharField(max_length=255, default='')
    cashback_price = models.IntegerField(default=0)

    def __str__(self):
        return self.user_id


class Location(models.Model):
    address_uz = models.CharField(max_length=255)
    address_ru = models.CharField(max_length=255)
    price = models.IntegerField(blank=True, default=0)
    old_price = models.IntegerField(blank=True, default=0)

    def get_address(self):
        return self.address_uz if translation.get_language() == 'uz' else self.address_ru

    def __str__(self):
        a = self.get_address()
        return a


class Order(models.Model):
    user_id = models.CharField(max_length=200, default='')
    fio = models.CharField(max_length=255, default='')
    phone = models.CharField(max_length=100, default='')
    created_at = models.CharField(max_length=100, default='',blank=True)
    update_at = models.CharField(max_length=100, default='',blank=True)
    status = models.IntegerField(default=0)
    total_amount = models.IntegerField(default=0)
    product = models.CharField(max_length=1000, blank=True)
    location = models.CharField(max_length=255, default='')
    tem_lat = models.CharField(max_length=200, default='')
    tem_long = models.CharField(max_length=200, default='')
    tem_address_name = models.CharField(max_length=255, default='')
    branch_name = models.CharField(max_length=100, default='')
    order_type = models.CharField(max_length=100, default='')
    date_ordered = models.DateField(auto_now_add=True)

    # @property
    # def get_cart_total(self):
    #     order_items = self.orderitem_set.all()
    #     total = sum([item.get_total for item in order_items])
    #     return total

    # @property
    # def get_cart_items(self):
    #     order_items = self.orderitem_set.all()
    #     total = sum([item.quantity for item in order_items])
    #     return total

    def __str__(self):
        return self.fio


class Order_items(models.Model):
    order_id = models.ForeignKey(Order, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    user_id = models.IntegerField(blank=True, default=0)
    phone = models.CharField(max_length=100, blank=True, default='')
    product = models.CharField(max_length=100, blank=True)
    location = models.CharField(max_length=100, blank=True, default='')
    price = models.IntegerField()
    count = models.IntegerField()
    order_type = models.CharField(max_length=100, default='')
    branch_name = models.CharField(max_length=100, default='')
    date_ordered = models.DateField(auto_now_add=True)
    
    # @property
    # def get_total(self):
    #     if self.product:
    #         total = self.product.price * self.quantity
    #     elif self.productServices:
    #         total = self.productServices.price * self.quantity
    #     else:
    #         total = 0
    #     return total
    
    def __str__(self):
        return str(self.order_id)


class Working(models.Model):
    title = models.CharField(max_length=200, default="")
    text = models.CharField(max_length=200, blank=True)
    working = models.BooleanField(default=True)
    delivery_price = models.IntegerField(default=0)
    cashback_price = models.FloatField(default=0.0)


    def __str__(self):
        return self.title
