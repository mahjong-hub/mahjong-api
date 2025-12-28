from rest_framework.routers import DefaultRouter

from hand.views import HandDetectionViewSet, HandCorrectionViewSet

router = DefaultRouter()
router.register('detection', HandDetectionViewSet, basename='detection')
router.register('correction', HandCorrectionViewSet, basename='correction')

urlpatterns = router.urls
