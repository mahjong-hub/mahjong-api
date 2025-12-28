from rest_framework.routers import DefaultRouter

from user.views import ClientViewSet

router = DefaultRouter()
router.register('client', ClientViewSet, basename='client')

urlpatterns = router.urls
