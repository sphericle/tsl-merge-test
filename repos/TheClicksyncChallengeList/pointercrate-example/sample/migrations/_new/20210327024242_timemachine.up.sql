-- Your SQL goes here

CREATE FUNCTION list_at(TIMESTAMP WITHOUT TIME ZONE)
RETURNS TABLE (
    name CITEXT,
    position_ SMALLINT,
    requirement SMALLINT,
    video VARCHAR(200),
    verifier INTEGER,
    publisher INTEGER,
    id INTEGER,
    level_id BIGINT,
    current_position SMALLINT
)
AS $$
    SELECT name, CASE WHEN t.position IS NULL THEN demons.position ELSE t.position END, requirement, video, verifier, publisher, demons.id, level_id, demons.position AS current_position
    FROM demons
    LEFT OUTER JOIN (
            SELECT DISTINCT ON (id) id, position
            FROM demon_modifications
            WHERE time >= $1 AND position != -1
            ORDER BY id, time
        ) t
    ON demons.id = t.id
    WHERE NOT EXISTS (SELECT 1 FROM demon_additions WHERE demon_additions.id = demons.id AND time >= $1)
$$
LANGUAGE SQL
STABLE;