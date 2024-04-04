UPDATE packages
SET holder='dojimanoryu', locker_id=0, shipping_number=NULL, delivered=true
WHERE tracking_number IN (0, 1);

DELETE FROM guide_payments;

DELETE FROM payments;

DELETE FROM shipping_guides;