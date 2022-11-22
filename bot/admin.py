from django.contrib import admin
from .models import (
                    BotUsers,
                    MenuCatagory,
                    Ovqatlar,
                    AddToCart,
                    Location,
                    Order,
                    Order_items,
                    Working,
                    Branch,
                    JoinedGroup
                    )
# Register your models here.

admin.site.register(Branch)
admin.site.register(BotUsers)
admin.site.register(MenuCatagory)
admin.site.register(Ovqatlar)
admin.site.register(AddToCart)
admin.site.register(Location)
admin.site.register(Order)
admin.site.register(Order_items)
admin.site.register(Working)
admin.site.register(JoinedGroup)


