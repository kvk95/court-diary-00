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
