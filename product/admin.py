
from django.contrib import admin
from .models import Product, ProductImage, Color, Size, Category,ProductVariant,Review, Wishlist, WishlistItem

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1  

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline, ProductVariantInline]
    list_display = ['name', 'is_active', 'total_stock','created_by', 'created_at']
    list_editable = ['is_active', 'total_stock']
    exclude = ['created_by']
    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
        

admin.site.register(Product, ProductAdmin)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Category)
admin.site.register(Review)
admin.site.site_header = 'Ecommerce Admin'

admin.site.register(Wishlist)
admin.site.register(WishlistItem)