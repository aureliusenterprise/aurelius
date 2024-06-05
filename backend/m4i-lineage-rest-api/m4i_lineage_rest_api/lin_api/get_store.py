from m4i_atlas_core import (ConfigStore)

from ..config import config
from ..credentials import credentials

store = ConfigStore.get_instance()
store.load({**config, **credentials})
