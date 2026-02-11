# from unittest.mock import patch

# from django.test import TestCase, override_settings

# from asset.constants import AssetRole, UploadStatus
# from asset.factories import AssetFactory, UploadSessionFactory
# from asset.models import AssetRef
# from hand.constants import DetectionStatus
# from hand.models import Hand, HandDetection
# from hand.services.hand_detection import (
#     create_detection,
#     find_existing_detection,
# )


# @override_settings(
#     TILE_DETECTOR_MODEL_NAME='tile_detector',
#     TILE_DETECTOR_MODEL_VERSION='v0.1.0',
# )
# class TestFindExistingDetection(TestCase):
#     def test_returns_none_when_no_asset_ref(self):
#         session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
#         asset = AssetFactory(upload_session=session, is_active=True)

#         result = find_existing_detection(asset)

#         self.assertIsNone(result)

#     def test_returns_none_when_no_detection(self):
#         session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
#         asset = AssetFactory(upload_session=session, is_active=True)
#         hand = Hand.objects.create(client=session.client, source='camera')
#         AssetRef.attach(
#             asset=asset,
#             owner=hand,
#             role=AssetRole.HAND_PHOTO.value,
#         )

#         result = find_existing_detection(asset)

#         self.assertIsNone(result)

#     def test_returns_existing_pending_detection(self):
#         session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
#         asset = AssetFactory(upload_session=session, is_active=True)
#         hand = Hand.objects.create(client=session.client, source='camera')
#         asset_ref = AssetRef.attach(
#             asset=asset,
#             owner=hand,
#             role=AssetRole.HAND_PHOTO.value,
#         )
#         detection = HandDetection.objects.create(
#             hand=hand,
#             asset_ref=asset_ref,
#             status=DetectionStatus.PENDING.value,
#             model_name='tile_detector',
#             model_version='v0.1.0',
#         )

#         result = find_existing_detection(asset)

#         self.assertEqual(result.id, detection.id)

#     def test_returns_existing_succeeded_detection(self):
#         session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
#         asset = AssetFactory(upload_session=session, is_active=True)
#         hand = Hand.objects.create(client=session.client, source='camera')
#         asset_ref = AssetRef.attach(
#             asset=asset,
#             owner=hand,
#             role=AssetRole.HAND_PHOTO.value,
#         )
#         detection = HandDetection.objects.create(
#             hand=hand,
#             asset_ref=asset_ref,
#             status=DetectionStatus.SUCCEEDED.value,
#             model_name='tile_detector',
#             model_version='v0.1.0',
#         )

#         result = find_existing_detection(asset)

#         self.assertEqual(result.id, detection.id)

#     def test_returns_none_when_detection_failed(self):
#         session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
#         asset = AssetFactory(upload_session=session, is_active=True)
#         hand = Hand.objects.create(client=session.client, source='camera')
#         asset_ref = AssetRef.attach(
#             asset=asset,
#             owner=hand,
#             role=AssetRole.HAND_PHOTO.value,
#         )
#         HandDetection.objects.create(
#             hand=hand,
#             asset_ref=asset_ref,
#             status=DetectionStatus.FAILED.value,
#             model_name='tile_detector',
#             model_version='v0.1.0',
#         )

#         result = find_existing_detection(asset)

#         self.assertIsNone(result)

#     def test_returns_none_when_different_model_version(self):
#         session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
#         asset = AssetFactory(upload_session=session, is_active=True)
#         hand = Hand.objects.create(client=session.client, source='camera')
#         asset_ref = AssetRef.attach(
#             asset=asset,
#             owner=hand,
#             role=AssetRole.HAND_PHOTO.value,
#         )
#         HandDetection.objects.create(
#             hand=hand,
#             asset_ref=asset_ref,
#             status=DetectionStatus.SUCCEEDED.value,
#             model_name='tile_detector',
#             model_version='v0.0.9',  # Different version
#         )

#         result = find_existing_detection(asset)

#         self.assertIsNone(result)


# @override_settings(
#     TILE_DETECTOR_MODEL_NAME='tile_detector',
#     TILE_DETECTOR_MODEL_VERSION='v0.1.0',
# )
# class TestCreateDetection(TestCase):
#     def test_creates_hand_asset_ref_detection(self):
#         session = UploadSessionFactory(status=UploadStatus.COMPLETED.value)
#         asset = AssetFactory(upload_session=session, is_active=True)

#         detection = create_detection(
#             asset=asset,
#             client=session.client,
#             source='camera',
#         )

#         self.assertIsNotNone(detection.id)
#         self.assertEqual(detection.status, DetectionStatus.PENDING.value)

#         # Verify Hand was created
#         hand = detection.hand
#         self.assertEqual(hand.client, session.client)
#         self.assertEqual(hand.source, 'camera')

#         # Verify AssetRef was created
#         asset_ref = detection.asset_ref
#         self.assertEqual(asset_ref.asset, asset)
#         self.assertEqual(asset_ref.owner_id, hand.id)
#         self.assertEqual(asset_ref.role, AssetRole.HAND_PHOTO.value)

#         # Verify HandDetection fields
#         self.assertEqual(detection.model_name, 'tile_detector')
#         self.assertEqual(detection.model_version, 'v0.1.0')
