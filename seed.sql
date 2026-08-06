INSERT INTO warehouses (code, name, latitude, longitude, city, is_active) VALUES
('WH-JKT-01', 'Gudang Jakarta Timur', -6.2088, 106.8456, 'Jakarta', true),
('WH-SBY-01', 'Gudang Surabaya Utara', -7.2575, 112.7521, 'Surabaya', true),
('WH-BDG-01', 'Gudang Bandung Barat', -6.9175, 107.6191, 'Bandung', true);

INSERT INTO skus (code, name, unit_price, weight_kg) VALUES
('SKU-LAPTOP-PRO', 'Laptop Pro 15"', 15000000, 2.1),
('SKU-MOUSE-USB', 'Mouse USB Wireless', 250000, 0.1);

INSERT INTO stock_levels (warehouse_id, sku_id, quantity, reserved_quantity, version) VALUES
(1, 1, 50, 0, 1),
(1, 2, 200, 0, 1),
(2, 1, 30, 0, 1),
(2, 2, 150, 0, 1),
(3, 1, 10, 0, 1),
(3, 2, 80, 0, 1);