import uvicorn

from aurelius_fastapi_example import main
from aurelius_fastapi_example.globals import SETTINGS

uvicorn.run(
    main,
    host=SETTINGS.host,
    port=SETTINGS.port,
    factory=True,
)
