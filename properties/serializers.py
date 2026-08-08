from rest_framework import serializers

from .models import (
    ImageAsset,
    MortgageDetail,
    PresaleDetail,
    Property,
    RentDetail,
    SaleDetail,
)


class ImageAssetSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageAsset
        fields = ["id", "image", "caption", "uploaded_at"]


class SaleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = SaleDetail
        exclude = ["property"]


class PresaleDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = PresaleDetail
        exclude = ["property"]


class RentDetailSerializer(serializers.ModelSerializer):
    days_until_contract_end = serializers.ReadOnlyField()

    class Meta:
        model = RentDetail
        exclude = ["property"]


class MortgageDetailSerializer(serializers.ModelSerializer):
    days_until_contract_end = serializers.ReadOnlyField()

    class Meta:
        model = MortgageDetail
        exclude = ["property"]


DETAIL_SERIALIZER_MAP = {
    Property.TransactionType.SALE: ("sale_detail", SaleDetailSerializer),
    Property.TransactionType.PRESALE: ("presale_detail", PresaleDetailSerializer),
    Property.TransactionType.RENT: ("rent_detail", RentDetailSerializer),
    Property.TransactionType.MORTGAGE: ("mortgage_detail", MortgageDetailSerializer),
}


class PropertySerializer(serializers.ModelSerializer):
    """
    سریالایزر اصلی فایل ملکی. فیلد `detail` بسته به `transaction_type`
    محتوای SaleDetail / PresaleDetail / RentDetail / MortgageDetail را
    می‌خواند و می‌نویسد — طوری که فرانت‌اند با یک endpoint واحد کار کند.
    """

    detail = serializers.DictField(write_only=True)
    detail_data = serializers.SerializerMethodField(read_only=True)
    owner_agent_name = serializers.CharField(source="owner_agent.get_full_name", read_only=True)
    images = ImageAssetSerializer(many=True, read_only=True)

    class Meta:
        model = Property
        fields = [
            "id", "code", "title", "transaction_type", "property_kind", "status",
            "province", "city", "district", "full_address", "map_link",
            "area_sqm", "land_area_sqm", "bedrooms", "build_year",
            "total_floors", "unit_floor", "units_per_floor", "direction",
            "document_type", "has_elevator", "parking_count", "has_storage",
            "has_balcony", "amenities", "heating_system", "cooling_system",
            "floor_covering", "is_renovated", "unit_condition",
            "owner_name", "owner_phone", "is_exclusive",
            "public_description", "private_note", "renewal_priority_flag",
            "owner_agent", "owner_agent_name", "images",
            "created_at", "updated_at",
            "detail", "detail_data",
        ]
        read_only_fields = ["owner_agent", "created_at", "updated_at", "renewal_priority_flag"]

    def get_detail_data(self, obj):
        rel_name, serializer_cls = DETAIL_SERIALIZER_MAP[obj.transaction_type]
        detail_obj = getattr(obj, rel_name, None)
        if detail_obj is None:
            return None
        return serializer_cls(detail_obj).data

    def validate(self, attrs):
        transaction_type = attrs.get("transaction_type") or getattr(self.instance, "transaction_type", None)
        if transaction_type not in DETAIL_SERIALIZER_MAP:
            raise serializers.ValidationError({"transaction_type": "نوع معامله نامعتبر است."})
        return attrs

    def create(self, validated_data):
        detail_payload = validated_data.pop("detail")
        request = self.context["request"]
        validated_data["owner_agent"] = request.user

        rel_name, serializer_cls = DETAIL_SERIALIZER_MAP[validated_data["transaction_type"]]
        detail_serializer = serializer_cls(data=detail_payload)
        detail_serializer.is_valid(raise_exception=True)

        property_obj = Property.objects.create(**validated_data)
        detail_serializer.save(property=property_obj)
        return property_obj

    def update(self, instance, validated_data):
        detail_payload = validated_data.pop("detail", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if detail_payload is not None:
            rel_name, serializer_cls = DETAIL_SERIALIZER_MAP[instance.transaction_type]
            detail_obj = getattr(instance, rel_name, None)
            detail_serializer = serializer_cls(instance=detail_obj, data=detail_payload, partial=True)
            detail_serializer.is_valid(raise_exception=True)
            detail_serializer.save(property=instance)
        return instance


class RenewalContactResultSerializer(serializers.Serializer):
    """برای ثبت نتیجه‌ی تماس در ماژول «قراردادهای رو‌به‌اتمام»."""

    renewal_status = serializers.ChoiceField(choices=[
        ("WANTS_RENEWAL", "تمایل به تمدید"),
        ("WANTS_TO_LEAVE", "تمایل به تخلیه"),
        ("UNCLEAR", "نامشخص / تماس مجدد لازم است"),
        ("RENEWED", "تمدید نهایی شد"),
    ])
    last_contact_result = serializers.CharField(required=False, allow_blank=True)
    next_contact_date = serializers.DateField(required=False, allow_null=True)
