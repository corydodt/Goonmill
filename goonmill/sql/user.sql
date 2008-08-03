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

CREATE TABLE workspaceConstituent (
    id INTEGER PRIMARY KEY,
    workspaceId INTEGER,
    npcId INTEGER,
    encounterId INTEGER,
    monsterGroupId INTEGER
);

CREATE TABLE npc (
    id INTEGER PRIMARY KEY,
    name longtext,
    stencilId INTEGER,
    classes longtext,
    gear longtext,
    spells longtext,
    image longtext
);

CREATE TABLE encounter (
    id INTEGER PRIMARY KEY,
    name longtext
);

CREATE TABLE monsterGroup (
    id INTEGER PRIMARY KEY,
    stencilId INTEGER,
    name longtext,
    image longtext
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
