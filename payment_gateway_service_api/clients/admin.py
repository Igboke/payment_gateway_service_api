from django.contrib import admin
from .models import Client
from django.contrib.auth.admin import UserAdmin
from .forms import ClientCreationForm, ClientChangeForm, AddressCreationForm
from .utils import Address

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    add_form = AddressCreationForm
    list_display = ("street_line1","street_line2","city","state_province","country")
    search_fields = ("city","state_province","country")
    ordering = ("city",)  
    filter_horizontal = ()
    add_fieldsets = (
        (None, {
            "classes":("wide","collapse"),
            "fields":("street_line1","street_line2","city","state_province","country","postal_code"),    
        }),
    )

class ClientAdmin(UserAdmin):
    """
    This is the admin class for Client
    """
    form = ClientChangeForm
    add_form = ClientCreationForm
    list_display = ("email","first_name","last_name","is_staff","is_active")
    list_filter = ("is_staff","is_active")
    search_fields = ("email","first_name","last_name","middle_name")
    ordering = ("email",)
    filter_horizontal = ()
    add_fieldsets = (
        (None, {
            "classes":("wide","collapse"),
            "fields":("email","password","password2"),    
        }),
        ("Personal Info", {
            "classes":("collapse",),
            "fields":("first_name","middle_name","last_name")
        }),
        ("Address", {
            "classes":("collapse",),
            "fields":("house_address",)
        }),
    )
    fieldsets = (
        (None, {
            "fields":("email",),
        }),
        ("Personal Info", {
            "classes":("collapse",),
            "fields":("first_name","middle_name","last_name")
        }),
        ("Address", {
            "classes":("collapse",),
            "fields":("house_address",)
        }),
        ("Permissions", {
            "fields":("is_staff","is_active"),
        }),
        ("Important Dates", {
            "fields":("last_login","date_joined"),
        }),
    )

admin.site.register(Client, ClientAdmin)