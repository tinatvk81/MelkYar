from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import ActivityLog, User


@admin.register(User)
class MelkyarUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "role", "phone_number", "is_active", "date_joined")
    list_filter = ("role", "is_active")
    fieldsets = UserAdmin.fieldsets + (
        ("اطلاعات ملک‌یار", {"fields": ("role", "phone_number", "admin_note")}),
    )


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ("created_at", "user", "action", "target_repr")
    list_filter = ("action",)
    search_fields = ("target_repr", "user__username")
    readonly_fields = [f.name for f in ActivityLog._meta.fields]

    def has_add_permission(self, request):
        return False
