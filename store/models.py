from django.db import models
from django.contrib.auth.models import User
import uuid
from django.utils import timezone

class Category(models.Model):
    name=models.CharField(max_length=200)


    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='brands/')

    def __str__(self):
        return self.name



class Product(models.Model):
    name=models.CharField(max_length=100)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    price=models.IntegerField()
    description=models.TextField()
    image=models.ImageField(upload_to='products/')
    category=models.ForeignKey(Category,on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class EmailOTP(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)


    def __str__(self):
        return f"{self.email}-{self.otp}"



class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True
    )
    created_at = models.DateTimeField(
        default=timezone.now
    )

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"


