from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerAgentOrAdmin(BasePermission):
    """
    قانون اصلی کنترل دسترسی فایل‌های ملکی:
      - مدیر: دسترسی کامل به هر رکورد.
      - مشاور: فقط به رکوردی که owner_agent آن خودش است دسترسی دارد.

    این پرمیشن روی سطح آبجکت (object-level) اجرا می‌شود؛ فیلتر سطح
    کوئری‌ست هم در ViewSet.get_queryset() انجام می‌شود تا حتی در لیست هم
    فایل مشاور دیگر اصلاً نمایش داده نشود (نه فقط قابل ویرایش نباشد).
    """

    def has_object_permission(self, request, view, obj):
        if request.user.is_admin_role:
            return True
        return obj.owner_agent_id == request.user.id
