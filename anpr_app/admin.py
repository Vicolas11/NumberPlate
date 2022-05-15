from anpr_app.models import ( Photo, User, VehicleOwner)
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
admin.site.unregister(Group)

@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {'fields': ('email', 'password',)}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','gender','contact',)}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',),
        }),
    )
    list_display = ('id','email','username','first_name', 'last_name', 'is_staff','gender','contact')
    search_fields = ('email', 'first_name', 'last_name',)
    ordering = ('-id',)


@admin.register(VehicleOwner)
class VehicleOwner(admin.ModelAdmin):
    fieldsets = (
        (_('Personal info'), {'fields': ('plate_number','first_name','last_name','age','vehicle_model','entered','avatar')}),
    )
    list_display = ('id','plate_number','first_name','last_name','age','vehicle_model','entered',)
    search_fields = ('id','plate_number', 'vehicle_model',)
    ordering = ('-id',)


@admin.register(Photo)
class PhotoOwner(admin.ModelAdmin):
    fieldsets = (
        (_('Personal info'), {'fields': ('roi','img','title')}),
    )
    list_display = ('id','title',)
    search_fields = ('id','title',)
    ordering = ('-id',)
