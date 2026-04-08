USE courtdiary;

-- =============================================================================
-- UUID v7 Auto-Generation Triggers
-- These ensure IDs are generated for ALL insertion methods:
-- - Python ORM inserts
-- - Direct SQL inserts
-- - Bulk imports
-- - Data migrations
-- =============================================================================

DELIMITER $$

-- ─────────────────────────────────────────────────────────────────────────────
-- Chamber
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_chamber_before_insert
BEFORE INSERT ON chamber
FOR EACH ROW
BEGIN
    IF NEW.chamber_id IS NULL OR NEW.chamber_id = '' THEN
        SET NEW.chamber_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Users
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_users_before_insert
BEFORE INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.user_id IS NULL OR NEW.user_id = '' THEN
        SET NEW.user_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- User Profiles
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_user_profiles_before_insert
BEFORE INSERT ON user_profiles
FOR EACH ROW
BEGIN
    IF NEW.profile_id IS NULL OR NEW.profile_id = '' THEN
        SET NEW.profile_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- User Chamber Link
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_user_chamber_link_before_insert
BEFORE INSERT ON user_chamber_link
FOR EACH ROW
BEGIN
    IF NEW.link_id IS NULL OR NEW.link_id = '' THEN
        SET NEW.link_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Chamber Modules
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_chamber_modules_before_insert
BEFORE INSERT ON chamber_modules
FOR EACH ROW
BEGIN
    IF NEW.chamber_module_id IS NULL OR NEW.chamber_module_id = '' THEN
        SET NEW.chamber_module_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- User Roles
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_user_roles_before_insert
BEFORE INSERT ON user_roles
FOR EACH ROW
BEGIN
    IF NEW.user_role_id IS NULL OR NEW.user_role_id = '' THEN
        SET NEW.user_role_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Role Permissions
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_role_permissions_before_insert
BEFORE INSERT ON role_permissions
FOR EACH ROW
BEGIN
    IF NEW.permission_id IS NULL OR NEW.permission_id = '' THEN
        SET NEW.permission_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Cases
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_cases_before_insert
BEFORE INSERT ON cases
FOR EACH ROW
BEGIN
    IF NEW.case_id IS NULL OR NEW.case_id = '' THEN
        SET NEW.case_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Hearings
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_hearings_before_insert
BEFORE INSERT ON hearings
FOR EACH ROW
BEGIN
    IF NEW.hearing_id IS NULL OR NEW.hearing_id = '' THEN
        SET NEW.hearing_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Case Notes
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_case_notes_before_insert
BEFORE INSERT ON case_notes
FOR EACH ROW
BEGIN
    IF NEW.note_id IS NULL OR NEW.note_id = '' THEN
        SET NEW.note_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Case AORs
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_case_aors_before_insert
BEFORE INSERT ON case_aors
FOR EACH ROW
BEGIN
    IF NEW.case_aor_id IS NULL OR NEW.case_aor_id = '' THEN
        SET NEW.case_aor_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Clients
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_clients_before_insert
BEFORE INSERT ON clients
FOR EACH ROW
BEGIN
    IF NEW.client_id IS NULL OR NEW.client_id = '' THEN
        SET NEW.client_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Case Clients
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_case_clients_before_insert
BEFORE INSERT ON case_clients
FOR EACH ROW
BEGIN
    IF NEW.case_client_id IS NULL OR NEW.case_client_id = '' THEN
        SET NEW.case_client_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Client Bills
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_client_bills_before_insert
BEFORE INSERT ON client_bills
FOR EACH ROW
BEGIN
    IF NEW.bill_id IS NULL OR NEW.bill_id = '' THEN
        SET NEW.bill_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Client Payments
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_client_payments_before_insert
BEFORE INSERT ON client_payments
FOR EACH ROW
BEGIN
    IF NEW.payment_id IS NULL OR NEW.payment_id = '' THEN
        SET NEW.payment_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Client Documents
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_client_documents_before_insert
BEFORE INSERT ON client_documents
FOR EACH ROW
BEGIN
    IF NEW.document_id IS NULL OR NEW.document_id = '' THEN
        SET NEW.document_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Client Communications
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_client_communications_before_insert
BEFORE INSERT ON client_communications
FOR EACH ROW
BEGIN
    IF NEW.comm_id IS NULL OR NEW.comm_id = '' THEN
        SET NEW.comm_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- PROFILE IMAGES
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_profile_images_before_insert
BEFORE INSERT ON profile_images
FOR EACH ROW
BEGIN
    IF NEW.image_id IS NULL OR NEW.image_id = '' THEN
        SET NEW.image_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Case Collaborations
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_case_collaborations_before_insert
BEFORE INSERT ON case_collaborations
FOR EACH ROW
BEGIN
    IF NEW.collaboration_id IS NULL OR NEW.collaboration_id = '' THEN
        SET NEW.collaboration_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- User Invitations
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_user_invitations_before_insert
BEFORE INSERT ON user_invitations
FOR EACH ROW
BEGIN
    IF NEW.invitation_id IS NULL OR NEW.invitation_id = '' THEN
        SET NEW.invitation_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Login Audit
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_login_audit_before_insert
BEFORE INSERT ON login_audit
FOR EACH ROW
BEGIN
    IF NEW.login_id IS NULL OR NEW.login_id = '' THEN
        SET NEW.login_id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- DB Call Log
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_db_call_log_before_insert
BEFORE INSERT ON db_call_log
FOR EACH ROW
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Exception Log
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_exception_log_before_insert
BEFORE INSERT ON exception_log
FOR EACH ROW
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- Activity Log
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_activity_log_before_insert
BEFORE INSERT ON activity_log
FOR EACH ROW
BEGIN
    IF NEW.id IS NULL OR NEW.id = '' THEN
        SET NEW.id = generate_uuid_v7();
    END IF;
END$$

-- ─────────────────────────────────────────────────────────────────────────────
-- email_link
-- ─────────────────────────────────────────────────────────────────────────────

CREATE TRIGGER trg_email_link_before_insert
BEFORE INSERT ON email_link
FOR EACH ROW
BEGIN
    IF NEW.link_id IS NULL OR NEW.link_id = '' THEN
        SET NEW.link_id = generate_uuid_v7();
    END IF;
END$$

DELIMITER ;

-- ─────────────────────────────────────────────────────────────────────────────
-- Verify All Triggers Created
-- ─────────────────────────────────────────────────────────────────────────────

SELECT 
    TRIGGER_NAME,
    EVENT_MANIPULATION,
    EVENT_OBJECT_TABLE,
    ACTION_TIMING
FROM INFORMATION_SCHEMA.TRIGGERS 
WHERE TRIGGER_SCHEMA = 'courtdiary'
  AND TRIGGER_NAME LIKE 'trg_%_before_insert'
ORDER BY EVENT_OBJECT_TABLE;

SELECT '✅ All UUID v7 triggers created successfully!' AS status_message;