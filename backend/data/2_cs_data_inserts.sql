USE courtdiary;

-- =============================================================================
-- 15. SEED DATA — TIER 0  (Pure REFM — no dependencies)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.1  Geographic
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_countries (code, description, phone_code, sort_order) VALUES
('IN', 'India', '+91', 1);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.2  Plans & Modules
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_plan_types (code, description, max_users, max_cases, price_monthly_amt, price_annual_amt, sort_order) VALUES
('FREE', 'Free',       3,    75,    0.00,     0.00,    10),
('PRO',  'Pro',        10,   300,   999.00,   9999.00, 20),
('ENT',  'Enterprise', NULL, NULL,  2999.00, 29999.00, 30);

INSERT IGNORE INTO refm_modules (code, name, description, sort_order) VALUES
('DASH',  'Dashboard',       'Overview & statistics',         10),
('CASES', 'Cases',           'Case register & details',       20),
('HEAR',  'Hearings',        'Hearing schedule & history',    30),
('CAL',   'Calendar',        'Court & personal calendar',     40),
('USERS', 'User Management', 'Manage chamber users & roles',  50),
('RPT',   'Reports',         'Analytics & exports',           60),
('SET',   'Settings',        'Chamber configuration',         70);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.3  Case & Hearing Statuses
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_case_status (code, description, color_code, sort_order) VALUES
('AC',  'Active',    '#3b82f6', 10),
('ADJ', 'Adjourned', '#f97316', 20),
('DIS', 'Disposed',  '#64748b', 30),
('CLO', 'Closed',    '#64748b', 40),
('OVD', 'Overdue',   '#ef4444', 50);

INSERT IGNORE INTO refm_hearing_status (code, description, color_code, sort_order) VALUES
('UP',  'Upcoming',       '#3b82f6', 10),
('SC',  'Scheduled',      '#3b82f6', 15),
('CMP', 'Completed',      '#22c55e', 20),
('ADJ', 'Adjourned',      '#f97316', 30),
('OR',  'Order Reserved', '#a855f7', 40),
('DIS', 'Disposed',       '#64748b', 50);

INSERT IGNORE INTO refm_case_types (code, description, sort_order) VALUES
('CRIM', 'Criminal',      10),
('CIVL', 'Civil Suit',    20),
('WRIT', 'Writ Petition', 30),
('FAM',  'Family Matter', 40),
('LAB',  'Labour Case',   50),
('TAX',  'Tax Matter',    60),
('CON',  'Consumer Case', 70);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.4  Email & Communication
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_email_encryption (code, description, sort_order) VALUES
('N', 'None', 10), ('T', 'TLS', 20), ('S', 'SSL', 30), ('B', 'Both', 40);

INSERT IGNORE INTO refm_email_status (code, description, color_code, sort_order) VALUES
('P', 'Pending',   '#f97316', 10),
('S', 'Sent',      '#3b82f6', 20),
('D', 'Delivered', '#22c55e', 30),
('O', 'Opened',    '#a855f7', 40),
('F', 'Failed',    '#ef4444', 50),
('B', 'Bounced',   '#991b1b', 60);

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
('PN', 'Pending',   '#f97316', 10),
('SN', 'Sent',      '#3b82f6', 20),
('DL', 'Delivered', '#22c55e', 30),
('RD', 'Read',      '#a855f7', 40),
('FD', 'Failed',    '#ef4444', 50);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.5  User & Auth Statuses
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_login_status (code, description, sort_order) VALUES
('S', 'Success', 1),
('F', 'Failed',  2);

INSERT IGNORE INTO refm_user_deletion_status (code, description, sort_order) VALUES
('P', 'Pending',  1),
('D', 'Deleted',  2),
('R', 'Rejected', 3);

INSERT IGNORE INTO refm_invitation_status (code, description, color_code, sort_order) VALUES
('PN', 'Pending',  '#f97316', 10),
('AC', 'Accepted', '#22c55e', 20),
('RJ', 'Rejected', '#ef4444', 30),
('EX', 'Expired',  '#64748b', 40);

-- ─────────────────────────────────────────────────────────────────────────────
-- 15.6  Billing, Party Roles, AOR, Collab Access
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_billing_status (code, description, color_code, sort_order) VALUES
('PN', 'Pending',   '#f97316', 10),
('PD', 'Paid',      '#22c55e', 20),
('OV', 'Overdue',   '#ef4444', 30),
('CN', 'Cancelled', '#64748b', 40),
('AD', 'Adjusted',  '#a855f7', 50);

INSERT IGNORE INTO refm_party_roles (code, description, category, sort_order) VALUES
('PET', 'Petitioner',         'PARTY', 10),
('RES', 'Respondent',         'PARTY', 20),
('APP', 'Appellant',          'PARTY', 30),
('DEF', 'Defendant',          'PARTY', 40),
('PLT', 'Plaintiff',          'PARTY', 50),
('WIT', 'Witness',            'REP',   60),
('AOR', 'Advocate on Record', 'REP',   70);

INSERT IGNORE INTO refm_aor_status (code, description, color_code, sort_order) VALUES
('AC', 'Active',      '#22c55e', 10),
('WD', 'Withdrawn',   '#64748b', 20),
('SU', 'Substituted', '#f97316', 30);

INSERT IGNORE INTO refm_collab_access (code, description, permissions, color_code, sort_order) VALUES
('RO', 'Read Only',   'view',                    '#3b82f6', 10),
('RW', 'Read Write',  'view,edit,create',        '#a855f7', 20),
('FU', 'Full Access', 'view,edit,create,delete', '#22c55e', 30);


-- =============================================================================
-- 16. SEED DATA — TIER 1  (REFM with FK to other REFM)
-- =============================================================================

INSERT IGNORE INTO refm_states (code, description, country_code, sort_order) VALUES
('TN', 'Tamil Nadu',  'IN', 1),
('KL', 'Kerala',      'IN', 2),
('KA', 'Karnataka',   'IN', 3),
('MH', 'Maharashtra', 'IN', 4),
('DL', 'Delhi',       'IN', 5);

INSERT INTO refm_courts (court_name, state_code, court_type, sort_order) VALUES
('Madras High Court',                    'TN', 'High Court',     10),
('City Civil Court, Chennai',            'TN', 'Civil Court',    20),
('District Court, Chengalpattu',         'TN', 'District Court', 30),
('Principal District Court, Coimbatore', 'TN', 'District Court', 40),
('Family Court, Chennai',                'TN', 'Family Court',   50),
('JM Court, Saidapet',                   'TN', 'Magistrate',     60);


-- ─────────────────────────────────────────────────────────────────────────────
-- 17. SEED DATA — TIER 2 (Core Entities: chamber + users)
-- =============================================================================

-- 17.1 Chambers
INSERT INTO chamber (chamber_name, email, phone, city, state_code, plan_code, created_by) 
VALUES 
('VijayKrishnan & Associates', 'office@vkchamber.in', '9876543210', 'Chennai', 'TN', 'PRO', NULL);

SET @chamber_vk = (SELECT chamber_id FROM chamber WHERE chamber_name = 'VijayKrishnan & Associates');

INSERT INTO chamber (chamber_name, email, phone, city, state_code, plan_code, created_by) 
VALUES 
('Sundar Associates', 'office@sundarlaw.in', '9445123456', 'Coimbatore', 'TN', 'FREE', NULL);

SET @chamber_sundar = (SELECT chamber_id FROM chamber WHERE chamber_name = 'Sundar Associates');

-- 17.2 Users
SET @pwd_hash = '$argon2id$v=19$m=65536,t=3,p=4$hfCeE0IoZay1lhLifA+BkA$3rA1GrCAkdhLzYyGi2S7lc422/W2eEPIqW3MD4u1B48';

INSERT INTO users (user_id, email, password_hash, first_name, last_name, phone, created_by) VALUES
(UUID(), 'admin@vkchamber.in',  @pwd_hash, 'Vijay', 'Krishnan', '9876543210', NULL),
(UUID(), 'priya@vkchamber.in',  @pwd_hash, 'Priya', 'Natarajan', '8123456789', NULL),
(UUID(), 'karthik@vkchamber.in',@pwd_hash, 'Karthik', 'Raja', '9001234567', NULL),
(UUID(), 'lokesh@sundarlaw.in', @pwd_hash, 'Lokesh', 'Mani', '9445123456', NULL);

SET @user_vijay   = (SELECT user_id FROM users WHERE email = 'admin@vkchamber.in');
SET @user_priya   = (SELECT user_id FROM users WHERE email = 'priya@vkchamber.in');
SET @user_karthik = (SELECT user_id FROM users WHERE email = 'karthik@vkchamber.in');
SET @user_lokesh  = (SELECT user_id FROM users WHERE email = 'lokesh@sundarlaw.in');

-- 18. SEED DATA — TIER 3 (Bridge Tables)
-- =============================================================================

-- 18.1 User Profiles
INSERT INTO user_profiles (profile_id, user_id, address, country, state, city, postal_code, 
                           header_color, sidebar_color, primary_color, font_family, updated_by) 
VALUES
(UUID(), @user_vijay,   'No. 45, Anna Salai, Teynampet', 'IN', 'TN', 'Chennai', '600018', '222 33% 10%', '222 40% 12%', '32.4 99% 63%', 'Nunito, sans-serif', @user_vijay),
(UUID(), @user_priya,   'Flat 3B, Greenwoods Apartment, Adyar', 'IN', 'TN', 'Chennai', '600020', '230 20% 15%', '230 25% 18%', '215 100% 55%', 'Inter, sans-serif', @user_vijay),
(UUID(), @user_karthik, '12/5, Gandhi Nagar, Chengalpattu', 'IN', 'TN', 'Chengalpattu', '603001', '0 0% 12%', '0 0% 15%', '262 83% 58%', 'Nunito, sans-serif', @user_vijay),
(UUID(), @user_lokesh,  'Plot 78, RS Puram', 'IN', 'TN', 'Coimbatore', '641002', '225 30% 11%', '225 35% 14%', '142 76% 36%', 'Roboto, sans-serif', @user_lokesh);

-- 18.2 User ↔ Chamber Links
INSERT INTO user_chamber_link (link_id, user_id, chamber_id, is_primary, joined_date, created_by) VALUES
(UUID(), @user_vijay,   @chamber_vk,     TRUE, '2024-01-15', @user_vijay),
(UUID(), @user_priya,   @chamber_vk,     TRUE, '2024-02-01', @user_vijay),
(UUID(), @user_karthik, @chamber_vk,     TRUE, '2024-03-10', @user_vijay),
(UUID(), @user_lokesh,  @chamber_sundar, TRUE, '2024-01-20', @user_lokesh);

-- 18.3 Chamber Modules
INSERT INTO chamber_modules (chamber_module_id, chamber_id, module_code, is_active, created_by) VALUES
(UUID(), @chamber_vk, 'DASH', TRUE, @user_vijay),
(UUID(), @chamber_vk, 'CASES', TRUE, @user_vijay),
(UUID(), @chamber_vk, 'HEAR', TRUE, @user_vijay),
(UUID(), @chamber_vk, 'CAL', TRUE, @user_vijay),
(UUID(), @chamber_vk, 'USERS', TRUE, @user_vijay),
(UUID(), @chamber_vk, 'RPT', TRUE, @user_vijay),
(UUID(), @chamber_vk, 'SET', TRUE, @user_vijay);

INSERT INTO chamber_modules (chamber_module_id, chamber_id, module_code, is_active, created_by) VALUES
(UUID(), @chamber_sundar, 'DASH', TRUE, @user_lokesh),
(UUID(), @chamber_sundar, 'CASES', TRUE, @user_lokesh),
(UUID(), @chamber_sundar, 'HEAR', TRUE, @user_lokesh),
(UUID(), @chamber_sundar, 'CAL', TRUE, @user_lokesh),
(UUID(), @chamber_sundar, 'USERS', FALSE, @user_lokesh),
(UUID(), @chamber_sundar, 'RPT', FALSE, @user_lokesh),
(UUID(), @chamber_sundar, 'SET', TRUE, @user_lokesh);

-- =============================================================================
-- 19. SEED DATA — TIER 4 (Roles & Permissions) — NEW DESIGN
-- =============================================================================

-- 19.1 Master Security Roles (Global Templates)
INSERT INTO security_roles (role_name, description, is_system, created_by) VALUES
('Administrator', 'Full access to all modules', TRUE, @user_vijay),
('Senior Advocate', 'Manage cases, hearings and clients', TRUE, @user_vijay),
('Clerk', 'Basic data entry and viewing only', TRUE, @user_vijay);

-- 19.2 Chamber-specific Roles (Copy from master)
INSERT INTO chamber_roles (chamber_id, role_name, description, is_system, created_by) VALUES
(@chamber_vk, 'Administrator', 'Full access to all modules', TRUE, @user_vijay),
(@chamber_vk, 'Senior Advocate', 'Manage cases, hearings and clients', TRUE, @user_vijay),

(@chamber_sundar, 'Administrator', 'Full access to all modules', TRUE, @user_lokesh),
(@chamber_sundar, 'Senior Advocate', 'Manage cases, hearings and clients', TRUE, @user_lokesh);

-- 19.3 User Roles (link to chamber_roles)
SET @link_vijay_vk   = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_vijay AND chamber_id = @chamber_vk);
SET @link_priya_vk   = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_priya AND chamber_id = @chamber_vk);
SET @link_karthik_vk = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_karthik AND chamber_id = @chamber_vk);
SET @link_lokesh_sundar = (SELECT link_id FROM user_chamber_link WHERE user_id = @user_lokesh AND chamber_id = @chamber_sundar);

SET @role_admin_vk   = (SELECT role_id FROM chamber_roles WHERE chamber_id = @chamber_vk AND role_name = 'Administrator');
SET @role_senior_vk  = (SELECT role_id FROM chamber_roles WHERE chamber_id = @chamber_vk AND role_name = 'Senior Advocate');
SET @role_admin_sundar = (SELECT role_id FROM chamber_roles WHERE chamber_id = @chamber_sundar AND role_name = 'Administrator');

INSERT INTO user_roles (link_id, chamber_role_id, start_date, created_by) VALUES
(@link_vijay_vk,   @role_admin_vk,   '2024-01-15', @user_vijay),
(@link_priya_vk,   @role_senior_vk,  '2024-02-01', @user_vijay),
(@link_karthik_vk, @role_senior_vk,   '2024-03-10', @user_vijay),
(@link_lokesh_sundar, @role_admin_sundar, '2024-01-20', @user_lokesh);

-- 19.4 Role Permissions (per chamber role)
SET @cm_dash  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'DASH');
SET @cm_cases = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'CASES');
SET @cm_hear  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'HEAR');
SET @cm_cal   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'CAL');
SET @cm_users = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'USERS');
SET @cm_rpt   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'RPT');
SET @cm_set   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_vk AND module_code = 'SET');

-- Administrator - Full Access
INSERT INTO role_permissions (chamber_role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, import_ind, export_ind, created_by) 
VALUES
(@role_admin_vk, @cm_dash,  TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_cases, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_hear,  TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_cal,   TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_users, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_rpt,   TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay),
(@role_admin_vk, @cm_set,   TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_vijay);

-- Senior Advocate - Limited but strong on core modules
INSERT INTO role_permissions (chamber_role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, import_ind, export_ind, created_by) 
VALUES
(@role_senior_vk, @cm_dash,  FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_hear,  FALSE, TRUE,  TRUE,  TRUE,  FALSE, TRUE,  TRUE,  @user_vijay),
(@role_senior_vk, @cm_cal,   FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_users, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay),
(@role_senior_vk, @cm_rpt,   FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, TRUE,  @user_vijay),
(@role_senior_vk, @cm_set,   FALSE, TRUE,  FALSE, FALSE, FALSE, FALSE, FALSE, @user_vijay);

-- =============================================================================
-- Add Role Permissions for Sundar Associates
-- =============================================================================

-- Get chamber_module_ids for Sundar Associates
SET @cm_dash_s  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_sundar AND module_code = 'DASH');
SET @cm_cases_s = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_sundar AND module_code = 'CASES');
SET @cm_hear_s  = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_sundar AND module_code = 'HEAR');
SET @cm_cal_s   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_sundar AND module_code = 'CAL');
SET @cm_users_s = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_sundar AND module_code = 'USERS');
SET @cm_rpt_s   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_sundar AND module_code = 'RPT');
SET @cm_set_s   = (SELECT chamber_module_id FROM chamber_modules WHERE chamber_id = @chamber_sundar AND module_code = 'SET');

-- Administrator for Sundar - Full Access
INSERT INTO role_permissions 
    (chamber_role_id, chamber_module_id, allow_all_ind, read_ind, write_ind, create_ind, delete_ind, import_ind, export_ind, created_by) 
VALUES
(@role_admin_sundar, @cm_dash_s,  TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_lokesh),
(@role_admin_sundar, @cm_cases_s, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_lokesh),
(@role_admin_sundar, @cm_hear_s,  TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_lokesh),
(@role_admin_sundar, @cm_cal_s,   TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_lokesh),
(@role_admin_sundar, @cm_users_s, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_lokesh),
(@role_admin_sundar, @cm_rpt_s,   TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_lokesh),
(@role_admin_sundar, @cm_set_s,   TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, @user_lokesh);


-- =============================================================================
-- 20. SEED DATA — TIER 6  (Cases — Dashboard Ready)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 20.1  Active Cases (Various Statuses for Dashboard Widgets)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO cases (chamber_id, case_number, court_id, case_type_code, filing_year,
                   petitioner, respondent, aor_user_id, case_summary, status_code,
                   next_hearing_date, last_hearing_date, created_by) VALUES
-- OVERDUE CASES (next_hearing_date < TODAY for Overdue widget)
(@chamber_vk, 'Crl.O.P.No.234/2025',   1, 'CRIM', 2025,
 'State of Tamil Nadu', 'Arjun Prasad',      @user_priya,
 'Quashing of FIR u/s 420 IPC – financial fraud',                      'AC',  '2026-03-20', '2026-03-15', @user_vijay),

(@chamber_vk, 'W.P.(MD)No.5678/2025',  1, 'WRIT', 2025,
 'Tmt. Saraswathi',     'The Tahsildar',     @user_priya,
 'Challenge to patta cancellation order',                               'AC',  '2026-03-22', '2026-03-18', @user_vijay),

(@chamber_vk, 'Crl.M.C.No.89/2026',    6, 'CRIM', 2026,
 'Ramesh Kumar',        'Inspector of Police', @user_priya,
 'Anticipatory bail petition',                                         'AC',  '2026-03-18', '2026-03-10', @user_vijay),

-- UPCOMING THIS WEEK (for This Week Hearings widget)
(@chamber_vk, 'O.S.No.456/2025',       2, 'CIVL', 2025,
 'Meenkshi Textiles',   'Global Exports Ltd',  @user_priya,
 'Suit for specific performance of sale agreement',                     'AC',  '2026-03-26', '2026-03-19', @user_vijay),

(@chamber_vk, 'F.C.No.123/2025',       5, 'FAM',  2025,
 'Lakshmi Devi',        'Suresh Babu',         @user_priya,
 'Divorce petition under Hindu Marriage Act',                           'AC',  '2026-03-27', '2026-03-12', @user_vijay),

(@chamber_vk, 'L.C.No.78/2025',        3, 'LAB',  2025,
 'Workmen Union',       'ABC Manufacturing',   @user_priya,
 'Labour dispute – wrongful termination',                                'AC',  '2026-03-28', '2026-03-14', @user_vijay),

-- FUTURE CASES (Active but not overdue)
(@chamber_vk, 'Crl.O.P.No.567/2026',   1, 'CRIM', 2026,
 'State of Tamil Nadu', 'Murugan',             @user_priya,
 'Quashing of criminal proceedings',                                    'AC',  '2026-04-15', NULL,         @user_vijay),

(@chamber_vk, 'W.P.No.9012/2026',      1, 'WRIT', 2026,
 'Chennai Developers',  'DTCP',                @user_priya,
 'Writ against planning permission denial',                             'AC',  '2026-04-20', NULL,         @user_vijay),

-- ADJOURNED CASES
(@chamber_vk, 'O.S.No.789/2024',       2, 'CIVL', 2024,
 'Subramanian',         'Venkatesh',           @user_priya,
 'Property partition suit',                                             'ADJ', '2026-04-05', '2026-03-21', @user_vijay),

-- DISPOSED/CLOSED (for stats)
(@chamber_vk, 'Crl.M.C.No.45/2024',    6, 'CRIM', 2024,
 'Anand',               'State of TN',         @user_priya,
 'Bail application – disposed',                                         'DIS', NULL,         '2026-02-15', @user_vijay),

(@chamber_vk, 'F.C.No.56/2024',        5, 'FAM',  2024,
 'Priya',               'Rajesh',              @user_priya,
 'Custody matter – closed',                                             'CLO', NULL,         '2026-01-30', @user_vijay),

-- Sundar Associates Cases
(@chamber_sundar, 'O.S.No.145/2024',   4, 'CIVL', 2024,
 'M/s Blue Sky Builders', 'T.N. Housing Board', @user_lokesh,
 'Specific performance of sale agreement – construction dispute',       'AC',  '2026-04-10', '2026-03-01', @user_lokesh),

(@chamber_sundar, 'Crl.O.P.No.88/2025', 1, 'CRIM', 2025,
 'State of Tamil Nadu', 'Ganesh',              @user_lokesh,
 'Criminal revision petition',                                          'AC',  '2026-03-25', '2026-03-10', @user_lokesh);


-- =============================================================================
-- 21. SEED DATA — TIER 7  (Hearings — Dashboard Ready)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 21.1  Hearings (Various Dates for Dashboard Widgets)
-- ─────────────────────────────────────────────────────────────────────────────

SET @case1  = (SELECT case_id FROM cases WHERE case_number = 'Crl.O.P.No.234/2025');
SET @case2  = (SELECT case_id FROM cases WHERE case_number = 'W.P.(MD)No.5678/2025');
SET @case3  = (SELECT case_id FROM cases WHERE case_number = 'O.S.No.145/2024');
SET @case4  = (SELECT case_id FROM cases WHERE case_number = 'O.S.No.456/2025');
SET @case5  = (SELECT case_id FROM cases WHERE case_number = 'F.C.No.123/2025');
SET @case6  = (SELECT case_id FROM cases WHERE case_number = 'L.C.No.78/2025');
SET @case7  = (SELECT case_id FROM cases WHERE case_number = 'Crl.M.C.No.89/2026');
SET @case8  = (SELECT case_id FROM cases WHERE case_number = 'Crl.O.P.No.567/2026');
SET @case9  = (SELECT case_id FROM cases WHERE case_number = 'Crl.O.P.No.88/2025');

-- TODAY'S HEARINGS (for Today's Hearings widget) - Adjust date as needed
INSERT INTO hearings (chamber_id, case_id, hearing_date, status_code, purpose, notes, next_hearing_date, created_by) VALUES
(@chamber_vk, @case1, '2026-03-24', 'UP',  'Final arguments',       'Awaiting final disposal',            NULL,         @user_priya),
(@chamber_vk, @case2, '2026-03-24', 'UP',  'Evidence stage',        'Witness examination',                NULL,         @user_priya),
(@chamber_vk, @case7, '2026-03-24', 'UP',  'Admission hearing',     'Notice issued',                      NULL,         @user_karthik);

-- THIS WEEK HEARINGS (for This Week widget)
INSERT INTO hearings (chamber_id, case_id, hearing_date, status_code, purpose, notes, next_hearing_date, created_by) VALUES
(@chamber_vk, @case4, '2026-03-26', 'UP',  'First hearing',         'For admission',                      NULL,         @user_priya),
(@chamber_vk, @case5, '2026-03-27', 'UP',  'Interim application',   'Maintenance pendente lite',          NULL,         @user_priya),
(@chamber_vk, @case6, '2026-03-28', 'UP',  'Evidence',              'Document production',                NULL,         @user_karthik),
(@chamber_sundar, @case9, '2026-03-25', 'UP',  'Arguments',           'Final submissions',                  NULL,         @user_lokesh);

-- COMPLETED HEARINGS (Past - for history)
INSERT INTO hearings (chamber_id, case_id, hearing_date, status_code, purpose, notes, next_hearing_date, created_by) VALUES
(@chamber_vk, @case1, '2026-01-20', 'CMP', 'Admission hearing',     'Notice issued to respondent',        '2026-03-15', @user_priya),
(@chamber_vk, @case1, '2026-03-15', 'CMP', 'Preliminary hearing',   'Issues framed',                      '2026-03-24', @user_priya),
(@chamber_vk, @case2, '2026-02-10', 'ADJ', 'Counter affidavit',     'Adjourned due to non-filing',       '2026-03-18', @user_karthik),
(@chamber_vk, @case2, '2026-03-18', 'CMP', 'Filing stage',          'Counter filed',                      '2026-03-24', @user_priya),
(@chamber_sundar, @case3, '2026-03-01', 'CMP', 'Framing of issues',   'Issues framed',                      '2026-04-10', @user_lokesh);

-- ADJOURNED HEARINGS
INSERT INTO hearings (chamber_id, case_id, hearing_date, status_code, purpose, notes, next_hearing_date, created_by) VALUES
(@chamber_vk, @case4, '2026-03-19', 'ADJ', 'First hearing',         'Counsel not available',              '2026-03-26', @user_priya);


-- =============================================================================
-- 22. SEED DATA — TIER 8  (Case Notes, AORs, Clients)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 22.1  Case Notes
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO case_notes (chamber_id, case_id, user_id, note_text, is_private, created_by) VALUES
(@chamber_vk, @case1, @user_priya,   'Client mentioned new evidence – witness statement from neighbour. Follow up before next hearing.', FALSE, @user_priya),
(@chamber_vk, @case1, @user_vijay,   'Internal: Consider settlement if opposing party approaches. Max limit: 5 lakhs.',                 TRUE,  @user_vijay),
(@chamber_vk, @case1, @user_karthik, 'Court fee receipt collected. Original filed in case file.',                                       FALSE, @user_karthik),
(@chamber_vk, @case2, @user_priya,   'Tahsildar office confirmed – patta cancellation was procedural error. Strong case for quashing.', FALSE, @user_priya),
(@chamber_vk, @case2, @user_vijay,   'Client wants expedited hearing. File urgency petition if not listed in March.',                   TRUE,  @user_vijay),
(@chamber_sundar, @case3, @user_lokesh, 'Builder agreed to mediation. Schedule for mid-March before framing of issues.',               FALSE, @user_lokesh);

-- ─────────────────────────────────────────────────────────────────────────────
-- 22.2  Case AORs
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO case_aors (case_id, user_id, chamber_id, is_primary, appointment_date, status_code, created_by) VALUES
(@case1, @user_priya, @chamber_vk,     TRUE,  '2025-01-10', 'AC', @user_vijay),
(@case2, @user_priya, @chamber_vk,     TRUE,  '2025-03-05', 'AC', @user_vijay),
(@case3, @user_lokesh, @chamber_sundar, TRUE, '2024-08-12', 'AC', @user_lokesh),
(@case4, @user_priya, @chamber_vk,     TRUE,  '2025-06-15', 'AC', @user_vijay),
(@case5, @user_priya, @chamber_vk,     TRUE,  '2025-07-20', 'AC', @user_vijay);


-- =============================================================================
-- 23. SEED DATA — TIER 9  (Config: Email Settings & Templates)
-- =============================================================================

INSERT INTO email_settings (chamber_id, from_email, smtp_host, smtp_port, smtp_user,
                             smtp_password, encryption_code, is_default, status_ind, created_by) VALUES
(@chamber_vk, 'no-reply@vkchamber.in', 'smtp.gmail.com', 587, 'no-reply@vkchamber.in', 'app-password-placeholder', 'T', TRUE,  TRUE, @user_vijay),
(@chamber_vk, 'office@vkchamber.in',   'smtp.zoho.com',  587, 'office@vkchamber.in',   'zoho-password-placeholder', 'T', FALSE, TRUE, @user_vijay);

INSERT INTO email_templates (chamber_id, code, subject, content, is_customized, enabled_ind, created_by) VALUES
(@chamber_vk, 'hearing_tomorrow',
 'Court Hearing Tomorrow – Urgent: {Case Number}',
 '<p>Dear Advocate,</p><p><strong>Tomorrow</strong> hearing:<br>Case: <b>{Case Number}</b></p><p>Prepare urgently.</p><p>VijayKrishnan & Associates</p>',
 TRUE, TRUE, @user_vijay);


-- =============================================================================
-- 24. SEED DATA — TIER 10  (Collaboration & Invitations)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 24.1  Case Collaborations
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO case_collaborations (case_id, owner_chamber_id, collaborator_chamber_id,
                                  access_level, invited_by, invited_date, accepted_date, status_code, created_by)
VALUES (@case1, @chamber_vk, @chamber_sundar, 'RW', @user_vijay, '2026-02-15', '2026-02-16', 'AC', @user_vijay);

-- ─────────────────────────────────────────────────────────────────────────────
-- 24.2  User Invitations (for Pending Invites widget)
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO user_invitations (chamber_id, email, role_id, invited_by, invited_date, expires_date,
                               status_code, message, created_by)
VALUES 
(@chamber_vk, 'newlawyer@example.com', @role_senior, @user_vijay, '2026-03-20', '2026-04-19',
        'PN', 'Welcome to VijayKrishnan & Associates! Please accept this invitation.',
        @user_vijay),
(@chamber_vk, 'senlawyer@example.com', @role_senior, @user_vijay, '2026-03-22', '2026-04-21',
        'PN', 'Join our team as a clerk.',
        @user_vijay);


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

INSERT INTO email_log (chamber_id, user_id, template_code, recipient_email, subject,
                        status_code, sent_at, metadata_json, created_by) VALUES
(@chamber_vk, @user_priya, 'hearing_tomorrow', 'priya@vkchamber.in',
 'Court Hearing Tomorrow – Urgent: Crl.O.P.No.234/2025',
 'D', '2026-03-23 17:02:15',
 JSON_OBJECT('case_id', 1, 'hearing_date', '2026-03-24'), @user_karthik);

-- ─────────────────────────────────────────────────────────────────────────────
-- 25.3  Login Audit
-- ─────────────────────────────────────────────────────────────────────────────

INSERT INTO login_audit (user_id, chamber_id, email, ip_address, user_agent, status_code, login_time) VALUES
(@user_vijay,   @chamber_vk, 'admin@vkchamber.in',   '117.192.45.12', 'Chrome / Windows', 'S', '2026-03-24 09:00:00'),
(@user_priya,   @chamber_vk, 'priya@vkchamber.in',   '117.192.45.13', 'Chrome / Mac',     'S', '2026-03-24 09:30:00'),
(@user_karthik, @chamber_vk, 'karthik@vkchamber.in', '49.204.123.88', 'Firefox / Linux',  'S', '2026-03-24 10:00:00'),
(@user_lokesh,  @chamber_sundar, 'lokesh@sundarlaw.in', '182.76.123.45', 'Chrome / Android', 'S', '2026-03-24 08:45:00'),
(@user_vijay,   @chamber_vk, 'admin@vkchamber.in',   '117.192.45.12', 'Chrome / Windows', 'F', '2026-03-23 18:30:00');


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
    cr.is_system
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
JOIN chamber_roles cr ON ur.chamber_role_id = cr.role_id     -- ← FIXED: Use chamber_role_id
ORDER BY c.chamber_name, u.email;

-- 4. Bonus: Check how many permissions exist per chamber role
SELECT 
    c.chamber_name,
    cr.role_name,
    COUNT(rp.permission_id) AS permission_count
FROM chamber_roles cr
JOIN chamber c ON cr.chamber_id = c.chamber_id
LEFT JOIN role_permissions rp ON rp.chamber_role_id = cr.role_id
GROUP BY c.chamber_name, cr.role_name
ORDER BY c.chamber_name, cr.role_name;

-- =============================================================================
-- END OF SEED DATA
-- =============================================================================

SELECT '✅ Dashboard-ready seed data loaded successfully!' AS status_message;