--
-- Cleanups for feats
--

UPDATE feat SET is_ranged_attack_feat='y' where name in ('Manyshot', 'Rapid Shot');
