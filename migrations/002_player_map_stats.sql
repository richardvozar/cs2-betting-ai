-- Additive schema expansion for per-player, per-map statistics.
ALTER TABLE players ADD COLUMN IF NOT EXISTS slug VARCHAR(160);
ALTER TABLE players ADD COLUMN IF NOT EXISTS country_code VARCHAR(8);
ALTER TABLE players ADD COLUMN IF NOT EXISTS primary_role VARCHAR(60);

ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS external_id VARCHAR(120);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS plus_minus INTEGER;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS headshot_percent NUMERIC(6, 2);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS first_kills INTEGER;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS first_deaths INTEGER;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS rating_version VARCHAR(40);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS ct_kills INTEGER;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS ct_deaths INTEGER;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS ct_adr NUMERIC(7, 2);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS ct_kast NUMERIC(6, 2);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS ct_rating NUMERIC(5, 2);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS t_kills INTEGER;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS t_deaths INTEGER;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS t_adr NUMERIC(7, 2);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS t_kast NUMERIC(6, 2);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS t_rating NUMERIC(5, 2);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS side_data_available BOOLEAN;
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS data_quality VARCHAR(40);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS confidence VARCHAR(40);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS confidence_score NUMERIC(5, 4);
ALTER TABLE player_map_stats ADD COLUMN IF NOT EXISTS source_payload JSONB;
ALTER TABLE player_map_stats ALTER COLUMN team_id DROP NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS ix_player_map_stats_external_id
ON player_map_stats (external_id)
WHERE external_id IS NOT NULL;
