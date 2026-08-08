from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .models import ActivityLog
from .permissions import IsAdminRole
from .serializers import AgentSerializer, MyTokenObtainPairSerializer

User = get_user_model()


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class AgentViewSet(viewsets.ModelViewSet):
    """
    مدیریت اکانت مشاوران — فقط برای مدیر.
    - ساخت مشاور جدید (مدیر یوزرنیم/رمز اولیه می‌دهد)
    - غیرفعال کردن مشاور هنگام خروج از مجموعه (is_active=False)
    - ریست رمز مشاور
    """

    serializer_class = AgentSerializer
    permission_classes = [IsAdminRole]

    def get_queryset(self):
        return User.objects.filter(role=User.Role.AGENT).order_by("-date_joined")

    def perform_create(self, serializer):
        agent = serializer.save()
        ActivityLog.objects.create(
            user=self.request.user,
            action=ActivityLog.Action.CREATE,
            target_repr=f"ساخت اکانت مشاور: {agent.username}",
        )

    def perform_update(self, serializer):
        was_active = self.get_object().is_active
        agent = serializer.save()

        # نکته‌ی امنیتی مهم: صرفِ is_active=False کافی نیست، چون توکن JWT
        # که مشاور از قبل دارد تا زمان انقضایش (تا ۲ ساعت طبق تنظیمات) هنوز
        # معتبر است. اینجا همه‌ی refresh tokenهای فعالش را هم باطل می‌کنیم
        # تا خروجش از سیستم فوری باشد.
        if was_active and not agent.is_active:
            for token in OutstandingToken.objects.filter(user=agent):
                try:
                    RefreshToken(token.token).blacklist()
                except Exception:
                    pass
            ActivityLog.objects.create(
                user=self.request.user,
                action=ActivityLog.Action.UPDATE,
                target_repr=f"غیرفعال‌سازی و باطل‌کردن توکن‌های مشاور: {agent.username}",
            )
        else:
            ActivityLog.objects.create(
                user=self.request.user,
                action=ActivityLog.Action.UPDATE,
                target_repr=f"ویرایش اکانت مشاور: {agent.username}",
            )
