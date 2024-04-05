import time
import threading
from lib.graph.warehouses import RushWGraph, rushWGraph
from lib.model.database import initdb
from flask import Flask, request, jsonify

app = Flask("RushCargo")

# Time to Wait between Graphs Updates
UPDATE_TIME = 60
WAIT_BUSY_TIME = 0.05


# GET Method for Route Calculations
@app.route("/graph-calc/<building_type>")
def graph_calc(building_type: str):
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


# Function to Update the Graphs
def updateGraphs(t0: int) -> None:
    while True:
        t1 = t0

        # Countdown
        while t1 > 0:
            time.sleep(1)
            t1 -= 1

        # Update Graphs
        app.logger.info("Rush Cargo Warehouses Graph is being Updated")
        rushWGraph.update()
        app.logger.info("Rush Cargo Warehouses Graph has been Updated")


if __name__ == "__main__":
    # Initialize Database
    db, _, _ = initdb()

    # Get Database Connection Cursor
    c = db.getCursor()

    # Initialize RushWGraph Class
    rushWGraph = RushWGraph(c, False)

    # Call the Update Function with Multithreading
    threadUpdate = threading.Thread(
        target=updateGraphs, args=(UPDATE_TIME,), daemon=True, name="update-rushwgraph"
    )
    threadUpdate.start()

    # Initialize Flask Server
    app.run(debug=True, port=5000, use_reloader=False)
