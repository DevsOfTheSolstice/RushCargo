--Stat complete year
SELECT 
COUNT(*) AS total_trips,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 1) AS January,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 2) AS February,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 3) AS March,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 4) AS April,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 5) AS May,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 6) AS June,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 7) AS July,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 8) AS August,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 9) AS September,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 10) AS October,
     COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 11) AS November,
    COUNT(*) FILTER (WHERE EXTRACT(MONTH FROM completed_date) = 12) AS December
 FROM
     Orders.Automatic_Orders
WHERE
    EXTRACT(YEAR FROM completed_date) = 2024;

--Stat total orders in a year
  SELECT
    COUNT(*) AS total_trips
FROM
    Orders.Automatic_Orders
WHERE
    EXTRACT(YEAR FROM completed_date) = 2024;

--Stat orders in a MONTH

SELECT 
    COUNT(*) AS total_trips
FROM 
    Orders.Automatic_Orders
WHERE
    EXTRACT(MONTH FROM completed_date) = 1

--Stat orders in a Day

SELECT 
    COUNT(*) AS total_trips
FROM 
    Automatic_Orders
WHERE 
    EXTRACT(DAY FROM completed_date) = 1

--Query for the routes

SELECT warehouse_routes.*, branch_routes.*
        FROM Orders.Warehouse_Transfer_Orders AS warehouse_routes
        FULL OUTER JOIN Orders.Branch_Transfer_Order AS branch_routes
        ON warehouse_routes.order_number = branch_routes.order_number
        WHERE warehouse_routes.trucker = 'truckkun'
        OR branch_routes.trucker = 'truckkun'

--Query for reject

UPDATE orders.Warehouse_Transfer_Orders
    SET rejected = true
    WHERE order_number = 0

UPDATE orders.Branch_Transfer_Order
    SET rejected = true
    WHERE order_number = 0

