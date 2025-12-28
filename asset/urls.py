from rest_framework.routers import DefaultRouter

from asset.views import AssetViewSet, UploadViewSet

router = DefaultRouter()
router.register('upload', UploadViewSet, basename='upload')
router.register('', AssetViewSet, basename='asset')

urlpatterns = router.urls
