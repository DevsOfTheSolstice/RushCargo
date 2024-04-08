UPDATE users.users
SET gps_address='Hotel Lakeview, habitacion 302'
WHERE username='dojimanoryu';

UPDATE vehicles.drivers
SET salary=0.0001
WHERE username='driver100';

UPDATE vehicles.truckers
SET affiliated_warehouse=34
WHERE username='trucknochichi';

UPDATE vehicles.motorcyclists
SET motorcycle=NULL
WHERE username='yukari'

UPDATE users.natural_clients
SET affiliated_branch=52
WHERE username='dojimanoryu'

DELETE FROM users.natural_clients
WHERE username='dojimanoryu'

DELETE FROM users.clients
WHERE username='dojimanoryu'

DELETE FROM users.users
WHERE username='dojimanoryu'

SELECT pkgs.tracking_number, pkg_desc.content, wo.warehouse_from AS warehouse
FROM shippings.packages pkgs
INNER JOIN shippings.package_descriptions pkg_desc ON pkgs.tracking_number = pkg_desc.tracking_number
LEFT JOIN shippings.shipping_guides shg ON pkgs.shipping_number = shg.shipping_number
LEFT JOIN orders.warehouse_transfer_orders wo ON pkgs.shipping_number = wo.shipping_number
LEFT JOIN orders.automatic_orders ao ON wo.order_number = ao.order_number
WHERE pkgs.delivered = false AND ao.completed_date IS NULL
AND wo.order_number = (
    SELECT MIN(wo_inner.order_number) 
    FROM orders.warehouse_transfer_orders wo_inner
    LEFT JOIN orders.automatic_orders ao_inner ON wo_inner.order_number = ao_inner.order_number
    WHERE wo_inner.shipping_number = pkgs.shipping_number
    AND ao_inner.completed_date IS NULL
);