from django.urls import path
from rest_framework.routers import DefaultRouter

from user.views import ClientViewSet

router = DefaultRouter()
router.register('client', ClientViewSet, basename='client')

urlpatterns = [
    path(
        'client/',
        ClientViewSet.as_view({'put': 'update'}),
        name='client-update',
    ),
] + router.urls
