-- user: id, name, passwordHash, cookie
-- INSERT INTO user VALUES (...)

-- workspace: id, name, userId, url
INSERT INTO workspace VALUES (1, 'Nest of Crayons', NULL, '0.12345');

-- workspaceConstituent: id, workspaceId, npcId, encounterId, monsterGroupId
INSERT INTO workspaceConstituent VALUES (1, 1, NULL, NULL, 1);
-- monsterGroup: id, stencilId, name, image
INSERT INTO monsterGroup VALUES (1, 501, NULL, NULL);
-- groupie: id, monsterGroupId, hitPoints, alignment, name, gear, spells
INSERT INTO groupie VALUES (1, 1, NULL, NULL, NULL, NULL, NULL);

INSERT INTO workspaceConstituent VALUES (2, 1, NULL, NULL, 2);
INSERT INTO monsterGroup VALUES (2, 379, NULL, NULL);
INSERT INTO groupie VALUES (2, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (3, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (4, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (5, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (6, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (7, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (8, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (9, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (10, 2, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (11, 2, NULL, NULL, NULL, NULL, NULL);

INSERT INTO workspaceConstituent VALUES (3, 1, NULL, NULL, 3);
INSERT INTO monsterGroup VALUES (3, 554, NULL, NULL);
INSERT INTO groupie VALUES (12, 3, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (13, 3, NULL, NULL, 'Mr. Bonypants', NULL, NULL);
INSERT INTO groupie VALUES (14, 3, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (15, 3, NULL, NULL, NULL, NULL, NULL);

-- INSERT INTO workspaceConstituent VALUES (3, 'Phase Ghoul', 1001, NULL, 1);

INSERT INTO workspaceConstituent VALUES (4, 1, NULL, 1, NULL);
-- encounter: id, name
INSERT INTO encounter VALUES (1, 'SW corner of graveyard');

INSERT INTO workspaceConstituent VALUES (5, 1, 1, NULL, NULL);
-- npc: id, name, stencilId, classes, gear, spells, image
INSERT INTO npc VALUES (1, 'Munnig', 390, 'Ftr:4/Rog:2', NULL, NULL, NULL);

