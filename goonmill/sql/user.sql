BEGIN;

CREATE TABLE user (
    id INTEGER PRIMARY KEY,
    name varchar(100),
    passwordHash varchar(50),
    cookie varchar(100)
);

CREATE TABLE workspace (
    id INTEGER PRIMARY KEY,
    name varchar(255),
    userId INTEGER,
    url varchar(255)
);

CREATE TABLE constituent (
    id INTEGER PRIMARY KEY,
    workspaceId INTEGER,
    data longtext
);

COMMIT;
