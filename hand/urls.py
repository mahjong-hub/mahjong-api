from rest_framework.routers import DefaultRouter

from hand.views import DetectionViewSet

router = DefaultRouter()
router.register('detect', DetectionViewSet, basename='detect')

urlpatterns = router.urls
