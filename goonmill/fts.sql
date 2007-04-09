--
-- Full-text search table
--

DROP TABLE monster_text;
CREATE TABLE monster_text (
    id INTEGER REFERENCES monster(id),
    name text,
    data text
);

INSERT INTO monster_text SELECT id, name, name || ' ' || family || ' ' || type || ' ' || full_text FROM monster;
