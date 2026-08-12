import pytest

pytestmark = pytest.mark.django_db

class TestPropertyFeatures:

    def test_search_by_code(self, agent1_client, agent1_sale_listing):
        # جستجو بر اساس کد فایل
        resp = agent1_client.get("/api/properties/listings/", {"search": "TEST-S-1"})
        assert resp.status_code == 200
        # بررسی اینکه حداقل یک نتیجه دارد و کد آن درست است
        results = resp.data.get("results", resp.data)
        assert any(item["code"] == "TEST-S-1" for item in results)

    def test_filter_by_city(self, agent1_client, agent1_sale_listing):
        # فیلتر بر اساس شهر
        resp = agent1_client.get("/api/properties/listings/", {"city": agent1_sale_listing.city})
        assert resp.status_code == 200
        results = resp.data.get("results", resp.data)
        assert all(item["city"] == agent1_sale_listing.city for item in results)

    def test_ordering_by_area(self, agent1_client):
        # تست مرتب‌سازی
        resp = agent1_client.get("/api/properties/listings/", {"ordering": "area_sqm"})
        assert resp.status_code == 200

    def test_reject_transaction_type_change(self, agent1_client, agent1_sale_listing):
        # تلاش برای تغییر SALE به RENT باید با خطا مواجه شود
        payload = {
            "transaction_type": "RENT",
            "detail": {
                "deposit_amount": 1000,
                "monthly_rent": 500
            }
        }
        resp = agent1_client.patch(
            f"/api/properties/listings/{agent1_sale_listing.id}/",
            payload,
            format="json"
        )
        assert resp.status_code == 400
        assert "transaction_type" in resp.data
