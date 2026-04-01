USE courtdiary;

-- =============================================================================
-- COURT DIARY — SEED DATA (4-Char Code Convention)
-- Rules:
--   1. All CODEs are 4 chars (except refm_modules which uses functional codes)
--   2. Same NAME across tables = Same CODE (e.g., 'Active' = XXAC everywhere)
--   3. Pattern: 2 chars table prefix + 2 chars name
--      Example: refm_plan_types → 'Free' → PTFR
--               refm_case_status → 'Active' → CSAC
--               refm_hearing_status → 'Scheduled' → HSSC
-- =============================================================================

-- =============================================================================
-- 15. SEED DATA — TIER 0  (Pure REFM — no dependencies)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.1  Geographic
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_countries (code, description, phone_code, sort_order) VALUES
('IN  ', 'India', '+91', 1);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.2  Plans & Modules
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_plan_types (code, description, max_users, max_cases, price_monthly_amt, price_annual_amt, sort_order) VALUES
('PTFR', 'Free',       3,    75,    0.00,     0.00,    10),
('PTPR', 'Pro',        10,   300,   999.00,   9999.00, 20),
('PTEN', 'Enterprise', NULL, NULL,  2999.00, 29999.00, 30);

INSERT IGNORE INTO refm_modules (code, name, description, sort_order) VALUES
('ADMN', 'Admin',           'System administration & control',     10),
('BILL', 'Billing',         'Invoices, payments & accounts',       20),
('CALD', 'Calendar',        'Court & personal calendar',           30),
('CASE', 'Cases',           'Case register & details',             40),
('CLNT', 'Clients',         'Client management & details',         50),
('COLL', 'Collaborations',  'Inter-chamber case sharing',          60),
('DASH', 'Dashboard',       'Overview & statistics',               70),
('HEAR', 'Hearings',        'Hearing schedule & history',          80),
('RPRT', 'Reports',         'Analytics & exports',                 90),
('SETT', 'Settings',        'Chamber configuration',               100),
('USER', 'User Management', 'Manage chamber users & roles',        110);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.3  Case & Hearing Statuses
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_case_status (code, description, color_code, sort_order) VALUES
('CSAC', 'Active',    '#3b82f6', 10),
('CSAD', 'Adjourned', '#f97316', 20),
('CSDI', 'Disposed',  '#64748b', 30),
('CSCL', 'Closed',    '#64748b', 40);

INSERT IGNORE INTO refm_hearing_status (code, description, color_code, sort_order) VALUES
('HSUP', 'Upcoming',       '#3b82f6', 10),
('HSSC', 'Scheduled',      '#3b82f6', 15),
('HSCP', 'Completed',      '#22c55e', 20),
('HSAD', 'Adjourned',      '#f97316', 30),
('HSOR', 'Order Reserved', '#a855f7', 40),
('HSDI', 'Disposed',       '#64748b', 50);

INSERT INTO refm_hearing_purpose (code, description, color_code, sort_order, status_ind) VALUES
('HPAD', 'Admission', '#3b82f6', 1, TRUE),
('HPAP', 'Appearance', '#6366f1', 2, TRUE),
('HPAR', 'Arguments', '#8b5cf6', 3, TRUE),
('HPBH', 'Bail Hearing', '#f59e0b', 4, TRUE),
('HPCO', 'Compliance', '#10b981', 5, TRUE),
('HPCE', 'Cross-Examination', '#ef4444', 6, TRUE),
('HPEV', 'Evidence', '#14b8a6', 7, TRUE),
('HPFC', 'Framing of Charges', '#f97316', 8, TRUE),
('HPFI', 'Framing of Issues', '#84cc16', 9, TRUE),
('HPIR', 'Interim Relief', '#22c55e', 10, TRUE),
('HPME', 'Mediation', '#0ea5e9', 11, TRUE),
('HPMN', 'Mention', '#64748b', 12, TRUE),
('HPOP', 'Order Pronounced', '#1d4ed8', 13, TRUE),
('HPPH', 'Part-Heard', '#9333ea', 14, TRUE),
('HPPL', 'Pleadings', '#eab308', 15, TRUE),
('HPSE', 'Sentencing', '#dc2626', 16, TRUE),
('HPST', 'Steps', '#059669', 17, TRUE),
('HPSN', 'Summons/Notice', '#0891b2', 18, TRUE),
('HPWS', 'Written Statement', '#65a30d', 19, TRUE),
('HPOT', 'Other', '#6b7280', 20, TRUE);

INSERT IGNORE INTO refm_case_types (code, description, sort_order) VALUES
('CTCR', 'Criminal',      10),
('CTCV', 'Civil Suit',    20),
('CTWR', 'Writ Petition', 30),
('CTFM', 'Family Matter', 40),
('CTLB', 'Labour Case',   50),
('CTTX', 'Tax Matter',    60),
('CTCN', 'Consumer Case', 70);

INSERT IGNORE INTO refm_client_type (code, description, sort_order) VALUES
('CTIN', 'Individual', 10),
('CTCO', 'Corporate', 20),
('CTGO', 'Government', 30),
('CTTR', 'Trust', 40);

INSERT IGNORE INTO refm_party_type (code, description, sort_order) VALUES
('PTCL', 'Client', 10),
('PTCP', 'Party to Case', 20);

INSERT IGNORE INTO refm_engagement_type (code, description, sort_order) VALUES
('ETPE', 'Petitioner', 10),
('ETRE', 'Respondent', 20);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.4  Email & Communication
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_email_encryption (code, description, sort_order) VALUES
('EENN', 'None', 10),
('EETL', 'TLS',  20),
('EESS', 'SSL',  30),
('EEBT', 'Both', 40);

INSERT IGNORE INTO refm_email_status (code, description, color_code, sort_order) VALUES
('ESPN', 'Pending',   '#f97316', 10),
('ESSN', 'Sent',      '#3b82f6', 20),
('ESDL', 'Delivered', '#22c55e', 30),
('ESOP', 'Opened',    '#a855f7', 40),
('ESFL', 'Failed',    '#ef4444', 50),
('ESBN', 'Bounced',   '#991b1b', 60);

INSERT IGNORE INTO refm_email_templates (code, subject, content, category, sort_order) VALUES
('hearing_tomorrow',
 'Hearing Tomorrow – {Case Number}',
 '<p>Dear {Advocate},</p><p>Hearing tomorrow: <strong>{Case Number}</strong><br>Court: {Court Name}<br>Purpose: {Purpose}</p>',
 'REMINDER', 100),
('welcome_user',
 'Welcome to {Chamber Name}',
 '<p>Hello {FirstName},</p><p>Your account is active.<br>Login: {Email}</p>',
 'WELCOME', 10);

INSERT IGNORE INTO refm_comm_status (code, description, color_code, sort_order) VALUES
('CSPN', 'Pending',   '#f97316', 10),
('CSSN', 'Sent',      '#3b82f6', 20),
('CSDL', 'Delivered', '#22c55e', 30),
('CSRD', 'Read',      '#a855f7', 40),
('CSFL', 'Failed',    '#ef4444', 50);

INSERT IGNORE INTO refm_entity_type (code, description, sort_order) VALUES
('ENTU', 'User',    10),
('ENTC', 'Client',  20);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.5  User & Auth Statuses
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_login_status (code, description, sort_order) VALUES
('LSSU', 'Success', 1),
('LSFA', 'Failed',  2);

INSERT IGNORE INTO refm_user_deletion_status (code, description, sort_order) VALUES
('DSPN', 'Pending',  1),
('DSDE', 'Deleted',  2),
('DSRJ', 'Rejected', 3);

INSERT IGNORE INTO refm_invitation_status (code, description, color_code, sort_order) VALUES
('ISPN', 'Pending',  '#f97316', 10),
('ISAC', 'Accepted', '#22c55e', 20),
('ISRJ', 'Rejected', '#ef4444', 30),
('ISEX', 'Expired',  '#64748b', 40);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.6  Billing, Party Roles, AOR, Collab Access
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_billing_status (code, description, color_code, sort_order) VALUES
('BSPN', 'Pending',   '#f97316', 10),
('BSPD', 'Paid',      '#22c55e', 20),
('BSOV', 'Overdue',   '#ef4444', 30),
('BSCN', 'Cancelled', '#64748b', 40),
('BSAD', 'Adjusted',  '#a855f7', 50);

INSERT IGNORE INTO refm_party_roles (code, description, category, sort_order) VALUES
('PRPE', 'Petitioner',         'PARTY', 10),
('PRRE', 'Respondent',         'PARTY', 20),
('PRAP', 'Appellant',          'PARTY', 30),
('PRDE', 'Defendant',          'PARTY', 40),
('PRPL', 'Plaintiff',          'PARTY', 50),
('PRWI', 'Witness',            'REP',   60),
('PRAO', 'Advocate on Record', 'REP',   70);

INSERT IGNORE INTO refm_aor_status (code, description, color_code, sort_order) VALUES
('ASAC', 'Active',      '#22c55e', 10),
('ASWD', 'Withdrawn',   '#64748b', 20),
('ASSU', 'Substituted', '#f97316', 30);

INSERT IGNORE INTO refm_collab_access (code, description, permissions, color_code, sort_order) VALUES
('CARO', 'Read Only',   'view',                    '#3b82f6', 10),
('CARW', 'Read Write',  'view,edit,create',        '#a855f7', 20),
('CAFU', 'Full Access', 'view,edit,create,delete', '#22c55e', 30);


-- =============================================================================
-- 16. SEED DATA — TIER 1  (REFM with FK to other REFM)
-- =============================================================================

INSERT IGNORE INTO refm_states (code, description, country_code, sort_order) VALUES
('TN  ', 'Tamil Nadu',  'IN  ', 1),
('KL  ', 'Kerala',      'IN  ', 2),
('KA  ', 'Karnataka',   'IN  ', 3),
('MH  ', 'Maharashtra', 'IN  ', 4),
('DL  ', 'Delhi',       'IN  ', 5);

INSERT INTO refm_courts (court_name, state_code, court_type, sort_order) VALUES
('Madras High Court',                    'TN  ', 'High Court',     10),
('City Civil Court, Chennai',            'TN  ', 'Civil Court',    20),
('District Court, Chengalpattu',         'TN  ', 'District Court', 30),
('Principal District Court, Coimbatore', 'TN  ', 'District Court', 40),
('Family Court, Chennai',                'TN  ', 'Family Court',   50),
('JM Court, Saidapet',                   'TN  ', 'Magistrate',     60);


-- =============================================================================
-- 17. SEED DATA — TIER 2  (Core Entities: chamber + users)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 17.1  Chambers
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO chamber (chamber_name, email, phone, city, state_code, plan_code, created_by) VALUES
('VijayKrishnan & Associates', 'office@vkchamber.in',  '9876543210', 'Chennai',    'TN  ', 'PTPR', NULL),
('Sundar Associates',          'office@sundarlaw.in',  '9445123456', 'Coimbatore', 'TN  ', 'PTFR', NULL);

SET @chamber_vk     = (SELECT chamber_id FROM chamber WHERE chamber_name = 'VijayKrishnan & Associates');
SET @chamber_sundar = (SELECT chamber_id FROM chamber WHERE chamber_name = 'Sundar Associates');

-- ─────────────────────────────────────────────────────────────────────────────
-- 17.2  Users (chamber-agnostic)
-- ─────────────────────────────────────────────────────────────────────────────

SET @pwd_hash = '$argon2id$v=19$m=65536,t=3,p=4$hfCeE0IoZay1lhLifA+BkA$3rA1GrCAkdhLzYyGi2S7lc422/W2eEPIqW3MD4u1B48';

INSERT INTO users (email, password_hash, first_name, last_name, phone, created_by) VALUES
('admin@vkchamber.in',   @pwd_hash, 'Vijay',   'Krishnan', '9876543210', NULL),
('priya@vkchamber.in',   @pwd_hash, 'Priya',   'Natarajan','8123456789', 1),
('karthik@vkchamber.in', @pwd_hash, 'Karthik', 'Raja',     '9001234567', 1),
('lokesh@sundarlaw.in',  @pwd_hash, 'Lokesh',  'Mani',     '9445123456', NULL);

SET @user_vijay   = (SELECT user_id FROM users WHERE email = 'admin@vkchamber.in');
SET @user_priya   = (SELECT user_id FROM users WHERE email = 'priya@vkchamber.in');
SET @user_karthik = (SELECT user_id FROM users WHERE email = 'karthik@vkchamber.in');
SET @user_lokesh  = (SELECT user_id FROM users WHERE email = 'lokesh@sundarlaw.in');


-- =============================================================================
-- 18. SEED DATA — TIER 3  (Bridge Tables: profiles, links, modules)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 18.1  User Profiles
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO user_profiles (user_id, address, country, state, city, postal_code,
                           header_color, sidebar_color, primary_color, font_family, updated_by) VALUES
(@user_vijay,   'No. 45, Anna Salai, Teynampet',         'IN  ', 'TN  ', 'Chennai',    '600018', '222 33% 10%', '222 40% 12%', '32.4 99% 63%',  'Nunito, sans-serif', @user_vijay),
(@user_priya,   'Flat 3B, Greenwoods Apartment, Adyar',  'IN  ', 'TN  ', 'Chennai',    '600020', '230 20% 15%', '230 25% 18%', '215 100% 55%',  'Inter, sans-serif',  @user_vijay),
(@user_karthik, '12/5, Gandhi Nagar, Chengalpattu',      'IN  ', 'TN  ', 'Chengalpattu','603001','0 0% 12%',    '0 0% 15%',    '262 83% 58%',   'Nunito, sans-serif', @user_vijay),
(@user_lokesh,  'Plot 78, RS Puram',                     'IN  ', 'TN  ', 'Coimbatore', '641002', '225 30% 11%', '225 35% 14%', '142 76% 36%',   'Roboto, sans-serif', @user_lokesh);

-- ─────────────────────────────────────────────────────────────────────────────
-- 18.2  User ↔ Chamber Links
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO user_chamber_link (user_id, chamber_id, primary_ind, joined_date, created_by) VALUES
(@user_vijay,   @chamber_vk,     TRUE, '2024-01-15', @user_vijay),
(@user_priya,   @chamber_vk,     TRUE, '2024-02-01', @user_vijay),
(@user_karthik, @chamber_vk,     TRUE, '2024-03-10', @user_vijay),
(@user_lokesh,  @chamber_sundar, TRUE, '2024-01-20', @user_lokesh);

SET @link_vijay_vk      = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_vijay   AND chamber_id = @chamber_vk);
SET @link_priya_vk      = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_priya   AND chamber_id = @chamber_vk);
SET @link_karthik_vk    = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_karthik AND chamber_id = @chamber_vk);
SET @link_lokesh_sundar = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_lokesh  AND chamber_id = @chamber_sundar);

-- ─────────────────────────────────────────────────────────────────────────────
-- 18.3  Chamber Modules
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO chamber_modules (chamber_id, module_code, active_ind, created_by) VALUES
(@chamber_vk, 'ADMN', TRUE,  @user_vijay),
(@chamber_vk, 'DASH', TRUE,  @user_vijay),
(@chamber_vk, 'CASE', TRUE,  @user_vijay),
(@chamber_vk, 'HEAR', TRUE,  @user_vijay),
(@chamber_vk, 'CALD', TRUE,  @user_vijay),
(@chamber_vk, 'CLNT', TRUE,  @user_vijay),
(@chamber_vk, 'BILL', TRUE,  @user_vijay),
(@chamber_vk, 'USER', TRUE,  @user_vijay),
(@chamber_vk, 'RPRT', TRUE,  @user_vijay),
(@chamber_vk, 'SETT', TRUE,  @user_vijay),
(@chamber_vk, 'COLL', TRUE,  @user_vijay);

INSERT INTO chamber_modules (chamber_id, module_code, active_ind, created_by) VALUES
(@chamber_sundar, 'ADMN', TRUE,  @user_lokesh),
(@chamber_sundar, 'DASH', TRUE,  @user_lokesh),
(@chamber_sundar, 'CASE', TRUE,  @user_lokesh),
(@chamber_sundar, 'HEAR', TRUE,  @user_lokesh),
(@chamber_sundar, 'CALD', TRUE,  @user_lokesh),
(@chamber_sundar, 'CLNT', TRUE,  @user_lokesh),
(@chamber_sundar, 'BILL', TRUE,  @user_lokesh),
(@chamber_sundar, 'USER', FALSE, @user_lokesh),
(@chamber_sundar, 'RPRT', FALSE, @user_lokesh),
(@chamber_sundar, 'SETT', TRUE,  @user_lokesh),
(@chamber_sundar, 'COLL', TRUE,  @user_lokesh);


-- =============================================================================
-- 19. SEED DATA — TIER 4 & 5  (Roles & Permissions)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 19.1  Security Roles (Master Templates)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO security_roles (role_name, description, admin_ind, system_ind, created_by) VALUES
('Administrator',   'Full access to all modules',         TRUE, TRUE, @user_vijay),
('Senior Advocate', 'Manage cases, hearings and clients', FALSE, TRUE, @user_vijay);

-- ─────────────────────────────────────────────────────────────────────────────
-- 19.2  Chamber Roles (Copy from master)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO chamber_roles (chamber_id, role_name, description, admin_ind, system_ind, created_by) VALUES
(@chamber_vk, 'Administrator',   'Full access to all modules',         TRUE, TRUE, @user_vijay),
(@chamber_vk, 'Senior Advocate', 'Manage cases, hearings and clients', FALSE, TRUE, @user_vijay),

(@chamber_sundar, 'Administrator', 'Full access to all modules', FALSE, TRUE, @user_lokesh);

-- ─────────────────────────────────────────────────────────────────────────────
-- 19.3  User Roles (link to chamber_roles)
-- ─────────────────────────────────────────────────────────────────────────────

SET @role_admin_vk   = (SELECT role_id FROM chamber_roles WHERE chamber_id = @chamber_vk   AND role_name = 'Administrator');
SET @role_senior_vk  = (SELECT role_id FROM chamber_roles WHERE chamber_id = @chamber_vk   AND role_name = 'Senior Advocate');
SET @role_admin_sundar = (SELECT role_id FROM chamber_roles WHERE chamber_id = @chamber_sundar AND role_name = 'Administrator');

INSERT INTO user_roles (link_id, role_id, start_date, created_by) VALUES
(@link_vijay_vk,      @role_admin_vk,   '2024-01-15', @user_vijay),
(@link_priya_vk,      @role_senior_vk,  '2024-02-01', @user_vijay),
(@link_karthik_vk,    @role_senior_vk,  '2024-03-10', @user_vijay),
(@link_lokesh_sundar, @role_admin_sundar, '2024-01-20', @user_lokesh);

-- ─────────────────────────────────────────────────────────────────────────────
-- 19.4  Role Permissions (per chamber role)
-- ─────────────────────────────────────────────────────────────────────────────

SET @cm_admn  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'ADMN');
SET @cm_dash  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'DASH');
SET @cm_case  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'CASE');
SET @cm_hear  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'HEAR');
SET @cm_cald  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'CALD');
SET @cm_clnt  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'CLNT');
SET @cm_bill  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'BILL');
SET @cm_user  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'USER');
SET @cm_rprt  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'RPRT');
SET @cm_sett  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'SETT');
SET @cm_coll  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'COLL');

-- Administrator - Full Access
INSERT INTO role_permissions (role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, import_ind, export_ind, created_by) VALUES
(@role_admin_vk, @cm_admn, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_dash, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_case, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_hear, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_cald, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_clnt, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_bill, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_user, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_rprt, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_sett, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_coll, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay);

-- Senior Advocate - Manage Cases/Hearings
INSERT INTO role_permissions (role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, import_ind, export_ind, created_by) VALUES
(@role_senior_vk, @cm_admn, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_dash, FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_case, FALSE, TRUE,  TRUE,  TRUE,  FALSE, TRUE,  TRUE,  @user_vijay),
(@role_senior_vk, @cm_hear, FALSE, TRUE,  TRUE,  TRUE,  FALSE, TRUE,  TRUE,  @user_vijay),
(@role_senior_vk, @cm_cald, FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_clnt, FALSE, TRUE,  TRUE,  TRUE,  FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_bill, FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_user, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_rprt, FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, TRUE,  @user_vijay),
(@role_senior_vk, @cm_sett, FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_coll, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay);


-- =============================================================================
-- 20. SEED DATA — TIER 6  (Cases — Dashboard Ready)
-- =============================================================================

INSERT INTO cases (chamber_id, case_number, court_id, case_type_code, filing_year,
                   petitioner, respondent, aor_user_id, case_summary, status_code,
                   next_hearing_date, last_hearing_date, created_by) VALUES
-- OVERDUE CASES
(@chamber_vk, 'Crl.O.P.No.234/2025',   1, 'CTCR', 2025,
 'State of Tamil Nadu', 'Arjun Prasad',      @user_priya,
 'Quashing of FIR u/s 420 IPC – financial fraud',                      'CSAC',  '2026-03-20', '2026-03-15', @user_vijay),

(@chamber_vk, 'W.P.(MD)No.5678/2025',  1, 'CTWR', 2025,
 'Tmt. Saraswathi',     'The Tahsildar',     @user_priya,
 'Challenge to patta cancellation order',                               'CSAC',  '2026-03-22', '2026-03-18', @user_vijay),

(@chamber_vk, 'Crl.M.C.No.89/2026',    6, 'CTCR', 2026,
 'Ramesh Kumar',        'Inspector of Police', @user_priya,
 'Anticipatory bail petition',                                         'CSAC',  '2026-03-18', '2026-03-10', @user_vijay),

-- UPCOMING THIS WEEK
(@chamber_vk, 'O.S.No.456/2025',       2, 'CTCV', 2025,
 'Meenkshi Textiles',   'Global Exports Ltd',  @user_priya,
 'Suit for specific performance of sale agreement',                     'CSAC',  '2026-03-26', '2026-03-19', @user_vijay),

(@chamber_vk, 'F.C.No.123/2025',       5, 'CTFM', 2025,
 'Lakshmi Devi',        'Suresh Babu',         @user_priya,
 'Divorce petition under Hindu Marriage Act',                           'CSAC',  '2026-03-27', '2026-03-12', @user_vijay),

(@chamber_vk, 'L.C.No.78/2025',        3, 'CTLB', 2025,
 'Workmen Union',       'ABC Manufacturing',   @user_priya,
 'Labour dispute – wrongful termination',                                'CSAC',  '2026-03-28', '2026-03-14', @user_vijay),

-- FUTURE CASES
(@chamber_vk, 'Crl.O.P.No.567/2026',   1, 'CTCR', 2026,
 'State of Tamil Nadu', 'Murugan',             @user_priya,
 'Quashing of criminal proceedings',                                    'CSAC',  '2026-04-15', NULL,         @user_vijay),

(@chamber_vk, 'W.P.No.9012/2026',      1, 'CTWR', 2026,
 'Chennai Developers',  'DTCP',                @user_priya,
 'Writ against planning permission denial',                             'CSAC',  '2026-04-20', NULL,         @user_vijay),

-- ADJOURNED CASES
(@chamber_vk, 'O.S.No.789/2024',       2, 'CTCV', 2024,
 'Subramanian',         'Venkatesh',           @user_priya,
 'Property partition suit',                                             'CSAD', '2026-04-05', '2026-03-21', @user_vijay),

-- DISPOSED/CLOSED
(@chamber_vk, 'Crl.M.C.No.45/2024',    6, 'CTCR', 2024,
 'Anand',               'State of TN',         @user_priya,
 'Bail application – disposed',                                         'CSDI', NULL,         '2026-02-15', @user_vijay),

(@chamber_vk, 'F.C.No.56/2024',        5, 'CTFM', 2024,
 'Priya',               'Rajesh',              @user_priya,
 'Custody matter – closed',                                             'CSCL', NULL,         '2026-01-30', @user_vijay),

-- Sundar Associates Cases
(@chamber_sundar, 'O.S.No.145/2024',   4, 'CTCV', 2024,
 'M/s Blue Sky Builders', 'T.N. Housing Board', @user_lokesh,
 'Specific performance of sale agreement – construction dispute',       'CSAC',  '2026-04-10', '2026-03-01', @user_lokesh),

(@chamber_sundar, 'Crl.O.P.No.88/2025', 1, 'CTCR', 2025,
 'State of Tamil Nadu', 'Ganesh',              @user_lokesh,
 'Criminal revision petition',                                          'CSAC',  '2026-03-25', '2026-03-10', @user_lokesh);


-- =============================================================================
-- 21. SEED DATA — TIER 7  (Hearings — Dashboard Ready)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 21.1  Hearings (Various Dates for Dashboard Widgets)
-- ─────────────────────────────────────────────────────────────────────────────

-- =============================================================================
-- FETCH CASE IDS (VK CHAMBER ONLY)
-- =============================================================================

SELECT case_id INTO @case1 FROM cases WHERE case_number = 'Crl.O.P.No.234/2025' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case2 FROM cases WHERE case_number = 'W.P.(MD)No.5678/2025' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case3 FROM cases WHERE case_number = 'Crl.M.C.No.89/2026' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case4 FROM cases WHERE case_number = 'O.S.No.456/2025' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case5 FROM cases WHERE case_number = 'F.C.No.123/2025' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case6 FROM cases WHERE case_number = 'L.C.No.78/2025' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case7 FROM cases WHERE case_number = 'Crl.O.P.No.567/2026' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case8 FROM cases WHERE case_number = 'W.P.No.9012/2026' AND chamber_id = @chamber_vk LIMIT 1;
SELECT case_id INTO @case9 FROM cases WHERE case_number = 'O.S.No.789/2024' AND chamber_id = @chamber_vk LIMIT 1;

-- =============================================================================
-- HEARINGS (ALL 9 CASES)
-- =============================================================================

INSERT INTO hearings 
(chamber_id, case_id, hearing_date, status_code, purpose_code, notes, next_hearing_date, created_by) VALUES

-- =========================
-- OVERDUE CASES
-- =========================

(@chamber_vk, @case1, '2026-03-20', 'HSUP', 'HPAR', 'Final arguments pending', '2026-03-24', @user_priya),
(@chamber_vk, @case2, '2026-03-22', 'HSUP', 'HPEV', 'Witness examination ongoing', '2026-03-24', @user_priya),
(@chamber_vk, @case3, '2026-03-18', 'HSUP', 'HPAD', 'Anticipatory bail hearing', '2026-03-25', @user_priya),

-- =========================
-- TODAY'S HEARINGS
-- =========================

(@chamber_vk, @case1, '2026-03-24', 'HSUP', 'HPAR', 'Final arguments hearing', NULL, @user_priya),
(@chamber_vk, @case2, '2026-03-24', 'HSUP', 'HPEV', 'Evidence stage hearing', NULL, @user_priya),
(@chamber_vk, @case3, '2026-03-24', 'HSUP', 'HPAR', 'Arguments stage', NULL, @user_priya),

-- =========================
-- UPCOMING THIS WEEK
-- =========================

(@chamber_vk, @case4, '2026-03-26', 'HSUP', 'HPAD', 'First hearing (admission)', NULL, @user_priya),
(@chamber_vk, @case5, '2026-03-27', 'HSUP', 'HPME', 'Mediation scheduled', NULL, @user_priya),
(@chamber_vk, @case6, '2026-03-28', 'HSUP', 'HPEV', 'Document evidence submission', NULL, @user_priya),

-- =========================
-- FUTURE HEARINGS
-- =========================

(@chamber_vk, @case7, '2026-04-15', 'HSUP', 'HPAR', 'Arguments to be presented', NULL, @user_priya),
(@chamber_vk, @case8, '2026-04-20', 'HSUP', 'HPPL', 'Pleadings stage', NULL, @user_priya),

-- =========================
-- ADJOURNED CASE
-- =========================

(@chamber_vk, @case9, '2026-03-21', 'HSAD', 'HPAD', 'Adjourned due to counsel absence', '2026-04-05', @user_priya),

-- =========================
-- COMPLETED HISTORY (for richness)
-- =========================

(@chamber_vk, @case1, '2026-03-15', 'HSCP', 'HPAD', 'Preliminary hearing completed', '2026-03-24', @user_priya),
(@chamber_vk, @case2, '2026-03-18', 'HSCP', 'HPPL', 'Pleadings completed', '2026-03-24', @user_priya),
(@chamber_vk, @case3, '2026-03-10', 'HSCP', 'HPAD', 'Initial hearing completed', '2026-03-24', @user_priya);

-- ===============================================================================================================
-- 22-25. REMAINING SEED DATA (Clients, Case Clients, Case Notes, AORs, Email, Invitations, Logs)
-- ===============================================================================================================

-- -----------------------------------------------------------------------------
-- 22.1  Clients (Based on Case Petitioners/Respondents)
-- -----------------------------------------------------------------------------

INSERT INTO clients (chamber_id, client_type_code, party_type_code, client_name, display_name, 
                     contact_person, email, phone, alternate_phone, 
                     address_line1, city, state_code, postal_code, country_code,
                     id_proof_type, id_proof_number, source_code, referral_source,
                     client_since, notes, deleted_ind, created_by) VALUES
-- Case parties (PTCP)
(@chamber_vk, 'CTIN', 'PTCP', 'Arjun Prasad', 'Mr. Arjun Prasad', 'Arjun Prasad', 'arjun.prasad@email.com', '9876501234', NULL,
 'No. 15, Gandhi Nagar', 'Chennai', 'TN', '600020', 'IN', 'PAN', 'ABCDE1234F', 'REF', 'Existing client referral',
 '2024-01-10', 'Accused in Crl.O.P.No.234/2025 - FIR quashing case', FALSE, @user_vijay),

(@chamber_vk, 'CTIN', 'PTCP', 'Tmt. Saraswathi', 'Mrs. Saraswathi', 'Saraswathi', 'saraswathi@email.com', '9876502345', NULL,
 'No. 28, Temple Street', 'Chengalpattu', 'TN', '603001', 'IN', 'Aadhaar', '1234-5678-9012', 'WALK', 'Direct walk-in',
 '2024-02-15', 'Writ petition against patta cancellation', FALSE, @user_vijay),

(@chamber_vk, 'CTIN', 'PTCP', 'Ramesh Kumar', 'Mr. Ramesh Kumar', 'Ramesh Kumar', 'ramesh.kumar@email.com', '9876503456', '9876503457',
 'No. 42, Anna Nagar', 'Chennai', 'TN', '600040', 'IN', 'PAN', 'XYZAB5678C', 'REF', 'Senior Advocate referral',
 '2025-12-20', 'Anticipatory bail petition - Crl.M.C.No.89/2026', FALSE, @user_priya),

(@chamber_vk, 'CTIN', 'PTCP', 'Lakshmi Devi', 'Mrs. Lakshmi Devi', 'Lakshmi Devi', 'lakshmi.devi@email.com', '9876505678', NULL,
 'No. 67, Residential Area', 'Chennai', 'TN', '600028', 'IN', 'Aadhaar', '9876-5432-1098', 'REF', 'Family friend referral',
 '2025-07-15', 'Divorce petition - F.C.No.123/2025', FALSE, @user_priya),

(@chamber_vk, 'CTCO', 'PTCP', 'Workmen Union', 'Workmen Union - Local Chapter', 'Secretary (Name Redacted)', 'union@workmen.org', '9876506789', NULL,
 'Trade Union Office, Teynampet', 'Chennai', 'TN', '600018', 'IN', 'Registration', 'TU/2020/1234', 'REF', 'Trade association referral',
 '2025-03-20', 'Labour dispute - wrongful termination case', FALSE, @user_vijay),

(@chamber_vk, 'CTIN', 'PTCP', 'Murugan', 'Mr. Murugan', 'Murugan', 'murugan@email.com', '9876507890', NULL,
 'No. 89, Village Road', 'Kanchipuram', 'TN', '631501', 'IN', 'PAN', 'MURGA1234D', 'WALK', 'Direct approach',
 '2026-01-05', 'Criminal proceedings quashing - Crl.O.P.No.567/2026', FALSE, @user_priya),

(@chamber_vk, 'CTCO', 'PTCP', 'Chennai Developers', 'Chennai Developers Ltd', 'VP Legal (Name Redacted)', 'legal@chennaidev.com', '9876508901', '9876508902',
 'Corporate Office, OMR', 'Chennai', 'TN', '600096', 'IN', 'GST', '33CHNDE1234F1Z9', 'REF', 'Corporate client',
 '2026-01-20', 'Writ against DTCP planning permission denial', FALSE, @user_vijay),

(@chamber_vk, 'CTIN', 'PTCP', 'Subramanian', 'Mr. Subramanian', 'Subramanian', 'subramanian@email.com', '9876509012', NULL,
 'No. 34, Heritage Colony', 'Chennai', 'TN', '600041', 'IN', 'PAN', 'SUBRA5678E', 'REF', 'Long-time client',
 '2024-05-10', 'Property partition suit - O.S.No.789/2024', FALSE, @user_vijay),

(@chamber_vk, 'CTIN', 'PTCP', 'Anand', 'Mr. Anand', 'Anand', 'anand@email.com', '9876500123', NULL,
 'No. 12, Bail Road', 'Chennai', 'TN', '600034', 'IN', 'Aadhaar', '1111-2222-3333', 'WALK', 'Court complex reference',
 '2024-01-05', 'Bail application - disposed (Crl.M.C.No.45/2024)', FALSE, @user_priya),

(@chamber_vk, 'CTIN', 'PTCP', 'Priya', 'Mrs. Priya', 'Priya', 'priya.custody@email.com', '9876500234', NULL,
 'No. 56, Family Court Area', 'Chennai', 'TN', '600014', 'IN', 'Aadhaar', '4444-5555-6666', 'REF', 'Family court referral',
 '2024-01-15', 'Custody matter - closed (F.C.No.56/2024)', FALSE, @user_vijay),

(@chamber_sundar, 'CTCO', 'PTCP', 'M/s Blue Sky Builders', 'Blue Sky Builders Pvt Ltd', 'Managing Director', 'contact@bluesky.com', '9445101234', '9445101235',
 'Construction Site Office, Gandhipuram', 'Coimbatore', 'TN', '641012', 'IN', 'GST', '33BLUSK1234F1Z2', 'WEB', 'Website contact',
 '2024-08-01', 'Construction dispute - specific performance case', FALSE, @user_lokesh),

(@chamber_sundar, 'CTIN', 'PTCP', 'Ganesh', 'Mr. Ganesh', 'Ganesh', 'ganesh.criminal@email.com', '9445102345', NULL,
 'No. 78, Court Road', 'Coimbatore', 'TN', '641018', 'IN', 'PAN', 'GANES9012F', 'REF', 'Local advocate referral',
 '2025-03-10', 'Criminal revision petition - Crl.O.P.No.88/2025', FALSE, @user_lokesh),

-- General chamber clients (PTCL)
(@chamber_vk, 'CTCO', 'PTCL', 'Meenkshi Textiles', 'Meenkshi Textiles Pvt Ltd', 'Rajesh Mehta (Director)', 'contact@meenkshi.com', '9876504567', '9876504568',
 'Plot 156, Industrial Estate', 'Chennai', 'TN', '600032', 'IN', 'GST', '33ABCDE1234F1Z5', 'WEB', 'Website inquiry',
 '2025-06-10', 'Corporate advisory client — not currently a party to litigation', FALSE, @user_vijay),

(@chamber_vk, 'CTIN', 'PTCL', 'Sundar Raj', 'Mr. Sundar Raj', 'Sundar Raj', 'sundar.raj@email.com', '9876509999', NULL,
 'No. 101, Main Road', 'Chennai', 'TN', '600050', 'IN', 'PAN', 'SUNDR1234X', 'REF', 'Walk-in consultation',
 '2026-02-01', 'General advisory client — no active case', FALSE, @user_vijay);


-- Store client IDs for case linking
SET @client_arjun        = (SELECT client_id FROM clients WHERE client_name = 'Arjun Prasad' AND chamber_id = @chamber_vk);
SET @client_saraswathi   = (SELECT client_id FROM clients WHERE client_name = 'Tmt. Saraswathi' AND chamber_id = @chamber_vk);
SET @client_ramesh       = (SELECT client_id FROM clients WHERE client_name = 'Ramesh Kumar' AND chamber_id = @chamber_vk);
SET @client_meenkshi     = (SELECT client_id FROM clients WHERE client_name = 'Meenkshi Textiles' AND chamber_id = @chamber_vk);
SET @client_lakshmi      = (SELECT client_id FROM clients WHERE client_name = 'Lakshmi Devi' AND chamber_id = @chamber_vk);
SET @client_workmen      = (SELECT client_id FROM clients WHERE client_name = 'Workmen Union' AND chamber_id = @chamber_vk);
SET @client_murugan      = (SELECT client_id FROM clients WHERE client_name = 'Murugan' AND chamber_id = @chamber_vk);
SET @client_chennai_dev  = (SELECT client_id FROM clients WHERE client_name = 'Chennai Developers' AND chamber_id = @chamber_vk);
SET @client_subramanian  = (SELECT client_id FROM clients WHERE client_name = 'Subramanian' AND chamber_id = @chamber_vk);
SET @client_anand        = (SELECT client_id FROM clients WHERE client_name = 'Anand' AND chamber_id = @chamber_vk);
SET @client_priya_cust   = (SELECT client_id FROM clients WHERE client_name = 'Priya' AND chamber_id = @chamber_vk);
SET @client_bluesky      = (SELECT client_id FROM clients WHERE client_name = 'M/s Blue Sky Builders' AND chamber_id = @chamber_sundar);
SET @client_ganesh       = (SELECT client_id FROM clients WHERE client_name = 'Ganesh' AND chamber_id = @chamber_sundar);

-- -----------------------------------------------------------------------------
-- 22.2  Case Clients (Link Clients to Cases with Party Roles)
-- -----------------------------------------------------------------------------

INSERT INTO case_clients (chamber_id, case_id, client_id, party_role_code, 
                          primary_ind, engagement_type_code, created_by) VALUES
-- VijayKrishnan & Associates Case-Client Links
(@chamber_vk, @case1, @client_arjun,       'PRPE', TRUE,  'ETPE', @user_vijay),
(@chamber_vk, @case1, @client_saraswathi,  'PRRE', FALSE, 'ETRE', @user_vijay),

(@chamber_vk, @case2, @client_saraswathi,  'PRPE', TRUE,  'ETPE', @user_vijay),
(@chamber_vk, @case2, @client_ramesh,      'PRRE', FALSE, 'ETRE', @user_vijay),

(@chamber_vk, @case3, @client_ramesh,      'PRPE', TRUE,  'ETPE', @user_priya),
(@chamber_vk, @case3, @client_murugan,     'PRRE', FALSE, 'ETRE', @user_priya),

(@chamber_vk, @case4, @client_meenkshi,    'PRPE', TRUE,  'ETPE', @user_vijay),
(@chamber_vk, @case4, @client_lakshmi,     'PRRE', FALSE, 'ETRE', @user_vijay),

(@chamber_vk, @case5, @client_lakshmi,     'PRPE', TRUE,  'ETPE', @user_priya),
(@chamber_vk, @case5, @client_subramanian, 'PRRE', FALSE, 'ETRE', @user_priya),

(@chamber_vk, @case6, @client_workmen,     'PRPE', TRUE,  'ETPE', @user_vijay),
(@chamber_vk, @case6, @client_bluesky,     'PRRE', FALSE, 'ETRE', @user_vijay),

(@chamber_vk, @case7, @client_murugan,     'PRPE', TRUE,  'ETPE', @user_priya),
(@chamber_vk, @case7, @client_anand,       'PRRE', FALSE, 'ETRE', @user_priya),

(@chamber_vk, @case8, @client_chennai_dev, 'PRPE', TRUE,  'ETPE', @user_vijay),
(@chamber_vk, @case8, @client_ganesh,      'PRRE', FALSE, 'ETRE', @user_vijay),

(@chamber_vk, @case9, @client_subramanian, 'PRPE', TRUE,  'ETPE', @user_vijay),
(@chamber_vk, @case9, @client_priya_cust,  'PRRE', FALSE, 'ETRE', @user_vijay);


-- -----------------------------------------------------------------------------
-- 22.3  Case Notes (Detailed Notes per Case)
-- -----------------------------------------------------------------------------

INSERT INTO case_notes (chamber_id, case_id, user_id, note_text, 
                        private_ind, created_by) VALUES
-- Case 1: Crl.O.P.No.234/2025 (Arjun Prasad - FIR Quashing)
(@chamber_vk, @case1, @user_priya, 
 'Client mentioned new evidence – witness statement from neighbour confirming alibi. Need to file supplementary affidavit before next hearing.', 
 FALSE, @user_priya),
(@chamber_vk, @case1, @user_vijay, 
 'INTERNAL: Consider settlement if opposing party approaches. Max limit: 5 lakhs. Client has financial constraints.', 
 TRUE, @user_vijay),
(@chamber_vk, @case1, @user_karthik, 
 'Court fee receipt collected (Rs. 500). Original filed in case file. Copy with client.', 
 FALSE, @user_karthik),

-- Case 2: W.P.(MD)No.5678/2025 (Saraswathi - Patta Cancellation)
(@chamber_vk, @case2, @user_priya, 
 'Tahsildar office confirmed – patta cancellation was procedural error. Strong case for quashing. Got verbal confirmation from clerk.', 
 FALSE, @user_priya),
(@chamber_vk, @case2, @user_vijay, 
 'Client wants expedited hearing. File urgency petition if not listed in March batch. Client is senior citizen.', 
 TRUE, @user_vijay),

-- Case 3: Crl.M.C.No.89/2026 (Ramesh Kumar - Anticipatory Bail)
(@chamber_vk, @case3, @user_priya, 
 'Police inspector indicated willingness for compromise. Need to discuss with client before next date.', 
 FALSE, @user_priya),
(@chamber_vk, @case3, @user_karthik, 
 'Previous bail orders from similar cases collected. Ready for submission.', 
 FALSE, @user_karthik),

-- Case 4: O.S.No.456/2025 (Meenkshi Textiles - Specific Performance)
(@chamber_vk, @case4, @user_vijay, 
 'Opposing party showed interest in settlement during last adjournment. Client open to 15% premium over agreement value.', 
 TRUE, @user_vijay),
(@chamber_vk, @case4, @user_priya, 
 'Sale deed draft reviewed. Minor corrections needed in clause 7(b). Will send revised copy by Friday.', 
 FALSE, @user_priya),

-- Case 5: F.C.No.123/2025 (Lakshmi Devi - Divorce)
(@chamber_vk, @case5, @user_priya, 
 'Maintenance pendente lite amount agreed at Rs. 25,000/month. Respondent''s lawyer confirmed acceptance.', 
 FALSE, @user_priya),
(@chamber_vk, @case5, @user_vijay, 
 'Custody of minor child - client willing to give visitation rights on weekends. Document this in settlement.', 
 TRUE, @user_vijay),

-- Case 6: L.C.No.78/2025 (Workmen Union - Labour Dispute)
(@chamber_vk, @case6, @user_vijay, 
 'Union leader wants reinstatement + back wages. Management offering only reinstatement. Gap needs negotiation.', 
 TRUE, @user_vijay),
(@chamber_vk, @case6, @user_karthik, 
 'Labour commissioner office confirmed - conciliation failed. Ready for adjudication.', 
 FALSE, @user_karthik);

-- ─────────────────────────────────────────────────────────────────────────────
-- 22.2  Case AORs
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO case_aors (case_id, user_id, chamber_id, primary_ind, appointment_date, status_code, created_by) VALUES
(@case1, @user_priya, @chamber_vk,     TRUE,  '2025-01-10', 'ASAC', @user_vijay),
(@case2, @user_priya, @chamber_vk,     TRUE,  '2025-03-05', 'ASAC', @user_vijay),
(@case3, @user_lokesh, @chamber_sundar, TRUE, '2024-08-12', 'ASAC', @user_lokesh),
(@case4, @user_priya, @chamber_vk,     TRUE,  '2025-06-15', 'ASAC', @user_vijay),
(@case5, @user_priya, @chamber_vk,     TRUE,  '2025-07-20', 'ASAC', @user_vijay);

-- =============================================================================
-- 23. SEED DATA — TIER 9  (Config: Email Settings & Templates)
-- =============================================================================

INSERT INTO email_settings (chamber_id, from_email, smtp_host, smtp_port, smtp_user, smtp_password, encryption_code, default_ind, status_ind, created_by) VALUES
(@chamber_vk, 'no-reply@vkchamber.in', 'smtp.gmail.com', 587, 'no-reply@vkchamber.in', 'app-password-placeholder', 'EETL', TRUE,  TRUE, @user_vijay),
(@chamber_vk, 'office@vkchamber.in',   'smtp.zoho.com',  587, 'office@vkchamber.in',   'zoho-password-placeholder', 'EETL', FALSE, TRUE, @user_vijay);

INSERT INTO email_templates (chamber_id, code, subject, content, customized_ind, enabled_ind, created_by) VALUES
(@chamber_vk, 'hearing_tomorrow', 'Court Hearing Tomorrow – Urgent: {Case Number}', '<p>Dear Advocate,</p><p><strong>Tomorrow</strong> hearing:<br>Case: <b>{Case Number}</b></p>', TRUE, TRUE, @user_vijay);
-- =============================================================================
-- 24. SEED DATA — TIER 10  (Collaboration & Invitations)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 24.1  Case Collaborations
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO case_collaborations (case_id, owner_chamber_id, collaborator_chamber_id, access_level, invited_by, invited_date, accepted_date, status_code, created_by)
VALUES (@case1, @chamber_vk, @chamber_sundar, 'CARW', @user_vijay, '2026-02-15', '2026-02-16', 'ISAC', @user_vijay);

-- ─────────────────────────────────────────────────────────────────────────────
-- 24.2  User Invitations (for Pending Invites widget)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO user_invitations (chamber_id, email, role_id, invited_by, invited_date, expires_date, status_code, message, created_by)
VALUES 
(@chamber_vk, 'newlawyer@example.com', @role_senior_vk, @user_vijay, '2026-03-20', '2026-04-19', 'ISPN', 'Welcome to VijayKrishnan & Associates!', @user_vijay),
(@chamber_vk, 'senlawyer@example.com', @role_senior_vk, @user_vijay, '2026-03-22', '2026-04-21', 'ISPN', 'Join our team as a Senior Advocate.', @user_vijay);

-- Users (varied avatar styles)
INSERT INTO profile_images (user_id, client_id, image_data, description, created_by)
VALUES
(@user_vijay,   NULL, 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiM0YzUxYzgiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjQwIiByPSIxNSIgZmlsbD0iI2ZmZiIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNzAiIHI9IjIwIiBmaWxsPSIjZmZmIi8+PHJlY3QgeD0iNDUiIHk9IjUwIiB3aWR0aD0iMTAiIGhlaWdodD0iMjAiIGZpbGw9IiNmZmYiLz48cG9seWdvbiBwb2ludHM9IjUwLDMwIDU1LDQwIDQ1LDQwIiBmaWxsPSIjZmZmIi8+PC9zdmc+', 'Avatar: abstract person icon for Vijay',   @user_vijay),
(@user_priya,   NULL, 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNTAiIGZpbGw9IiNmYzRlMDIiLz48Y2lyY2xlIGN4PSIzNSIgY3k9IjQwIiByPSI4IiBmaWxsPSIjZmZmIi8+PGNpcmNsZSBjeD0iNjUiIGN5PSI0MCIgcj0iOCIgZmlsbD0iI2ZmZiIvPjxwYXRoIGQ9Ik0zMCA3MCBRNTAgODAgNzAgNzAiIHN0cm9rZT0iI2ZmZiIgZmlsbD0ibm9uZSIgc3Ryb2tlLXdpZHRoPSI2Ii8+PC9zdmc+', 'Avatar: smiley face for Priya',   @user_vijay),
(@user_karthik, NULL, 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiMyMjJkMzIiLz48cG9seWdvbiBwb2ludHM9IjUwLDEwIDkwLDMwIDkwLDcwIDUwLDkwIDEwLDcwIDEwLDMwIiBmaWxsPSIjZTU5YzQyIiBmaWxsLW9wYWNpdHk9IjAuOSIvPjx0ZXh0IHg9IjUwIiB5PSI1NSIgZm9udC1zaXplPSIzMCIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iIGZpbGw9IiNmZmYiIGZvbnQtZmFtaWx5PSJtb25vc3BhY2UiPks8L3RleHQ+PC9zdmc+', 'Avatar: hexagon with initial K for Karthik', @user_vijay),
(@user_lokesh,  NULL, 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNTAiIGZpbGw9IiNmZjY2Y2MiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzMCIgZmlsbD0iI2ZmZmZmZiIgZmlsbC1vcGFjaXR5PSIwLjMiLz48cGF0aCBkPSJNMzUsMzUgTDY1LDY1IE02NSwzNSBMNjUsMzUiIHN0cm9rZT0iI2ZmZiIgc3Ryb2tlLXdpZHRoPSI4IiBmaWxsPSJub25lIi8+PC9zdmc+', 'Avatar: abstract cross pattern for Lokesh',  @user_vijay);

-- Clients (diverse avatars)
INSERT INTO profile_images (user_id, client_id, image_data, description, created_by)
VALUES
( NULL, @client_arjun,       'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiMxNTQzNjAiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iI2ZmZDk2NiIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNTAiIHI9IjI1IiBmaWxsPSIjMTU0MzYwIi8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LXNpemU9IjI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSIgZmlsbD0iI2ZmZmZmZiIgZm9udC1mYW1pbHk9IkFyaWFsIj5BUDwvdGV4dD48L3N2Zz4=', 'Avatar: ringed initial for Arjun Prasad',       @user_vijay),
( NULL, @client_saraswathi,  'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiM5YzI3YzAiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iI2ZmYzQwMCIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNDAiIHI9IjEwIiBmaWxsPSIjOWMyN2MwIi8+PHJlY3QgeD0iNDUiIHk9IjUwIiB3aWR0aD0iMTAiIGhlaWdodD0iMjAiIGZpbGw9IiM5YzI3YzAiLz48cG9seWdvbiBwb2ludHM9IjUwLDcwIDQwLDYwIDYwLDYwIiBmaWxsPSIjOWMyN2MwIi8+PC9zdmc+', 'Avatar: abstract flower for Saraswathi',   @user_vijay),
( NULL, @client_ramesh,      'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiMyQzNCNUUiLz48cG9seWdvbiBwb2ludHM9IjUwLDIwIDgwLDQwIDgwLDYwIDUwLDgwIDIwLDYwIDIwLDQwIiBmaWxsPSIjRkZENjY2Ii8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LXNpemU9IjI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSIgZmlsbD0iIzJDM0I1RSIgZm9udC1mYW1pbHk9IkFyaWFsIj5SSzwvdGV4dD48L3N2Zz4=', 'Avatar: diamond with initials RK for Ramesh',      @user_priya),
( NULL, @client_meenkshi,    'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNTAiIGZpbGw9IiM5RTlFOUUiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjQwIiByPSIxMiIgZmlsbD0iI2ZmZiIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNzAiIHI9IjE4IiBmaWxsPSIjZmZmIi8+PHJlY3QgeD0iNDUiIHk9IjUwIiB3aWR0aD0iMTAiIGhlaWdodD0iMjAiIGZpbGw9IiM5ZTllOWUiLz48L3N2Zz4=', 'Avatar: snowman style for Meenkshi Textiles', @user_vijay),
( NULL, @client_lakshmi,     'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNFNUIzMkIiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjIiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzNSIgc3Ryb2tlPSIjZmZmIiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9IjUiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIyNSIgc3Ryb2tlPSIjZmZmIiBmaWxsPSJub25lIiBzdHJva2Utd2lkdGg9IjUiLz48L3N2Zz4=', 'Avatar: target pattern for Lakshmi Devi',      @user_priya),
( NULL, @client_workmen,     'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiMxRjI5MzUiLz48cG9seWdvbiBwb2ludHM9IjUwLDEwIDkwLDM1IDkwLDY1IDUwLDkwIDEwLDY1IDEwLDM1IiBmaWxsPSIjRkZBNjI2Ii8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LXNpemU9IjI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSIgZmlsbD0iIzFGMjkzNSIgZm9udC1mYW1pbHk9IkFyaWFsIj5XPC90ZXh0Pjwvc3ZnPg==', 'Avatar: pentagon with W for Workmen Union',     @user_vijay),
( NULL, @client_murugan,     'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiMxRjg3QkUiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iI0ZGQzEwNyIvPjxjaXJjbGUgY3g9IjUwIiBjeT0iNTAiIHI9IjI1IiBmaWxsPSIjMjI4QkUwIi8+PHJlY3QgeD0iNDUiIHk9IjQ1IiB3aWR0aD0iMTAiIGhlaWdodD0iMTAiIGZpbGw9IiNmZmMiLz48L3N2Zz4=', 'Avatar: bullseye for Murugan',           @user_priya),
( NULL, @client_chennai_dev, 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiNFMjhFNjAiLz48cmVjdCB4PSIyMCIgeT0iMjAiIHdpZHRoPSI2MCIgaGVpZ2h0PSI2MCIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjMiLz48cmVjdCB4PSIzNSIgeT0iMzUiIHdpZHRoPSIzMCIgaGVpZ2h0PSIzMCIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjYiLz48dGV4dCB4PSI1MCIgeT0iNTUiIGZvbnQtc2l6ZT0iMjgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGR5PSIuM2VtIiBmaWxsPSIjZmZmIiBmb250LWZhbWlseT0iQXJpYWwiPkNEPC90ZXh0Pjwvc3ZnPg==', 'Avatar: stacked squares for Chennai Developers',@user_vijay),
( NULL, @client_subramanian, 'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiM0RDU2NzAiLz48cGF0aCBkPSJNMzAsMjAgTDcwLDIwIEw4MCw1MCBMNzAsODAgTDMwLDgwIEwyMCw1MCBaIiBmaWxsPSIjRkZENzU1Ii8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LXNpemU9IjI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSIgZmlsbD0iIzRENTY3MCIgZm9udC1mYW1pbHk9IkFyaWFsIj5TVTwvdGV4dD48L3N2Zz4=', 'Avatar: house shape for Subramanian',       @user_vijay),
( NULL, @client_anand,       'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PGNpcmNsZSBjeD0iNTAiIGN5PSI1MCIgcj0iNTAiIGZpbGw9IiNGRjhDMDAiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzMCIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjMiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIxNSIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjYiLz48L3N2Zz4=', 'Avatar: concentric circles for Anand',             @user_priya),
( NULL, @client_priya_cust,  'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiM5QjI2MjYiLz48cG9seWdvbiBwb2ludHM9IjUwLDIwIDc1LDQwIDc1LDYwIDUwLDgwIDI1LDYwIDI1LDQwIiBmaWxsPSIjRkZERDk5Ii8+PHRleHQgeD0iNTAiIHk9IjU1IiBmb250LXNpemU9IjI4IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkeT0iLjNlbSIgZmlsbD0iIzliMjYyNiIgZm9udC1mYW1pbHk9IkFyaWFsIj5QQzwvdGV4dD48L3N2Zz4=', 'Avatar: diamond with PC for Priya (custody)',   @user_vijay),
( NULL, @client_bluesky,     'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiMyOTc5QkYiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjIiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzMCIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjUiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIyMCIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjgiLz48L3N2Zz4=', 'Avatar: gradient circles for Blue Sky Builders', @user_lokesh),
( NULL, @client_ganesh,      'data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIiB2aWV3Qm94PSIwIDAgMTAwIDEwMCI+PHJlY3Qgd2lkdGg9IjEwMCIgaGVpZ2h0PSIxMDAiIGZpbGw9IiM2NjRDNjAiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0NSIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjIiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIzNSIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjQiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIyNSIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjYiLz48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSIxNSIgZmlsbD0iI0ZGRkZGRiIgZmlsbC1vcGFjaXR5PSIwLjgiLz48L3N2Zz4=', 'Avatar: bullseye pattern for Ganesh',            @user_lokesh);

-- =============================================================================
-- 25. SEED DATA — TIER 11  (Audit & Activity Logs for Dashboard)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 25.1  Activity Log (Recent Activity widget)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO activity_log (chamber_id, user_id, action, target, ip_address, metadata_json, created_date, created_by) VALUES
(@chamber_vk, @user_priya,   'CASE_UPDATE',    'case:1', '117.192.45.12', JSON_OBJECT('case_id', 1, 'changed', 'next_hearing_date'), '2026-03-24 09:15:00', @user_priya),
(@chamber_vk, @user_karthik, 'HEARING_CREATE', 'case:2', '49.204.123.88', JSON_OBJECT('hearing_id', 3, 'case_id', 2),                '2026-03-24 10:30:00', @user_karthik),
(@chamber_vk, @user_vijay,   'CASE_CREATE',    'case:7', '117.192.45.12', JSON_OBJECT('case_id', 7, 'case_number', 'Crl.O.P.No.567/2026'), '2026-03-23 14:20:00', @user_vijay),
(@chamber_vk, @user_priya,   'NOTE_CREATE',    'case:1', '117.192.45.12', JSON_OBJECT('note_id', 1, 'case_id', 1),                    '2026-03-23 16:45:00', @user_priya),
(@chamber_vk, @user_karthik, 'CASE_UPDATE',    'case:4', '49.204.123.88', JSON_OBJECT('case_id', 4, 'changed', 'status_code'),         '2026-03-23 11:00:00', @user_karthik),
(@chamber_vk, @user_vijay,   'USER_INVITE',    'user',   '117.192.45.12', JSON_OBJECT('email', 'newlawyer@example.com'),               '2026-03-22 09:00:00', @user_vijay),
(@chamber_vk, @user_priya,   'HEARING_UPDATE', 'case:2', '117.192.45.12', JSON_OBJECT('hearing_id', 2, 'case_id', 2),                  '2026-03-22 15:30:00', @user_priya),
(@chamber_sundar, @user_lokesh, 'CASE_CREATE', 'case:3', '182.76.123.45', JSON_OBJECT('case_id', 3, 'case_number', 'O.S.No.145/2024'), '2026-03-21 10:00:00', @user_lokesh),
(@chamber_vk, @user_karthik, 'DOCUMENT_UPLOAD','case:1', '49.204.123.88', JSON_OBJECT('case_id', 1, 'doc_type', 'affidavit'),           '2026-03-21 14:15:00', @user_karthik),
(@chamber_vk, @user_vijay,   'SETTINGS_UPDATE','chamber','117.192.45.12', JSON_OBJECT('setting', 'email_config'),                      '2026-03-20 11:30:00', @user_vijay);

-- ─────────────────────────────────────────────────────────────────────────────
-- 25.2  Email Log
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO email_log (chamber_id, user_id, template_code, recipient_email, subject, status_code, sent_at, metadata_json, created_by) VALUES
(@chamber_vk, @user_priya, 'hearing_tomorrow', 'priya@vkchamber.in', 'Court Hearing Tomorrow – Urgent: Crl.O.P.No.234/2025', 'ESDL', '2026-03-23 17:02:15', JSON_OBJECT('case_id', 1, 'hearing_date', '2026-03-24'), @user_karthik);


-- ─────────────────────────────────────────────────────────────────────────────
-- 25.3  Login Audit
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO login_audit (user_id, chamber_id, email, ip_address, user_agent, status_code, login_time) VALUES
(@user_vijay,   @chamber_vk, 'admin@vkchamber.in',   '117.192.45.12', 'Chrome / Windows', 'LSSU', '2026-03-24 09:00:00'),
(@user_priya,   @chamber_vk, 'priya@vkchamber.in',   '117.192.45.13', 'Chrome / Mac',     'LSSU', '2026-03-24 09:30:00'),
(@user_karthik, @chamber_vk, 'karthik@vkchamber.in', '49.204.123.88', 'Firefox / Linux',  'LSSU', '2026-03-24 10:00:00'),
(@user_lokesh,  @chamber_sundar, 'lokesh@sundarlaw.in', '182.76.123.45', 'Chrome / Android', 'LSSU', '2026-03-24 08:45:00'),
(@user_vijay,   @chamber_vk, 'admin@vkchamber.in',   '117.192.45.12', 'Chrome / Windows', 'LSFA', '2026-03-23 18:30:00');


-- =============================================================================
-- 26. VERIFICATION QUERIES (Dashboard Data Check) — FIXED
-- =============================================================================

-- 1. Confirm 'role_code' column no longer exists in users table (as expected)
SELECT COLUMN_NAME
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'courtdiary'
  AND COLUMN_NAME = 'role_code';
-- Should return 0 rows

-- 2. Verify Chamber Roles (per chamber)
SELECT 
    cr.role_id,
    c.chamber_name,
    cr.role_name,
    cr.description,
    cr.admin_ind
FROM chamber_roles cr
JOIN chamber c ON cr.chamber_id = c.chamber_id
ORDER BY c.chamber_name, cr.role_name;

-- 3. Verify User Role Assignments (Fixed)
SELECT
    u.email,
    c.chamber_name,
    cr.role_name,
    ur.start_date,
    ur.end_date
FROM user_roles ur
JOIN user_chamber_link ucl ON ur.link_id = ucl.link_id
JOIN users u ON ucl.user_id = u.user_id
JOIN chamber c ON ucl.chamber_id = c.chamber_id
JOIN chamber_roles cr ON ur.role_id = cr.role_id     -- ← FIXED: Use role_id
ORDER BY c.chamber_name, u.email;

-- 4. Bonus: Check how many permissions exist per chamber role
SELECT 
    c.chamber_name,
    cr.role_name,
    COUNT(rp.permission_id) AS permission_count
FROM chamber_roles cr
JOIN chamber c ON cr.chamber_id = c.chamber_id
LEFT JOIN role_permissions rp ON rp.role_id = cr.role_id
GROUP BY c.chamber_name, cr.role_name
ORDER BY c.chamber_name, cr.role_name;

-- =============================================================================
-- END OF SEED DATA
-- =============================================================================

SELECT '✅ Dashboard-ready seed data loaded successfully!' AS status_message;