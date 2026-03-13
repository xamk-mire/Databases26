-- Seed order tracking history for existing orders
-- Run this after applying the AddOrderTracking migration (e.g. via psql or pgAdmin)

-- Order 1: Full tracking history (PENDING -> CONFIRMED -> SHIPPED)
INSERT INTO order_tracking (order_id, status, recorded_at, notes)
VALUES
  (1, 'PENDING', '2024-01-15 10:00:00', 'Order placed'),
  (1, 'CONFIRMED', '2024-01-16 09:00:00', 'Payment received'),
  (1, 'SHIPPED', '2024-01-18 14:30:00', 'Dispatched via standard delivery');

UPDATE orders SET order_status = 'SHIPPED' WHERE order_id = 1;

-- Order 2: PENDING -> CONFIRMED
INSERT INTO order_tracking (order_id, status, recorded_at, notes)
VALUES
  (2, 'PENDING', '2024-02-20 11:15:00', 'Order placed'),
  (2, 'CONFIRMED', '2024-02-21 08:00:00', 'Processing');

UPDATE orders SET order_status = 'CONFIRMED' WHERE order_id = 2;

-- Orders 3, 4, 5: Initial PENDING only
INSERT INTO order_tracking (order_id, status, recorded_at, notes)
VALUES
  (3, 'PENDING', '2024-01-22 16:45:00', 'Order placed'),
  (4, 'PENDING', '2024-02-10 09:30:00', 'Order placed'),
  (5, 'PENDING', '2024-03-01 13:00:00', 'Order placed');
