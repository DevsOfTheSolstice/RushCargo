--INSERT INTO Shippings.Shipping_Guides (shipping_number, client_from, client_to, branch_from, branch_to, delivery_included)
--VALUES (1, 'maddog', 'dojimanoryu', 4, 5, 'true');

--INSERT INTO Shippings.Shipping_Guides (shipping_number, client_from, client_to, branch_from, branch_to, delivery_included)
--VALUES (2, 'dojimanoryu', 'maddog', 5, 4, 'true');

--INSERT INTO Orders.Orders (order_number, generated_date, generated_hour)
--VALUES (1, '2024-4-2', '11:23:54');

--INSERT INTO Orders.Orders (order_number, generated_date, generated_hour)
--VALUES (2, '2024-4-3', '12:24:55');

--INSERT INTO Orders.Automatic_Orders (order_number, admin_verification)
--VALUES (1, 'admin0');

--INSERT INTO Orders.Automatic_Orders (order_number, admin_verification)
--VALUES (2, 'admin0');

--INSERT INTO Orders.Warehouse_Transfer_Orders (order_number, trucker, warehouse_from, warehouse_to, shipping_number)
--VALUES (1, 'truckkun', 0, 1, 1);

--Branch is only to OR from a warehouse
--INSERT INTO Orders.Branch_Transfer_Order (order_number, trucker, shipping_number, warehouse, branch, withdrawal)
--VALUES (1, 'truckkun', 2, 1, 4, 'true');

INSERT INTO Shippings.Shipping_Guides (shipping_number, client_from, client_to, branch_from, branch_to, delivery_included)
VALUES (3, 'maddog', 'dojimanoryu', 4, 5, 'true');

INSERT INTO Shippings.Shipping_Guides (shipping_number, client_from, client_to, branch_from, branch_to, delivery_included)
VALUES (4, 'maddog', 'dojimanoryu', 4, 5, 'true');

INSERT INTO Orders.Orders (order_number, generated_date, generated_hour)
VALUES (3, '2024-4-2', '11:23:54');

INSERT INTO Orders.Orders (order_number, generated_date, generated_hour)
VALUES (4, '2024-4-3', '12:24:55');

INSERT INTO Orders.Automatic_Orders (order_number, admin_verification, completed_date)
VALUES (3, 'admin0', '2024-4-3');

INSERT INTO Orders.Automatic_Orders (order_number, admin_verification, completed_date)
VALUES (4, 'admin0', '2024-4-3')


