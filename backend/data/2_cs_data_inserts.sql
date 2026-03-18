
-- =============================================================================
-- 10. SAMPLE DATA INSERTS
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.1 Reference Data
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
('N', 'None', 10), ('T', 'TLS',  20), ('S', 'SSL',  30), ('B', 'Both', 40);

INSERT IGNORE INTO refm_email_status (code, description, color_code, sort_order) VALUES
('P', 'Pending',   '#f97316', 10), ('S', 'Sent',      '#3b82f6', 20),
('D', 'Delivered', '#22c55e', 30), ('O', 'Opened',    '#a855f7', 40),
('F', 'Failed',    '#ef4444', 50), ('B', 'Bounced',   '#991b1b', 60);

INSERT INTO refm_login_status (code, description, sort_order) VALUES 
('S', 'Success', 1), ('F', 'Failed', 2);

INSERT INTO refm_user_deletion_status (code, description, sort_order) VALUES 
('P', 'Pending', 1), ('D', 'Deleted', 2);

INSERT IGNORE INTO refm_billing_status (code, description, color_code, sort_order) VALUES
('PN', 'Pending', '#f97316', 10), ('PD', 'Paid', '#22c55e', 20),
('OV', 'Overdue', '#ef4444', 30), ('CN', 'Cancelled', '#64748b', 40), ('AD', 'Adjusted', '#a855f7', 50);

INSERT IGNORE INTO refm_comm_status (code, description, color_code, sort_order) VALUES
('PN', 'Pending', '#f97316', 10), ('SN', 'Sent', '#3b82f6', 20),
('DL', 'Delivered', '#22c55e', 30), ('RD', 'Read', '#a855f7', 40), ('FD', 'Failed', '#ef4444', 50);

INSERT INTO refm_party_roles (code, description, category, sort_order) VALUES
('PET', 'Petitioner', 'PARTY', 10), ('RES', 'Respondent', 'PARTY', 20),
('APP', 'Appellant', 'PARTY', 30), ('DEF', 'Defendant', 'PARTY', 40),
('PLT', 'Plaintiff', 'PARTY', 50), ('WIT', 'Witness', 'REP', 60),
('AOR', 'Advocate on Record', 'REP', 70);

INSERT IGNORE INTO refm_email_templates (code, subject, content, category, sort_order) VALUES
('hearing_tomorrow', 'Hearing Tomorrow – {Case Number}',
 '<p>Dear {Advocate},</p><p>Hearing tomorrow:<br><strong>{Case Number}</strong><br>Court: {Court Name}<br>Purpose: {Purpose}</p>',
 'REMINDER', 100),
('welcome_user', 'Welcome to {Chamber Name}',
 '<p>Hello {FirstName},</p><p>Your account is active.<br>Login: {Email}</p>',
 'WELCOME', 10);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.2 chamber & Users (Decoupled)
-- ─────────────────────────────────────────────────────────────────────────────

-- chamber
INSERT INTO chamber (chamber_name, email, phone, city, state_code, plan_code, created_by) VALUES
('VijayKrishnan & Associates', 'office@vkchamber.in', '9876543210', 'Chennai', 'TN', 'PRO', NULL),
('Sundar Associates', 'office@sundarlaw.in', '9445123456', 'Coimbatore', 'TN', 'FREE', NULL);

-- Users (NO chamber_id - chamber-agnostic)
SET @pwd_hash = '$argon2id$v=19$m=65536,t=3,p=4$Z2lBWE9sVjF3L1h4eQ$7JQ4wq5mZy3b8s8u5O8l5G1Y3c3S6J0JY5c1q8P0o7A';

INSERT INTO users (email, password_hash, first_name, last_name, phone, role_code, created_by) VALUES
('admin@vkchamber.in',   @pwd_hash, 'Vijay',   'Krishnan', '9876543210', 'ADM', NULL),
('priya@vkchamber.in',   @pwd_hash, 'Priya',   'Menon',    '8123456789', 'SEN', 1),
('karthik@vkchamber.in', @pwd_hash, 'Karthik', 'Raja',     '9001234567', 'CLK', 1),
('lokesh@sundarlaw.in',  @pwd_hash, 'Lokesh',  'Mani',     '9445123456', 'ADM', 1);

-- User Profiles
INSERT INTO user_profiles (user_id, address, country, state, city, postal_code, 
                           header_color, sidebar_color, primary_color, font_family, updated_by) VALUES
(1, 'No. 45, Anna Salai, Teynampet', 'IN', 'TN', 'Chennai', '600018',
 '222 33% 10%', '222 40% 12%', '32.4 99% 63%', 'Nunito, sans-serif', 1),
(2, 'Flat 3B, Greenwoods Apartment, Adyar', 'IN', 'TN', 'Chennai', '600020',
 '230 20% 15%', '230 25% 18%', '215 100% 55%', 'Inter, sans-serif', 1),
(3, '12/5, Gandhi Nagar, Chengalpattu', 'IN', 'TN', 'Chengalpattu', '603001',
 '0 0% 12%', '0 0% 15%', '262 83% 58%', 'Nunito, sans-serif', 1),
(4, 'Plot 78, RS Puram', 'IN', 'TN', 'Coimbatore', '641002',
 '225 30% 11%', '225 35% 14%', '142 76% 36%', 'Roboto, sans-serif', 4);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.3 User ↔ Chamber Links (NEW BRIDGE TABLE)
-- ─────────────────────────────────────────────────────────────────────────────

-- Get IDs for linking
SET @chamber_vk = (SELECT chamber_id FROM chamber WHERE chamber_name = 'VijayKrishnan & Associates');
SET @chamber_sundar = (SELECT chamber_id FROM chamber WHERE chamber_name = 'Sundar Associates');
SET @user_vijay = (SELECT user_id FROM users WHERE email = 'admin@vkchamber.in');
SET @user_priya = (SELECT user_id FROM users WHERE email = 'priya@vkchamber.in');
SET @user_karthik = (SELECT user_id FROM users WHERE email = 'karthik@vkchamber.in');
SET @user_lokesh = (SELECT user_id FROM users WHERE email = 'lokesh@sundarlaw.in');

-- Create membership links
INSERT INTO user_chamber_link (user_id, chamber_id, is_primary, created_by) VALUES
(@user_vijay,   @chamber_vk,     TRUE,  @user_vijay),
(@user_priya,   @chamber_vk,     TRUE,  @user_vijay),
(@user_karthik, @chamber_vk,     TRUE,  @user_vijay),
(@user_lokesh,  @chamber_sundar, TRUE,  @user_lokesh);

-- Example: Consultant advocate in MULTIPLE chamber (optional)
-- INSERT INTO user_chamber_link (user_id, chamber_id, is_primary, role_override, created_by) VALUES
-- (@user_priya, @chamber_sundar, FALSE, 'CONS', @user_lokesh);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.4 Chamber Modules
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO chamber_modules (chamber_id, module_code, is_active, created_by) VALUES
(1, 'DASH',  TRUE, 1), (1, 'CASES', TRUE, 1), (1, 'HEAR',  TRUE, 1),
(1, 'CAL',   TRUE, 1), (1, 'USERS', TRUE, 1), (1, 'RPT',   TRUE, 1), (1, 'SET',   TRUE, 1);

INSERT INTO chamber_modules (chamber_id, module_code, is_active, created_by) VALUES
(2, 'DASH',  TRUE, 4), (2, 'CASES', TRUE, 4), (2, 'HEAR',  TRUE, 4),
(2, 'CAL',   TRUE, 4), (2, 'USERS', FALSE, 4), (2, 'RPT',   FALSE, 4), (2, 'SET',   TRUE, 4);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.5 Security: Roles & Permissions
-- ─────────────────────────────────────────────────────────────────────────────

-- Roles
INSERT INTO security_roles (role_name, role_code, description, created_by) VALUES
('Administrator',   'ADM', 'Full access',                    1),
('Senior Advocate', 'SEN', 'Manage cases & hearings',        1),
('Clerk',           'CLK', 'View & basic entry',             1);

-- Get link IDs for role assignments
SET @link_vijay_vk = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_vijay AND chamber_id = @chamber_vk);
SET @link_priya_vk = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_priya AND chamber_id = @chamber_vk);
SET @link_karthik_vk = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_karthik AND chamber_id = @chamber_vk);
SET @link_lokesh_sundar = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_lokesh AND chamber_id = @chamber_sundar);

-- Get role IDs
SET @role_admin = (SELECT role_id FROM security_roles WHERE role_code = 'ADM');
SET @role_senior = (SELECT role_id FROM security_roles WHERE role_code = 'SEN');
SET @role_clerk = (SELECT role_id FROM security_roles WHERE role_code = 'CLK');

-- User Roles (via link_id - contextual!)
INSERT INTO user_roles (link_id, role_id, created_by) VALUES
(@link_vijay_vk,     @role_admin,  @user_vijay),
(@link_priya_vk,     @role_senior, @user_vijay),
(@link_karthik_vk,   @role_clerk,  @user_vijay),
(@link_lokesh_sundar, @role_admin, @user_lokesh);

-- Role Permissions (Admin gets full access)
SET @cm1_dash  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = 1 AND module_code = 'DASH');
SET @cm1_cases = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = 1 AND module_code = 'CASES');
SET @cm1_hear  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = 1 AND module_code = 'HEAR');
SET @cm1_cal   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = 1 AND module_code = 'CAL');
SET @cm1_users = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = 1 AND module_code = 'USERS');
SET @cm1_rpt   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = 1 AND module_code = 'RPT');
SET @cm1_set   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = 1 AND module_code = 'SET');

INSERT INTO role_permissions (role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, created_by) VALUES
(1, @cm1_dash,  TRUE, TRUE, TRUE, TRUE, TRUE, 1),
(1, @cm1_cases, TRUE, TRUE, TRUE, TRUE, TRUE, 1),
(1, @cm1_hear,  TRUE, TRUE, TRUE, TRUE, TRUE, 1),
(1, @cm1_cal,   TRUE, TRUE, TRUE, TRUE, TRUE, 1),
(1, @cm1_users, TRUE, TRUE, TRUE, TRUE, TRUE, 1),
(1, @cm1_rpt,   TRUE, TRUE, TRUE, TRUE, TRUE, 1),
(1, @cm1_set,   TRUE, TRUE, TRUE, TRUE, TRUE, 1);

INSERT INTO role_permissions (role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, created_by) VALUES
(2, @cm1_dash,  FALSE, TRUE,  FALSE, FALSE, FALSE, 1),
(2, @cm1_cases, FALSE, TRUE,  TRUE,  TRUE,  FALSE, 1),
(2, @cm1_hear,  FALSE, TRUE,  TRUE,  TRUE,  FALSE, 1),
(2, @cm1_cal,   FALSE, TRUE,  FALSE, FALSE, FALSE, 1),
(2, @cm1_users, FALSE, FALSE, FALSE, FALSE, FALSE, 1),
(2, @cm1_rpt,   FALSE, TRUE,  FALSE, FALSE, FALSE, 1),
(2, @cm1_set,   FALSE, TRUE,  FALSE, FALSE, FALSE, 1);

INSERT INTO role_permissions (role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, created_by) VALUES
(3, @cm1_dash,  FALSE, TRUE, FALSE, FALSE, FALSE, 1),
(3, @cm1_cases, FALSE, TRUE, FALSE, FALSE, FALSE, 1),
(3, @cm1_hear,  FALSE, TRUE, FALSE, FALSE, FALSE, 1),
(3, @cm1_cal,   FALSE, TRUE, FALSE, FALSE, FALSE, 1),
(3, @cm1_users, FALSE, FALSE, FALSE, FALSE, FALSE, 1),
(3, @cm1_rpt,   FALSE, FALSE, FALSE, FALSE, FALSE, 1),
(3, @cm1_set,   FALSE, FALSE, FALSE, FALSE, FALSE, 1);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.6 Core Business: Cases & Hearings
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

INSERT INTO hearings (chamber_id, case_id, hearing_date, status_code, purpose, notes, next_hearing_date, created_by) VALUES
(1, 1, '2026-01-20', 'CMP', 'Admission hearing',    'Notice issued to respondent', '2026-03-15', 2),
(1, 1, '2026-03-15', 'UP',  'Final arguments',      'Awaiting final disposal',     NULL,       2),
(1, 2, '2026-02-10', 'ADJ', 'Counter affidavit stage', 'Adjourned due to non-filing', '2026-02-28', 3),
(2, 3, '2026-03-01', 'CMP', 'Framing of issues',    'Issues framed',               '2026-04-10', 4);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.7 Case Notes
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO case_notes (chamber_id, case_id, user_id, note_text, is_private, created_by) VALUES
(1, 1, 2, 'Client mentioned new evidence - witness statement from neighbor. Follow up before next hearing.', FALSE, 2),
(1, 1, 1, 'Internal: Consider settlement option if opposing party approaches. Max limit: 5 lakhs.', TRUE, 1),
(1, 1, 3, 'Court fee receipt collected. Original filed in case file.', FALSE, 3),
(1, 2, 2, 'Tahsildar office confirmed - patta cancellation was procedural error. Strong case for quashing.', FALSE, 2),
(1, 2, 1, 'Client wants expedited hearing. File urgency petition if not listed in March.', TRUE, 1),
(2, 3, 4, 'Builder agreed to mediation. Schedule for mid-March before framing of issues.', FALSE, 4);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.8 Email Settings & Templates
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO email_settings (chamber_id, from_email, smtp_host, smtp_port, smtp_user, smtp_password, encryption_code, is_default, status_ind, created_by) VALUES
(1, 'no-reply@vkchamber.in', 'smtp.gmail.com', 587, 'no-reply@vkchamber.in', 'app-password-placeholder', 'T', TRUE,  TRUE, 1),
(1, 'office@vkchamber.in',   'smtp.zoho.com',  587, 'office@vkchamber.in',   'zoho-password-placeholder',  'T', FALSE, TRUE, 1);

INSERT INTO email_templates (chamber_id, code, subject, content, is_customized, enabled_ind, created_by) VALUES
(1, 'hearing_tomorrow',
 'Court Hearing Tomorrow – Urgent: {Case Number}',
 '<p>Dear Advocate,</p><p><strong>Tomorrow</strong> hearing:<br>Case: <b>{Case Number}</b></p><p>Prepare urgently.</p><p>VijayKrishnan & Associates</p>',
 TRUE, TRUE, 1);

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.9 Audit Logs (Sample)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO activity_log (chamber_id, user_id, action, target, ip_address, metadata_json, created_by) VALUES
(1, 2, 'CASE_UPDATE',    'cases',    '117.192.45.12',
 JSON_OBJECT('case_id', 1, 'changed', 'next_hearing_date'), 2),
(1, 3, 'HEARING_CREATE', 'hearings', '49.204.123.88',
 JSON_OBJECT('hearing_id', 3, 'case_id', 2), 3);

INSERT INTO email_log (chamber_id, user_id, template_code, recipient_email, subject, status_code, sent_at, metadata_json, created_by) VALUES
(1, 2, 'hearing_tomorrow', 'priya@vkchamber.in',
 'Court Hearing Tomorrow – Urgent: Crl.O.P.No.234/2025',
 'D', '2026-02-17 17:02:15',
 JSON_OBJECT('case_id', 1, 'hearing_date', '2026-02-18'), 3);

-- =============================================================================
-- END OF SCHEMA & SAMPLE DATA
-- =============================================================================

SELECT '✅ Full Court Diary schema with contextual membership loaded successfully!' AS status_message;