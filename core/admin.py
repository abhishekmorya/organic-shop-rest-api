from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

class UserAdmin(BaseUserAdmin):

    ordering = ('id',)
    list_display = ('email', 'name')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('name',)}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.UserAddress)
admin.site.register(models.UserDetails)
admin.site.register(models.Category)
admin.site.register(models.Product)
admin.site.register(models.ShoppingCart)
admin.site.register(models.PaymentMode)
admin.site.register(models.Offer)
admin.site.register(models.Order)
admin.site.register(models.PriceDetail)