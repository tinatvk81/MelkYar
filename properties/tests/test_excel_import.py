"""
تست‌های سرویس Import اکسل (properties/services/excel_import.py).
"""
import io
from datetime import date

import openpyxl
import pytest

from properties.models import Property
from properties.services.excel_import import import_excel_file

pytestmark = pytest.mark.django_db

BASE_HEADERS = [
    "کد ملک", "عنوان آگهی", "نوع ملک", "استان", "شهر", "منطقه/محله",
    "آدرس کامل", "لینک موقعیت (نقشه)", "متراژ زیربنا (متر)", "متراژ زمین (متر)",
    "تعداد اتاق خواب", "سال ساخت", "تعداد کل طبقات ساختمان", "طبقه واحد",
    "تعداد واحد در طبقه", "جهت ساختمان", "نوع سند", "آسانسور (بله/خیر)",
    "پارکینگ (تعداد)", "انباری (بله/خیر)", "بالکن (بله/خیر)",
    "امکانات رفاهی", "سیستم گرمایش", "سیستم سرمایش", "نوع کفپوش",
    "وضعیت بازسازی (بله/خیر)", "وضعیت واحد", "نام مالک", "شماره تماس مالک",
    "نوع فایل (انحصاری/غیرانحصاری)", "نام مشاور ثبت‌کننده", "تاریخ ثبت فایل",
    "تاریخ آخرین بروزرسانی", "وضعیت فایل", "توضیحات عمومی (نمایش به مشتری)",
    "یادداشت خصوصی مشاور", "پوشه/لینک تصاویر",
]
SALE_COLUMNS = ["قیمت کل (تومان)", "قیمت هر متر (تومان)", "شرایط پرداخت (نقد/اقساط)",
                "مبلغ پیش‌پرداخت", "قابل معاوضه (بله/خیر)"]


def _blank_base_row(**overrides):
    row = {h: "" for h in BASE_HEADERS}
    row.update(overrides)
    return [row[h] for h in BASE_HEADERS]


def _build_workbook(sheet_name, headers, rows):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = sheet_name
    ws.append(headers)
    for row in rows:
        ws.append(row)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf

class TestJalaliDateImport:
    def test_jalali_date_with_english_digits_is_converted(self):
        from properties.services.excel_import import _to_date

        result = _to_date("1404/01/01", "تاریخ پایان قرارداد", required=True)

        # 1404/01/01 برابر با 2025/03/21 میلادی است
        assert result == date(2025, 3, 21)

    def test_jalali_date_with_persian_digits_is_converted(self):
        from properties.services.excel_import import _to_date

        result = _to_date("۱۴۰۴/۰۱/۰۱", "تاریخ پایان قرارداد", required=True)

        assert result == date(2025, 3, 21)

    def test_invalid_jalali_date_returns_row_error(self):
        from properties.services.excel_import import RowError, _to_date

        with pytest.raises(RowError):
            _to_date("1404/13/40", "تاریخ پایان قرارداد", required=True)


class TestExcelImportSale:
    def test_valid_row_creates_property_and_detail(self, agent1):
        row = _blank_base_row(
            **{
                "کد ملک": "IMP-1",
                "عنوان آگهی": "تست ایمپورت",
                "نوع ملک": "آپارتمان مسکونی",
                "استان": "تهران", "شهر": "تهران",
                "آسانسور (بله/خیر)": "بله",
                "انباری (بله/خیر)": "خیر",
                "بالکن (بله/خیر)": "خیر",
                "وضعیت بازسازی (بله/خیر)": "خیر",
                "نوع فایل (انحصاری/غیرانحصاری)": "انحصاری",
                "نام مشاور ثبت‌کننده": agent1.username,
            }
        ) + [5000000000, 50000000, "نقد", "", "خیر"]

        f = _build_workbook("فروش", BASE_HEADERS + SALE_COLUMNS, [row])
        report = import_excel_file(f)

        assert report["created"] == 1
        assert report["skipped"] == 0
        prop = Property.objects.get(code="IMP-1")
        assert prop.owner_agent == agent1
        assert prop.sale_detail.total_price == 5000000000

    def test_missing_agent_is_reported_as_error_not_exception(self):
        row = _blank_base_row(
            **{
                "کد ملک": "IMP-2",
                "نوع ملک": "آپارتمان مسکونی",
                "نام مشاور ثبت‌کننده": "کسی-که-وجود-ندارد",
            }
        ) + [1000000000, "", "نقد", "", "خیر"]

        f = _build_workbook("فروش", BASE_HEADERS + SALE_COLUMNS, [row])
        report = import_excel_file(f)

        assert report["created"] == 0
        assert report["skipped"] == 1
        assert "پیدا نشد" in report["errors"][0]["message"]

    def test_duplicate_code_is_rejected(self, agent1):
        common = {
            "نوع ملک": "آپارتمان مسکونی",
            "استان": "تهران", "شهر": "تهران",
            "نوع فایل (انحصاری/غیرانحصاری)": "انحصاری",
            "نام مشاور ثبت‌کننده": agent1.username,
        }
        row1 = _blank_base_row(**{**common, "کد ملک": "IMP-DUP"}) + [1000000000, "", "نقد", "", "خیر"]
        row2 = _blank_base_row(**{**common, "کد ملک": "IMP-DUP"}) + [2000000000, "", "نقد", "", "خیر"]

        f = _build_workbook("فروش", BASE_HEADERS + SALE_COLUMNS, [row1, row2])
        report = import_excel_file(f)

        assert report["created"] == 1
        assert report["skipped"] == 1
        assert "تکراری" in report["errors"][0]["message"]

    def test_invalid_row_does_not_block_valid_rows_after_it(self, agent1):
        bad_row = _blank_base_row(
            **{"کد ملک": "", "نام مشاور ثبت‌کننده": agent1.username}
        ) + [1000000000, "", "نقد", "", "خیر"]
        good_row = _blank_base_row(
            **{
                "کد ملک": "IMP-3", "نوع ملک": "آپارتمان مسکونی",
                "استان": "تهران", "شهر": "تهران",
                "نوع فایل (انحصاری/غیرانحصاری)": "انحصاری",
                "نام مشاور ثبت‌کننده": agent1.username,
            }
        ) + [3000000000, "", "نقد", "", "خیر"]

        f = _build_workbook("فروش", BASE_HEADERS + SALE_COLUMNS, [bad_row, good_row])
        report = import_excel_file(f)

        assert report["created"] == 1
        assert report["skipped"] == 1
        assert Property.objects.filter(code="IMP-3").exists()
