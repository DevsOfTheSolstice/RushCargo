import asyncio
import time
import threading

from flask import Flask, request, jsonify

from lib.graph.warehouses import RushWGraph, rushWGraph

from lib.model.database import initAsyncPool

app = Flask("RushCargo")

# Time to Wait between Graphs Updates
UPDATE_TIME = 300
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


async def updateGraphs(apool, updateTime: int) -> None:
    """
    Function to Update the Graphs

    :param apool: Asynchronous Connection Pool with the Remote Database
    :param int updateTime: Interval of Time in Seconds between the Warehouses Graph Updates
    """

    async with apool.connection() as aconn:
        while True:
            t1 = updateTime

            # Countdown
            while t1 > 0:
                time.sleep(1)
                t1 -= 1

            # Update Graphs
            app.logger.info("Rush Cargo Warehouses Graph is being Updated")
            await asyncio.gather(rushWGraph.update(aconn))
            app.logger.info("Rush Cargo Warehouses Graph has been Updated")


def graphEventsHandler(apool, updateTime: int) -> None:
    """
    Main Handler of the Warehouses Graph

    :param apool: Asynchronous Connection Pool with the Remote Database
    :param int updateTime: Interval of Time in Seconds between the Warehouses Graph Updates
    """

    # Graph Updater
    asyncio.run(updateGraphs(apool, updateTime))


if __name__ == "__main__":
    # Initialize Database
    apool, _, _ = initAsyncPool()

    print(1)

    # Initialize RushWGraph Class
    rushWGraph = asyncio.run(RushWGraph.createFromApp(apool, False))

    print(2)

    # Call the Update Function with Multithreading
    threadUpdate = threading.Thread(
        target=graphEventsHandler,
        args=(apool, UPDATE_TIME),
        daemon=True,
        name="update-rushwgraph",
    )
    threadUpdate.start()

    # Initialize Flask Server
    app.run(debug=True, port=5000, use_reloader=False)

    # Close Remote Database Connection Pool
    asyncio.run(apool.closePool())
