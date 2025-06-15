from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views
from .views import AvatarRetrieveUpdateDestroyAPIView, CustomUserViewSet

router = DefaultRouter()
router.register('', CustomUserViewSet, basename='users')

urlpatterns = [
    path('api/users/me/', views.CurrentUserView.as_view(), name='current-user'),
    path('api/users/', include(router.urls)),
    path('api/auth/', include('djoser.urls.authtoken')),
    path('api/users/me/avatar/', AvatarRetrieveUpdateDestroyAPIView.as_view(), name='user-avatar'),
]
