-- Populate DB with sample tables for testing
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE
);
CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    price DECIMAL(10, 2)
);
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    product_id INT REFERENCES products(id),
    quantity INT
);
-- Additional tables for testing multithreading
CREATE TABLE categories (id SERIAL PRIMARY KEY, name VARCHAR(100));
CREATE TABLE suppliers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100),
    contact VARCHAR(100)
);
CREATE TABLE inventory (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    stock INT
);
CREATE TABLE reviews (
    id SERIAL PRIMARY KEY,
    product_id INT REFERENCES products(id),
    user_id INT REFERENCES users(id),
    rating INT,
    comment TEXT
);
CREATE TABLE logs (
    id SERIAL PRIMARY KEY,
    action VARCHAR(100),
    timestamp TIMESTAMP DEFAULT NOW()
);
CREATE TABLE settings (
    id SERIAL PRIMARY KEY,
    key VARCHAR(100),
    value TEXT
);
CREATE TABLE notifications (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    message TEXT,
    read BOOLEAN DEFAULT FALSE
);
CREATE TABLE payments (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    amount DECIMAL(10, 2),
    method VARCHAR(50)
);
CREATE TABLE addresses (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    street VARCHAR(200),
    city VARCHAR(100),
    zip VARCHAR(20)
);
CREATE TABLE coupons (
    id SERIAL PRIMARY KEY,
    code VARCHAR(50),
    discount DECIMAL(5, 2)
);
INSERT INTO users (name, email)
VALUES ('Alice', 'alice@example.com'),
    ('Bob', 'bob@example.com'),
    ('Charlie', 'charlie@example.com'),
    ('Diana', 'diana@example.com'),
    ('Eve', 'eve@example.com');
INSERT INTO products (name, price)
VALUES ('Widget', 10.99),
    ('Gadget', 25.50),
    ('Tool', 15.75),
    ('Device', 30.00),
    ('Accessory', 5.99);
INSERT INTO orders (user_id, product_id, quantity)
VALUES (1, 1, 2),
    (2, 2, 1),
    (3, 3, 3),
    (4, 4, 1),
    (5, 5, 2);
INSERT INTO categories (name)
VALUES ('Electronics'),
    ('Tools'),
    ('Accessories');
INSERT INTO suppliers (name, contact)
VALUES ('Supplier A', 'contact@a.com'),
    ('Supplier B', 'contact@b.com');
INSERT INTO inventory (product_id, stock)
VALUES (1, 100),
    (2, 50),
    (3, 75),
    (4, 25),
    (5, 200);
INSERT INTO reviews (product_id, user_id, rating, comment)
VALUES (1, 1, 5, 'Great!'),
    (2, 2, 4, 'Good value');
INSERT INTO logs (action)
VALUES ('User login'),
    ('Order placed');
INSERT INTO settings (key, value)
VALUES ('theme', 'dark'),
    ('language', 'en');
INSERT INTO notifications (user_id, message)
VALUES (1, 'Order shipped'),
    (2, 'Payment received');
INSERT INTO payments (order_id, amount, method)
VALUES (1, 21.98, 'Credit Card');
INSERT INTO addresses (user_id, street, city, zip)
VALUES (1, '123 Main St', 'Anytown', '12345');
INSERT INTO coupons (code, discount)
VALUES ('SAVE10', 10.00),
    ('NEWUSER', 5.00);