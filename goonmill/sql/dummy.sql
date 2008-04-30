INSERT INTO workspace VALUES (1, 'Nest of Crayons', NULL, '0.12345');

INSERT INTO constituent VALUES (1, NULL, 1, 'monsterGroup', NULL, 1);
INSERT INTO monsterGroup VALUES (1, 501, NULL);
INSERT INTO groupie VALUES (1, 1, NULL, NULL, NULL, NULL, NULL);

INSERT INTO constituent VALUES (2, NULL, 2, 'monsterGroup', NULL, 1);
INSERT INTO monsterGroup VALUES (2, 379, NULL);
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

INSERT INTO constituent VALUES (4, '2 dead crew', 3, 'monsterGroup', NULL, 1);
INSERT INTO monsterGroup VALUES (3, 554, NULL);
INSERT INTO groupie VALUES (12, 3, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (13, 3, NULL, NULL, 'Mr. Bonypants', NULL, NULL);
INSERT INTO groupie VALUES (14, 3, NULL, NULL, NULL, NULL, NULL);
INSERT INTO groupie VALUES (15, 3, NULL, NULL, NULL, NULL, NULL);

-- FIXME: name for stencils should be NULL and looked up from the base
INSERT INTO constituent VALUES (3, 'Phase Ghoul', 1001, 'stencil', NULL, 1);
INSERT INTO stencil VALUES (1001);

INSERT INTO constituent VALUES (5, 'SW Corner of Graveyard', 5, 'encounter', NULL, 1);
INSERT INTO encounter VALUES (5);

INSERT INTO constituent VALUES (6, 'Munnig', 6, 'npc', NULL, 1);
INSERT INTO npc VALUES (6, 390, 'Ftr:4/Rog:2', NULL, NULL);

