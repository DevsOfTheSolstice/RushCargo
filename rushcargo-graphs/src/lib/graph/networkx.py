import networkx as nx
import matplotlib.pyplot as plt
from psycopg import sql

from .constants import *

from ..model.constants import *


class RushWGraph:
    """
    Graph Class that Represents a the Rush Cargo Warehouse Connections
    """

    # Graph
    __DiGraph = None

    # Database Connection
    __c = None
    __items = None

    def __init__(self, remoteCursor, draw: bool = False):
        """
        Rush Cargo Warehouse Connection Graph Class Constructor

        :param Cursor remoteCursor: Remote Database Connection Cursor
        :param bool draw: Specifies whether to Draw or not the NetworkX Graph
        """

        # Iniliaze NetworkX Graph Class
        self.__DiGraph = nx.DiGraph()

        # Save Database Connection Information
        self.__c = remoteCursor

        # Set Nodes
        self.setRegionMainNodes(draw)

        # Draw Graph
        if draw:
            self.draw()

    def __getNodesValue(self, key: str) -> list:
        """
        Method that Retuns a List of the Nodes Values for a Given Key

        :param str key: Key which is Used to Access the Node Attribute Value at Node's ``data``
        :return: List of Nodes Value for a Given Attribute
        :rtype: list
        """

        return [node[1][key] for node in self.__DiGraph.nodes(data=True)]

    def __regionMainNodesQuery(self):
        """
        Method that Retuns a Query to Get All the Region Main Warehouses from its Remote View

        :return: SQL Query Get All the Region Main Warehouses from its Remote View
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {regionNameField}, {warehouseIdField} FROM {connectionsViewName}.{regionMainWarehousesViewName}"
        ).format(
            regionNameField=sql.Identifier(REGIONS_NAME),
            warehouseIdField=sql.Identifier(WAREHOUSES_ID),
            connectionsViewName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            regionMainWarehousesViewName=sql.Identifier(
                REGIONS_MAIN_WAREHOUSES_VIEW_NAME
            ),
        )

    def setRegionMainNodes(self, draw: bool = False):
        """
        Method that Add All the Region Main Warehouse Nodes to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes
        :return: Nothing
        :rtype: None
        """

        # Query to Get All Region Main Warehouses from its Remote View
        regionQuery = self.__regionMainNodesQuery()

        # Execute Query and Fetch Items (Nodes)
        try:
            self.__items = self.__c.execute(regionQuery).fetchall()

        except Exception as err:
            print(err)

        # Nodes
        nodeList = []

        # Add Region Main Warehouse Nodes
        for node in self.__items:
            # Get Node Attributes from Tuple
            _, warehouseId = node

            nodeList.append(warehouseId)

        # Add Nodes
        if not draw:
            self.__DiGraph.add_nodes_from(nodeList)

        else:
            self.__DiGraph.add_nodes_from(
                nodeList,
                color=GRAPH_REGION_MAIN_WAREHOUSE_NODE_COLOR,
                size=GRAPH_REGION_MAIN_WAREHOUSE_NODE_SIZE,
                edgecolors=GRAPH_MAIN_REGION_WAREHOUSE_EDGE_COLOR,
                width=GRAPH_MAIN_REGION_WAREHOUSE_WIDTH,
            )

    def draw(self):
        """
        Method to Draw the Graph and it in a Local File

        :return: Nothing
        :rtype: NoneType
        """

        # Get Nodes Attributes
        colors = self.__getNodesValue("color")
        sizes = self.__getNodesValue("size")
        edgeColors = self.__getNodesValue("edgecolors")

        # Draw Nodes
        nx.draw(
            self.__DiGraph,
            node_color=colors,
            node_size=sizes,
            edgecolors=edgeColors,
            with_labels=GRAPH_WITH_LABELS,
            font_color=GRAPH_FONT_COLOR,
            font_size=GRAPH_FONT_SIZE,
        )

        # Show Matplotlib Graph
        # plt.show()

        # Save Graph Locally
        plt.savefig(
            RUSHWGRAPH_FILENAME,
            dpi=RUSHWGRAPH_DPI,
            orientation=RUSHWGRAPH_ORIENTATION,
        )
