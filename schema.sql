
DROP TABLE IF EXISTS volunteers;

CREATE TABLE volunteers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL ,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    age INTEGER NOT NULL CHECK (age > 0),
    city TEXT NOT NULL ,
    status TEXT NOT NULL ,
    institute TEXT NOT NULL ,
    reason TEXT NOT NULL
);
