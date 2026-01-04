from django.contrib import admin
from .models import Category, Product, Brand, EmailOTP,Order,OrderItem


# customize product display in admin
class ProductAdmin(admin.ModelAdmin):
    list_display = ('id','name','brand','price','category')
    list_filter = ('brand','category')
    search_fields = ('name','brand')
    ordering = ('id',)


# customize category display
class CategoryAdmin(admin.ModelAdmin):
     list_display = ('id','name')
     search_fields = ('name',)

# Register Models
admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(Brand)
admin.site.register(EmailOTP)
admin.site.register(Order)
admin.site.register(OrderItem)




