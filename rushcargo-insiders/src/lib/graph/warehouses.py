from unidecode import unidecode
import networkx as nx
import matplotlib.pyplot as plt
from psycopg import sql

from .constants import *

from ..model.constants import *

# Rush Cargo Warehouse Graph
rushWGraph = None


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

    def __getNodesValue(self, graph, key: str) -> list:
        """
        Method that Retuns a List of the Nodes Values for a Given Key

        :param graph: NetworkX Graph to Iterate
        :param str key: Key which is Used to Access the Node Attribute Value at Node's ``data``
        :return: List of Nodes Value for a Given Attribute
        :rtype: list
        """

        return [node[1][key] for node in graph.nodes(data=True)]

    def __getEdgesValue(self, graph, key: str) -> list:
        """
        Method that Retuns a List of the Nodes Edges Values for a Given Key

        :param graph: NetworkX Graph to Iterate
        :param str key: Key which is Used to Access the Edge Attribute Value
        :return: List of Edges Value for a Given Attribute
        :rtype: list
        """

        return nx.get_edge_attributes(graph, key).values()

    def __regionsMainNodesQuery(self):
        """
        Method that Retuns a Query to Get All the Regions Main Warehouse Nodes from its Remote View

        :return: SQL Query Get All the Region Main Warehouses from its Remote View
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {countryNameField}, {regionNameField}, {cityNameField}, {buildingNameField}, {warehouseIdField} FROM {connectionsSchemeName}.{regionMainWarehousesViewName}"
        ).format(
            countryNameField=sql.Identifier(COUNTRIES_NAME),
            regionNameField=sql.Identifier(REGIONS_NAME),
            cityNameField=sql.Identifier(CITIES_NAME),
            buildingNameField=sql.Identifier(BUILDINGS_NAME),
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
            "SELECT {citiesMain}.{countryNameField}, {citiesMain}.{regionNameField}, {citiesMain}.{cityNameField}, {citiesMain}.{buildingNameField}, {citiesMain}.{warehouseIdField} FROM {connectionsSchemeName}.{cityMainWarehousesViewName} AS {citiesMain} FULL OUTER JOIN {connectionsSchemeName}.{regionMainWarehousesViewName} AS {regionsMain} ON {citiesMain}.{warehouseIdField} = {regionsMain}.{warehouseIdField} WHERE {regionsMain}.{warehouseIdField} IS NULL"
        ).format(
            countryNameField=sql.Identifier(COUNTRIES_NAME),
            regionNameField=sql.Identifier(REGIONS_NAME),
            cityNameField=sql.Identifier(CITIES_NAME),
            buildingNameField=sql.Identifier(BUILDINGS_NAME),
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
            "SELECT {warehouses}.{countryNameField}, {warehouses}.{regionNameField}, {warehouses}.{cityNameField}, {warehouses}.{buildingNameField}, {warehouses}.{warehouseIdField} FROM {connectionsSchemeName}.{warehouses} AS {warehouses} FULL OUTER JOIN {connectionsSchemeName}.{cityMainWarehousesViewName} AS {citiesMain} ON {warehouses}.{warehouseIdField} = {citiesMain}.{warehouseIdField} FULL OUTER JOIN {connectionsSchemeName}.{regionMainWarehousesViewName} AS {regionsMain} ON {warehouses}.{warehouseIdField} = {regionsMain}.{warehouseIdField} WHERE {citiesMain}.{warehouseIdField} IS NULL AND {regionsMain}.{warehouseIdField} IS NULL"
        ).format(
            countryNameField=sql.Identifier(COUNTRIES_NAME),
            regionNameField=sql.Identifier(REGIONS_NAME),
            cityNameField=sql.Identifier(CITIES_NAME),
            buildingNameField=sql.Identifier(BUILDINGS_NAME),
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

    def __storeGraph(self, baseFileName: str, layout: str, level: str, locationId: int):
        """
        Method to Store the NetworkX Graph Image Locally

        :param str baseFileName: Graph Base File Name
        :param str layout: Graph Layout
        :param str level: Graph Level Command (``countries``, ``regions`` and ``cities``)
        :param int locationId: Location ID at its Remote Table where the Warehouses are Located
        :return: Nothing
        :rtype: None
        """

        # Set Graph Title
        plt.title(f"{RUSWGRAPH_TITLE}: Location ID {locationId} at {level} Table")

        # Save Graph Locally
        plt.savefig(
            f"{baseFileName}-{level}-{locationId}-{layout}.png",
            bbox_inches=RUSWGRAPH_BBOX,
            transparent=GRAPH_TRANSPARENT,
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

        # Add Region Main Warehouse Nodes
        for node in self.__items:
            # Get Node Attributes from Tuple
            countryName, regionName, cityName, buildingName, warehouseId = node

            # Add Node
            if not draw:
                self.__DiGraph.add_node(
                    warehouseId,
                    country=unidecode(countryName),
                    region=unidecode(regionName),
                    city=unidecode(cityName),
                    building=unidecode(buildingName),
                )

            # Add Node with Some Style Attributes (when Drawing)
            else:
                self.__DiGraph.add_node(
                    warehouseId,
                    country=countryName,
                    region=regionName,
                    city=cityName,
                    building=buildingName,
                    alpha=GRAPH_REGION_MAIN_WAREHOUSE_NODE_ALPHA,
                    color=GRAPH_REGION_MAIN_WAREHOUSE_NODE_COLOR,
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

        # Add City Main Warehouse Nodes
        for node in self.__items:
            # Get Node Attributes from Tuple
            countryName, regionName, cityName, buildingName, warehouseId = node

            # Add Node
            if not draw:
                self.__DiGraph.add_node(
                    warehouseId,
                    country=unidecode(countryName),
                    region=unidecode(regionName),
                    city=unidecode(cityName),
                    building=unidecode(buildingName),
                )

            # Add Node with Some Style Attributes (when Drawing)
            else:
                self.__DiGraph.add_node(
                    warehouseId,
                    country=countryName,
                    region=regionName,
                    city=cityName,
                    building=buildingName,
                    alpha=GRAPH_CITY_MAIN_WAREHOUSE_NODE_ALPHA,
                    color=GRAPH_CITY_MAIN_WAREHOUSE_NODE_COLOR,
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

        # Add City Warehouse Nodes
        for node in self.__items:
            # Get Node Attributes from Tuple
            countryName, regionName, cityName, buildingName, warehouseId = node

            # Add Node
            if not draw:
                self.__DiGraph.add_node(
                    warehouseId,
                    country=unidecode(countryName),
                    region=unidecode(regionName),
                    city=unidecode(cityName),
                    building=unidecode(buildingName),
                )

            # Add Node with Some Style Attributes (when Drawing)
            else:
                self.__DiGraph.add_node(
                    warehouseId,
                    country=countryName,
                    region=regionName,
                    city=cityName,
                    building=buildingName,
                    alpha=GRAPH_CITY_WAREHOUSE_NODE_ALPHA,
                    color=GRAPH_CITY_WAREHOUSE_NODE_COLOR,
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
                    edge_color=GRAPH_WAREHOUSE_EDGE_COLOR,
                )

            # Add Edge of Connection Type 'City'
            elif connType == CONN_TYPE_CITY:
                self.__DiGraph.add_edge(
                    warehouseFromId,
                    warehouseToId,
                    weight=routeDistance,
                    weightAttraction=1000000 / routeDistance,
                    edge_color=GRAPH_WAREHOUSE_EDGE_COLOR,
                )

    def draw(self, layout: str, level: str, locationId: int, warehouseIds: list[int]):
        """
        Method to Draw the Graph and it in a Local File

        :param str layout: Graph Layout
        :param str level: Graph Level Command (``countries``, ``regions`` and ``cities``)
        :param int locationId: Location ID at its Remote Table where the Warehouses are Located
        :param list warehouseIds: List of Warehouse Node IDs to Draw
        :return: Nothing
        :rtype: NoneType
        """

        # Draw and Store Graphs in Different Styles
        pos = None

        # Circular Layout
        if layout == LAYOUT_CIRCULAR:
            # Check if the Nodes Positions for the Circular Layout have been Calculated
            if self.__circular == None:
                self.__circular = nx.circular_layout(self.__DiGraph)

            pos = self.__circular

        # Kamada Kawai Layout
        elif layout == LAYOUT_KAMADA:
            # Check if the Nodes Positions for the Kamada Kawaii Layout have been Calculated
            if self.__kamada == None:
                self.__kamada = nx.kamada_kawai_layout(self.__DiGraph)

            pos = self.__kamada

        # Shell Layout
        elif layout == LAYOUT_SHELL:
            # Check if the Nodes Positions for the Shell Layout have been Calculated
            if self.__shell == None:
                self.__shell = nx.shell_layout(self.__DiGraph)

            pos = self.__shell

        # Spring Layout
        elif layout == LAYOUT_SPRING:
            # Check if the Nodes Positions for the Spring Layout have been Calculated
            if self.__spring == None:
                self.__spring = nx.spring_layout(
                    self.__DiGraph,
                    k=SPRING_DISTANCE,
                    iterations=SPRING_ITERATIONS,
                    weight="weightAttraction",
                )

            pos = self.__spring

        # Get Nodes Degree
        nodesDegree = self.__DiGraph.degree()

        # Remove Isolated Nodes from Warehouses IDs
        for n in nodesDegree:
            # Check Node Degree
            if n[1] != 0:
                continue

            try:
                index = warehouseIds.index(n[0])
                del warehouseIds[index]

            except ValueError:
                pass

        # Subgraph to Print
        subgraph = nx.induced_subgraph(self.__DiGraph, warehouseIds)

        # Get Nodes Attributes
        nodesAlpha = self.__getNodesValue(subgraph, "alpha")
        nodeColors = self.__getNodesValue(subgraph, "color")
        nodeEdgeColors = self.__getNodesValue(subgraph, "edgecolors")

        # Get Size Factor
        factor = None

        if level == COUNTRIES_TABLE_NAME:
            factor = GRAPH_COUNTRY_WAREHOUSE_SIZE_FACTOR

        elif level == REGIONS_TABLE_NAME:
            factor = GRAPH_REGION_WAREHOUSE_SIZE_FACTOR

        elif level == CITIES_TABLE_NAME:
            factor = GRAPH_CITY_WAREHOUSE_SIZE_FACTOR

        # Get Nodes Edges Attributes
        edgeColor = self.__getEdgesValue(subgraph, "edge_color")

        # Draw the Graph with the Given Layout, and Save it Locally
        plt.figure()
        nx.draw_networkx_nodes(
            subgraph,
            pos=pos,
            alpha=nodesAlpha,
            node_size=GRAPH_NODE_SIZE * factor,
            node_color=nodeColors,
            edgecolors=nodeEdgeColors,
        )
        nx.draw_networkx_labels(
            subgraph,
            pos=pos,
            alpha=GRAPH_FONT_ALPHA,
            font_color=GRAPH_FONT_COLOR,
            font_size=GRAPH_FONT_SIZE,
            font_weight=GRAPH_FONT_WEIGHT,
        )
        nx.draw_networkx_edges(
            subgraph,
            pos=pos,
            arrows=GRAPH_WITH_ARROWS,
            alpha=GRAPH_WAREHOUSE_EDGE_ALPHA,
            edge_color=edgeColor,
            node_size=GRAPH_NODE_SIZE * factor,
            width=GRAPH_EDGE_WIDTH * factor,
        )

        # Drawing Arguments
        self.__storeGraph(RUSHWGRAPH_FILENAME, layout, level, locationId)

    def getShortest(self, warehouseFromId: int, warehouseToId: int) -> tuple[list, int]:
        """
        Method to Get the Shortest Path between the Two Warehouse Nodes

        :return: Tuple that Contains a List of Dictionaries with the Nodes' Data, and the Route Distance
        :rtype: tuple
        """

        # Get Nodes that Constitute the Shortest Path between the Two Nodes
        nodes = nx.shortest_path(
            self.__DiGraph, int(warehouseFromId), int(warehouseToId), weight="weight"
        )

        # Get the Distance between the Two Nodes
        routeDistance = nx.shortest_path_length(
            self.__DiGraph, int(warehouseFromId), int(warehouseToId), weight="weight"
        )

        # Nodes Attributes List
        nodesAttr = []
        pos = 0

        # Get Nodes Attributes
        countryName = nx.get_node_attributes(self.__DiGraph, name="country")
        regionName = nx.get_node_attributes(self.__DiGraph, name="region")
        cityName = nx.get_node_attributes(self.__DiGraph, name="city")
        buildingName = nx.get_node_attributes(self.__DiGraph, name="building")

        for node in nodes:
            nodesAttr.append(
                {
                    "pos": pos,
                    "id": node,
                    "country": countryName[node],
                    "region": regionName[node],
                    "city": cityName[node],
                    "building": buildingName[node],
                }
            )
            pos += 1

        return nodesAttr, routeDistance

    def hasPath(self, warehouseFromId: int, warehouseToId: int) -> bool:
        """
        Method to Check if there's a Path between the Two Warehouse Nodes

        :param int warehouseFromId: Starting Node ID
        :param int warehouseToId: End Node ID
        :return: Specifies whether or not there's a Path between the Two Nodes
        :rtype: bool
        """

        return nx.has_path(self.__DiGraph, int(warehouseFromId), int(warehouseToId))
