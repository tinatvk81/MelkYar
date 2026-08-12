from datetime import date
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

# 1. تابع کمکی
def validate_image_size(image):
    max_mb = 5
    if image.size > max_mb * 1024 * 1024:
        raise ValidationError(f"حجم تصویر نباید بیشتر از {max_mb} مگابایت باشد.")

# 2. مدل Amenity (قبل از Property باشد)
class Amenity(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام امکانات")

    class Meta:
        verbose_name = "امکانات رفاهی"
        verbose_name_plural = "امکانات رفاهی"

    def __str__(self):
        return self.name

# 3. مدل Property
class Property(models.Model):
    # ... کدهای TransactionType و غیره ...
    class TransactionType(models.TextChoices):
        SALE = "SALE", "فروش"
        PRESALE = "PRESALE", "پیش‌خرید"
        RENT = "RENT", "اجاره"
        MORTGAGE = "MORTGAGE", "رهن کامل"

    class PropertyKind(models.TextChoices):
        APARTMENT = "APARTMENT", "آپارتمان مسکونی"
        VILLA = "VILLA", "ویلایی"
        OFFICE = "OFFICE", "اداری"
        COMMERCIAL = "COMMERCIAL", "تجاری"
        LAND = "LAND", "زمین"
        OTHER = "OTHER", "سایر"

    class FileStatus(models.TextChoices):
        ACTIVE = "ACTIVE", "فعال"
        RESERVED = "RESERVED", "رزرو شده"
        CLOSED = "CLOSED", "معامله‌شده"
        INACTIVE = "INACTIVE", "غیرفعال"

    class DocumentType(models.TextChoices):
        SINGLE_PAGE = "SINGLE_PAGE", "تک برگ"
        TASSELED = "TASSELED", "منگوله‌دار"
        AGREEMENT = "AGREEMENT", "قولنامه‌ای"
        OTHER = "OTHER", "سایر"

    owner_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="properties",
        verbose_name="مشاور ثبت‌کننده",
    )

    code = models.CharField("کد ملک", max_length=30, unique=True)
    title = models.CharField("عنوان آگهی", max_length=255)
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    property_kind = models.CharField("نوع ملک", max_length=15, choices=PropertyKind.choices)
    status = models.CharField(max_length=10, choices=FileStatus.choices, default=FileStatus.ACTIVE)

    province = models.CharField("استان", max_length=100)
    city = models.CharField("شهر", max_length=100)
    district = models.CharField("منطقه/محله", max_length=150, blank=True)
    full_address = models.TextField("آدرس کامل", blank=True)
    map_link = models.URLField("لینک موقعیت روی نقشه", blank=True)

    area_sqm = models.PositiveIntegerField("متراژ زیربنا (متر)", null=True, blank=True)
    land_area_sqm = models.PositiveIntegerField("متراژ زمین (متر)", null=True, blank=True)
    bedrooms = models.PositiveSmallIntegerField("تعداد اتاق خواب", null=True, blank=True)
    build_year = models.PositiveSmallIntegerField("سال ساخت", null=True, blank=True)
    total_floors = models.PositiveSmallIntegerField("تعداد کل طبقات ساختمان", null=True, blank=True)
    unit_floor = models.SmallIntegerField("طبقه واحد", null=True, blank=True)
    units_per_floor = models.PositiveSmallIntegerField("تعداد واحد در طبقه", null=True, blank=True)
    direction = models.CharField("جهت ساختمان", max_length=50, blank=True)
    document_type = models.CharField(max_length=15, choices=DocumentType.choices, blank=True)

    has_elevator = models.BooleanField("آسانسور", default=False)
    parking_count = models.PositiveSmallIntegerField("تعداد پارکینگ", default=0)
    has_storage = models.BooleanField("انباری", default=False)
    has_balcony = models.BooleanField("بالکن", default=False)
    
    # فیلد متنی قدیمی (برای اکسل)
    amenities = models.CharField("امکانات رفاهی", max_length=500, blank=True, help_text="با کاما جدا کنید")
    
    # فیلد جدید ManyToMany (مدل Amenity الان در بالای فایل تعریف شده و شناخته می‌شود)
    property_amenities = models.ManyToManyField(
        Amenity,
        blank=True,
        related_name="properties",
        verbose_name="امکانات رفاهی مرتبط",
    )

    heating_system = models.CharField("سیستم گرمایش", max_length=100, blank=True)
    cooling_system = models.CharField("سیستم سرمایش", max_length=100, blank=True)
    floor_covering = models.CharField("نوع کفپوش", max_length=100, blank=True)
    is_renovated = models.BooleanField("بازسازی شده", default=False)
    unit_condition = models.CharField("وضعیت واحد", max_length=150, blank=True)

    owner_name = models.CharField("نام مالک", max_length=150, blank=True)
    owner_phone = models.CharField("شماره تماس مالک", max_length=20, blank=True)
    is_exclusive = models.BooleanField("فایل انحصاری", default=False)

    public_description = models.TextField("توضیحات عمومی (نمایش به مشتری)", blank=True)
    private_note = models.TextField("یادداشت خصوصی مشاور", blank=True)

    renewal_priority_flag = models.BooleanField("اولویت یک‌ماهه", default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "فایل ملکی"
        verbose_name_plural = "فایل‌های ملکی"
        ordering = ["-updated_at"]

    def __str__(self):
        return f"{self.code} - {self.title}"



class Contract(models.Model):
    property = models.OneToOneField(
        Property,
        on_delete=models.CASCADE,
        related_name="contract",
    )
    contract_start_date = models.DateField(null=True, blank=True)
    contract_end_date = models.DateField(null=True, blank=True)
    current_tenant_name = models.CharField(max_length=255, blank=True, default="")
    current_tenant_phone = models.CharField(max_length=32, blank=True, default="")
    renewal_status = models.CharField(max_length=32, blank=True, default="UNCLEAR")
    last_contact_result = models.TextField(blank=True, default="")
    next_contact_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Contract for {self.property.code}"


class ImageAsset(models.Model):
    """گالری تصاویر برای هر فایل ملکی (چند عکس)."""

    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="ملک"
    )
    image = models.ImageField(
        upload_to="property_images/",
        validators=[
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"]),
            validate_image_size,
        ],
        verbose_name="تصویر"
    )
    caption = models.CharField(max_length=150, blank=True, verbose_name="توضیح تصویر")
    is_primary = models.BooleanField(default=False, verbose_name="تصویر اصلی (کاور)")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ آپلود")

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "تصویر فایل"
        verbose_name_plural = "تصاویر فایل‌ها"

    def save(self, *args, **kwargs):
        # قانون: در هر فایل فقط یک عکس می‌تواند اصلی باشد.
        if self.is_primary:
            ImageAsset.objects.filter(
                property=self.property,
                is_primary=True
            ).exclude(id=self.id).update(is_primary=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Image for {self.property.code} - Order: {self.sort_order}"

# ---------------------------------------------------------------------------
# جزئیات اختصاصیِ هر نوع معامله
# ---------------------------------------------------------------------------

class SaleDetail(models.Model):
    class PaymentTerms(models.TextChoices):
        CASH = "CASH", "نقد"
        INSTALLMENT = "INSTALLMENT", "اقساط"

    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="sale_detail")
    total_price = models.BigIntegerField("قیمت کل (تومان)")
    price_per_sqm = models.BigIntegerField("قیمت هر متر (تومان)", null=True, blank=True)
    payment_terms = models.CharField(max_length=15, choices=PaymentTerms.choices, default=PaymentTerms.CASH)
    down_payment = models.BigIntegerField("مبلغ پیش‌پرداخت", null=True, blank=True)
    is_exchangeable = models.BooleanField("قابل معاوضه", default=False)

    class Meta:
        verbose_name = "جزئیات فروش"
        verbose_name_plural = "جزئیات فروش"


class PresaleDetail(models.Model):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="presale_detail")
    total_contract_price = models.BigIntegerField("قیمت کل قرارداد (تومان)")
    builder_company = models.CharField("شرکت/سازنده", max_length=200, blank=True)
    progress_percent = models.PositiveSmallIntegerField("درصد پیشرفت پروژه", null=True, blank=True)
    estimated_delivery_date = models.DateField("تاریخ تحویل تخمینی", null=True, blank=True)
    amount_paid = models.BigIntegerField("مبلغ پرداخت‌شده تاکنون", null=True, blank=True)
    amount_remaining = models.BigIntegerField("مبلغ باقی‌مانده", null=True, blank=True)
    installment_terms = models.CharField("شرایط اقساط باقی‌مانده", max_length=255, blank=True)
    contract_number = models.CharField("شماره قرارداد پیش‌فروش", max_length=100, blank=True)

    class Meta:
        verbose_name = "جزئیات پیش‌خرید"
        verbose_name_plural = "جزئیات پیش‌خرید"


class ContractMixin(models.Model):
    """فیلدهای مشترک اجاره و رهن‌کامل (تاریخ قرارداد، مستاجر، وضعیت تمدید)."""

    class RenewalStatus(models.TextChoices):
        NOT_CHECKED = "NOT_CHECKED", "بررسی نشده"
        WANTS_RENEWAL = "WANTS_RENEWAL", "تمایل به تمدید"
        WANTS_TO_LEAVE = "WANTS_TO_LEAVE", "تمایل به تخلیه"
        UNCLEAR = "UNCLEAR", "نامشخص / تماس مجدد لازم است"
        RENEWED = "RENEWED", "تمدید نهایی شد"

    contract_start_date = models.DateField("تاریخ شروع قرارداد")
    contract_end_date = models.DateField("تاریخ پایان قرارداد")
    current_tenant_name = models.CharField("نام مستاجر فعلی", max_length=150, blank=True)
    current_tenant_phone = models.CharField("شماره تماس مستاجر فعلی", max_length=20, blank=True)
    renewal_status = models.CharField(max_length=20, choices=RenewalStatus.choices, default=RenewalStatus.NOT_CHECKED)
    last_contact_result = models.CharField("نتیجه آخرین تماس", max_length=255, blank=True)
    next_contact_date = models.DateField("تاریخ تماس بعدی", null=True, blank=True)

    class Meta:
        abstract = True

    @property
    def days_until_contract_end(self) -> int:
        return (self.contract_end_date - date.today()).days


class RentDetail(ContractMixin):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="rent_detail")
    deposit_amount = models.BigIntegerField("مبلغ ودیعه/رهن (تومان)")
    monthly_rent = models.BigIntegerField("مبلغ اجاره ماهانه (تومان)")
    convertible_to_mortgage = models.BooleanField("قابل تبدیل رهن/اجاره", default=False)
    yearly_increase_percent = models.PositiveSmallIntegerField("درصد افزایش سالانه پیشنهادی", null=True, blank=True)

    class Meta:
        verbose_name = "جزئیات اجاره"
        verbose_name_plural = "جزئیات اجاره"


class MortgageDetail(ContractMixin):
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name="mortgage_detail")
    deposit_amount = models.BigIntegerField("مبلغ رهن کامل (تومان)")

    class Meta:
        verbose_name = "جزئیات رهن کامل"
        verbose_name_plural = "جزئیات رهن کامل"




