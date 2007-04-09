ALTER TABLE feat ADD COLUMN is_ranged_attack_feat boolean;

UPDATE feat SET is_ranged_attack_feat='y' where name in ('Manyshot', 'Rapid Shot');
