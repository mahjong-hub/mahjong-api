import modal
from pathlib import Path

from .app import app
from .utils import validate_tile_code

volume = modal.Volume.from_name('mahjong-model-weights-vol')

MODEL_DIR = '/models'


@app.function(
    gpu='T4',
    timeout=60,
    volumes={MODEL_DIR: volume},
)
def detect_tiles(model_version: str, image_url: str) -> dict:
    """Detect mahjong tiles in an image using a YOLO model."""
    from ultralytics import YOLO

    model_path = Path(MODEL_DIR) / model_version / 'model.pt'
    model = YOLO(model_path)
    results = model(image_url)

    detections = []
    inference_time_ms = 0.0

    for result in results:
        inference_time_ms = result.speed.get('inference', 0.0)

        for box in result.boxes:
            cls_id = int(box.cls.cpu().numpy().item())
            label = model.names[cls_id]
            tile_code = validate_tile_code(label)
            if tile_code is None:
                continue

            confidence = float(box.conf.cpu().numpy().item())
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().tolist()

            detections.append(
                {
                    'tile_code': tile_code,
                    'confidence': confidence,
                    'x1': x1,
                    'y1': y1,
                    'x2': x2,
                    'y2': y2,
                },
            )

    return {
        'detections': detections,
        'model_version': model_version,
        'inference_time_ms': inference_time_ms,
    }
