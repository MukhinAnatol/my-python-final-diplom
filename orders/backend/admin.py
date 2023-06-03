from django.contrib import admin

from django.contrib.auth.admin import UserAdmin

from .models import CustomUser, Order, OrderItem

class CustomUserAdmin(UserAdmin):

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': (
            'is_active',
            'is_staff',
            'is_superuser',
            'groups',
            'user_permissions')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),}),)

    list_display = ('id', 'email', 'first_name', 'last_name', 'company', 'type')
    list_filter = ('is_staff', 'is_active', 'is_superuser', 'groups')
    search_fields = ("email", 'last_name')
    ordering = ('email',)
    filter_horizontal = ('groups', 'user_permissions')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status']
    list_filter = ['status']

@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['id', 'shop', 'quantity', 'product_info']

admin.site.register(CustomUser, CustomUserAdmin)

