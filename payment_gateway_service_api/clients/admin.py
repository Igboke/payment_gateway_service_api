from django.contrib import admin
from .models import Client
from django.contrib.auth.admin import UserAdmin
from .forms import ClientCreationForm, ClientChangeForm
from django.contrib.auth import get_user_model

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
            "fields":("street","town","state")
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
            "fields":("street","town","state")
        }),
        ("Permissions", {
            "fields":("is_staff","is_active"),
        }),
        ("Important Dates", {
            "fields":("last_login","date_joined"),
        }),
    )

admin.site.register(Client, ClientAdmin)