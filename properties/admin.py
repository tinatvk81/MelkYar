from django.contrib import admin

from .models import (
    Amenity,
    ImageAsset,
    MortgageDetail,
    PresaleDetail,
    Property,
    RentDetail,
    SaleDetail,
)

@admin.register(Amenity)
class AmenityAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)
    ordering = ("name",)


class ImageInline(admin.TabularInline):
    model = ImageAsset
    extra = 1


class SaleDetailInline(admin.StackedInline):
    model = SaleDetail
    can_delete = False


class PresaleDetailInline(admin.StackedInline):
    model = PresaleDetail
    can_delete = False


class RentDetailInline(admin.StackedInline):
    model = RentDetail
    can_delete = False


class MortgageDetailInline(admin.StackedInline):
    model = MortgageDetail
    can_delete = False


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ("code", "title", "transaction_type", "city", "district", "status", "owner_agent")
    list_filter = ("transaction_type", "status", "city", "property_kind")
    search_fields = ("code", "title", "full_address", "owner_name")
    inlines = [SaleDetailInline, PresaleDetailInline, RentDetailInline, MortgageDetailInline, ImageInline]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser or getattr(request.user, "is_admin_role", False):
            return qs
        return qs.filter(owner_agent=request.user)
