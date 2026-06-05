from m4i_analytics.graphs.languages.archimate.metamodel.Concepts import (
    Aspect,
    Layer,
    _ElementType,
)
from m4i_analytics.shared.model.PseudoEnum import PseudoEnum


class ArchiElement(PseudoEnum):
    NODE = _ElementType("Node", "ar3_Node", Layer.OTHER, Aspect.OTHER)
    LABEL = _ElementType("Label", "ar3_Label", Layer.OTHER, Aspect.OTHER)
    VIEWREF = _ElementType("View Reference", "ar3_Diagram", Layer.OTHER, Aspect.OTHER)

    @classmethod
    def getElementByTag(cls, tag, attributes=None):
        """
        Find a specific ArchiMate element by its exchange format tag name.

        :returns: The ArchiMate element matching the tag name. If there is no match, returns None instead.
        :rtype: ElementType

        :param str tag: The exchange format tag name of the element.
        :param str attributes: *Optional*. Additional attributes that define
            the element when there are several subtypes of the same tag.
        """

        if attributes is None:
            attributes = {}
        result = [
            e[1]
            for e in cls.getAll()
            if e[1]["tag"] == tag
            and (not attributes or len(set(e[1]["attributes"].items()) ^ set(attributes.items())) == 0)
        ]
        return result[0] if result else None

    # END getElementByTag

    @classmethod
    def getElementByName(cls, name):
        """
        Find a specific ArchiMate element by its human readable type name.

        :returns: The ArchiMate element matching the type name. If there is no match, returns None instead.
        :rtype: ElementType

        :param str name: The human readable type name of the element.
        """

        result = [e[1] for e in cls.getAll() if e[1]["name"] == name]
        return result[0] if result else None

    # END getElementByName

    @classmethod
    def getElementsByLayer(cls, layer):
        """
        Find all ArchiMate elements that are part of a specific layer
        (horizontal slice of the language framework).

        :returns: A list of all elements in a particular layer.
        :rtype: :func: list of ElementType

        :param Layer layer: The layer for which to retrieve the elements.
        """

        return [e[1] for e in cls.getAll() if e[1]["layer"] == layer]

    # END getElementsByLayer

    @classmethod
    def getElementsByAspect(cls, aspect):
        """
        Find all ArchiMate elements that are part of a specific aspect
        (vertical slice of the language framework).

        :returns: A list of all elements in a particular aspect.
        :rtype: :func: list of ElementType

        :param Aspect aspect: The aspect for which to retrieve the elements.
        """

        return [e[1] for e in cls.getAll() if e[1]["aspect"] == aspect]

    # END getElementsByAspect


# END ViewNodeType
