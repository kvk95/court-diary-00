-- =============================================================================
-- SAMPLE DATA INSERTS – COURT DIARY
-- Run after all CREATE TABLE and ALTER TABLE statements
-- 2025/2026 version
-- =============================================================================

USE courtdiary;

-- =============================================================================
-- 0. HELPER VARIABLES
-- (Adjust IDs based on your AUTO_INCREMENT starts if running partially)
-- =============================================================================

-- Chamber IDs
SET @chamber_vk_id     = 1;   -- VijayKrishnan & Associates
SET @chamber_sundar_id = 2;   -- Sundar Associates

-- User IDs
SET @admin_vk          = 1;   -- Vijay Krishnan (Admin)
SET @senior_vk         = 2;   -- Priya Menon (Senior)
SET @clerk_vk          = 3;   -- Karthik Raja (Clerk)
SET @admin_sundar      = 4;   -- Lokesh Mani (Admin - Sundar)

-- =============================================================================
-- 1. REFERENCE / LOOKUP TABLES
-- (Master data – safe to run multiple times with INSERT IGNORE)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 1.1 Geographic & Court Data
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_countries (code, description, phone_code, sort_order) VALUES
('IN', 'India', '+91', 1);

INSERT IGNORE INTO refm_states (code, description, country_code, sort_order) VALUES
('TN', 'Tamil Nadu',   'IN', 1),
('KL', 'Kerala',       'IN', 2),
('KA', 'Karnataka',    'IN', 3),
('MH', 'Maharashtra',  'IN', 4),
('DL', 'Delhi',        'IN', 5);

INSERT INTO refm_courts (court_name, state_code, court_type, sort_order) VALUES
('Madras High Court',                'TN', 'High Court',     10),
('City Civil Court, Chennai',        'TN', 'Civil Court',    20),
('District Court, Chengalpattu',     'TN', 'District Court', 30),
('Principal District Court, Coimbatore', 'TN', 'District Court', 40),
('Family Court, Chennai',            'TN', 'Family Court',   50);

-- ─────────────────────────────────────────────────────────────────────────────
-- 1.2 Case & Hearing Statuses
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_case_status (code, description, color_code, sort_order) VALUES
('AC',  'Active',    '#3b82f6', 10),
('ADJ', 'Adjourned', '#f97316', 20),
('DIS', 'Disposed',  '#64748b', 30),
('CLO', 'Closed',    '#64748b', 40),
('OVD', 'Overdue',   '#ef4444', 50);

INSERT IGNORE INTO refm_hearing_status (code, description, color_code, sort_order) VALUES
('UP',  'Upcoming',      '#3b82f6', 10),
('CMP', 'Completed',     '#22c55e', 20),
('ADJ', 'Adjourned',     '#f97316', 30),
('OR',  'Order Reserved','#a855f7', 40),
('DIS', 'Disposed',      '#64748b', 50);

INSERT IGNORE INTO refm_case_types (code, description, sort_order) VALUES
('CRIM', 'Criminal',      10),
('CIVL', 'Civil Suit',    20),
('WRIT', 'Writ Petition', 30),
('FAM',  'Family Matter', 40),
('LAB',  'Labour Case',   50),
('TAX',  'Tax Matter',    60),
('CON',  'Consumer Case', 70);

-- ─────────────────────────────────────────────────────────────────────────────
-- 1.3 System Configuration & Plans
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_plan_types (code, description, max_users, max_cases, price_monthly_amt, price_annual_amt, sort_order) VALUES
('FREE', 'Free',       3,   75, 0.00,    0.00,     10),
('PRO',  'Pro',       10,  300, 999.00,  9999.00,  20),
('ENT',  'Enterprise', NULL, NULL, 2999.00, 29999.00, 30);

INSERT IGNORE INTO refm_modules (code, name, description, sort_order) VALUES
('DASH',  'Dashboard',      'Overview & statistics', 10),
('CASES', 'Cases',          'Case register & details', 20),
('HEAR',  'Hearings',       'Hearing schedule & history', 30),
('CAL',   'Calendar',       'Court & personal calendar', 40),
('USERS', 'User Management','Manage chamber users & roles', 50),
('RPT',   'Reports',        'Analytics & exports', 60),
('SET',   'Settings',       'Chamber configuration', 70);

INSERT IGNORE INTO refm_email_encryption (code, description, sort_order) VALUES
('N', 'None', 10),
('T', 'TLS',  20),
('S', 'SSL',  30),
('B', 'Both', 40);

INSERT IGNORE INTO refm_user_deletion_status (code, description, color_code, sort_order) VALUES
('P', 'Pending',   '#f97316', 10),
('A', 'Approved',  '#22c55e', 20),
('R', 'Rejected',  '#ef4444', 30),
('C', 'Completed', '#64748b', 40);

INSERT IGNORE INTO refm_email_status (code, description, color_code, sort_order) VALUES
('P', 'Pending',   '#f97316', 10),
('S', 'Sent',      '#3b82f6', 20),
('D', 'Delivered', '#22c55e', 30),
('O', 'Opened',    '#a855f7', 40),
('F', 'Failed',    '#ef4444', 50),
('B', 'Bounced',   '#991b1b', 60);


-- =============================================================================
-- 2. CORE ENTITIES (CHAMBERS & USERS)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.1 Chambers
-- Note: created_by is NULL initially to avoid FK constraints before users exist
-- (Section 8 of CREATE script adds FK, but NULL is valid)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO chambers (chamber_name, email, phone, city, state_code, plan_code, created_by) VALUES
('VijayKrishnan & Associates', 'office@vkchamber.in', '9876543210', 'Chennai',     'TN', 'PRO',  NULL),
('Sundar Associates',          'office@sundarlaw.in', '9445123456', 'Coimbatore',  'TN', 'FREE', NULL);

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.2 Users
-- Note: First user (ID 1) must have created_by = NULL to avoid self-reference FK error
-- Password Hash: Placeholder for "password" (Argon2id)
-- ─────────────────────────────────────────────────────────────────────────────

SET @pwd_hash = '$argon2id$v=19$m=65536,t=3,p=4$Z2lBWE9sVjF3L1h4eQ$7JQ4wq5mZy3b8s8u5O8l5G1Y3c3S6J0JY5c1q8P0o7A';

INSERT INTO users (chamber_id, email, password_hash, first_name, last_name, phone, role_code, created_by) VALUES
(1, 'admin@vkchamber.in',   @pwd_hash, 'Vijay',   'Krishnan', '9876543210', 'ADM', NULL),  -- Root Admin
(1, 'priya@vkchamber.in',   @pwd_hash, 'Priya',   'Menon',    '8123456789', 'SEN', 1),
(1, 'karthik@vkchamber.in', @pwd_hash, 'Karthik', 'Raja',     '9001234567', 'CLK', 1),
(2, 'lokesh@vkchamber.in',  @pwd_hash, 'Lokesh',  'Mani',     '9445123456', 'ADM', 1);


-- =============================================================================
-- 3. SECURITY & PERMISSIONS
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.1 Roles
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO security_roles (chamber_id, role_name, role_code, description, created_by) VALUES
(1, 'Administrator',     'ADM', 'Full access',           1),
(1, 'Senior Advocate',   'SEN', 'Manage cases & hearings', 1),
(1, 'Clerk',             'CLK', 'View & basic entry',    1),
(2, 'Administrator',     'ADM', 'Full access',           4);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.2 User ↔ Role Mapping
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO user_roles (user_id, role_id, created_by) VALUES
(1, 1, 1),   -- admin_vk → Administrator
(2, 2, 1),   -- senior_vk → Senior Advocate
(3, 3, 1),   -- clerk_vk → Clerk
(4, 4, 4);   -- admin_lokesh → Administrator

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.3 Role Permissions
-- (Grant full access to Admin role for all modules)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO role_permissions (role_id, module_code, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, created_by)
SELECT 1, code, TRUE, TRUE, TRUE, TRUE, TRUE, 1
FROM refm_modules;


-- =============================================================================
-- 4. CORE BUSINESS DATA (CASES & HEARINGS)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.1 Cases
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO cases (chamber_id, case_number, court_id, case_type_code, filing_year,
                   petitioner, respondent, aor_user_id, case_summary, status_code, next_hearing_date, created_by) VALUES
(1, 'Crl.O.P.No.234/2025', 1, 'CRIM', 2025,
 'State of Tamil Nadu', 'Arjun Prasad', 2,
 'Quashing of FIR u/s 420 IPC – financial fraud', 'AC', '2026-03-15', 1),

(1, 'W.P.(MD)No.5678/2025', 1, 'WRIT', 2025,
 'Tmt. Saraswathi', 'The Tahsildar', 2,
 'Challenge to patta cancellation order', 'ADJ', '2026-02-28', 1),

(2, 'O.S.No.145/2024', 4, 'CIVL', 2024,
 'M/s Blue Sky Builders', 'T.N. Housing Board', 4,
 'Specific performance of sale agreement – construction dispute', 'AC', '2026-04-10', 4);

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.2 Hearings
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO hearings (chamber_id, case_id, hearing_date, status_code, purpose, notes, next_hearing_date, created_by) VALUES
(1, 1, '2026-01-20', 'CMP', 'Admission hearing',    'Notice issued to respondent', '2026-03-15', 2),
(1, 1, '2026-03-15', 'UP',  'Final arguments',      'Awaiting final disposal',     NULL,       2),

(1, 2, '2026-02-10', 'ADJ', 'Counter affidavit stage', 'Adjourned due to non-filing', '2026-02-28', 3),

(2, 3, '2026-03-01', 'CMP', 'Framing of issues',    'Issues framed',               '2026-04-10', 4);


-- =============================================================================
-- 5. CONFIGURATION & EMAIL
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.1 SMTP Settings
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO email_settings (chamber_id, from_email, smtp_host, smtp_port, smtp_user, smtp_password, encryption_code, is_default, status_ind, created_by) VALUES
(1, 'no-reply@vkchamber.in', 'smtp.gmail.com', 587, 'no-reply@vkchamber.in', 'app-password-placeholder', 'T', TRUE,  TRUE, 1),
(1, 'office@vkchamber.in',   'smtp.zoho.com',  587, 'office@vkchamber.in',   'zoho-password-placeholder',  'T', FALSE, TRUE, 1);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.2 Email Templates (System Defaults)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_email_templates (code, subject, content, category, sort_order) VALUES
('hearing_tomorrow', 'Hearing Tomorrow – {Case Number}',
 '<p>Dear {Advocate},</p><p>Hearing tomorrow:<br><strong>{Case Number}</strong><br>Court: {Court Name}<br>Purpose: {Purpose}</p>',
 'REMINDER', 100),

('welcome_user', 'Welcome to {Chamber Name}',
 '<p>Hello {FirstName},</p><p>Your account is active.<br>Login: {Email}</p>',
 'WELCOME', 10);

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.3 Email Templates (Chamber Customizations)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO email_templates (chamber_id, code, subject, content, is_customized, enabled_ind, created_by) VALUES
(1, 'hearing_tomorrow',
 'Court Hearing Tomorrow – Urgent: {Case Number}',
 '<p>Dear Advocate,</p><p><strong>Tomorrow</strong> hearing:<br>Case: <b>{Case Number}</b></p><p>Prepare urgently.</p><p>VijayKrishnan & Associates</p>',
 TRUE, TRUE, 1);


-- =============================================================================
-- 6. LOGGING & AUDIT SAMPLES
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.1 Login Audit
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO login_audit (chamber_id, user_id, email, ip_address, user_agent, status_ind, login_time) VALUES
(1, 1, 'admin@vkchamber.in',  '117.192.45.12',  'Chrome / Windows', TRUE, '2026-02-18 09:15:22'),
(1, 2, 'priya@vkchamber.in',  '49.204.123.88',  'Safari / Mac',     TRUE, '2026-02-18 10:02:45');

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.2 Activity Log
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO activity_log (chamber_id, user_id, action, target, ip_address, metadata_json, created_by) VALUES
(1, 2, 'CASE_UPDATE',    'cases',    '117.192.45.12',
 JSON_OBJECT('case_id', 1, 'changed', 'next_hearing_date'), 2),

(1, 3, 'HEARING_CREATE', 'hearings', '49.204.123.88',
 JSON_OBJECT('hearing_id', 3, 'case_id', 2), 3);

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.3 Email Log
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO email_log (chamber_id, user_id, template_code, recipient_email, subject, status_code, sent_at, metadata_json, created_by) VALUES
(1, 2, 'hearing_tomorrow', 'priya@vkchamber.in',
 'Court Hearing Tomorrow – Urgent: Crl.O.P.No.234/2025',
 'D', '2026-02-17 17:02:15',
 JSON_OBJECT('case_id', 1, 'hearing_date', '2026-02-18'), 3);

-- =============================================================================
-- END OF SAMPLE DATA
-- =============================================================================

SELECT 'Sample data inserted successfully' AS status_message;