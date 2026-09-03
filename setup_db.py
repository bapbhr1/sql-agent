"""Génère la base de test ecommerce.db."""

from __future__ import annotations

import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecommerce.db")

SCHEMA = """
DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id         INTEGER PRIMARY KEY,
    name       TEXT    NOT NULL,
    email      TEXT    NOT NULL UNIQUE,
    country    TEXT    NOT NULL,
    created_at TEXT    NOT NULL
);

CREATE TABLE products (
    id       INTEGER PRIMARY KEY,
    name     TEXT    NOT NULL,
    category TEXT    NOT NULL,
    price    REAL    NOT NULL,
    stock    INTEGER NOT NULL
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL,
    product_id  INTEGER NOT NULL,
    quantity    INTEGER NOT NULL,
    total_price REAL    NOT NULL,
    order_date  TEXT    NOT NULL,
    status      TEXT    NOT NULL,
    FOREIGN KEY (user_id)    REFERENCES users (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);
"""

USERS = [
    (1, "Alice Martin", "alice@example.com", "France", "2024-01-15"),
    (2, "Bob Dupont", "bob@example.com", "France", "2024-02-03"),
    (3, "Carla Rossi", "carla@example.com", "Italie", "2024-02-20"),
    (4, "David Smith", "david@example.com", "Royaume-Uni", "2024-03-11"),
    (5, "Elena Garcia", "elena@example.com", "Espagne", "2024-04-01"),
]

PRODUCTS = [
    (1, "Clavier mécanique", "Périphériques", 89.90, 120),
    (2, "Souris ergonomique", "Périphériques", 45.50, 200),
    (3, "Écran 27 pouces 4K", "Écrans", 349.00, 35),
    (4, "Casque à réduction de bruit", "Audio", 199.99, 80),
    (5, "Webcam Full HD", "Périphériques", 59.90, 0),
    (6, "Station d'accueil USB-C", "Accessoires", 129.00, 25),
]

# (id, user_id, product_id, quantity, total_price, order_date, status)
ORDERS = [
    (1, 1, 1, 1, 89.90, "2024-05-02", "livré"),
    (2, 1, 3, 2, 698.00, "2024-05-10", "livré"),
    (3, 2, 2, 3, 136.50, "2024-05-12", "expédié"),
    (4, 3, 4, 1, 199.99, "2024-06-01", "livré"),
    (5, 4, 3, 1, 349.00, "2024-06-05", "annulé"),
    (6, 5, 6, 2, 258.00, "2024-06-15", "livré"),
    (7, 2, 1, 1, 89.90, "2024-07-01", "expédié"),
    (8, 1, 4, 1, 199.99, "2024-07-08", "livré"),
    (9, 3, 2, 2, 91.00, "2024-07-20", "livré"),
    (10, 5, 3, 1, 349.00, "2024-08-02", "en attente"),
]


def main() -> None:
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript(SCHEMA)
        conn.executemany(
            "INSERT INTO users (id, name, email, country, created_at) VALUES (?, ?, ?, ?, ?);",
            USERS,
        )
        conn.executemany(
            "INSERT INTO products (id, name, category, price, stock) VALUES (?, ?, ?, ?, ?);",
            PRODUCTS,
        )
        conn.executemany(
            "INSERT INTO orders (id, user_id, product_id, quantity, total_price, order_date, status) VALUES (?, ?, ?, ?, ?, ?, ?);",
            ORDERS,
        )
        conn.commit()
    finally:
        conn.close()

    print(f"DB: {DB_PATH} ({len(USERS)} users, {len(PRODUCTS)} products, {len(ORDERS)} orders)")


if __name__ == "__main__":
    main()
