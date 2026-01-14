from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

# ================= Role Admin =================

class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

#===================Document Upload================#
class UsersecurityAdmin(admin.ModelAdmin):
    list_display = ('id','user','user_id','is_mpin_enabled','is_fingerprint_enabled','is_face_lock_enabled','created_at')

    readonly_fields = ('created_at','updated_at','user_id')
    search_fields = ('user_username','user_user_id')

# ================= User Admin =================
class CustomUserAdmin(BaseUserAdmin):
    model = User

    # Columns to display in user list
    list_display = (
        "id",
        "user_id",          
        "username",
        "full_name",
        "Email_ID",
        "mobile_number",
        "gender",
        "role",
        "is_active",
    )

    # Make user_id read-only in admin
    readonly_fields = ("user_id",)

    # Filters on sidebar
    list_filter = ("is_active", "gender", "role")
    search_fields = ("username", "full_name", "Email_ID", "mobile_number", "user_id")
    ordering = ("id",)

    # Fieldsets for user detail page
    fieldsets = (
        ("System Info", {
            "fields": ("user_id",),  
        }),
        ("Login Info", {
            "fields": ("username", "password")
        }),
        ("Personal Info", {
            "fields": ("full_name", "Email_ID", "mobile_number", "gender", "DOB", "Address")
        }),
        ("Permissions", {
            "fields": ("role", "is_active", "is_staff", "is_superuser")
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "password1", "password2", "role", "is_active"),
        }),
    )
