INSERT INTO workspace VALUES (1, 'Nest of Crayons', NULL, '0.12345');

INSERT INTO constituent VALUES (1, NULL, 501, 1, 'monsterGroup', NULL, 1);
INSERT INTO monsterGroup VALUES (1);
INSERT INTO groupie VALUES (1, 1, 57, NULL, NULL, NULL);

INSERT INTO constituent VALUES (2, NULL, 379, 2, 'monsterGroup', NULL, 1);
INSERT INTO monsterGroup VALUES (2);
INSERT INTO groupie VALUES (2, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (3, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (4, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (5, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (6, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (7, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (8, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (9, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (10, 2, 12, NULL, NULL, NULL);
INSERT INTO groupie VALUES (11, 2, 12, NULL, NULL, NULL);

INSERT INTO constituent VALUES (3, '2 dead crew', 554, 3, 'monsterGroup', NULL, 1);
INSERT INTO monsterGroup VALUES (3);
INSERT INTO groupie VALUES (12, 3, 8, NULL, NULL, NULL);
INSERT INTO groupie VALUES (13, 3, 7, 'Mr. Bonypants', NULL, NULL);
INSERT INTO groupie VALUES (14, 3, 8, NULL, NULL, NULL);
INSERT INTO groupie VALUES (15, 3, 6, NULL, NULL, NULL);

-- FIXME: name for stencils should be NULL and looked up from the base
INSERT INTO constituent VALUES (4, 'Phase Ghoul', 1001, 4, 'stencil', NULL, 1);
INSERT INTO stencil VALUES (4);

INSERT INTO constituent VALUES (5, 'SW Corner of Graveyard', NULL, 5, 'encounter', NULL, 1);
INSERT INTO encounter VALUES (5);

INSERT INTO constituent VALUES (6, 'Munnig', 390, 6, 'npc', NULL, 1);
INSERT INTO npc VALUES (6, 'Ftr:4/Rog:2', NULL, NULL);

