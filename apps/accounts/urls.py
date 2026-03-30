from django.urls import path

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
    TokenBlacklistView
)

from .views import UserCrudVievSet,LoginView
urlpatterns = [

    path('auth/login/', LoginView.as_view(), name='token_obtain_pair'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('token/blacklist/', TokenBlacklistView.as_view(), name='token_blacklist'),


    path("users/",UserCrudVievSet.as_view({"get":"list","post":"create"})),
    path("users/<int:pk>/",UserCrudVievSet.as_view({"get":"retrieve","patch":"partial_update","delete":"destroy"})),

    path("adduser/",UserCrudVievSet.as_view({"get":"me"}))
]