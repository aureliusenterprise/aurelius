from enum import Enum

from pandas import DataFrame

from m4i_analytics.graphs.model.Graph import Graph, NodeAttribute


class ViewAttribute(Enum):
    """
    This class enumerates the keys to the view properties that need to be
    mapped for standardized analytics functions.
    """

    ID = "id"
    NAME = "name"
    TYPE = "type"
    CONNECTIONS = "connections"
    NODES = "nodes"
    PROPERTIES = "properties"


# END ViewAttributes


class ArchimateModel(Graph):
    """
    This class represents an ArchiMate model for various standardized analytics
    functions. The sets of nodes, edges and views are represented as Pandas
    DataFrames. To use your custom dataframes with standardized analytics
    functions, please map your columns to the attributes as specified in the
    respective enums.
    """

    def __init__(
        self,
        name=None,
        nodes=None,
        edges=None,
        views=None,
        organizations=None,
        defaultAttributeMapping=False,
    ):
        """
        Create a new ArchimateModel instance.

        :returns: a new ArchimateModel instance
        :rtype: ArchimateModel

        :param str name: The name of your model
        :param pandas.DataFrame nodes: The nodes in your model.
        :param pandas.DataFrame edges: The edges in your model.
        :param pandas.DataFrame views: The views in your model.
        :param pandas.DataFrame organizations: The organization of your model.
        :param bool defaultAttributeMapping: Whether or not you want to map
            the columns of your dataframes to the graph attributes based on a
            predefined template for this type of graph.

        """

        super().__init__(
            name if name is not None else "",
            nodes if nodes is not None else DataFrame(columns=["id", "name", "type", "label"]),
            edges
            if edges is not None
            else DataFrame(columns=["id", "name", "type", "label", "source", "target"]),
            defaultAttributeMapping=defaultAttributeMapping,
        )
        self.name = name
        self.views = (
            views
            if views is not None
            else DataFrame(columns=["id", "name", "type", "nodes", "connections", "properties"])
        )
        self.organizations = organizations if organizations is not None else DataFrame()
        self._viewAttributeMapping = {}
        self._organizationsAttributeMapping = {}

        if type(self) is ArchimateModel and defaultAttributeMapping:
            self.applyDefaultAttributeMapping()

    # END __init__

    def hasValidAttributeMapping(self):
        """
        Checks whether the mapping of attributes for nodes, edges and views is
        complete, and fits with the current DataFrame columns.

        :returns: Whether or not the current attribute mapping is valid.
        :rtype: bool
        """

        return super().hasValidAttributeMapping() and self.hasValidViewAttributeMapping()

    def putViewAttributeMapping(self, key, ref):
        """
        Add a new view property mapping or override an existing one.

        :param str key: The lookup name of the property
        :param str ref: The name of the DataFrame column that contains the property value

        :exception TypeError: Thrown when there is no view DataFrame associated with this graph
        :exception ValueError: Thrown when the column name reference does not exist in the DataFrame
        """

        if isinstance(key, ViewAttribute):
            key = key.value

        if self.views is None:
            raise TypeError(
                "There are no views associated with this model! "
                "Please assign a dataframe to the views property first, "
                "before attempting to map property names."
            )

        elif not any(filter(lambda attr: attr == ref, list(self.views))):
            raise ValueError("The property you are attempting to map does not exist!")

        self._viewAttributeMapping[key] = ref

    # END putViewAttributeMapping

    def getViewAttributeMapping(self, key):
        """
        Retrieve the name of the DataFrame column that contains a particular
        view property. If the property has not been mapped, this returns None.

        :returns: The name of the DataFrame column for a particular view property.
        :rtype: str

        :param str key: The lookup name of the property.
        """

        if isinstance(key, ViewAttribute):
            key = key.value

        return self._viewAttributeMapping.get(key)

    # END getViewAttributeMapping

    def hasValidViewAttributeMapping(self):
        """
        Checks whether the mapping of attributes for views is complete, and fits
        with the current DataFrame columns.

        :returns: Whether or not the current attribute mapping is valid.
        :rtype: bool
        """

        df_cols = list(self.views)
        mapping_keys = list(self._viewAttributeMapping.keys())
        attrs = [a.value for a in ViewAttribute]

        return (
            isinstance(self.views, DataFrame)
            and not any(filter(lambda a: a not in mapping_keys, attrs))
            and not any(
                filter(
                    lambda n: n not in df_cols,
                    list(self._viewAttributeMapping.values()),
                )
            )
        )

    # END hasValidViewAttributeMapping

    def applyDefaultAttributeMapping(self):
        """
        Initializes the attribute mapping for this model with the column names
        as they are when the model is retrieved from the m4i repository.

        :exception ValueError: Thrown when the model does not match the m4i format.
        """

        super().applyDefaultAttributeMapping()

        self.putViewAttributeMapping(ViewAttribute.ID, "id")
        self.putViewAttributeMapping(ViewAttribute.NAME, "name")
        self.putViewAttributeMapping(ViewAttribute.TYPE, "type")
        self.putViewAttributeMapping(ViewAttribute.CONNECTIONS, "connections")
        self.putViewAttributeMapping(ViewAttribute.NODES, "nodes")
        self.putViewAttributeMapping(ViewAttribute.PROPERTIES, "properties")

    # END applyDefaultAttributeMapping

    def organize(self):
        """
        Fill the organization part of the model. Concepts are grouped by layer
        and placed in separate folders. Relationships all go into the
        relationships folder. Any previously applied organization is replaced.
        """

        self.organizations = DataFrame(
            [
                {
                    "idRef": node["id"],
                    "level1": node[self.getNodeAttributeMapping(NodeAttribute.TYPE)]["layer"].capitalize(),
                    "level2": None,
                }
                for node in self.nodes.to_dict(orient="records")
                if node is not None and node[self.getNodeAttributeMapping(NodeAttribute.TYPE)] is not None
            ]
            + [
                {"idRef": edge["id"], "level1": "Relations", "level2": None}
                for edge in self.edges.to_dict(orient="records")
                if edge is not None
            ]
            + [
                {"idRef": view["id"], "level1": "Views", "level2": None}
                for view in self.views.to_dict(orient="records")
                if view is not None
            ]
        )

    # END organize


# END ArchimateModel
