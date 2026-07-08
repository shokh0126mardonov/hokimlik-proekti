from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView,
)

from .views import (
    UserCrudVievSet, 
    LoginView, 
    ImportOqsoqolView, 
    ApplicantViewSets
)

router = DefaultRouter()
router.register(r'applicants', ApplicantViewSets, basename='applicant')

urlpatterns = [
    path('', include(router.urls)),
    
    # Authentication (JWT) endpointlari
    path("auth/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    
    # Users (Foydalanuvchilar) CRUD endpointlari
    path("users/", UserCrudVievSet.as_view({"get": "list", "post": "create"})),
    path(
        "users/<int:pk>/",
        UserCrudVievSet.as_view(
            {"get": "retrieve", "patch": "partial_update", "delete": "destroy"}
        ),
    ),

    path('add-oqsoqol-json/', ImportOqsoqolView.as_view(), name='import_oqsoqol_json')
]