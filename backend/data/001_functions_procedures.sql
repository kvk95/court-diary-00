USE courtdiary;

-- =============================================================================
-- UUID v7 Generation Function (RFC-compliant)
-- Format: 017f22e2-79b0-7cc3-98c4-dc0c0c0c0c0c
-- =============================================================================

DROP FUNCTION IF EXISTS generate_uuid_v7;

DELIMITER $$

CREATE FUNCTION generate_uuid_v7()
RETURNS CHAR(36)
DETERMINISTIC
NO SQL
COMMENT 'Generates UUID version 7 (time-ordered)'
BEGIN
    DECLARE ts_ms BIGINT UNSIGNED;
    DECLARE r1 BIGINT UNSIGNED;
    DECLARE r2 BIGINT UNSIGNED;

    -- Current timestamp in milliseconds
    SET ts_ms = UNIX_TIMESTAMP(NOW(3)) * 1000 + MICROSECOND(NOW(3)) DIV 1000;

    -- Random parts
    SET r1 = FLOOR(RAND() * 0x1000000000000);  -- 48 bits
    SET r2 = FLOOR(RAND() * 0x1000000000000);  -- 48 bits

    -- Build UUID v7: xxxxxxxxxxxx-7xxx-yxxx-xxxxxxxxxxxx
    RETURN LOWER(CONCAT(
        LPAD(HEX(ts_ms), 12, '0'),                     -- 48-bit timestamp
        '-',
        '7', LPAD(HEX(r1 >> 36), 3, '0'),              -- Version 7 + 12 random bits
        '-',
        LPAD(HEX(((r1 & 0xFFFFFFFFF) << 2) | 0x8), 4, '0'), -- Variant (10xx)
        '-',
        LPAD(HEX(r2 >> 32), 4, '0'),                   -- 16 random bits
        '-',
        LPAD(HEX(r2 & 0xFFFFFFFF), 8, '0')             -- 32 random bits
    ));
END$$

DELIMITER ;

-- ─────────────────────────────────────────────────────────────────────────────
-- Verify Function Created
-- ─────────────────────────────────────────────────────────────────────────────

SELECT 
    ROUTINE_NAME,
    ROUTINE_TYPE,
    DATA_TYPE
FROM INFORMATION_SCHEMA.ROUTINES 
WHERE ROUTINE_SCHEMA = 'courtdiary' 
  AND ROUTINE_NAME = 'generate_uuid_v7';

-- Test the function
SELECT generate_uuid_v7() AS test_uuid;

-- ─────────────────────────────────────────────────────────────────────────────
-- apply_role_permissions
-- ─────────────────────────────────────────────────────────────────────────────

DROP PROCEDURE IF EXISTS apply_role_permissions;

DELIMITER $$

CREATE PROCEDURE apply_role_permissions (
    IN p_chamber_id CHAR(36),
    IN p_user_id CHAR(36)
)
BEGIN

    INSERT INTO role_permissions (
        role_id,
        chamber_module_id,
        allow_all_ind,
        read_ind,
        write_ind,
        create_ind,
        delete_ind,
        import_ind,
        export_ind,
        created_by
    )
    SELECT
        cr.role_id,
        cm.chamber_module_id,
        rpm.allow_all_ind,
        rpm.read_ind,
        rpm.write_ind,
        rpm.create_ind,
        rpm.delete_ind,
        rpm.import_ind,
        rpm.export_ind,
        p_user_id
    FROM role_permission_master rpm

    JOIN chamber_roles cr
        ON cr.security_role_id = rpm.security_role_id
       AND cr.chamber_id = p_chamber_id
       AND cr.status_ind = TRUE
       AND cr.deleted_ind = FALSE

    JOIN chamber_modules cm
        ON cm.module_code = rpm.module_code
       AND cm.chamber_id = p_chamber_id
       AND cm.active_ind = TRUE
       AND cm.deleted_ind = FALSE

    WHERE NOT EXISTS (
        SELECT 1
        FROM role_permissions rp
        WHERE rp.role_id = cr.role_id
          AND rp.chamber_module_id = cm.chamber_module_id
    );

END$$

DELIMITER ;