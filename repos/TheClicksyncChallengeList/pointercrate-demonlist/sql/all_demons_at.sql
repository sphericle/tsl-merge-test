SELECT demons.id AS "demon_id!", demons.name AS "demon_name!: String", demons.position_ as "position!", demons.requirement as "requirement!", demons.level_id, CASE WHEN verifiers.link_banned THEN NULL ElSE demons.video::text END, demons.thumbnail AS "thumbnail!", verifiers.id AS "verifier_id!", verifiers.name AS "verifier_name!: String", verifiers.banned AS "verifier_banned!", publishers.id AS "publisher_id!", publishers.name AS "publisher_name!: String", publishers.banned AS "publisher_banned!", demons.current_position as "current_position!"
FROM list_at($1) AS demons
    INNER JOIN players as publishers
        ON demons.publisher = publishers.id
    INNER JOIN players AS verifiers
        ON demons.verifier = verifiers.id
ORDER BY position_