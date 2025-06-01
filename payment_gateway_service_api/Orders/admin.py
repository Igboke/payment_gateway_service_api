from django.contrib import admin
from .models import Orders, OrderItem


# Inline for OrderItem
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1


class OrdersAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline]

    list_display = (
        "client",
        "status",
        "total_amount",
        "shipping_address",
        "billing_address",
        "created_at",
    )
    list_filter = ("status", "created_at", "client")
    search_fields = ("client__first_name", "client__last_name", "status")

    readonly_fields = ("total_amount", "created_at", "updated_at")

    fieldsets = (
        (
            None,
            {
                "fields": ("client", "status", ("shipping_address", "billing_address")),
            },
        ),
        (
            "Order Details",
            {
                "fields": ("total_amount",),
            },
        ),
        (
            "Timestamps",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )

    def save_formset(self, request, form, formset, change):
        """
        Override save_formset to recalculate total_amount after inlines are saved.
        """
        super().save_formset(request, form, formset, change)
        order = form.instance
        # Recalculate and save the total amount
        order.calculate_total_amount()
        order.save()


admin.site.register(Orders, OrdersAdmin)
