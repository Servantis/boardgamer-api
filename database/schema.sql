PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS attendance (
    id TEXT PRIMARY KEY,

    game_night_id TEXT NOT NULL,
    player_id TEXT NOT NULL,

    status TEXT NOT NULL DEFAULT 'maybe'
        CHECK (status IN ('accepted', 'declined', 'maybe')),

    comment TEXT,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (game_night_id) REFERENCES game_nights(id)
        ON DELETE CASCADE,

    FOREIGN KEY (player_id) REFERENCES players(id)
        ON DELETE CASCADE,

    UNIQUE (game_night_id, player_id)
);

CREATE TABLE IF NOT EXISTS game_night_reviews (
    id TEXT PRIMARY KEY,

    game_night_id TEXT NOT NULL,
    reviewer_player_id TEXT NOT NULL,
    reviewed_host_player_id TEXT,

    host_rating INTEGER
        CHECK (host_rating IS NULL OR host_rating BETWEEN 1 AND 5),

    food_rating INTEGER
        CHECK (food_rating IS NULL OR food_rating BETWEEN 1 AND 5),

    overall_rating INTEGER NOT NULL
        CHECK (overall_rating BETWEEN 1 AND 5),

    comment TEXT,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (game_night_id) REFERENCES game_nights(id)
        ON DELETE CASCADE,

    FOREIGN KEY (reviewer_player_id) REFERENCES players(id)
        ON DELETE CASCADE,

    FOREIGN KEY (reviewed_host_player_id) REFERENCES players(id)
        ON DELETE SET NULL,

    UNIQUE (game_night_id, reviewer_player_id)
);

CREATE TABLE IF NOT EXISTS game_nights (
    id TEXT PRIMARY KEY,

    group_id TEXT NOT NULL,

    date_time TEXT NOT NULL,
    location_id TEXT,
    host_player_id TEXT,

    status TEXT NOT NULL DEFAULT 'planned'
        CHECK (status IN ('planned', 'cancelled', 'completed')),

    notes TEXT,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (group_id) REFERENCES gaming_groups(id)
        ON DELETE CASCADE,

    FOREIGN KEY (location_id) REFERENCES locations(id)
        ON DELETE SET NULL,

    FOREIGN KEY (host_player_id) REFERENCES players(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS game_suggestions (
    id TEXT PRIMARY KEY,

    game_night_id TEXT NOT NULL,
    game_id TEXT NOT NULL,
    suggested_by_player_id TEXT NOT NULL,

    comment TEXT,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (game_night_id) REFERENCES game_nights(id)
        ON DELETE CASCADE,

    FOREIGN KEY (game_id) REFERENCES games(id)
        ON DELETE CASCADE,

    FOREIGN KEY (suggested_by_player_id) REFERENCES players(id)
        ON DELETE CASCADE,

    UNIQUE (game_night_id, game_id)
);

CREATE TABLE IF NOT EXISTS game_votes (
    id TEXT PRIMARY KEY,

    suggestion_id TEXT NOT NULL,
    player_id TEXT NOT NULL,

    vote_value INTEGER NOT NULL DEFAULT 1
        CHECK (vote_value IN (-1, 0, 1)),

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (suggestion_id) REFERENCES game_suggestions(id)
        ON DELETE CASCADE,

    FOREIGN KEY (player_id) REFERENCES players(id)
        ON DELETE CASCADE,

    UNIQUE (suggestion_id, player_id)
);

CREATE TABLE IF NOT EXISTS games (
    id TEXT PRIMARY KEY,

    group_id TEXT NOT NULL,

    title TEXT NOT NULL,
    min_players INTEGER,
    max_players INTEGER,
    duration_minutes INTEGER,
    game_genre TEXT,
    owner_player_id TEXT,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (group_id) REFERENCES gaming_groups(id)
        ON DELETE CASCADE,

    FOREIGN KEY (owner_player_id) REFERENCES players(id)
        ON DELETE SET NULL,

    CHECK (min_players IS NULL OR min_players > 0),
    CHECK (max_players IS NULL OR max_players > 0),
    CHECK (
        min_players IS NULL
        OR max_players IS NULL
        OR max_players >= min_players
    ),
    CHECK (duration_minutes IS NULL OR duration_minutes > 0)
);

CREATE TABLE IF NOT EXISTS gaming_groups (
    id TEXT PRIMARY KEY,

    name TEXT NOT NULL,
    description TEXT,
    created_by_player_id TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (created_by_player_id) REFERENCES players(id)
        ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS group_members (
    id TEXT PRIMARY KEY,

    group_id TEXT NOT NULL,
    player_id TEXT NOT NULL,

    role TEXT NOT NULL DEFAULT 'member'
        CHECK (role IN ('owner', 'admin', 'member')),

    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'invited', 'left', 'removed')),

    rotation_order INTEGER
        CHECK (rotation_order IS NULL OR rotation_order > 0),

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (group_id) REFERENCES gaming_groups(id)
        ON DELETE CASCADE,

    FOREIGN KEY (player_id) REFERENCES players(id)
        ON DELETE CASCADE,

    UNIQUE (group_id, player_id)
);

CREATE TABLE IF NOT EXISTS locations (
    id TEXT PRIMARY KEY,

    group_id TEXT NOT NULL,

    name TEXT NOT NULL,
    address TEXT,
    owner_player_id TEXT,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),

    FOREIGN KEY (group_id) REFERENCES gaming_groups(id)
        ON DELETE CASCADE,

    FOREIGN KEY (owner_player_id) REFERENCES players(id)
        ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS player_devices (
    id TEXT PRIMARY KEY,

    player_id TEXT NOT NULL,
    installation_id TEXT NOT NULL UNIQUE,

    device_name TEXT,
    platform TEXT,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    last_seen_at TEXT,

    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),
 	version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1),
    FOREIGN KEY (player_id) REFERENCES players(id)
);

CREATE TABLE IF NOT EXISTS players (
    id TEXT PRIMARY KEY,

    name TEXT NOT NULL,
    email TEXT UNIQUE,
    is_active INTEGER NOT NULL DEFAULT 1
        CHECK (is_active IN (0, 1)),

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    deleted_at TEXT,
    version INTEGER NOT NULL DEFAULT 1
        CHECK (version >= 1)
);

CREATE TABLE IF NOT EXISTS sync_outbox (
    id TEXT PRIMARY KEY,

    entity_name TEXT NOT NULL,
    entity_id TEXT NOT NULL,

    operation TEXT NOT NULL
        CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),

    payload_json TEXT NOT NULL,

    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    retry_count INTEGER NOT NULL DEFAULT 0
        CHECK (retry_count >= 0),

    last_error TEXT
);

CREATE TABLE IF NOT EXISTS sync_state (
    id TEXT PRIMARY KEY,

    last_pull_at TEXT,
    last_push_at TEXT
);

CREATE INDEX IF NOT EXISTS idx_attendance_deleted_at
    ON attendance(deleted_at);

CREATE INDEX IF NOT EXISTS idx_attendance_game_night_id
    ON attendance(game_night_id);

CREATE INDEX IF NOT EXISTS idx_attendance_player_id
    ON attendance(player_id);

CREATE INDEX IF NOT EXISTS idx_attendance_updated_at
    ON attendance(updated_at);

CREATE INDEX IF NOT EXISTS idx_game_night_reviews_deleted_at
    ON game_night_reviews(deleted_at);

CREATE INDEX IF NOT EXISTS idx_game_night_reviews_game_night_id
    ON game_night_reviews(game_night_id);

CREATE INDEX IF NOT EXISTS idx_game_night_reviews_reviewed_host_player_id
    ON game_night_reviews(reviewed_host_player_id);

CREATE INDEX IF NOT EXISTS idx_game_night_reviews_reviewer_player_id
    ON game_night_reviews(reviewer_player_id);

CREATE INDEX IF NOT EXISTS idx_game_night_reviews_updated_at
    ON game_night_reviews(updated_at);

CREATE INDEX IF NOT EXISTS idx_game_nights_deleted_at
    ON game_nights(deleted_at);

CREATE INDEX IF NOT EXISTS idx_game_nights_group_id
    ON game_nights(group_id);

CREATE INDEX IF NOT EXISTS idx_game_nights_group_id_date_time
    ON game_nights(group_id, date_time);

CREATE INDEX IF NOT EXISTS idx_game_nights_host_player_id
    ON game_nights(host_player_id);

CREATE INDEX IF NOT EXISTS idx_game_nights_location_id
    ON game_nights(location_id);

CREATE INDEX IF NOT EXISTS idx_game_nights_updated_at
    ON game_nights(updated_at);

CREATE INDEX IF NOT EXISTS idx_game_suggestions_deleted_at
    ON game_suggestions(deleted_at);

CREATE INDEX IF NOT EXISTS idx_game_suggestions_game_id
    ON game_suggestions(game_id);

CREATE INDEX IF NOT EXISTS idx_game_suggestions_game_night_id
    ON game_suggestions(game_night_id);

CREATE INDEX IF NOT EXISTS idx_game_suggestions_suggested_by_player_id
    ON game_suggestions(suggested_by_player_id);

CREATE INDEX IF NOT EXISTS idx_game_suggestions_updated_at
    ON game_suggestions(updated_at);

CREATE INDEX IF NOT EXISTS idx_game_votes_deleted_at
    ON game_votes(deleted_at);

CREATE INDEX IF NOT EXISTS idx_game_votes_player_id
    ON game_votes(player_id);

CREATE INDEX IF NOT EXISTS idx_game_votes_suggestion_id
    ON game_votes(suggestion_id);

CREATE INDEX IF NOT EXISTS idx_game_votes_updated_at
    ON game_votes(updated_at);

CREATE INDEX IF NOT EXISTS idx_games_deleted_at
    ON games(deleted_at);

CREATE INDEX IF NOT EXISTS idx_games_group_id
    ON games(group_id);

CREATE INDEX IF NOT EXISTS idx_games_owner_player_id
    ON games(owner_player_id);

CREATE INDEX IF NOT EXISTS idx_games_updated_at
    ON games(updated_at);

CREATE INDEX IF NOT EXISTS idx_gaming_groups_created_by_player_id
    ON gaming_groups(created_by_player_id);

CREATE INDEX IF NOT EXISTS idx_gaming_groups_deleted_at
    ON gaming_groups(deleted_at);

CREATE INDEX IF NOT EXISTS idx_gaming_groups_updated_at
    ON gaming_groups(updated_at);

CREATE INDEX IF NOT EXISTS idx_group_members_deleted_at
    ON group_members(deleted_at);

CREATE INDEX IF NOT EXISTS idx_group_members_group_id
    ON group_members(group_id);

CREATE INDEX IF NOT EXISTS idx_group_members_player_id
    ON group_members(player_id);

CREATE INDEX IF NOT EXISTS idx_group_members_updated_at
    ON group_members(updated_at);

CREATE INDEX IF NOT EXISTS idx_locations_deleted_at
    ON locations(deleted_at);

CREATE INDEX IF NOT EXISTS idx_locations_group_id
    ON locations(group_id);

CREATE INDEX IF NOT EXISTS idx_locations_owner_player_id
    ON locations(owner_player_id);

CREATE INDEX IF NOT EXISTS idx_locations_updated_at
    ON locations(updated_at);

CREATE INDEX IF NOT EXISTS idx_players_deleted_at
    ON players(deleted_at);

CREATE INDEX IF NOT EXISTS idx_players_updated_at
    ON players(updated_at);

CREATE INDEX IF NOT EXISTS idx_sync_outbox_created_at
    ON sync_outbox(created_at);

CREATE INDEX IF NOT EXISTS idx_sync_outbox_entity
    ON sync_outbox(entity_name, entity_id);

CREATE INDEX IF NOT EXISTS idx_sync_outbox_operation
    ON sync_outbox(operation);

CREATE TABLE IF NOT EXISTS server_change_log (
    id TEXT PRIMARY KEY,
    entity_name TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    operation TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    payload_json TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);

CREATE INDEX IF NOT EXISTS idx_server_change_log_created_at
    ON server_change_log(created_at);

CREATE INDEX IF NOT EXISTS idx_server_change_log_entity
    ON server_change_log(entity_name, entity_id);

INSERT OR IGNORE INTO sync_state (id, last_pull_at, last_push_at)
VALUES ('default', NULL, NULL);
