import django_filters as df

from .models import Property


class PropertyFilter(df.FilterSet):
    """
    فیلترهای صفحه‌ی «فهرست فایل‌ها» (جستجوی یکپارچه شبیه دیوار):
    نوع معامله، شهر/منطقه، بازه‌ی قیمت، بازه‌ی متراژ، تعداد اتاق،
    آسانسور، پارکینگ، نوع سند.

    بازه‌ی قیمت روی هر ۴ جدول جزئیات جدا تعریف شده (چون هرکدام ستون قیمت
    خودش را دارد: total_price / total_contract_price / deposit_amount+
    monthly_rent / deposit_amount) — این فیلتر خودش تشخیص می‌دهد کدام
    فیلد قیمت را بر اساس transaction_type چک کند.
    """

    price_min = df.NumberFilter(method="filter_price_min", label="حداقل قیمت (تومان)")
    price_max = df.NumberFilter(method="filter_price_max", label="حداکثر قیمت (تومان)")
    area_min = df.NumberFilter(field_name="area_sqm", lookup_expr="gte")
    area_max = df.NumberFilter(field_name="area_sqm", lookup_expr="lte")
    bedrooms_min = df.NumberFilter(field_name="bedrooms", lookup_expr="gte")

    class Meta:
        model = Property
        fields = [
            "transaction_type", "property_kind", "status", "city", "district",
            "has_elevator", "parking_count", "has_storage", "document_type",
            "is_exclusive",
        ]

    def _price_field(self, queryset_item_type):
        return {
            "SALE": "sale_detail__total_price",
            "PRESALE": "presale_detail__total_contract_price",
            "RENT": "rent_detail__deposit_amount",  # می‌توان بعداً بر اساس اجاره تبدیلی هم فیلتر زد
            "MORTGAGE": "mortgage_detail__deposit_amount",
        }

    def filter_price_min(self, queryset, name, value):
        return self._filter_price(queryset, gte=value)

    def filter_price_max(self, queryset, name, value):
        return self._filter_price(queryset, lte=value)

    def _filter_price(self, queryset, gte=None, lte=None):
        # فیلتر روی هر ۴ نوع معامله به‌صورت OR انجام می‌شود؛ اگر کاربر همزمان
        # transaction_type را هم انتخاب کرده باشد، درعمل فقط یک شاخه معتبر می‌ماند.
        from django.db.models import Q

        price_fields = self._price_field(None)
        q = Q()
        for field in price_fields.values():
            kwargs = {}
            if gte is not None:
                kwargs[f"{field}__gte"] = gte
            if lte is not None:
                kwargs[f"{field}__lte"] = lte
            q |= Q(**kwargs)
        return queryset.filter(q).distinct()
