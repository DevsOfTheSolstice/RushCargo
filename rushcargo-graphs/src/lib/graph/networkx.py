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

    # Graph Layouts
    __spring = None
    __spectral = None
    __shell = None
    __random = None
    __kamada = None
    __circular = None

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
        self.setRegionsMainNodes(draw)
        self.setCitiesMainNodes(draw)
        self.setCitiesNodes(draw)

        # Set Nodes Edges
        self.setConnectionsNodeEdges(draw)

        if draw:
            # Get Graph Layouts
            self.__spring = nx.spring_layout(
                self.__DiGraph,
                k=SPRING_DISTANCE,
                iterations=SPRING_ITERATIONS,
                weight="weightAttraction",
            )
            self.__shell = nx.shell_layout(self.__DiGraph)
            self.__spectral = nx.spectral_layout(self.__DiGraph)
            self.__random = nx.random_layout(self.__DiGraph)
            self.__circular = nx.circular_layout(self.__DiGraph)
            self.__kamada = nx.kamada_kawai_layout(self.__DiGraph)

            # Draw Graph
            self.draw()

    def __getNodesValue(self, key: str) -> list:
        """
        Method that Retuns a List of the Nodes Values for a Given Key

        :param str key: Key which is Used to Access the Node Attribute Value at Node's ``data``
        :return: List of Nodes Value for a Given Attribute
        :rtype: list
        """

        return [node[1][key] for node in self.__DiGraph.nodes(data=True)]

    def __getEdgesValue(self, key: str) -> list:
        """
        Method that Retuns a List of the Nodes Edges Values for a Given Key

        :param str key: Key which is Used to Access the Edge Attribute Value
        :return: List of Edges Value for a Given Attribute
        :rtype: list
        """

        return nx.get_edge_attributes(self.__DiGraph, key).values()

    def __regionsMainNodesQuery(self):
        """
        Method that Retuns a Query to Get All the Regions Main Warehouse Nodes from its Remote View

        :return: SQL Query Get All the Region Main Warehouses from its Remote View
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {regionNameField}, {warehouseIdField} FROM {connectionsSchemeName}.{regionMainWarehousesViewName}"
        ).format(
            regionNameField=sql.Identifier(REGIONS_NAME),
            warehouseIdField=sql.Identifier(WAREHOUSES_ID),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            regionMainWarehousesViewName=sql.Identifier(
                REGIONS_MAIN_WAREHOUSES_VIEW_NAME
            ),
        )

    def __citiesMainNodesQuery(self):
        """
        Method that Retuns a Query to Get All the Cities Main Warehouse Nodes from its Remote View

        :return: SQL Query Get All the City Main Warehouses from its Remote View
        :rtype: Composed
        """

        # Doesn't Include the Intersection of Region Main Warehouses and City Main Warehouses
        return sql.SQL(
            "SELECT {citiesMain}.{cityNameField}, {citiesMain}.{warehouseIdField} FROM {connectionsSchemeName}.{cityMainWarehousesViewName} AS {citiesMain} FULL OUTER JOIN {connectionsSchemeName}.{regionMainWarehousesViewName} AS {regionsMain} ON {citiesMain}.{warehouseIdField} = {regionsMain}.{warehouseIdField} WHERE {regionsMain}.{warehouseIdField} IS NULL"
        ).format(
            cityNameField=sql.Identifier(CITIES_NAME),
            warehouseIdField=sql.Identifier(WAREHOUSES_ID),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            cityMainWarehousesViewName=sql.Identifier(CITIES_MAIN_WAREHOUSES_VIEW_NAME),
            citiesMain=sql.Identifier(CITIES_MAIN),
            regionMainWarehousesViewName=sql.Identifier(
                REGIONS_MAIN_WAREHOUSES_VIEW_NAME
            ),
            regionsMain=sql.Identifier(REGIONS_MAIN),
        )

    def __citiesNodesQuery(self):
        """
        Method that Retuns a Query to Get All the Cities Warehouse Nodes (doesn't Include the Cities Main Warehouse Nodes) from its Remote View

        :return: SQL Query Get All the City Warehouses from its Remote View
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {warehouses}.{cityNameField}, {warehouses}.{warehouseIdField} FROM {connectionsSchemeName}.{warehouses} AS {warehouses} FULL OUTER JOIN {connectionsSchemeName}.{cityMainWarehousesViewName} AS {citiesMain} ON {warehouses}.{warehouseIdField} = {citiesMain}.{warehouseIdField} FULL OUTER JOIN {connectionsSchemeName}.{regionMainWarehousesViewName} AS {regionsMain} ON {warehouses}.{warehouseIdField} = {regionsMain}.{warehouseIdField} WHERE {citiesMain}.{warehouseIdField} IS NULL AND {regionsMain}.{warehouseIdField} IS NULL"
        ).format(
            cityNameField=sql.Identifier(CITIES_NAME),
            warehouses=sql.Identifier(WAREHOUSES_VIEW_NAME),
            warehouseIdField=sql.Identifier(WAREHOUSES_ID),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            cityMainWarehousesViewName=sql.Identifier(CITIES_MAIN_WAREHOUSES_VIEW_NAME),
            citiesMain=sql.Identifier(CITIES_MAIN),
            regionMainWarehousesViewName=sql.Identifier(
                REGIONS_MAIN_WAREHOUSES_VIEW_NAME
            ),
            regionsMain=sql.Identifier(REGIONS_MAIN),
        )

    def __connectionsNodeEdgesQuery(self):
        """
        Method that Retuns a Query to Get All the Region Main, Cities Main and Cities Warehouse Nodes Edges from its Remote View

        :return: SQL Query Get All the City Warehouses from its Remote View
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {warehousesConn}.{warehouseFromIdField}, {warehousesConn}.{warehouseToIdField}, {warehousesConn}.{warehouseRouteDistance}, {warehousesConn}.{warehouseConnType} FROM {connectionsSchemeName}.{warehouseConnectionsTableName} AS {warehousesConn}"
        ).format(
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            warehouseConnectionsTableName=sql.Identifier(WAREHOUSES_CONN_TABLE_NAME),
            warehousesConn=sql.Identifier(WAREHOUSES_CONN),
            warehouseFromIdField=sql.Identifier(WAREHOUSES_CONN_WAREHOUSE_FROM_ID),
            warehouseToIdField=sql.Identifier(WAREHOUSES_CONN_WAREHOUSE_TO_ID),
            warehouseRouteDistance=sql.Identifier(WAREHOUSES_CONN_ROUTE_DISTANCE),
            warehouseConnType=sql.Identifier(WAREHOUSES_CONN_CONN_TYPE),
        )

    def __storeGraph(self, title: str):
        """
        Method to Store the NetworkX Graph Image Locally

        :param str title: Graph File Name
        :return: Nothing
        :rtype: None
        """

        # Set Graph Title
        plt.title(RUSWGRAPH_TITLE)

        # Save Graph Locally
        plt.savefig(
            title,
            dpi=RUSHWGRAPH_DPI,
            orientation=RUSHWGRAPH_ORIENTATION,
        )

        # Clear Figure
        plt.clf()

    def setRegionsMainNodes(self, draw: bool = False):
        """
        Method that Add All the Regions Main Warehouse Nodes to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes
        :return: Nothing
        :rtype: None
        """

        # Query to Get All Region Main Warehouses from its Remote View
        regionsMainQuery = self.__regionsMainNodesQuery()

        # Execute Query and Fetch Items (Nodes)
        try:
            self.__items = self.__c.execute(regionsMainQuery).fetchall()

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

        # Add Nodes with Some Style Attributes (when Drawing)
        else:
            self.__DiGraph.add_nodes_from(
                nodeList,
                color=GRAPH_REGION_MAIN_WAREHOUSE_NODE_COLOR,
                size=GRAPH_REGION_MAIN_WAREHOUSE_NODE_SIZE,
                edgecolors=GRAPH_WAREHOUSE_NODE_EDGE_COLOR,
            )

    def setCitiesMainNodes(self, draw: bool = False):
        """
        Method that Add All the Cities Main Warehouse Nodes to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes
        :return: Nothing
        :rtype: None
        """

        # Query to Get All Cities Main Warehouses from its Remote View
        citiesMainQuery = self.__citiesMainNodesQuery()

        # Execute Query and Fetch Items (Nodes)
        try:
            self.__items = self.__c.execute(citiesMainQuery).fetchall()

        except Exception as err:
            print(err)

        # Nodes
        nodeList = []

        # Add City Main Warehouse Nodes
        for node in self.__items:
            # Get Node Attributes from Tuple
            _, warehouseId = node

            nodeList.append(warehouseId)

        # Add Nodes
        if not draw:
            self.__DiGraph.add_nodes_from(nodeList)

        # Add Nodes with Some Style Attributes (when Drawing)
        else:
            self.__DiGraph.add_nodes_from(
                nodeList,
                color=GRAPH_CITY_MAIN_WAREHOUSE_NODE_COLOR,
                size=GRAPH_CITY_MAIN_WAREHOUSE_NODE_SIZE,
                edgecolors=GRAPH_WAREHOUSE_NODE_EDGE_COLOR,
            )

    def setCitiesNodes(self, draw: bool = False):
        """
        Method that Add All the Cities Warehouse Nodes (doesn't Include the Cities Main Warehouse Nodes) to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes
        :return: Nothing
        :rtype: None
        """

        # Query to Get All Cities Warehouses from its Remote View
        citiesQuery = self.__citiesNodesQuery()

        # Execute Query and Fetch Items (Nodes)
        try:
            self.__items = self.__c.execute(citiesQuery).fetchall()

        except Exception as err:
            print(err)

        # Nodes
        nodeList = []

        # Add City Warehouse Nodes
        for node in self.__items:
            # Get Node Attributes from Tuple
            _, warehouseId = node

            nodeList.append(warehouseId)

        # Add Nodes
        if not draw:
            self.__DiGraph.add_nodes_from(nodeList)

        # Add Nodes with Some Style Attributes (when Drawing)
        else:
            self.__DiGraph.add_nodes_from(
                nodeList,
                color=GRAPH_CITY_WAREHOUSE_NODE_COLOR,
                size=GRAPH_CITY_WAREHOUSE_NODE_SIZE,
                edgecolors=GRAPH_WAREHOUSE_NODE_EDGE_COLOR,
            )

    def setConnectionsNodeEdges(self, draw: bool = False):
        """
        Method that Add All the Region Main, Cities Main and Cities Warehouse Nodes Edges to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes Edges
        :return: Nothing
        :rtype: None
        """

        # Query to Get All Warehouses Connections from its Remote View
        connsQuery = self.__connectionsNodeEdgesQuery()

        # Execute Query and Fetch Items (Nodes)
        try:
            self.__items = self.__c.execute(connsQuery).fetchall()

        except Exception as err:
            print(err)

        # Add Nodes Edges
        for node in self.__items:
            # Get Node Edge Attributes from Tuple
            (
                warehouseFromId,
                warehouseToId,
                routeDistance,
                connType,
            ) = node

            # Add Edge Connection
            if not draw:
                self.__DiGraph.add_edge(
                    warehouseFromId,
                    warehouseToId,
                    length=routeDistance,
                    weight=routeDistance,
                )

            # Add Nodes Edges with Some Style Attributes (when Drawing)

            # Add Edge of Connection Type 'Region'
            elif connType == CONN_TYPE_REGION:
                self.__DiGraph.add_edge(
                    warehouseFromId,
                    warehouseToId,
                    weight=routeDistance,
                    weightAttraction=1 / routeDistance,
                    length=routeDistance,
                    edge_color=GRAPH_WAREHOUSE_EDGE_COLOR,
                    width=GRAPH_REGION_MAIN_WAREHOUSE_WIDTH,
                )

            # Add Edge of Connection Type 'City'
            elif connType == CONN_TYPE_CITY:
                self.__DiGraph.add_edge(
                    warehouseFromId,
                    warehouseToId,
                    weight=routeDistance,
                    weightAttraction=1000000 / routeDistance,
                    edge_color=GRAPH_WAREHOUSE_EDGE_COLOR,
                    width=GRAPH_REGION_MAIN_WAREHOUSE_WIDTH,
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

        # Get Nodes Edges Attributes
        widths = list(self.__getEdgesValue("width"))
        edgeColor = self.__getEdgesValue("edge_color")

        # Drawing Arguments
        args = {
            "arrows": GRAPH_WITH_ARROWS,
            "node_color": colors,
            "node_size": sizes,
            "edgecolors": edgeColors,
            "width": widths,
            "edge_color": edgeColor,
            "with_labels": GRAPH_WITH_LABELS,
            "font_color": GRAPH_FONT_COLOR,
            "font_size": GRAPH_FONT_SIZE,
            "font_weight": GRAPH_FONT_WEIGHT,
        }

        # Draw and Store Graphs in Different Styles

        # Circular Layout
        nx.draw(self.__DiGraph, pos=self.__circular, **args)
        self.__storeGraph(RUSHWGRAPH_CIRCULAR_FILENAME)

        # Kamada Kawai Layout
        nx.draw(self.__DiGraph, pos=self.__kamada, **args)
        self.__storeGraph(RUSHWGRAPH_KAMADA_FILENAME)

        # Random Layout
        nx.draw(self.__DiGraph, pos=self.__random, **args)
        self.__storeGraph(RUSHWGRAPH_RANDOM_FILENAME)

        # Shell Layout
        nx.draw(self.__DiGraph, pos=self.__shell, **args)
        self.__storeGraph(RUSHWGRAPH_SHELL_FILENAME)

        # Spectral Layout
        nx.draw(self.__DiGraph, pos=self.__spectral, **args)
        self.__storeGraph(RUSHWGRAPH_SPECTRAL_FILENAME)

        # Spring Layout
        nx.draw(self.__DiGraph, pos=self.__spring, **args)
        self.__storeGraph(RUSHWGRAPH_SPRING_FILENAME)
