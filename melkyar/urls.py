from django.contrib import admin
from django.urls import include, path
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import MyTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    # احراز هویت (ورود با یوزرنیم/رمز -> دریافت JWT)
    path("api/auth/login/", MyTokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/accounts/", include("accounts.urls")),
    path("api/properties/", include("properties.urls")),
]
