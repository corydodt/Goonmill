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
    name varchar(255),
    base INTEGER,
    otherId INTEGER,
    kind varchar(100),
    userId INTEGER,
    workspaceId INTEGER
);

CREATE TABLE npc (
    id INTEGER PRIMARY KEY,
    classes longtext,
    gear longtext,
    spells longtext
);

CREATE TABLE encounter (
    id INTEGER PRIMARY KEY
);

CREATE TABLE stencil (
    id INTEGER PRIMARY KEY
);

CREATE TABLE monsterGroup (
    id INTEGER PRIMARY KEY,
    name varchar(255)
);


CREATE TABLE groupie (
    id INTEGER PRIMARY KEY,
    monsterGroupId INTEGER, 
    hitPoints INTEGER,
    alignment varchar(40),
    name varchar(255),
    gear longtext,
    spells longtext
);

COMMIT;
