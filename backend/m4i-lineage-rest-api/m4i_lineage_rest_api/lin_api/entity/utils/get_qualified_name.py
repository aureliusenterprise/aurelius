import re
from typing import List

DELIMITER = "--"
WHITE_SPACE = re.compile("[\s]+")
ILLEGAL_CHARACTERS = re.compile("[&]+")


def get_qualified_name(*components: str, prefix: str = ""):
    """
    Returns a qualified name string based on the given name `components`.
    """

    not_empty = filter(None, components)

    lowercase = map(str.lower, not_empty)

    without_illegal_characters = map(
        lambda c: ILLEGAL_CHARACTERS.sub("", c),
        lowercase
    )

    with_hyphens = map(
        lambda c: WHITE_SPACE.sub("-", c),
        without_illegal_characters
    )

    qualified_name = DELIMITER.join(with_hyphens)

    if prefix:
        qualified_name = prefix + DELIMITER + qualified_name
    # END IF

    return qualified_name
# END get_qualified_name
