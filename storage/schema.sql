-- Single-user V1.0 foundation. JSON is serialized at the repository boundary.
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    education TEXT NOT NULL,
    major TEXT NOT NULL,
    target_direction TEXT NOT NULL,
    available_hours_per_day REAL CHECK (available_hours_per_day BETWEEN 0 AND 24),
    resume_text TEXT NOT NULL,
    profile_json TEXT NOT NULL CHECK (json_valid(profile_json)),
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS user_capabilities (
    id INTEGER PRIMARY KEY,
    capability_name TEXT NOT NULL UNIQUE CHECK (length(trim(capability_name)) > 0),
    level INTEGER NOT NULL CHECK (typeof(level) = 'integer' AND level BETWEEN 0 AND 4),
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS capability_evidence (
    id INTEGER PRIMARY KEY,
    capability_id INTEGER NOT NULL REFERENCES user_capabilities(id),
    evidence_type TEXT NOT NULL CHECK (length(trim(evidence_type)) > 0),
    content TEXT NOT NULL CHECK (length(trim(content)) > 0),
    source TEXT NOT NULL CHECK (length(trim(source)) > 0),
    source_id TEXT,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS target_jds (
    id INTEGER PRIMARY KEY,
    company TEXT NOT NULL,
    job_title TEXT NOT NULL,
    jd_text TEXT NOT NULL CHECK (length(trim(jd_text)) > 0),
    jd_analysis_json TEXT NOT NULL CHECK (json_valid(jd_analysis_json)),
    status TEXT NOT NULL CHECK (status IN ('active', 'archived')),
    created_at TEXT NOT NULL,
    archived_at TEXT,
    CHECK ((status = 'active' AND archived_at IS NULL) OR
           (status = 'archived' AND archived_at IS NOT NULL))
);
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY,
    capability TEXT NOT NULL CHECK (length(trim(capability)) > 0),
    task_text TEXT NOT NULL CHECK (length(trim(task_text)) > 0),
    task_key TEXT NOT NULL,
    reason TEXT NOT NULL,
    estimated_time TEXT NOT NULL,
    acceptance_criteria_json TEXT NOT NULL CHECK (json_valid(acceptance_criteria_json)),
    status TEXT NOT NULL CHECK (status IN
        ('pending', 'completed', 'partial', 'not_completed', 'superseded')),
    created_at TEXT, -- NULL for imported history with unknown creation time.
    completed_at TEXT,
    CHECK (status = 'completed' OR completed_at IS NULL)
);
CREATE TABLE IF NOT EXISTS planning_snapshots (
    id INTEGER PRIMARY KEY,
    trigger TEXT NOT NULL,
    active_jds_json TEXT NOT NULL CHECK (json_valid(active_jds_json)),
    capability_state_json TEXT NOT NULL CHECK (json_valid(capability_state_json)),
    priority_result_json TEXT NOT NULL CHECK (json_valid(priority_result_json)),
    selected_task_json TEXT NOT NULL CHECK (json_valid(selected_task_json)),
    reason TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    event_type TEXT NOT NULL CHECK (event_type IN
        ('TASK_CREATED', 'TASK_COMPLETED', 'TASK_PARTIAL', 'TASK_NOT_COMPLETED',
         'JD_ADDED', 'JD_ARCHIVED', 'JD_REPLACED', 'PROFILE_CONFIRMED', 'REPLAN')),
    entity_type TEXT NOT NULL CHECK (length(trim(entity_type)) > 0),
    entity_id TEXT NOT NULL CHECK (length(trim(entity_id)) > 0),
    payload_json TEXT NOT NULL CHECK (json_valid(payload_json)),
    created_at TEXT NOT NULL -- Event recording time, not inferred historical time.
);
CREATE TABLE IF NOT EXISTS memory_summaries (
    id INTEGER PRIMARY KEY,
    scope TEXT NOT NULL UNIQUE CHECK (length(trim(scope)) > 0),
    summary TEXT NOT NULL,
    covered_until_event_id INTEGER REFERENCES events(id),
    updated_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS evidence_capability ON capability_evidence(capability_id, id);
CREATE INDEX IF NOT EXISTS active_jds ON target_jds(status, id);
CREATE INDEX IF NOT EXISTS task_capability ON tasks(capability, id);
-- Only simultaneous pending duplicates are forbidden; historical tasks stay intact.
CREATE UNIQUE INDEX IF NOT EXISTS pending_task_key ON tasks(task_key)
    WHERE status = 'pending';
CREATE INDEX IF NOT EXISTS event_entity ON events(entity_type, entity_id, id);
CREATE INDEX IF NOT EXISTS event_type ON events(event_type, id);
-- A migration key lives in metadata, not in the product's entity schema.
CREATE UNIQUE INDEX IF NOT EXISTS event_migration_key
    ON events(json_extract(payload_json, '$.migration.import_key'))
    WHERE json_extract(payload_json, '$.migration.import_key') IS NOT NULL;
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
BEGIN SELECT RAISE(ABORT, 'events are append-only'); END;

-- Independent staging; never treated as confirmed Current State.
CREATE TABLE IF NOT EXISTS profile_drafts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    resume_text TEXT NOT NULL,
    resume_version TEXT NOT NULL,
    draft_json TEXT NOT NULL CHECK (json_valid(draft_json)),
    status TEXT NOT NULL CHECK (status IN ('draft', 'confirmed', 'discarded')),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    confirmed_at TEXT
);
