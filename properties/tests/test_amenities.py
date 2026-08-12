import pytest

from properties.models import Amenity


pytestmark = pytest.mark.django_db


class TestAmenityApi:
    def test_authenticated_agent_can_list_amenities(self, agent1_client):
        Amenity.objects.create(name="آسانسور")
        Amenity.objects.create(name="پارکینگ")

        response = agent1_client.get("/api/properties/amenities/")

        assert response.status_code == 200

        # چون Pagination در settings فعال است، نتیجه‌ها داخل results هستند.
        amenities = response.data["results"]

        assert len(amenities) == 2
        returned_names = {item["name"] for item in amenities}
        assert returned_names == {"آسانسور", "پارکینگ"}

    def test_admin_can_create_amenity(self, admin_client):
        response = admin_client.post(
            "/api/properties/amenities/",
            {"name": "استخر"},
            format="json",
        )

        assert response.status_code == 201
        assert response.data["name"] == "استخر"
        assert Amenity.objects.filter(name="استخر").exists()

    def test_agent_cannot_create_amenity(self, agent1_client):
        response = agent1_client.post(
            "/api/properties/amenities/",
            {"name": "سونا"},
            format="json",
        )

        assert response.status_code == 403
        assert not Amenity.objects.filter(name="سونا").exists()

    def test_duplicate_amenity_name_is_rejected(self, admin_client):
        Amenity.objects.create(name="پارکینگ")

        response = admin_client.post(
            "/api/properties/amenities/",
            {"name": "پارکینگ"},
            format="json",
        )

        assert response.status_code == 400
        assert "name" in response.data


class TestPropertyAmenities:
    def test_agent_can_set_amenities_on_own_property(
        self,
        agent1_client,
        agent1_sale_listing,
    ):
        elevator = Amenity.objects.create(name="آسانسور")
        parking = Amenity.objects.create(name="پارکینگ")

        response = agent1_client.patch(
            f"/api/properties/listings/{agent1_sale_listing.id}/",
            {
                "amenity_ids": [elevator.id, parking.id],
            },
            format="json",
        )

        assert response.status_code == 200

        agent1_sale_listing.refresh_from_db()

        actual_ids = set(
            agent1_sale_listing.property_amenities.values_list("id", flat=True)
        )
        assert actual_ids == {elevator.id, parking.id}

    def test_property_response_contains_amenities(
        self,
        agent1_client,
        agent1_sale_listing,
    ):
        elevator = Amenity.objects.create(name="آسانسور")
        warehouse = Amenity.objects.create(name="انباری")

        agent1_sale_listing.property_amenities.set([elevator, warehouse])

        response = agent1_client.get(
            f"/api/properties/listings/{agent1_sale_listing.id}/"
        )

        assert response.status_code == 200
        assert "property_amenities" in response.data

        returned_names = {
            item["name"]
            for item in response.data["property_amenities"]
        }

        assert returned_names == {"آسانسور", "انباری"}

    def test_agent_cannot_update_other_agents_property_amenities(
        self,
        agent1_client,
        agent2_rent_listing,
    ):
        elevator = Amenity.objects.create(name="آسانسور")

        response = agent1_client.patch(
            f"/api/properties/listings/{agent2_rent_listing.id}/",
            {
                "amenity_ids": [elevator.id],
            },
            format="json",
        )

        # در PropertyViewSet برای ملکِ مشاور دیگر، queryset آن را برنمی‌گرداند.
        assert response.status_code == 404

        agent2_rent_listing.refresh_from_db()
        assert agent2_rent_listing.property_amenities.count() == 0
