from django.db import models
from django.forms import ValidationError
from product.models import Product, ProductVariant

from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

ORDER_STATUS = (
    ('created', 'Created'),
    ('shipped', 'Shipped'),
    ('delivered', 'Delivered'),
    ('canceled', 'Canceled'),
    ('refunded', 'Refunded'),
)

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=25)
    is_expired = models.BooleanField(default=False)
    discount_price = models.FloatField(default=10.00)
    minimum_amount = models.FloatField(default=500.00)

    def __str__(self):
        return str(self.id)




class Cart(models.Model):

    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        total = 0
        for item in self.items.all():
            total += item.product.get_final_price(item.variant_product) * item.quantity
        return total

    @property
    def total_with_discount(self):
        total=self.total
        if self.coupon and self.coupon.is_expired == False and total >= self.coupon.minimum_amount:
            total = total - self.coupon.discount_price
        return total
    
    def convert_to_order(self, shipping_address,partial):
        order = Order.objects.create(
            user=self.user,
            shipping_address=shipping_address,
            total=self.total_with_discount,
            coupon=self.coupon
            )
        if not partial:
            order_items = []
            for item in self.items.all():
                order_item = OrderItem(
                    order=order,
                    product=item.product,
                    variant_product=item.variant_product,
                    quantity=item.quantity,
                    product_name=item.product.name,
                    product_price=item.product.get_final_price(item.variant_product),
                )
                order_items.append(order_item)
                item.product.decrement_stock(item.variant_product, item.quantity)

            OrderItem.objects.bulk_create(order_items)
            self.items.all().delete() 
            self.coupon = None
            self.save()
        return order

    def __str__(self):
        return self.user.username + "'s cart"

    class Meta:
        ordering = ["-created_at"]

class CartItem(models.Model):
    cart= models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant_product=models.ForeignKey(ProductVariant,on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total(self):
        return self.product.get_final_price(self.variant_product) * self.quantity

    class Meta:
        ordering = ["-created_at"]
        unique_together = ('cart', 'product',"variant_product")

    def __str__(self) -> str:
        return f"{self.cart.user.username if self.cart.user.username else 'username'} - {self.product.name if self.product.name else 'pname'} - {self.variant_product if self.variant_product else 'none'}"
    
    def clean(self):
        if self.variant_product and not self.product:
            self.product = self.variant_product.product
        if self.variant_product and self.variant_product.product != self.product:
            raise ValidationError("Variant product must belong to the product.")
        if self.product.variants.exists() and not self.variant_product:
            raise ValidationError("Variant product must be set when product has variants.")
        if self.product.is_active == False:
            raise ValidationError("Product is not active.")
        
        if self.product.is_in_stock(self.variant_product) == False:
            raise ValidationError("Product is not in stock.")

    def save(self, *args, **kwargs):
        self.full_clean()

        super().save(*args, **kwargs)

class Order(models.Model):
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=ORDER_STATUS, default='created')
    shipping_address = models.ForeignKey('profiles.Address', related_name='shipping_address', on_delete=models.SET_NULL, null=True, blank=True)
    total=models.FloatField(default=0.0,validators=[MinValueValidator(1.0)],help_text="Total price of order, should be more than 1.0 ")
    coupon=models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True,blank=True)
    coupon_code=models.CharField(max_length=10,default="",null=True,blank=True)
    payment_id=models.CharField(max_length=100,null=True,blank=True)



    def save(self, *args, **kwargs):
        if self.coupon:
            self.coupon_code=self.coupon.coupon_code
        super().save(*args, **kwargs )

    def __str__(self):
        return 'Order: ' + str(self.id)

    class Meta:
        ordering = ["-created_at"]

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant_product = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=255,null=True, blank=True,default="")
    product_price = models.DecimalField(max_digits=10, decimal_places=2,null=True,blank=True)
    quantity = models.IntegerField(default=1)

    @property
    def total(self):
        return self.product_price * self.quantity


    def clean(self):
        if self.variant_product and not self.product:
            self.product = self.variant_product.product
        if self.variant_product and self.variant_product.product != self.product:
            raise ValidationError("Variant product must belong to the product.")
        if self.product.variants.exists() and not self.variant_product:
            raise ValidationError("Variant product must be set when product has variants.")
        
    def save(self, *args, **kwargs):
        self.full_clean()       
        super().save(*args, **kwargs)

    
    def __str__(self):
        return self.product.name + " - " + str(self.quantity)