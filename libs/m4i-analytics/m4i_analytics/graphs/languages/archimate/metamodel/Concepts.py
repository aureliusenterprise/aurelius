from m4i_analytics.shared.model.PseudoEnum import PseudoEnum


class _ConceptType(dict):
    def __init__(self, typename, tag, parent=None, attributes=None):
        if attributes is None:
            attributes = {}
        self["typename"] = typename
        self["tag"] = tag
        self["parent"] = parent
        self["attributes"] = attributes

    # END __init__

    def is_instance_of(self, concept_type):
        """
        :returns: Whether or not this concept is a child of the given concept type.
        :rtype: bool

        :param _ConceptType concept_type: the parent concept type.
        """

        result = concept_type == self["parent"]
        if not result and self["parent"] is not None:
            result = self["parent"].is_instance_of(concept_type)
        return result

    # END is_instance_of

    def __eq__(self, other):
        return not self < other and not other < self

    # END __eq__

    def __ne__(self, other):
        return self < other or other < self

    # END __ne__

    def __gt__(self, other):
        return other < self

    # END __gt__

    def __ge__(self, other):
        return not self < other

    # END __ge__

    def __le__(self, other):
        return not other < self

    # END __le__

    def __lt__(self, other):
        return not isinstance(other, _ConceptType) or self["typename"] < other["typename"]

    # END __lt__

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(self["typename"])

    # END __hash__


# END _ConceptType


class Aspect(PseudoEnum):
    """
    Aspect enumerates all aspects of the Archimate 3.0 language framework
    """

    ACTIVE = "Active Structure"
    BEHAVIORAL = "Behavioral"
    COMPOSITE = "Composite"
    MOTIVATION = "Motivation"
    OTHER = "Other"
    PASSIVE = "Passive Structure"


# END Aspect


class Layer(PseudoEnum):
    """
    Layer enumerates all layers of the Archimate 3.0 language framework
    """

    APPLICATION = "Application"
    BUSINESS = "Business"
    COMPOSITE = "Composite"
    IMPLEMENTATION_MIGRATION = "Implementation & Migration"
    MOTIVATION = "Motivation"
    OTHER = "Other"
    PHYSICAL = "Physical"
    STRATEGY = "Strategy"
    TECHNOLOGY = "Technology"


# END Layer


class _ElementType(_ConceptType):
    def __init__(self, typename, tag, layer, aspect, parent=None, attributes=None):
        if attributes is None:
            attributes = {}
        super().__init__(typename, tag, parent=parent, attributes=attributes)
        self["layer"] = layer
        self["aspect"] = aspect

    # END __init__


# END _ElementType


class ElementType(PseudoEnum):
    """
    ElementType enumerates all element types in Archimate 3.0
    """

    JUNCTION = _ElementType("Junction", "ar3_Junction", Layer.OTHER, Aspect.OTHER)

    AND_JUNCTION = _ElementType("And Junction", "ar3_AndJunction", Layer.OTHER, Aspect.OTHER, parent=JUNCTION)
    APPLICATION_COLLABORATION = _ElementType(
        "Application Collaboration", "ar3_ApplicationCollaboration", Layer.APPLICATION, Aspect.ACTIVE
    )
    APPLICATION_COMPONENT = _ElementType(
        "Application Component", "ar3_ApplicationComponent", Layer.APPLICATION, Aspect.ACTIVE
    )
    APPLICATION_EVENT = _ElementType(
        "Application Event", "ar3_ApplicationEvent", Layer.APPLICATION, Aspect.BEHAVIORAL
    )
    APPLICATION_FUNCTION = _ElementType(
        "Application Function", "ar3_ApplicationFunction", Layer.APPLICATION, Aspect.BEHAVIORAL
    )
    APPLICATION_INTERACTION = _ElementType(
        "Application Interaction", "ar3_ApplicationInteraction", Layer.APPLICATION, Aspect.BEHAVIORAL
    )
    APPLICATION_INTERFACE = _ElementType(
        "Application Interface", "ar3_ApplicationInterface", Layer.APPLICATION, Aspect.ACTIVE
    )
    APPLICATION_PROCESS = _ElementType(
        "Application Process", "ar3_ApplicationProcess", Layer.APPLICATION, Aspect.BEHAVIORAL
    )
    APPLICATION_SERVICE = _ElementType(
        "Application Service", "ar3_ApplicationService", Layer.APPLICATION, Aspect.BEHAVIORAL
    )
    ARTIFACT = _ElementType("Artifact", "ar3_Artifact", Layer.TECHNOLOGY, Aspect.PASSIVE)
    ASSESSMENT = _ElementType("Assessment", "ar3_Assessment", Layer.MOTIVATION, Aspect.MOTIVATION)
    BUSINESS_ACTOR = _ElementType("Business Actor", "ar3_BusinessActor", Layer.BUSINESS, Aspect.ACTIVE)
    BUSINESS_COLLABORATION = _ElementType(
        "Business Collaboration", "ar3_BusinessCollaboration", Layer.BUSINESS, Aspect.ACTIVE
    )
    BUSINESS_EVENT = _ElementType("Business Event", "ar3_BusinessEvent", Layer.BUSINESS, Aspect.BEHAVIORAL)
    BUSINESS_FUNCTION = _ElementType(
        "Business Function", "ar3_BusinessFunction", Layer.BUSINESS, Aspect.BEHAVIORAL
    )
    BUSINESS_INTERACTION = _ElementType(
        "Business Interaction", "ar3_BusinessInteraction", Layer.BUSINESS, Aspect.BEHAVIORAL
    )
    BUSINESS_INTERFACE = _ElementType(
        "Business Interface", "ar3_BusinessInterface", Layer.BUSINESS, Aspect.ACTIVE
    )
    BUSINESS_OBJECT = _ElementType("Business Object", "ar3_BusinessObject", Layer.BUSINESS, Aspect.PASSIVE)
    BUSINESS_PROCESS = _ElementType(
        "Business Process", "ar3_BusinessProcess", Layer.BUSINESS, Aspect.BEHAVIORAL
    )
    BUSINESS_ROLE = _ElementType("Business Role", "ar3_BusinessRole", Layer.BUSINESS, Aspect.ACTIVE)
    BUSINESS_SERVICE = _ElementType(
        "Business Service", "ar3_BusinessService", Layer.BUSINESS, Aspect.BEHAVIORAL
    )
    CAPABILITY = _ElementType("Capability", "ar3_Capability", Layer.STRATEGY, Aspect.BEHAVIORAL)
    COMMUNICATION_NETWORK = _ElementType(
        "Communication Network", "ar3_CommunicationNetwork", Layer.TECHNOLOGY, Aspect.PASSIVE
    )
    CONSTRAINT = _ElementType("Constraint", "ar3_Constraint", Layer.MOTIVATION, Aspect.MOTIVATION)
    CONTRACT = _ElementType("Contract", "ar3_Contract", Layer.BUSINESS, Aspect.PASSIVE)
    COURSE_OF_ACTION = _ElementType(
        "Course of Action", "ar3_CourseOfAction", Layer.STRATEGY, Aspect.BEHAVIORAL
    )
    DATA_OBJECT = _ElementType("Data Object", "ar3_DataObject", Layer.APPLICATION, Aspect.PASSIVE)
    DELIVERABLE = _ElementType(
        "Deliverable", "ar3_Deliverable", Layer.IMPLEMENTATION_MIGRATION, Aspect.PASSIVE
    )
    DEVICE = _ElementType("Device", "ar3_Device", Layer.TECHNOLOGY, Aspect.ACTIVE)
    DISTRIBUTION_NETWORK = _ElementType(
        "Distribution Network", "ar3_DistributionNetwork", Layer.PHYSICAL, Aspect.PASSIVE
    )
    DRIVER = _ElementType("Driver", "ar3_Driver", Layer.MOTIVATION, Aspect.MOTIVATION)
    EQUIPMENT = _ElementType("Equipment", "ar3_Equipment", Layer.PHYSICAL, Aspect.ACTIVE)
    FACILITY = _ElementType("Facility", "ar3_Facility", Layer.PHYSICAL, Aspect.ACTIVE)
    GAP = _ElementType("Gap", "ar3_Gap", Layer.IMPLEMENTATION_MIGRATION, Aspect.PASSIVE)
    GOAL = _ElementType("Goal", "ar3_Goal", Layer.MOTIVATION, Aspect.MOTIVATION)
    GROUPING = _ElementType("Grouping", "ar3_Grouping", Layer.COMPOSITE, Aspect.COMPOSITE)
    IMPLEMENTATION_EVENT = _ElementType(
        "Implementation Event", "ar3_ImplementationEvent", Layer.IMPLEMENTATION_MIGRATION, Aspect.BEHAVIORAL
    )
    LINEAGE_DATASET = _ElementType("Lineage Dataset", "lineage_dataset", Layer.OTHER, Aspect.OTHER)
    LINEAGE_PROCESS = _ElementType("Lineage Process", "lineage_process", Layer.OTHER, Aspect.OTHER)
    LOCATION = _ElementType("Location", "ar3_Location", Layer.COMPOSITE, Aspect.COMPOSITE)
    MATERIAL = _ElementType("Material", "ar3_Material", Layer.PHYSICAL, Aspect.PASSIVE)
    MEANING = _ElementType("Meaning", "ar3_Meaning", Layer.MOTIVATION, Aspect.MOTIVATION)
    NODE = _ElementType("Node", "ar3_Node", Layer.TECHNOLOGY, Aspect.ACTIVE)
    OR_JUNCTION = _ElementType("Or Junction", "ar3_OrJunction", Layer.OTHER, Aspect.OTHER, parent=JUNCTION)
    PATH = _ElementType("Path", "ar3_Path", Layer.TECHNOLOGY, Aspect.PASSIVE)
    OUTCOME = _ElementType("Outcome", "ar3_Outcome", Layer.MOTIVATION, Aspect.MOTIVATION)
    PLATEAU = _ElementType("Plateau", "ar3_Plateau", Layer.IMPLEMENTATION_MIGRATION, Aspect.COMPOSITE)
    PRINCIPLE = _ElementType("Principle", "ar3_Principle", Layer.MOTIVATION, Aspect.MOTIVATION)
    PRODUCT = _ElementType("Product", "ar3_Product", Layer.BUSINESS, Aspect.PASSIVE)
    REPRESENTATION = _ElementType("Representation", "ar3_Representation", Layer.BUSINESS, Aspect.PASSIVE)
    REQUIREMENT = _ElementType("Requirement", "ar3_Requirement", Layer.MOTIVATION, Aspect.MOTIVATION)
    RESOURCE = _ElementType("Resource", "ar3_Resource", Layer.STRATEGY, Aspect.COMPOSITE)
    STAKEHOLDER = _ElementType("Stakeholder", "ar3_Stakeholder", Layer.MOTIVATION, Aspect.ACTIVE)
    SYSTEM_SOFTWARE = _ElementType("System Software", "ar3_SystemSoftware", Layer.TECHNOLOGY, Aspect.ACTIVE)
    TECHNOLOGY_COLLABORATION = _ElementType(
        "Technology Collaboration", "ar3_TechnologyCollaboration", Layer.TECHNOLOGY, Aspect.ACTIVE
    )
    TECHNOLOGY_EVENT = _ElementType(
        "Technology Event", "ar3_TechnologyEvent", Layer.TECHNOLOGY, Aspect.BEHAVIORAL
    )
    TECHNOLOGY_FUNCTION = _ElementType(
        "Technology Function", "ar3_TechnologyFunction", Layer.TECHNOLOGY, Aspect.BEHAVIORAL
    )
    TECHNOLOGY_INTERACTION = _ElementType(
        "Technology Interaction", "ar3_TechnologyInteraction", Layer.TECHNOLOGY, Aspect.BEHAVIORAL
    )
    TECHNOLOGY_INTERFACE = _ElementType(
        "Technology Interface", "ar3_TechnologyInterface", Layer.TECHNOLOGY, Aspect.ACTIVE
    )
    TECHNOLOGY_PROCESS = _ElementType(
        "Technology Process", "ar3_TechnologyProcess", Layer.TECHNOLOGY, Aspect.BEHAVIORAL
    )
    TECHNOLOGY_SERVICE = _ElementType(
        "Technology Service", "ar3_TechnologyService", Layer.TECHNOLOGY, Aspect.BEHAVIORAL
    )
    UNKNOWN = _ElementType("Unknown", "ar3_Unknown", Layer.OTHER, Aspect.OTHER)
    VALUE = _ElementType("Value", "ar3_Value", Layer.MOTIVATION, Aspect.MOTIVATION)
    VALUE_STREAM = _ElementType("Value Stream", "ar3_ValueStream", Layer.STRATEGY, Aspect.BEHAVIORAL)
    WORK_PACKAGE = _ElementType(
        "Work Package", "ar3_WorkPackage", Layer.IMPLEMENTATION_MIGRATION, Aspect.BEHAVIORAL
    )

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


# END ElementType


class RelationshipClass(PseudoEnum):
    """
    RelationshipClass enumerates all relationship classes in Archimate 3.0.
    """

    STRUCTURAL = "Structural"
    DEPENDENCY = "Dependency"
    DYNAMIC = "Dynamic"
    OTHER = "Other"


# END RelationshipClass


class _RelationshipType(_ConceptType):
    def __init__(self, typename, tag, shorthand, relcls, parent=None, attributes=None):
        if attributes is None:
            attributes = {}
        super().__init__(typename, tag, parent=parent, attributes=attributes)
        self["shorthand"] = shorthand
        self["relcls"] = relcls

    # END __init__


# END _RelationshipType


class RelationshipType(PseudoEnum):
    """
    RelationshipType enumerates all relationship types in Archimate 3.0.
    """

    ACCESS = _RelationshipType("Access", "ar3_Access", "a", RelationshipClass.DEPENDENCY)
    ACCESS_ACCESS = _RelationshipType(
        "Access Access",
        "ar3_Access",
        "aa",
        RelationshipClass.DEPENDENCY,
        parent=ACCESS,
        attributes={"accessType": "Access"},
    )
    ACCESS_READ = _RelationshipType(
        "Access Read",
        "ar3_Access",
        "ar",
        RelationshipClass.DEPENDENCY,
        parent=ACCESS,
        attributes={"accessType": "Read"},
    )
    ACCESS_WRITE = _RelationshipType(
        "Access Write",
        "ar3_Access",
        "aw",
        RelationshipClass.DEPENDENCY,
        parent=ACCESS,
        attributes={"accessType": "Write"},
    )
    ACCESS_READ_WRITE = _RelationshipType(
        "Access Read/Write",
        "ar3_Access",
        "arw",
        RelationshipClass.DEPENDENCY,
        parent=ACCESS,
        attributes={"accessType": "ReadWrite"},
    )
    AGGREGATION = _RelationshipType("Aggregation", "ar3_Aggregation", "g", RelationshipClass.STRUCTURAL)
    ASSIGNMENT = _RelationshipType("Assignment", "ar3_Assignment", "i", RelationshipClass.STRUCTURAL)
    ASSOCIATION = _RelationshipType("Association", "ar3_Association", "o", RelationshipClass.OTHER)
    DIRECTED_ASSOCIATION = _RelationshipType(
        "Association",
        "ar3_Association",
        "do",
        RelationshipClass.OTHER,
        parent=ASSOCIATION,
        attributes={"isDirected": "true"},
    )
    COMPOSITION = _RelationshipType("Composition", "ar3_Composition", "c", RelationshipClass.STRUCTURAL)
    FLOW = _RelationshipType("Flow", "ar3_Flow", "f", RelationshipClass.DYNAMIC)
    INFLUENCE = _RelationshipType("Influence", "ar3_Influence", "n", RelationshipClass.DEPENDENCY)
    LINEAGE_RELATION = _RelationshipType(
        "Lineage Relation", "lineage_relation", "lr", RelationshipClass.OTHER
    )
    REALIZATION = _RelationshipType("Realization", "ar3_Realization", "r", RelationshipClass.STRUCTURAL)
    SERVING = _RelationshipType("Serving", "ar3_Serving", "v", RelationshipClass.DEPENDENCY)
    SPECIALIZATION = _RelationshipType("Specialization", "ar3_Specialization", "s", RelationshipClass.OTHER)
    TRIGGERING = _RelationshipType("Triggering", "ar3_Triggering", "t", RelationshipClass.DYNAMIC)

    @classmethod
    def getRelationshipByTag(cls, tag, attributes=None):
        """
        Find a specific ArchiMate relationship by its exchange format tag name.

        :returns: The ArchiMate relationship matching the tag name. If there is
            no match, returns None instead.
        :rtype: RelationshipType

        :param str tag: The exchange format tag name of the element.
        :param str attributes: *Optional*. Additional attributes that define
            the relationship when there are several subtypes of the same tag.
        """

        if attributes is None:
            attributes = {}
        result = [
            r[1]
            for r in cls.getAll()
            if r[1]["tag"] == tag
            and (not attributes or len(set(r[1]["attributes"].items()) ^ set(attributes.items())) == 0)
        ]
        return result[0] if result else None

    # END getRelationshipByTag

    @classmethod
    def getRelationshipByName(cls, typename):
        """
        Find a specific ArchiMate relationship by its human readable type name.

        :returns: The ArchiMate relationship matching the type name. If there
            is no match, returns None instead.
        :rtype: RelationshipType

        :param str name: The human readable type name of the element.
        """

        result = [r[1] for r in cls.getAll() if r[1]["typename"] == typename]
        return result[0] if result else None

    # END getRelationshipByTag

    @classmethod
    def getRelationshipsByClass(cls, relcls, attributes=None):
        """
        Find the ArchiMate relationships that are part of a particular relationship class.

        :returns: A list of all relationship types that are part of a particular class.
        :rtype: :func: list of RelationshipType

        :param RelationshipClass relcls: The class to which the relationship types should belong.
        """

        if attributes is None:
            attributes = {}
        return [r[1] for r in cls.getAll() if r[1]["relcls"] == relcls]

    # END getRelationshipByClass

    @classmethod
    def getRelationshipByShorthand(cls, shorthand, attributes=None):
        """
        Find the ArchiMate relationship that matches the given shorthand and attributes

        :returns: The relationship type that matches the given parameters
        :rtype: RelationshipType

        :param RelationshipClass shorthand: The shorthand that should match the resulting type.
        """

        if attributes is None:
            attributes = {}
        result = [
            r[1]
            for r in cls.getAll()
            if r[1]["shorthand"] == shorthand
            and (not attributes or len(set(r[1]["attributes"].items()) ^ set(attributes.items())) == 0)
        ]
        return result[0] if result else None

    # END getRelationshipByClass


# END RelationshipType
