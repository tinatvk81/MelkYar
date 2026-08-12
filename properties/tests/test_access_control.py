"""
تست‌های «قلب امنیتی» پروژه: مشاور فقط فایل خودش را می‌بیند/ویرایش می‌کند،
مدیر همه را می‌بیند. اگر این تست‌ها بعد از یک تغییر قرمز شدند، یعنی
کنترل دسترسی خراب شده — قبل از commit کردن آن تغییر حتماً بررسی کنید.
"""
import pytest

pytestmark = pytest.mark.django_db


class TestListingVisibility:
    def test_agent_sees_only_own_listing(self, agent1_client, agent1_sale_listing, agent2_rent_listing):
        resp = agent1_client.get("/api/properties/listings/")
        assert resp.status_code == 200
        codes = [item["code"] for item in resp.data["results"]]
        assert "TEST-S-1" in codes
        assert "TEST-R-1" not in codes

    def test_agent_cannot_see_other_agents_listing_by_direct_id(
        self, agent1_client, agent2_rent_listing
    ):
        resp = agent1_client.get(f"/api/properties/listings/{agent2_rent_listing.id}/")
        assert resp.status_code == 404

    def test_admin_sees_all_listings(self, admin_client, agent1_sale_listing, agent2_rent_listing):
        resp = admin_client.get("/api/properties/listings/")
        assert resp.status_code == 200
        codes = [item["code"] for item in resp.data["results"]]
        assert "TEST-S-1" in codes
        assert "TEST-R-1" in codes

    def test_agent_cannot_edit_other_agents_listing(self, agent1_client, agent2_rent_listing):
        resp = agent1_client.patch(
            f"/api/properties/listings/{agent2_rent_listing.id}/",
            {"title": "تلاش برای دستکاری فایل دیگری"},
            format="json",
        )
        assert resp.status_code == 404

    def test_agent_cannot_delete_other_agents_listing(self, agent1_client, agent2_rent_listing):
        resp = agent1_client.delete(f"/api/properties/listings/{agent2_rent_listing.id}/")
        assert resp.status_code == 404
        agent2_rent_listing.refresh_from_db()


class TestAgentAccountManagement:
    def test_only_admin_can_create_agent(self, agent1_client):
        resp = agent1_client.post(
            "/api/accounts/agents/",
            {"username": "sneaky_agent", "password": "StrongPass123!"},
            format="json",
        )
        assert resp.status_code == 403

    def test_admin_can_create_agent(self, admin_client):
        resp = admin_client.post(
            "/api/accounts/agents/",
            {"username": "new_agent_test", "password": "StrongPass123!"},
            format="json",
        )
        assert resp.status_code == 201
        assert resp.data["role"] == "AGENT"

    def test_deactivated_agent_cannot_login(self, agent1, admin_client):
        from rest_framework.test import APIClient

        agent1.is_active = False
        agent1.save()

        anon_client = APIClient()
        resp = anon_client.post(
            "/api/auth/login/",
            {"username": agent1.username, "password": "StrongPass123!"},
            format="json",
        )
        assert resp.status_code == 401


class TestRenewalTrackingModule:
    def test_renewal_list_only_shows_contracts_ending_soon(
        self, agent2_client, agent2_rent_listing, agent1_sale_listing
    ):
        resp = agent2_client.get("/api/properties/renewals/")
        assert resp.status_code == 200
        codes = [item["code"] for item in resp.data["results"]]
        assert "TEST-R-1" in codes
        assert "TEST-S-1" not in codes

    def test_log_contact_sets_renewal_priority_flag(self, agent2_client, agent2_rent_listing):
        resp = agent2_client.post(
            f"/api/properties/renewals/{agent2_rent_listing.id}/log-contact/",
            {"renewal_status": "WANTS_RENEWAL", "last_contact_result": "تمایل به تمدید دارد"},
            format="json",
        )
        assert resp.status_code == 200
        agent2_rent_listing.refresh_from_db()
        assert agent2_rent_listing.renewal_priority_flag is True
        assert agent2_rent_listing.rent_detail.renewal_status == "WANTS_RENEWAL"
