import os

import modal
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, HttpUrl
from starlette.middleware.base import (
    BaseHTTPMiddleware,
    RequestResponseEndpoint,
)
from starlette.responses import Response

from .app import app
from .detect import detect_tiles
from .utils import SUPPORTED_MODEL_VERSIONS, validate_model_version

auth_secret = modal.Secret.from_name('mahjong-cv-auth')

web_app = FastAPI()


class BearerAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: RequestResponseEndpoint,
    ) -> Response:
        auth = request.headers.get('Authorization', '')
        if not auth.startswith('Bearer '):
            return JSONResponse(
                {'detail': 'Missing bearer token'},
                status_code=401,
                headers={'WWW-Authenticate': 'Bearer'},
            )
        token = auth.removeprefix('Bearer ')
        if token != os.environ['AUTH_TOKEN']:
            return JSONResponse(
                {'detail': 'Invalid bearer token'},
                status_code=401,
                headers={'WWW-Authenticate': 'Bearer'},
            )
        return await call_next(request)


web_app.add_middleware(BearerAuthMiddleware)


class DetectRequest(BaseModel):
    image_url: HttpUrl
    version: str


@web_app.post('/detect')
async def accept_detection(body: DetectRequest):
    """Accept a tile detection request and spawn async inference."""
    if not validate_model_version(body.version):
        return JSONResponse(
            {
                'error': 'Unsupported model version. '
                f'Supported: {SUPPORTED_MODEL_VERSIONS}',
            },
            status_code=400,
        )

    call = detect_tiles.spawn(body.version, str(body.image_url))
    return JSONResponse({'call_id': call.object_id})


@web_app.get('/results/{call_id}')
async def poll_results(call_id: str):
    """Poll for detection results. Returns 202 while still processing."""
    function_call = modal.FunctionCall.from_id(call_id)
    try:
        result = function_call.get(timeout=0)
    except TimeoutError:
        return JSONResponse({'status': 'pending'}, status_code=202)
    return JSONResponse(result)


@app.function(secrets=[auth_secret])
@modal.asgi_app()
def fastapi_app():
    return web_app
