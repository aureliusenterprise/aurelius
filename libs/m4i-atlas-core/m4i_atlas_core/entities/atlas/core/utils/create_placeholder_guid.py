from random import randrange


def create_placehoder_guid() -> str:
    """
    Returns a placeholder guid for use with entities not yet committed to Atlas
    """
    guid = randrange(
        start=-10000,
        stop=0
    )

    return str(guid)
# END create_placeholder_guid
