from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/admin-panel/', include('admin_panel.urls')),
    path('api/receptionist/', include('receptionist.urls')),
    path('api/doctor/', include('doctor.urls')),
    path("api/pharmacist/", include("pharmacist.urls")),
    path("api/labtech/", include("labtech.urls")),


    # SimpleJWT Endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path("api/labtech/", include("labtech.urls")),
    path("api/pharmacist/", include("pharmacist.urls")),
]