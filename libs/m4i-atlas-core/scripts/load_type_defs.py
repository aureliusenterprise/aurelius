import asyncio

from scripts.config_sample import config
from scripts.credentials_sample import credentials

from m4i_atlas_core import (ConfigStore, connectors_types_def,
                            create_type_defs, data_dictionary_types_def,
                            kubernetes_types_def, process_types_def)


async def main():
    store = ConfigStore.get_instance()

    store.load({
        **config,
        **credentials
    })

    await create_type_defs(data_dictionary_types_def)
    await create_type_defs(process_types_def)
    await create_type_defs(connectors_types_def)
    await create_type_defs(kubernetes_types_def)
# END main


if __name__ == "__main__":
    asyncio.run(main())
# END MAIN
