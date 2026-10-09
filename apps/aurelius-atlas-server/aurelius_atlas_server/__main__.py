"""Run the server: ``uv run python -m aurelius_atlas_server``."""

import uvicorn

from aurelius_atlas_server.app import create_app
from aurelius_atlas_server.settings import load_settings

settings = load_settings()
uvicorn.run(create_app(settings), host=settings.host, port=settings.port)
