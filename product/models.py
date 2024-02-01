from collections.abc import Iterable
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Avg


class Category(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=50)
    hex_value = models.CharField(max_length=7)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=255)
    desc = models.TextField()
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    base_price = models.FloatField(default=0.0, validators=[MinValueValidator(1.0)], help_text="Base price of product, should be more than 1.0 ")
    total_stock=models.PositiveIntegerField(default=0, help_text="Total stock of product including all variants, must be greater than 0 ")
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)

    class Meta:
        ordering = ["total_stock","-created_at"]

    def __str__(self):
        return self.name
    
    @property
    def get_avg_rating(self):
        return self.reviews.aggregate(Avg('rating'))['rating__avg']
    
    def get_final_price(self, variant=None):
        if not variant or variant.variant_price is None:
            return self.base_price
        if variant.is_extra_price:
            return self.base_price + variant.variant_price
        else:
            return variant.variant_price
        
    def is_in_stock(self, variant=None):
        if not variant or variant.variant_stock is None:
            return self.total_stock > 0
        return variant.variant_stock > 0
    
    def decrement_stock(self, variant=None, quantity=1):
        if  variant and variant.variant_stock is not None:
            variant.variant_stock -= quantity
            variant.save()
        self.total_stock -= quantity
        self.save()

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, related_name='variants', on_delete=models.CASCADE)
    color = models.ForeignKey(Color, on_delete=models.CASCADE, null=True, blank=True)
    sizes = models.ForeignKey(Size, on_delete=models.CASCADE, null=True, blank=True)
    is_extra_price = models.BooleanField(default=False, help_text="If checked, the price will be added as extra price else this price will be the final price of product")
    variant_price = models.FloatField(null=True, blank=True, help_text="if left blank, the price will be same as base price")
    variant_stock = models.IntegerField(null=True, blank=True,help_text="if left blank, the stock will be same as total stock of product")


    def __str__(self) -> str:
        return f"{self.product.name if self.product.name else 'pname'} - {self.color if self.color else 'none'} - {self.sizes if self.sizes else 'none'}"
    

    def get_final_price(self):
        return self.product.get_final_price(self)
    
    class Meta:
        ordering = ["variant_price","variant_stock",'product']
        unique_together = ('product', 'color', 'sizes')


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.product.name




class Review(models.Model):
    product = models.ForeignKey(Product, related_name='reviews', on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', related_name='reviews', on_delete=models.CASCADE)
    comment = models.TextField(blank=True)
    rating = models.PositiveIntegerField(default=0, validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ('product', 'user')

    def __str__(self):
        return self.product.name
    


class Wishlist(models.Model):
    user = models.ForeignKey('auth.User', related_name='wishlist', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    share_token = models.CharField(max_length=255, blank=True)
    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.user.profile.full_name
    

class WishlistItem(models.Model):
    wishlist = models.ForeignKey(Wishlist, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='wishlist_items', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ('product', 'wishlist')

    def __str__(self):
        return self.product.name
    
