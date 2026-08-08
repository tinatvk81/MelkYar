from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    ورود با یوزرنیم/رمز. علاوه بر توکن، نقش و اطلاعات پایه‌ی کاربر را هم
    برمی‌گرداند تا فرانت‌اند بداند پنل مدیر نشان بدهد یا پنل مشاور.

    نکته‌ی امنیتی: SimpleJWT به‌صورت پیش‌فرض چک می‌کند is_active=True باشد
    (django's ModelBackend این را انجام می‌دهد) پس مشاور غیرفعال‌شده اصلاً
    نمی‌تواند توکن جدید بگیرد؛ این لایه‌ی دومِ دفاعی، مستقل از باطل‌کردن
    توکن‌های قدیمی در AgentViewSet است.
    """

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.get_full_name() or user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        data["role"] = self.user.role
        data["full_name"] = self.user.get_full_name() or self.user.username
        data["user_id"] = self.user.id
        return data


class AgentSerializer(serializers.ModelSerializer):
    """سریالایزر مدیریت مشاوران — فقط مدیر به این دسترسی دارد."""

    password = serializers.CharField(write_only=True, required=False, validators=[validate_password])

    class Meta:
        model = User
        fields = [
            "id", "username", "first_name", "last_name", "phone_number",
            "role", "is_active", "admin_note", "date_joined", "password",
        ]
        read_only_fields = ["date_joined"]

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        # اکانت‌های ساخته‌شده از این مسیر همیشه نقش مشاور دارند
        validated_data["role"] = User.Role.AGENT
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            # اگر مدیر رمز نداد، یک رمز موقت تصادفی ست می‌شود (باید بعداً عوض شود)
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
