from django.contrib import admin
from .forms import AddProductForm
from .models import Products


class ProductAdmin(admin.ModelAdmin):
    add_form = AddProductForm
    list_display = ("name", "quantity", "price", "is_available")
    list_filter = ("is_available",)
    search_fields = ("name", "price")
    ordering = ("name",)
    filter_horizontal = ()
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide", "collapse"),
                "fields": ("name", "quantity", "description", "price", "is_available"),
            },
        ),
    )


admin.site.register(Products, ProductAdmin)
