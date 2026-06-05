from __future__ import annotations

from enum import Enum
from typing import Any, Optional, Union

from pandas import DataFrame


class NodeAttribute(Enum):
    """
    This class enumerates the keys to the node properties that need to be
    mapped for standardized analytics functions.
    """

    ID = "id"
    NAME = "name"
    LABEL = "label"
    TYPE = "type"


# END NodeAttributes


class EdgeAttribute(Enum):
    """
    This class enumerates the keys to the edge properties that need to be
    mapped for standardized analytics functions.
    """

    ID = "id"
    NAME = "name"
    LABEL = "label"
    SOURCE = "source"
    TARGET = "target"
    TYPE = "type"


# END EdgeAttributes


class Graph:
    """
    This class represents a generic graph for various standardized analytics
    functions. The sets of nodes and edges are represented as Pandas DataFrames.
    To use your custom dataframes with standardized analytics functions, please
    map your columns to the attributes as specified in the respective enums.
    """

    def __init__(
        self,
        id: str,
        nodes: Optional[DataFrame] = None,
        edges: Optional[DataFrame] = None,
        data: Optional[DataFrame] = None,
        defaultAttributeMapping: bool = False,
    ) -> None:
        """
        Create a new Graph instance.

        :returns: a new Graph instance
        :rtype: Graph

        :param str id: The id of your graph.
        :param pandas.DataFrame nodes: *Optional*. A dataframe representing
            the nodes in your graph. Defaults to an empty dataframe with the
            columns: id x type x name x label.
        :param pandas.DataFrame edges: *Optional*. A dataframe representing
            the edges in your graph. Defaults to an empty dataframe with the
            columns: id x type x source x target x name x label.
        :param pandas.DataFrame data: *Optional*. A dataframe representing the
            properties of the elements of your graph. Preferred representation
            is a row per concept, keyed by ID, containing a properties object
            with key-value pairs.
        :param bool defaultAttributeMapping: *Optional*. Whether or not you want
            to map the columns of your dataframes to the graph attributes based
            on a predefined template for this type of graph.

        :exception TypeError: Thrown when defaultAttributeMapping is True,
            but there is no template specified for this type of graph.
        """

        self.id = id
        if nodes is None or len(list(nodes)) == 0:
            self.nodes = DataFrame(columns=["id", "name", "type", "label"])
        else:
            self.nodes = nodes
        if edges is None or len(list(edges)) == 0:
            self.edges = DataFrame(columns=["id", "name", "type", "label", "source", "target"])
        else:
            self.edges = edges
        if data is None:
            self.data = DataFrame()
        else:
            self.data = data
        self._nodeAttributeMapping = {}
        self._edgeAttributeMapping = {}

        if type(self) is Graph and defaultAttributeMapping:
            self.applyDefaultAttributeMapping()

    # END __init__

    def hasValidAttributeMapping(self):
        """
        Checks whether the mapping of attributes for nodes and edges is
        complete, and fits with the current DataFrame columns.

        :returns: Whether or not the current attribute mapping is valid.
        :rtype: bool
        """

        return self.hasValidNodeAttributeMapping() and self.hasValidEdgeAttributeMapping()

    def putNodeAttributeMapping(self, key: Union[str, NodeAttribute], ref: Optional[str]) -> None:
        """
        Add a new node property mapping or override an existing one.

        :param str key: The lookup name of the property
        :param str ref: The name of the DataFrame column that contains the property value

        :exception TypeError: Thrown when there is no nodes DataFrame associated with this graph
        :exception ValueError: Thrown when the column name reference does not exist in the DataFrame
        """

        if isinstance(key, NodeAttribute):
            key = key.value

        if self.nodes is None:
            raise TypeError(
                "There are no nodes associated with this graph! "
                "Please assign a dataframe to the nodes property first, "
                "before attempting to map property names."
            )

        elif not any(filter(lambda attr: attr == ref, list(self.nodes))):
            raise ValueError("The property you are attempting to map does not exist!")

        self._nodeAttributeMapping[key] = ref

    # END putNodeAttributeMapping

    def getNodeAttributeMapping(self, key: Union[str, NodeAttribute]) -> Optional[str]:
        """
        Retrieve the name of the DataFrame column that contains a particular
        node property. If the property has not been mapped, this returns None.

        :returns: The name of the DataFrame column for a particular node property.
        :rtype: str

        :param str key: The lookup name of the property.
        """

        if isinstance(key, NodeAttribute):
            key = key.value  # type: ignore[assignment]

        return self._nodeAttributeMapping.get(key)

    # END getNodeAttributeMapping

    def hasValidNodeAttributeMapping(self):
        """
        Checks whether the mapping of attributes for nodes is complete,
        and fits with the current DataFrame columns.

        :returns: Whether or not the current attribute mapping is valid.
        :rtype: bool
        """

        df_cols = list(self.nodes)
        mapping_keys = list(self._nodeAttributeMapping.keys())
        attrs = [a.value for a in NodeAttribute]

        return (
            isinstance(self.nodes, DataFrame)
            and not any(filter(lambda a: a not in mapping_keys, attrs))
            and not any(filter(lambda n: n not in df_cols, list(self._nodeAttributeMapping.values())))
        )

    # END hasValidNodeAttributeMapping

    def putEdgeAttributeMapping(self, key: Union[str, EdgeAttribute], ref: str) -> None:
        """
        Add a new edge property mapping or override an existing one.

        :param str key: The lookup name of the property
        :param str ref: The name of the DataFrame column that contains the property value

        :exception TypeError: Thrown when there is no edge DataFrame associated with this graph
        :exception ValueError: Thrown when the column name reference does not exist in the DataFrame
        """

        if isinstance(key, EdgeAttribute):
            key = key.value

        if self.edges is None:
            raise TypeError(
                "There are no edges associated with this graph! "
                "Please assign a dataframe to the edges property first, "
                "before attempting to map property names."
            )

        elif not any(filter(lambda attr: attr == ref, list(self.edges))):
            raise ValueError("The property you are attempting to map does not exist!")

        self._edgeAttributeMapping[key] = ref

    # END putEdgeAttributeMapping

    def getEdgeAttributeMapping(self, key: Union[str, EdgeAttribute]) -> Optional[str]:
        """
        Retrieve the name of the DataFrame column that contains a particular
        edge property. If the property has not been mapped, this returns None.

        :returns: The name of the DataFrame column for a particular edge property.
        :rtype: str

        :param str key: The lookup name of the property.
        """

        if isinstance(key, EdgeAttribute):
            key = key.value  # type: ignore[assignment]

        return self._edgeAttributeMapping.get(key)

    # END getEdgeAttributeMapping

    def hasValidEdgeAttributeMapping(self):
        """
        Checks whether the mapping of attributes for edges is complete,
        and fits with the current DataFrame columns.

        :returns: Whether or not the current attribute mapping is valid.
        :rtype: bool
        """

        df_cols = list(self.edges)
        mapping_keys = list(self._edgeAttributeMapping.keys())
        attrs = [a.value for a in EdgeAttribute]

        return (
            isinstance(self.edges, DataFrame)
            and not any(filter(lambda a: a not in mapping_keys, attrs))
            and not any(filter(lambda e: e not in df_cols, list(self._edgeAttributeMapping.values())))
        )

    # END hasValidEdgeAttributeMapping

    def getNodeById(self, nodeid: str) -> Optional[dict[str, Any]]:
        """
        Returns the node with the given ID.

        :returns: The node with the given ID, or None if no such node exists.
            If multiple nodes with the same ID exist, only the first encountered
            is returned.
        :rtype: dict

        :param str nodeid: The id of the node you're looking for.
        """

        result = [
            node
            for node in self.nodes.to_dict(orient="records")
            if node[self.getNodeAttributeMapping(NodeAttribute.ID)] == nodeid  # type: ignore[arg-type]
        ]
        return result[0] if result else None  # type: ignore[return-value]

    # END getNodeById

    def getEdgeById(self, edgeid: str) -> Optional[dict[str, Any]]:
        """
        Returns the edge with the given ID.

        :returns: The edge with the given ID, or None if no such edge exists.
            If multiple edges with the same ID exist, only the first encountered
            is returned.
        :rtype: dict

        :param str nodeid: The id of the edge you're looking for.
        """

        result = [
            edge
            for edge in self.edges.to_dict(orient="records")
            if edge[self.getEdgeAttributeMapping(EdgeAttribute.ID)] == edgeid  # type: ignore[arg-type]
        ]
        return result[0] if result else None  # type: ignore[return-value]

    # END getNodeById

    def getEdgeByEndpoints(self, source, target):
        """
        Find the edge with the given source and target in the given graph.

        :returns: The id of the edge with the given source and target in the
            given graph. If there is more than one match, returns the first
            occurrence.
        :rtype: str

        :param str source: The id of the source node.
        :param str target: The id of the target node.
        """

        source_key = self.getEdgeAttributeMapping(EdgeAttribute.SOURCE)
        target_key = self.getEdgeAttributeMapping(EdgeAttribute.TARGET)

        edges = [
            e
            for e in self.edges.to_dict(orient="records")
            if e[source_key] == source and e[target_key] == target
        ]
        return edges[0][self.getEdgeAttributeMapping(EdgeAttribute.ID)] if edges else None

    # END findEdge

    def applyDefaultAttributeMapping(self):
        """
        If this type of graph will often be instantiated with a specific set
        of columns, define this function to automatically map the graph
        attributes to these columns. The columns can be automatically mapped
        by setting the defaultAttributeMapping parameter of the constructor
        to True.
        """

        self.putNodeAttributeMapping(NodeAttribute.ID, "id")
        self.putNodeAttributeMapping(NodeAttribute.TYPE, "type")
        self.putNodeAttributeMapping(NodeAttribute.NAME, "name")
        self.putNodeAttributeMapping(NodeAttribute.LABEL, "label")

        self.putEdgeAttributeMapping(EdgeAttribute.ID, "id")
        self.putEdgeAttributeMapping(EdgeAttribute.TYPE, "type")
        self.putEdgeAttributeMapping(EdgeAttribute.NAME, "name")
        self.putEdgeAttributeMapping(EdgeAttribute.LABEL, "label")
        self.putEdgeAttributeMapping(EdgeAttribute.SOURCE, "source")
        self.putEdgeAttributeMapping(EdgeAttribute.TARGET, "target")

    # END applyDefaultAttributeMapping


# END Graph
