from copy import deepcopy

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
    Graph Class that Represents Rush Cargo Warehouse Connections
    """

    # Graph
    __DiGraph = None
    __draw = None
    __allWarehouses = None
    __nodesToCheck = None

    # Graph Layouts
    __circular = None
    __kamada = None
    # __random = None
    __shell = None
    # __spectral = None
    __spring = None

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
        self.__draw = draw

        # Save Database Connection Information
        self.__c = remoteCursor

        # Set Nodes
        self.__setRegionsMainNodes(draw)
        self.__setCitiesMainNodes(draw)
        self.__setCitiesNodes(draw)

        # Set Nodes Edges
        self.__setConnectionsNodeEdges(draw)

    def __getWarehousesDict(
        self, warehousesList: list[tuple[str, str, str, str, int]]
    ) -> dict:
        """
        Method to Get a Dictionary that Contains All the Warehouses ID, the Country, Region and City where it's Located and its Building Name

        :param list warehousesList: List of Fetched Warehouses
        :return: Dictionary that Contains All the Warehouses ID, the Locations Name where it's Located and its Building Name
        :rtype: dict
        """

        warehousesDict = {}

        for w in warehousesList:
            countryName, regionName, cityName, buildingName, buildingId = w

            warehousesDict[buildingId] = [
                countryName,
                regionName,
                cityName,
                buildingName,
            ]

        return warehousesDict

    def __getWarehouseConnsDicts(
        self, warehouseConnsList: list[tuple[int, int, int, str]]
    ) -> dict:
        """
        Method to Get a Warehouse Dictionary with its Connections Dictionaries, that Contain the Warehouse Sender and Receiver ID, the Route Distance and the Connection Type

        :param list warehouseConnList: List of Fetched Warehouse Connections
        :return: Warehouse Dictionary with its Connections Dictionaries that Contain the Warehouse IDs that are Participating in the Given Connection, the Route Distance and the Connection Type
        :rtype: dict
        """

        warehouseConnsDicts = {}

        for w in warehouseConnsList:
            warehouseFromId = w[0]
            warehouseToId = w[1]
            routeDistance = w[2]
            connType = w[3]

            # Check if the Given ID Exists in the Main Dictionary
            if warehouseFromId not in warehouseConnsDicts:
                warehouseConnsDicts[warehouseFromId] = {}

            warehouseConnsDicts[warehouseFromId][warehouseToId] = [
                routeDistance,
                connType,
            ]

        return warehouseConnsDicts

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

    def __allNodesQuery(self):
        """
        Method that Retuns a Query to Get All the Warehouse Nodes from its Remote View

        :return: SQL Query Get All the Warehouses from its Remote View
        :rtype: Composed
        """

        return sql.SQL(
            "SELECT {warehouseIdField} FROM {connectionsSchemeName}.{warehousesViewName}"
        ).format(
            warehouseIdField=sql.Identifier(WAREHOUSES_ID),
            connectionsSchemeName=sql.Identifier(CONNECTIONS_SCHEME_NAME),
            warehousesViewName=sql.Identifier(WAREHOUSES_VIEW_NAME),
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

    def __storeGraph(
        self, baseFileName: str, layout: str, level: str, locationId: int
    ) -> None:
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

    def __setRegionsMainNodes(self, draw: bool = False, update: bool = False) -> None:
        """
        Method that Add All the Regions Main Warehouse Nodes to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes
        :param bool update: Specificies wheter to Update or not the Nodes
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

        # Get Warehouses Dictionary from Fetched Items
        warehousesDict = self.__getWarehousesDict(self.__items)
        print(self.__DiGraph.nodes)

        if update and bool(self.__nodesToCheck):
            nodesChecked = []

            # Remove Nodes that are not inside the Warehouses Dictionary
            for key, value in self.__nodesToCheck.items():
                if key not in warehousesDict:
                    continue

                # Check if It's with the Same Connection Type
                elif value != REGIONS_MAIN:
                    try:
                        self.__DiGraph.remove_node(key)
                        nodesChecked.append(key)

                    except:
                        continue

                # Nothing to Modify
                else:
                    nodesChecked.append(key)
                    warehousesDict.pop(key)

            # Remove Nodes from the Warehouse Nodes to Check Dictionary
            for key in nodesChecked:
                self.__nodesToCheck.pop(key)

        print(len(warehousesDict))

        # Check if the Warehouses Dictionary is Empty
        if not bool(warehousesDict):
            return

        # Add Region Main Warehouse Nodes
        for key, value in warehousesDict.items():

            # Add Node
            if not draw:
                self.__DiGraph.add_node(
                    key,
                    nodeType=REGIONS_MAIN,
                    country=unidecode(value[0]),
                    region=unidecode(value[1]),
                    city=unidecode(value[2]),
                    building=unidecode(value[3]),
                )

            # Add Node with Some Style Attributes (when Drawing)
            else:
                self.__DiGraph.add_node(
                    key,
                    nodeType=REGIONS_MAIN,
                    country=unidecode(value[0]),
                    region=unidecode(value[1]),
                    city=unidecode(value[2]),
                    building=unidecode(value[3]),
                    alpha=GRAPH_REGION_MAIN_WAREHOUSE_NODE_ALPHA,
                    color=GRAPH_REGION_MAIN_WAREHOUSE_NODE_COLOR,
                    edgecolors=GRAPH_WAREHOUSE_NODE_EDGE_COLOR,
                )

    def __setCitiesMainNodes(self, draw: bool = False, update: bool = False) -> None:
        """
        Method that Add All the Cities Main Warehouse Nodes to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes
        :param bool update: Specificies wheter to Update or not the Nodes
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

        # Get Warehouses Dictionary from Fetched Items
        warehousesDict = self.__getWarehousesDict(self.__items)

        if update and bool(self.__nodesToCheck):
            nodesChecked = []

            # Remove Nodes that are not inside the Warehouses Dictionary
            for key, value in self.__nodesToCheck.items():
                if key not in warehousesDict:
                    continue

                # Check if It's with the Same Connection Type
                elif value == CITIES:
                    try:
                        self.__DiGraph.remove_node(key)
                        nodesChecked.append(key)

                    except:
                        continue

                # Nothing to Modify
                else:
                    nodesChecked.append(key)
                    warehousesDict.pop(key)

            # Remove Node from the Warehouse Nodes to Check Dictionary
            for key in nodesChecked:
                self.__nodesToCheck.pop(key)

        print(self.__DiGraph.nodes)

        # Check if the Warehouses Dictionary is Empty
        if not bool(warehousesDict):
            return

        # Add City Main Warehouse Nodes
        for key, value in warehousesDict.items():
            # Add Node
            if not draw:
                self.__DiGraph.add_node(
                    key,
                    nodeType=CITIES_MAIN,
                    country=unidecode(value[0]),
                    region=unidecode(value[1]),
                    city=unidecode(value[2]),
                    building=unidecode(value[3]),
                )

            # Add Node with Some Style Attributes (when Drawing)
            else:
                self.__DiGraph.add_node(
                    key,
                    nodeType=CITIES_MAIN,
                    country=unidecode(value[0]),
                    region=unidecode(value[1]),
                    city=unidecode(value[2]),
                    building=unidecode(value[3]),
                    alpha=GRAPH_CITY_MAIN_WAREHOUSE_NODE_ALPHA,
                    color=GRAPH_CITY_MAIN_WAREHOUSE_NODE_COLOR,
                    edgecolors=GRAPH_WAREHOUSE_NODE_EDGE_COLOR,
                )

        print(self.__DiGraph.nodes)

    def __setCitiesNodes(self, draw: bool = False) -> None:
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

        # Get Warehouses Dictionary from Fetched Items
        warehousesDict = self.__getWarehousesDict(self.__items)

        # Check if the Warehouses Dictionary is Empty
        if not bool(warehousesDict):
            return

        print(self.__DiGraph.nodes)

        # Add City Warehouse Nodes
        for key, value in warehousesDict.items():
            # Add Node
            if not draw:
                self.__DiGraph.add_node(
                    key,
                    nodeType=CITIES,
                    country=unidecode(value[0]),
                    region=unidecode(value[1]),
                    city=unidecode(value[2]),
                    building=unidecode(value[3]),
                )

            # Add Node with Some Style Attributes (when Drawing)
            else:
                self.__DiGraph.add_node(
                    key,
                    nodeType=CITIES,
                    country=unidecode(value[0]),
                    region=unidecode(value[1]),
                    city=unidecode(value[2]),
                    building=unidecode(value[3]),
                    alpha=GRAPH_CITY_WAREHOUSE_NODE_ALPHA,
                    color=GRAPH_CITY_WAREHOUSE_NODE_COLOR,
                    edgecolors=GRAPH_WAREHOUSE_NODE_EDGE_COLOR,
                )

        print(self.__DiGraph.nodes)

    def __setConnectionsNodeEdges(
        self, draw: bool = False, update: bool = False
    ) -> None:
        """
        Method that Add All the Region Main, Cities Main and Cities Warehouse Nodes Edges to the NetworkX Graph

        :param bool draw: Specifies whether to Draw or not the Nodes Edges
        :param bool update: Specificies wheter to Update or not the Nodes Edges
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

        # Get Warehouses Dictionary with its Connections from Fetched Items
        warehousesConnsDict = self.__getWarehouseConnsDicts(self.__items)

        if update:
            # Get Dictionary with the Current Warehouse Nodes Edges
            currWarehousesConns = list(
                self.__DiGraph.edges(data=GRAPH_WAREHOUSE_CONN_TYPE)
            )

            fromId = toId = connType = None

            # Remove Nodes Edges that are not inside the Warehouses Connections Dictionary
            for c in currWarehousesConns:
                fromId = c[0]
                toId = c[1]
                connType = c[2]

                # Check if the Node has been Isolated as a Sender
                if fromId not in warehousesConnsDict:
                    self.__DiGraph.remove_edges_from(
                        [edge for edge in currWarehousesConns if edge[0] == fromId]
                    )

                # Check if the Node Edge has been Removed from the Graph
                elif toId not in warehousesConnsDict[fromId]:
                    self.__DiGraph.remove_edge(fromId, toId)

                # Check if It's with the Same Connection Type
                elif connType != warehousesConnsDict[fromId][toId][1]:
                    self.__DiGraph.remove_edge(fromId, toId)

                # Remove Node from the Warehouses Dictionary
                else:
                    warehousesConnsDict[fromId].pop(toId)

        connType = None

        # Check if the Warehouses Dictionary is Empty
        if not bool(warehousesConnsDict):
            return

        # Add Nodes Edges
        for key, value in warehousesConnsDict.items():
            for subKey, subValue in value.items():
                connType = subValue[1]

                # Add Edge Connection
                if not draw:
                    self.__DiGraph.add_edge(
                        key,
                        subKey,
                        weight=subValue[0],
                        connType=connType,
                    )

                # Add Nodes Edges with Some Style Attributes (when Drawing)

                # Add Edge of Connection Type 'Region'
                elif connType == CONN_TYPE_REGION:
                    self.__DiGraph.add_edge(
                        key,
                        subKey,
                        weight=subValue[0],
                        weightAttraction=1 / subValue[0],
                        edge_color=GRAPH_WAREHOUSE_EDGE_COLOR,
                        connType=connType,
                    )

                # Add Edge of Connection Type 'City'
                elif connType == CONN_TYPE_CITY:
                    self.__DiGraph.add_edge(
                        key,
                        subKey,
                        weight=subValue[0],
                        weightAttraction=1 / subValue[0],
                        edge_color=GRAPH_WAREHOUSE_EDGE_COLOR,
                        connType=connType,
                    )

    def update(self) -> None:
        """
        Method to Update the Graph Nodes and Edges

        :return: Nothing
        :rtype: NoneType
        """

        # Query to Get All the Warehouses from its Remote View
        allQuery = self.__allNodesQuery()

        # Execute Query and Fetch Items (Nodes)
        try:
            self.__items = self.__c.execute(allQuery).fetchall()
            self.__allWarehouses = dict.fromkeys(item[0] for item in self.__items)

        except Exception as err:
            print(err)

        # Get Current Warehouse Nodes to Check
        self.__nodesToCheck = dict(self.__DiGraph.nodes(data=GRAPH_WAREHOUSE_NODE_TYPE))

        print(dict(self.__DiGraph.nodes))
        print(self.__allWarehouses)

        # Remove Nodes that are not inside the Warehouse Dictionary
        for key, _ in self.__nodesToCheck.items():
            # Check if the Node has been Removed from the Graph
            if key not in self.__allWarehouses:
                self.__DiGraph.remove_node(key)

        print(self.__DiGraph.nodes)

        # Set Nodes
        self.__setRegionsMainNodes(self.__draw, True)
        self.__setCitiesMainNodes(self.__draw, True)
        self.__setCitiesNodes(self.__draw)

        # Set Nodes Edges
        self.__setConnectionsNodeEdges(self.__draw, True)

        print(1)
        print(self.__DiGraph.nodes)
        input("adjfdajf")

    def draw(
        self, layout: str, level: str, locationId: int, warehouseIds: list[int]
    ) -> None:
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
        print(self.__DiGraph.nodes(data=True))
        nodesDegree = self.__DiGraph.degree()

        # Remove Isolated Nodes from Warehouses IDs
        for n in nodesDegree:
            # Check Node Degree
            if n[1] != 0:
                continue

            try:
                warehouseIds.remove(n[0])

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
