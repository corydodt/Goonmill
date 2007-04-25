BEGIN TRANSACTION;
CREATE TABLE ability (
  id INTEGER PRIMARY KEY,
  name varchar(100) NOT NULL default '',
  choice varchar(255) default '',
  benefit longtext,
  full_text longtext,
  reference varchar(255) default ''
);
INSERT INTO "ability" VALUES(1, 'Ability Drain', 'One ability score (Str, Dex, Con, Int, Wis, Cha)', 'This effect permanently reduces a living opponent’s ability score when the creature hits with a melee attack.', NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#abilityDrain');
INSERT INTO "ability" VALUES(2, 'Ability Damage', 'One ability score (Str, Dex, Con, Int, Wis, Cha)', 'This attack damages an opponent’s ability score.  Points lost to ability damage return at the rate of 1 point per day (or double that if the character gets complete bed rest) to each damaged ability, and the spells lesser restoration and restoration offset ability damage as well.', NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#abilityDamage');
INSERT INTO "ability" VALUES(3, 'Alternate Form', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#alternateForm');
INSERT INTO "ability" VALUES(4, 'Antimagic', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#antimagic');
INSERT INTO "ability" VALUES(5, 'Blindsight', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#blindsightAndBlindsense');
INSERT INTO "ability" VALUES(6, 'Blindsense', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#blindsightAndBlindsense');
INSERT INTO "ability" VALUES(7, 'Breath Weapon', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#breathWeapon');
INSERT INTO "ability" VALUES(8, 'Change Shape', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#changeShape');
INSERT INTO "ability" VALUES(9, 'Charm', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#charmAndCompulsion');
INSERT INTO "ability" VALUES(10, 'Compulsion', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#charmAndCompulsion');
INSERT INTO "ability" VALUES(11, 'Cold Immunity', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#coldImmunity');
INSERT INTO "ability" VALUES(12, 'Constrict', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#constrict');
INSERT INTO "ability" VALUES(13, 'Damage Reduction', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#damageReduction');
INSERT INTO "ability" VALUES(14, 'Darkvision', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#darkvision');
INSERT INTO "ability" VALUES(15, 'Death Attacks', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#deathAttacks');
INSERT INTO "ability" VALUES(16, 'Disease', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#disease');
INSERT INTO "ability" VALUES(17, 'Energy Drain', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#energyDrainAndNegativeLevels');
INSERT INTO "ability" VALUES(18, 'Etherealness', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#etherealness');
INSERT INTO "ability" VALUES(19, 'Evasion', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#evasionAndImprovedEvasion');
INSERT INTO "ability" VALUES(20, 'Improved Evasion', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#evasionAndImprovedEvasion');
INSERT INTO "ability" VALUES(21, 'Fast Healing', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#fastHealing');
INSERT INTO "ability" VALUES(22, 'Fear Aura', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#fearAura');
INSERT INTO "ability" VALUES(23, 'Frightful Presence', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#frightfulPresence');
INSERT INTO "ability" VALUES(24, 'Fire Immunity', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#fireImmunity');
INSERT INTO "ability" VALUES(25, 'Gaseous Form', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#gaseousForm');
INSERT INTO "ability" VALUES(26, 'Gaze Attack', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#gazeAttacks');
INSERT INTO "ability" VALUES(27, 'Improved Grab', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#improvedGrab');
INSERT INTO "ability" VALUES(28, 'Incorporeality', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#incorporeality');
INSERT INTO "ability" VALUES(29, 'Invisibility', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#invisibility');
INSERT INTO "ability" VALUES(30, 'Low-Light Vision', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#lowLightVision');
INSERT INTO "ability" VALUES(31, 'Paralysis', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#paralysis');
INSERT INTO "ability" VALUES(32, 'Poison', 'A type of poison', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#poison');
INSERT INTO "ability" VALUES(33, 'Polymorph', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#polymorph');
INSERT INTO "ability" VALUES(34, 'Pounce', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#pounce');
INSERT INTO "ability" VALUES(35, 'Powerful Charge', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#powerfulCharge');
INSERT INTO "ability" VALUES(36, 'Psionics', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#psionics');
INSERT INTO "ability" VALUES(37, 'Rake', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#rake');
INSERT INTO "ability" VALUES(38, 'Ray Attack', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#rays');
INSERT INTO "ability" VALUES(39, 'Regeneration', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#regeneration');
INSERT INTO "ability" VALUES(40, 'Resistance to Energy', 'A form of energy', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#resistanceToEnergy');
INSERT INTO "ability" VALUES(41, 'Scent', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#scent');
INSERT INTO "ability" VALUES(42, 'Sonic Attacks', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#sonicAttacks');
INSERT INTO "ability" VALUES(43, 'Spell Immunity', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#spellImmunity');
INSERT INTO "ability" VALUES(44, 'Spell Resistance', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#spellResistance');
INSERT INTO "ability" VALUES(45, 'Spells', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#spells');
INSERT INTO "ability" VALUES(46, 'Summon', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#summon');
INSERT INTO "ability" VALUES(47, 'Swallow Whole', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#swallowWhole');
INSERT INTO "ability" VALUES(48, 'Telepathy', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#telepathy');
INSERT INTO "ability" VALUES(49, 'Trample', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#trample');
INSERT INTO "ability" VALUES(50, 'Tremorsense', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#tremorsense');
INSERT INTO "ability" VALUES(51, 'Turn Resistance', '', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#turnResistance');
INSERT INTO "ability" VALUES(52, 'Vulnerability to Energy', 'A type of energy', NULL, NULL, 'http://www.d20srd.org/srd/specialAbilities.htm#vulnerabilitytoEnergy');
CREATE INDEX ability_name_idx ON ability(name);
COMMIT;
