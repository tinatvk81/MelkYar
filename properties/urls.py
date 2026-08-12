from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import (
    AmenityViewSet,
    ExcelImportView,
    PropertyViewSet,
    RenewalTrackingViewSet,
)

router = DefaultRouter()
router.register("listings", PropertyViewSet, basename="property")
router.register("amenities", AmenityViewSet, basename="amenity")
router.register("renewals", RenewalTrackingViewSet, basename="renewal")

urlpatterns = [
    path("import-excel/", ExcelImportView.as_view(), name="import-excel"),
]

urlpatterns += router.urls
