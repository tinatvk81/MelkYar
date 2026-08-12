"""
Fixture های مشترک برای همه‌ی تست‌ها.

نکته: از pytest-django استفاده می‌کنیم، پس دیتابیس تست به‌صورت خودکار
ساخته و بعد از هر تست پاک می‌شود — هیچ داده‌ای وارد دیتابیس واقعی نمی‌شود.
"""
from datetime import date, timedelta

import pytest
from rest_framework.test import APIClient

from accounts.models import User
from properties.models import Property, RentDetail, SaleDetail


@pytest.fixture
def admin_user(db):
    return User.objects.create_superuser(
        username="admin_test", password="StrongPass123!", role=User.Role.ADMIN
    )


@pytest.fixture
def agent1(db):
    return User.objects.create_user(
        username="agent1_test", password="StrongPass123!", role=User.Role.AGENT
    )


@pytest.fixture
def agent2(db):
    return User.objects.create_user(
        username="agent2_test", password="StrongPass123!", role=User.Role.AGENT
    )


def _make_client(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.fixture
def admin_client(admin_user):
    return _make_client(admin_user)


@pytest.fixture
def agent1_client(agent1):
    return _make_client(agent1)


@pytest.fixture
def agent2_client(agent2):
    return _make_client(agent2)


@pytest.fixture
def agent1_sale_listing(agent1):
    """یک فایل فروش متعلق به agent1."""
    prop = Property.objects.create(
        owner_agent=agent1,
        code="TEST-S-1",
        title="فایل تست فروش agent1",
        transaction_type=Property.TransactionType.SALE,
        property_kind=Property.PropertyKind.APARTMENT,
        province="تهران", city="تهران",
    )
    SaleDetail.objects.create(property=prop, total_price=1000000000)
    return prop


@pytest.fixture
def agent2_rent_listing(agent2):
    """یک فایل اجاره متعلق به agent2، با قرارداد نزدیک به پایان (برای تست ماژول تمدید)."""
    prop = Property.objects.create(
        owner_agent=agent2,
        code="TEST-R-1",
        title="فایل تست اجاره agent2",
        transaction_type=Property.TransactionType.RENT,
        property_kind=Property.PropertyKind.APARTMENT,
        province="تهران", city="تهران",
    )
    RentDetail.objects.create(
        property=prop,
        deposit_amount=100000000,
        monthly_rent=10000000,
        contract_start_date=date.today() - timedelta(days=335),
        contract_end_date=date.today() + timedelta(days=10),
        current_tenant_name="مستاجر تست",
        current_tenant_phone="0912xxxxxxx",
    )
    return prop
