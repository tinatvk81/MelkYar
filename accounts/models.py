from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    کاربر سیستم با دو نقش:
      - ADMIN  : مدیر مجموعه، دسترسی کامل به همه‌ی فایل‌های همه‌ی مشاوران
      - AGENT  : مشاور، فقط دسترسی به فایل‌هایی که خودش ثبت کرده

    نکته‌ی مهم امنیتی: مدیر خودش با پنل ادمین یا API مدیریت کاربران، اکانت
    مشاور می‌سازد (نه ثبت‌نام آزاد). برای غیرفعال کردن مشاور هنگام خروج از
    مجموعه، کافیست is_active را False کنید — فایل‌های او در دیتابیس و برای
    مدیر همچنان قابل مشاهده باقی می‌مانند.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "مدیر"
        AGENT = "AGENT", "مشاور"

    role = models.CharField(max_length=10, choices=Role.choices, default=Role.AGENT)
    phone_number = models.CharField("شماره موبایل", max_length=15, blank=True)

    # مدیر می‌تواند برای هر مشاور یادداشتی بگذارد (مثلاً تاریخ استخدام)
    admin_note = models.TextField("یادداشت مدیر درباره‌ی این کاربر", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_admin_role(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class ActivityLog(models.Model):
    """
    ثبت هر عملِ مهم روی فایل‌های ملکی برای شفافیت بین مدیر و مشاوران.
    (چه کسی، چه فایلی، چه کاری، چه زمانی)
    """

    class Action(models.TextChoices):
        CREATE = "CREATE", "ایجاد"
        UPDATE = "UPDATE", "ویرایش"
        DELETE = "DELETE", "حذف"
        STATUS_CHANGE = "STATUS_CHANGE", "تغییر وضعیت"
        RENEWAL_CONTACT = "RENEWAL_CONTACT", "ثبت نتیجه تماس تمدید"

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="activity_logs")
    action = models.CharField(max_length=20, choices=Action.choices)
    # به‌جای FK مستقیم به Property (که وابستگی چرخه‌ای می‌سازد)، از
    # content type ساده استفاده می‌کنیم تا لاگ برای هر مدلی قابل استفاده باشد.
    target_repr = models.CharField("شرح مورد", max_length=255)
    target_id = models.PositiveIntegerField(null=True, blank=True)
    detail = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "لاگ فعالیت"
        verbose_name_plural = "لاگ فعالیت‌ها"

    def __str__(self):
        return f"{self.user} - {self.get_action_display()} - {self.target_repr}"
