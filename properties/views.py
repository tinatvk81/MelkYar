from datetime import date, timedelta

from django.db.models import Q
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import ActivityLog
from accounts.permissions import IsAdminRole

from .filters import PropertyFilter
from .models import MortgageDetail, Property, RentDetail
from .serializers import PropertySerializer, RenewalContactResultSerializer
from .services.excel_import import import_excel_file

RENEWAL_WINDOW_DAYS = 30


class PropertyViewSet(viewsets.ModelViewSet):
    """
    CRUD کامل فایل‌های ملکی.

    قانون دسترسی (هسته‌ی اصلی امنیت پروژه):
      - مدیر همه‌ی رکوردها را می‌بیند.
      - مشاور فقط رکوردهایی را می‌بیند که owner_agent آن‌ها خودش است —
        این فیلتر در get_queryset اعمال می‌شود، یعنی حتی در لیست هم
        فایل مشاور دیگر اصلاً برنمی‌گردد (نه اینکه فقط قفل باشد).
    """

    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]
    filterset_class = PropertyFilter
    search_fields = ["title", "code", "full_address", "owner_name"]
    ordering_fields = ["created_at", "updated_at", "area_sqm"]

    def get_queryset(self):
        qs = Property.objects.select_related(
            "sale_detail", "presale_detail", "rent_detail", "mortgage_detail", "owner_agent"
        )
        user = self.request.user
        if user.is_admin_role:
            return qs
        return qs.filter(owner_agent=user)

    def perform_create(self, serializer):
        instance = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action=ActivityLog.Action.CREATE,
            target_repr=f"ثبت فایل: {instance.code} - {instance.title}",
            target_id=instance.id,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action=ActivityLog.Action.UPDATE,
            target_repr=f"ویرایش فایل: {instance.code} - {instance.title}",
            target_id=instance.id,
        )

    def perform_destroy(self, instance):
        ActivityLog.objects.create(
            user=self.request.user,
            action=ActivityLog.Action.DELETE,
            target_repr=f"حذف فایل: {instance.code} - {instance.title}",
            target_id=instance.id,
        )
        instance.delete()


class RenewalTrackingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ماژول «قراردادهای رو‌به‌اتمام»: فایل‌های اجاره/رهن که کمتر از
    RENEWAL_WINDOW_DAYS روز تا پایان قراردادشان مانده.
    """

    serializer_class = PropertySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cutoff = date.today() + timedelta(days=RENEWAL_WINDOW_DAYS)
        qs = Property.objects.filter(
            transaction_type__in=[Property.TransactionType.RENT, Property.TransactionType.MORTGAGE],
            status=Property.FileStatus.ACTIVE,
        ).filter(
            Q(rent_detail__contract_end_date__lte=cutoff) | Q(mortgage_detail__contract_end_date__lte=cutoff)
        ).select_related("rent_detail", "mortgage_detail", "owner_agent")

        user = self.request.user
        if not user.is_admin_role:
            qs = qs.filter(owner_agent=user)
        return qs.order_by("rent_detail__contract_end_date", "mortgage_detail__contract_end_date")

    @action(detail=True, methods=["post"], url_path="log-contact")
    def log_contact(self, request, pk=None):
        """ثبت نتیجه‌ی تماس با مستاجر فعلی (تمدید/تخلیه/نامشخص)."""
        property_obj = self.get_object()
        serializer = RenewalContactResultSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        detail = getattr(property_obj, "rent_detail", None) or getattr(property_obj, "mortgage_detail", None)
        if detail is None:
            return Response({"detail": "این فایل، فایل اجاره یا رهن نیست."}, status=status.HTTP_400_BAD_REQUEST)

        detail.renewal_status = data["renewal_status"]
        detail.last_contact_result = data.get("last_contact_result", detail.last_contact_result)
        detail.next_contact_date = data.get("next_contact_date", detail.next_contact_date)
        detail.save()

        # اگر مستاجر تمایل به تمدید داشت، فلگ اولویت یک‌ماهه فعال می‌شود تا
        # در جستجوی عمومی برای مشتری بعدی با نشان ویژه دیده شود.
        property_obj.renewal_priority_flag = data["renewal_status"] in ("WANTS_RENEWAL", "WANTS_TO_LEAVE")
        property_obj.save(update_fields=["renewal_priority_flag"])

        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.Action.RENEWAL_CONTACT,
            target_repr=f"نتیجه تماس تمدید: {property_obj.code}",
            target_id=property_obj.id,
            detail=data.get("last_contact_result", ""),
        )
        return Response(PropertySerializer(property_obj, context={"request": request}).data)


class ExcelImportView(APIView):
    """
    Endpoint آپلود اکسل (طبق قالب ۴ شیتی که ساختیم). فقط مدیر مجاز است.

    نکته‌ی مهم: قبل از Import، همه‌ی مشاورانی که در ستون «نام مشاور
    ثبت‌کننده» اکسل هستند باید از پنل مدیریت کاربران ساخته شده باشند،
    وگرنه آن سطرها با خطا رد می‌شوند (در گزارش خروجی مشخص است چرا).
    """

    permission_classes = [IsAdminRole]

    def post(self, request):
        file_obj = request.FILES.get("file")
        if not file_obj:
            return Response({"detail": "فایل اکسل ارسال نشده."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            report = import_excel_file(file_obj)
        except Exception as exc:
            return Response(
                {"detail": f"خواندن فایل اکسل با خطا مواجه شد: {exc}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ActivityLog.objects.create(
            user=request.user,
            action=ActivityLog.Action.CREATE,
            target_repr=f"Import اکسل: {file_obj.name}",
            detail=f"ایجادشده: {report['created']} | ردشده: {report['skipped']}",
        )
        return Response(report, status=status.HTTP_200_OK)
