import subprocess
from lib.graph.networkx import RushWGraph
from lib.model.database import initdb
from flask import Flask, request, jsonify

# RushWGraph Class
rushWGraph = None

app = Flask("RushCargo")


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


if __name__ == "__main__":
    # Initialize Database
    db, _, _ = initdb()

    # Get Database Connection Cursor
    c = db.getCursor()

    # Initialize RushWGraph Class
    rushWGraph = RushWGraph(c, False)

    # Initialize Flask Server
    app.run(debug=True, port=5000, use_reloader=False)
