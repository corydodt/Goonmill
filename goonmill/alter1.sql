ALTER TABLE feat ADD COLUMN is_ac_feat boolean;
ALTER TABLE feat ADD COLUMN is_speed_feat boolean;
ALTER TABLE feat ADD COLUMN is_attack_option_feat boolean;
ALTER TABLE feat ADD COLUMN is_special_action_feat boolean;

UPDATE feat SET is_ac_feat='y' where name in ('Dodge', 'Mobility', 'Deflect Arrows', 'Two-Weapon Defense');

UPDATE feat SET is_speed_feat='y' where name in ('Spring Attack', 'Ride-by Attack', 'Shot on the Run', 'Run');

UPDATE feat SET is_attack_option_feat='y' where name in ('Blind-Fight', 'Cleave', 'Combat Reflexes', 'Far Shot', 'Great Cleave', 'Improved Bull Rush', 'Improved Disarm', 'Improved Feint', 'Improved Overrun', 'Improved Precise Shot', 'Improved Sunder', 'Improved Trip', 'Mounted Combat', 'Point Blank Shot', 'Power Attack', 'Powerful Charge', 'Precise Shot', 'Quick Draw', 'Rapid Reload', 'Spirited Charge', 'Stunning Fist', 'Trample', 'Whirlwind Attack');
-- ; metamagic feats (if the creature casts spontaneously)
-- note: Powerful Charge was not in SRD database

UPDATE feat SET is_special_action_feat='y' where name in ('Snatch Arrows');
