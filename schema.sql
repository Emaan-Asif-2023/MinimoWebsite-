
DROP TABLE IF EXISTS volunteers;

CREATE TABLE volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL CHECK (length(name) > 0),
    email TEXT NOT NULL CHECK (length(email) > 0),
    phone TEXT NOT NULL CHECK (length(phone) > 0),
    age INTEGER NOT NULL CHECK (age > 0),
    city TEXT NOT NULL CHECK (length(city) > 0),
    status TEXT NOT NULL CHECK (length(status) > 0),
    institute TEXT NOT NULL CHECK (length(institute) > 0),
    reason TEXT NOT NULL CHECK (length(reason) > 0)
);
