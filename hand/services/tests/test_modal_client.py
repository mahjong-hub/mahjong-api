from unittest.mock import MagicMock, patch

from django.test import TestCase, override_settings

from hand.exceptions import ModalServiceError
from hand.services.modal_client import poll_detection_result, submit_detection


@override_settings(
    MODAL_CV_ENDPOINT='http://modal.test',
    MODAL_AUTH_TOKEN='test-token',
)
class TestSubmitDetection(TestCase):
    @patch('hand.services.modal_client._get_client')
    def test_returns_call_id(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.json.return_value = {'call_id': 'fc-abc123'}
        mock_response.raise_for_status.return_value = None

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = submit_detection(
            image_url='https://r2.example.com/image.jpg',
            model_version='v0',
        )

        self.assertEqual(result, 'fc-abc123')
        mock_client.post.assert_called_once_with(
            '/detect',
            json={
                'image_url': 'https://r2.example.com/image.jpg',
                'version': 'v0',
            },
        )

    @patch('hand.services.modal_client._get_client')
    def test_raises_modal_service_error_on_http_error(
        self,
        mock_get_client,
    ):
        import httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.post.side_effect = httpx.ConnectError('connection refused')
        mock_get_client.return_value = mock_client

        with self.assertRaises(ModalServiceError):
            submit_detection(
                image_url='https://r2.example.com/image.jpg',
                model_version='v0',
            )


@override_settings(
    MODAL_CV_ENDPOINT='http://modal.test',
    MODAL_AUTH_TOKEN='test-token',
)
class TestPollDetectionResult(TestCase):
    @patch('hand.services.modal_client._get_client')
    def test_returns_result_on_200(self, mock_get_client):
        result_data = {
            'detections': [
                {
                    'tile_code': '1B',
                    'x1': 10,
                    'y1': 20,
                    'x2': 110,
                    'y2': 120,
                    'confidence': 0.95,
                },
            ],
        }
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = result_data

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = poll_detection_result('fc-abc123')

        self.assertEqual(result, result_data)
        mock_client.get.assert_called_once_with('/results/fc-abc123')

    @patch('hand.services.modal_client._get_client')
    def test_returns_none_on_202(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.status_code = 202

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        result = poll_detection_result('fc-abc123')

        self.assertIsNone(result)

    @patch('hand.services.modal_client._get_client')
    def test_raises_modal_service_error_on_500(self, mock_get_client):
        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.text = 'Internal Server Error'

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.return_value = mock_response
        mock_get_client.return_value = mock_client

        with self.assertRaises(ModalServiceError):
            poll_detection_result('fc-abc123')

    @patch('hand.services.modal_client._get_client')
    def test_raises_modal_service_error_on_http_error(
        self,
        mock_get_client,
    ):
        import httpx

        mock_client = MagicMock()
        mock_client.__enter__ = MagicMock(return_value=mock_client)
        mock_client.__exit__ = MagicMock(return_value=False)
        mock_client.get.side_effect = httpx.ConnectError('connection refused')
        mock_get_client.return_value = mock_client

        with self.assertRaises(ModalServiceError):
            poll_detection_result('fc-abc123')
