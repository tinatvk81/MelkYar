from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    ExcelImportView,
    PropertyViewSet,
    RenewalTrackingViewSet,
)

router = DefaultRouter()
router.register("listings", PropertyViewSet, basename="property")
router.register("renewals", RenewalTrackingViewSet, basename="renewal")
router.register(r"amenities", AmenityViewSet, basename="amenity")

urlpatterns = [
    path("import-excel/", ExcelImportView.as_view(), name="import-excel"),
]

urlpatterns += router.urls
