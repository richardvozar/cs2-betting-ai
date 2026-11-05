-- Safe, repeatable schema expansion for match and map ingestion.
ALTER TABLE teams ADD COLUMN IF NOT EXISTS tag VARCHAR(40);
ALTER TABLE teams ADD COLUMN IF NOT EXISTS country_code VARCHAR(8);
ALTER TABLE teams ADD COLUMN IF NOT EXISTS world_ranking INTEGER;
ALTER TABLE teams ADD COLUMN IF NOT EXISTS vrs_ranking INTEGER;

ALTER TABLE matches ADD COLUMN IF NOT EXISTS event_external_id VARCHAR(120);
ALTER TABLE matches ADD COLUMN IF NOT EXISTS result_type VARCHAR(40);
ALTER TABLE matches ADD COLUMN IF NOT EXISTS is_forfeit BOOLEAN;
ALTER TABLE matches ADD COLUMN IF NOT EXISTS stats_eligible BOOLEAN;
ALTER TABLE matches ADD COLUMN IF NOT EXISTS unavailable_reason TEXT;

ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS status VARCHAR(40);
ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS duration_rounds INTEGER;
ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS result_type VARCHAR(40);
ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS result_status VARCHAR(40);
ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS is_forfeit BOOLEAN;
ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS stats_eligible BOOLEAN;
ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS unavailable_reason TEXT;
ALTER TABLE match_maps ADD COLUMN IF NOT EXISTS source_payload JSONB;

CREATE UNIQUE INDEX IF NOT EXISTS ix_match_maps_external_id
ON match_maps (external_id)
WHERE external_id IS NOT NULL;
