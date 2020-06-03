from django.contrib import admin
from .models import Cart, Tire, CartDetail

# ────────────────────────────────────────────────────────────────────────────────

class CartDetailAdmin(admin.ModelAdmin):
  # Fields displayed in the list page
  list_display = (
    'cart',
    'tire',
    'price_each',
    'quantity',
    'get_sub_total',
  )

  # Field that can be editted directly within the list page
  list_editable = ('quantity',)

  def get_sub_total(self, obj):
    return obj.quantity * obj.tire.price
    
  get_sub_total.short_description = "Subtotal ($)"

  readonly_fields = ('price_each', 'get_sub_total')

# ────────────────────────────────────────────────────────────────────────────────

class CartDetailInline(admin.TabularInline):
  model = CartDetail
  can_delete = True
  extra = 1 # Number of extra forms the formset will display in addition to the initial forms
  
# ────────────────────────────────────────────────────────────────────────────────

class CartAdmin(admin.ModelAdmin):
  # Fields displayed in the list page
  list_display = (
    'user',
    'date_ordered',
    'status',
    'discount_ratio_applied',
  )

  list_editable = ('status',)

  # Filters in the right sidebar of the list page
  list_filter = (
    'date_ordered',
    'status',
  )

  search_fields = (
    'user',
  )

  inlines = (CartDetailInline,)

# ────────────────────────────────────────────────────────────────────────────────

class TireAdmin(admin.ModelAdmin):
  # Fields displayed in the list page
  list_display = (
    'name',
    'brand',
    'year',
    'width',
    'aspect_ratio',
    'rim_size',
    'price',
    'season',
    'current_quantity',
    'total_quantity',
    'sold',
  )

  # Filters in the right sidebar of the list page
  list_filter = (
    'brand',
    'year',
    'season',
  )

  search_fields = (
    'name',
    'brand',
    'year',
  )

# ────────────────────────────────────────────────────────────────────────────────

# Register your models here
admin.site.register(CartDetail, CartDetailAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Tire, TireAdmin)