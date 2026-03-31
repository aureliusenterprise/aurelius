import uvicorn

from aurelius_fastapi_example import get_settings, main

settings = get_settings()

uvicorn.run(
    lambda: main(settings),
    factory=True,
    host=settings.host,
    port=settings.port,
)
