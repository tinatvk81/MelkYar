from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.db.models import Q

from properties.models import Property

RENEWAL_WINDOW_DAYS = 30


class Command(BaseCommand):
    """
    اجرای روزانه (با Cron یا Celery beat) برای پیدا کردن قراردادهای
    اجاره/رهنی که کمتر از ۳۰ روز تا پایانشان مانده.

    نمونه‌ی cron (هر روز ساعت ۸ صبح):
        0 8 * * * cd /path/to/project && python manage.py check_renewals

    در فاز ۲ می‌توان اینجا ارسال پیامک/ایمیل به مشاور مربوطه را هم اضافه کرد.
    """

    help = "قراردادهای اجاره/رهن نزدیک به پایان را پیدا و اعلام می‌کند."

    def handle(self, *args, **options):
        cutoff = date.today() + timedelta(days=RENEWAL_WINDOW_DAYS)
        qs = Property.objects.filter(
            transaction_type__in=[Property.TransactionType.RENT, Property.TransactionType.MORTGAGE],
            status=Property.FileStatus.ACTIVE,
        ).filter(
            Q(rent_detail__contract_end_date__lte=cutoff) | Q(mortgage_detail__contract_end_date__lte=cutoff)
        ).select_related("rent_detail", "mortgage_detail", "owner_agent")

        if not qs.exists():
            self.stdout.write(self.style.SUCCESS("هیچ قرارداد رو‌به‌اتمامی پیدا نشد."))
            return

        self.stdout.write(self.style.WARNING(f"{qs.count()} فایل نیازمند پیگیری تمدید:"))
        for prop in qs:
            detail = getattr(prop, "rent_detail", None) or getattr(prop, "mortgage_detail", None)
            days_left = detail.days_until_contract_end if detail else "?"
            self.stdout.write(
                f"  - [{prop.code}] {prop.title} | مشاور: {prop.owner_agent} | "
                f"{days_left} روز مانده | مستاجر: {detail.current_tenant_name} - {detail.current_tenant_phone}"
            )
            # TODO(فاز ۳): ارسال پیامک/نوتیفیکیشن به prop.owner_agent اینجا اضافه شود.
