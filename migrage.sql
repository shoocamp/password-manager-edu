CREATE TABLE password
(
    id         TEXT,
    user_id    INTEGER,
    name       TEXT,
    site       TEXT,
    password   TEXT,
    created_at INTEGER,
    updated_at INTEGER,
    UNIQUE(user_id, name) ON CONFLICT FAIL
);

CREATE TABLE users
(
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    name       TEXT UNIQUE,
    password   TEXT
);
