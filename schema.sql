-- schema.sql
DROP TABLE IF EXISTS volunteers;

CREATE TABLE volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    age INTEGER,
    city TEXT,
    status TEXT,
    institute TEXT,
    reason TEXT
);
