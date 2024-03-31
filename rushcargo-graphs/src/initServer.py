from lib.graph.networkx import RushWGraph
from lib.model.database import initdb

if __name__ == "__main__":
    # Initialize Database
    db, user = initdb()

    # Get Database Connection Cursor
    c = db.getCursor()

    # Initialize RushWGraph Class
    rushWGraph = RushWGraph(c, False)
