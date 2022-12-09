from django.contrib import admin
from .models import User,Product,Wishlist,Addcart,Transaction
# Register your models here.
admin.site.register(User)
admin.site.register(Product)
admin.site.register(Wishlist)
admin.site.register(Addcart)
admin.site.register(Transaction)