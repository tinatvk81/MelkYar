from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    """فقط مدیر مجاز است (برای مدیریت کاربران، Import اکسل، گزارش‌ها و ...)."""

    message = "فقط مدیر سیستم به این بخش دسترسی دارد."

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_admin_role
        )
