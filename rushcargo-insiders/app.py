import asyncio
import time
import threading

from flask import Flask, request, jsonify

from lib.graph.warehouses import RushWGraph, rushWGraph

from lib.model.database import initAsyncPool, AsyncPool

app = Flask("RushCargo")

# Initialize Database
apool, _, port, _ = initAsyncPool()

# Open Remote Database Connection Pool
asyncio.run(apool.openPool())

# Initialize RushWGraph Class
rushWGraph = asyncio.run(RushWGraph.createFromApp(apool, False))

# Time to Wait between Graphs Updates
UPDATE_TIME = 60
WAIT_BUSY_TIME = 0.05


@app.route("/graph-calc/<building_type>")
def graph_calc(building_type: str):
    """
    GET Method for Route Calculations

    :param str building_type: Building Type
    """

    # Check 'building_type' Parameter
    if building_type == "warehouses":
        # Get Request Arguments
        try:
            warehouseFromId = request.args.get("fromId")
            warehouseToId = request.args.get("toId")

        # Bad Route Request
        except:
            return (
                "Bad Warehouse Route Request. Couldn't Process Warehouse IDs",
                400,
            )

        # Check if the Nodes can be Found
        try:
            # Wait Until the Graph is Available
            while rushWGraph.isBusy():
                time.sleep(WAIT_BUSY_TIME)

            # Check if there's a Path between the Warehouses
            if rushWGraph.hasPath(warehouseFromId, warehouseToId):
                # Get Shortest Route
                nodes, routeDistance = rushWGraph.getShortest(
                    warehouseFromId, warehouseToId
                )

                # Return JSON with Route

                return (jsonify({"nodes": nodes, "distance": routeDistance}), 200)

            # Route not Found
            else:
                return "Route not Found between Warehouse Nodes", 404

        except:
            return "Bad Warehouse Route Request. Node not Found", 400

    # Bad Request
    else:
        return (
            f"Bad Graph Calculation Request. Building of Type '{building_type}' not Found",
            400,
        )


async def updateGraphs(apool: AsyncPool, updateTime: int) -> None:
    """
    Function to Update the Graphs

    :param AsyncPool apool: Asynchronous Connection Pool with the Remote Database
    :param int updateTime: Interval of Time in Seconds between the Warehouses Graph Updates
    """

    while True:
        t1 = updateTime

        # Countdown
        while t1 > 0:
            time.sleep(1)
            t1 -= 1

        # Update Graphs
        await asyncio.gather(rushWGraph.update(apool, app.logger))


def graphEventsHandler(apool: AsyncPool, updateTime: int) -> None:
    """
    Main Handler of the Warehouses Graph

    :param AsyncPool apool: Asynchronous Connection Pool with the Remote Database
    :param int updateTime: Interval of Time in Seconds between the Warehouses Graph Updates
    """

    # Graph Updater
    asyncio.run(updateGraphs(apool, updateTime))


# Call the Update Function with Multithreading
threadUpdate = threading.Thread(
    target=graphEventsHandler,
    args=(apool, UPDATE_TIME),
    daemon=True,
    name="update-rushwgraph",
)
threadUpdate.start()

if __name__ == "__main__":
    # Initialize Flask Server
    app.run(port=port)

    # Close Remote Database Connection Pool
    # asyncio.run(apool.closePool())
