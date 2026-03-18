-- =============================================================================
-- COURT DIARY - FULL SCHEMA (Production-Ready with Contextual Membership)
-- Design: Users are chamber-agnostic; membership via user_chamber_link
-- Roles are assigned per user-chamber context (link_id), not global user
-- 2025/2026 version
-- =============================================================================

-- =============================================================================
-- 1. DATABASE SETUP
-- =============================================================================
DROP DATABASE IF EXISTS courtdiary;
CREATE DATABASE courtdiary
    DEFAULT CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE courtdiary;

-- =============================================================================
-- 2. PURE REFERENCE / LOOKUP TABLES (No dependencies)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.1 Geographic & System References
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_countries;
CREATE TABLE refm_countries (
    code          CHAR(2) PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    phone_code    VARCHAR(8) NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Countries';

DROP TABLE IF EXISTS refm_states;
CREATE TABLE refm_states (
    code          CHAR(4) PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    country_code  CHAR(2) NOT NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    status_ind    BOOLEAN DEFAULT TRUE,
    CONSTRAINT fk_states_country
        FOREIGN KEY (country_code) REFERENCES refm_countries(code) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='States / Union Territories';

DROP TABLE IF EXISTS refm_courts;
CREATE TABLE refm_courts (
    court_id      INT AUTO_INCREMENT PRIMARY KEY,
    court_name    VARCHAR(150) NOT NULL,
    state_code    CHAR(4) NOT NULL,
    court_type    VARCHAR(60) NULL,
    address       TEXT NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    status_ind    BOOLEAN DEFAULT TRUE,
    created_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_courts_state
        FOREIGN KEY (state_code) REFERENCES refm_states(code) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Courts / benches';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.2 Case & Hearing Statuses
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_case_status;
CREATE TABLE refm_case_status (
    code          CHAR(4) PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case status';

DROP TABLE IF EXISTS refm_hearing_status;
CREATE TABLE refm_hearing_status (
    code          CHAR(4) PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Hearing status';

DROP TABLE IF EXISTS refm_case_types;
CREATE TABLE refm_case_types (
    code          CHAR(4) PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case types';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.3 System Configuration & Plans
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_plan_types;
CREATE TABLE refm_plan_types (
    code              CHAR(4) PRIMARY KEY,
    description       VARCHAR(60) NOT NULL,
    max_users         INT NULL,
    max_cases         INT NULL,
    price_monthly_amt DECIMAL(12,2) DEFAULT 0,
    price_annual_amt  DECIMAL(12,2) DEFAULT 0,
    currency_code     CHAR(3) DEFAULT 'INR',
    sort_order        INT NOT NULL,
    status_ind        BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Subscription plans';

DROP TABLE IF EXISTS refm_modules;
CREATE TABLE refm_modules (
    code          CHAR(8) PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    description   TEXT NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='System modules for permissions';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.4 Email & Communication References
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_email_encryption;
CREATE TABLE refm_email_encryption (
    code          CHAR(2) PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Email encryption methods';

DROP TABLE IF EXISTS refm_email_status;
CREATE TABLE refm_email_status (
    code          CHAR(2) PRIMARY KEY,
    description   VARCHAR(40) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Email delivery status codes';

DROP TABLE IF EXISTS refm_email_templates;
CREATE TABLE refm_email_templates (
    code          CHAR(30) PRIMARY KEY,
    subject       VARCHAR(255) NOT NULL,
    content       LONGTEXT NOT NULL,
    category      VARCHAR(50) NULL,
    description   VARCHAR(255) NULL,
    sort_order    INT NOT NULL DEFAULT 100,
    status_ind    BOOLEAN DEFAULT TRUE,
    created_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='System default email templates';

DROP TABLE IF EXISTS refm_login_status;
CREATE TABLE refm_login_status (
    code          CHAR(2) PRIMARY KEY,
    description   VARCHAR(20) NOT NULL,
    sort_order    INT NOT NULL
) ENGINE=InnoDB COMMENT='Lookup table for Login status log';

DROP TABLE IF EXISTS refm_comm_status;
CREATE TABLE refm_comm_status (
    code          CHAR(2) PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Communication status codes';

DROP TABLE IF EXISTS refm_billing_status;
CREATE TABLE refm_billing_status (
    code          CHAR(2) PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Billing status codes';

DROP TABLE IF EXISTS refm_user_deletion_status;
CREATE TABLE refm_user_deletion_status (
    code          CHAR(1) PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Account deletion request statuses';

DROP TABLE IF EXISTS refm_party_roles;
CREATE TABLE refm_party_roles (
    code          CHAR(3) PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    category      VARCHAR(30) NULL COMMENT 'PARTY=Main Party, REP=Representative, OTHR=Other',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Party roles in cases';

-- =============================================================================
-- 3. CORE ENTITIES (Chamber & Users - Decoupled)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.1 Chamber (Law Firms)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS chamber;
CREATE TABLE chamber (
    chamber_id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_name        VARCHAR(150) NOT NULL,
    email               VARCHAR(120) NULL UNIQUE,
    phone               VARCHAR(20) NULL,
    address_line1       VARCHAR(255),
    address_line2       VARCHAR(255),
    city                VARCHAR(80),
    state_code          CHAR(4) DEFAULT 'TN',
    postal_code         VARCHAR(12),
    country_code        CHAR(2) DEFAULT 'IN',
    plan_code           CHAR(4) DEFAULT 'FREE',
    subscription_start  DATE NULL,
    subscription_end    DATE NULL,
    status_ind          BOOLEAN DEFAULT TRUE,
    is_deleted          BOOLEAN DEFAULT FALSE,
    deleted_date        TIMESTAMP NULL,
    deleted_by          BIGINT NULL,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    CONSTRAINT fk_chamber_state
        FOREIGN KEY (state_code) REFERENCES refm_states(code) ON DELETE RESTRICT,
    CONSTRAINT fk_chamber_country
        FOREIGN KEY (country_code) REFERENCES refm_countries(code) ON DELETE RESTRICT,
    CONSTRAINT fk_chamber_plan
        FOREIGN KEY (plan_code) REFERENCES refm_plan_types(code) ON DELETE RESTRICT
    -- FKs to users added in Section 9 (deferred)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Law chamber / firm';

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.2 Users (Chamber-Agnostic - NO chamber_id FK)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id               BIGINT AUTO_INCREMENT PRIMARY KEY,
    -- ❌ REMOVED: chamber_id BIGINT NOT NULL,
    
    email                 VARCHAR(120) NOT NULL,
    password_hash         VARCHAR(255) NOT NULL,
    first_name            VARCHAR(60) NOT NULL,
    last_name             VARCHAR(60) NULL,
    phone                 VARCHAR(20) NULL,
    
    -- Global defaults (can be overridden per chamber link)
    role_code             CHAR(4) DEFAULT 'MEMB',
    status_ind            BOOLEAN DEFAULT TRUE,
    
    -- Audit & soft-delete
    is_deleted            BOOLEAN DEFAULT FALSE,
    deleted_date          TIMESTAMP NULL,
    deleted_by            BIGINT NULL,
    
    -- Security flags
    email_verified_ind    BOOLEAN DEFAULT FALSE,
    phone_verified_ind    BOOLEAN DEFAULT FALSE,
    two_factor_ind        BOOLEAN DEFAULT FALSE,
    google_auth_ind       BOOLEAN DEFAULT FALSE,
    
    -- Activity tracking
    last_login_date       TIMESTAMP NULL,
    password_changed_date TIMESTAMP NULL,
    
    created_date          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by            BIGINT NULL,
    updated_date          TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by            BIGINT NULL,
    
    CONSTRAINT uk_user_email
        UNIQUE KEY (email),
    CONSTRAINT fk_users_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_users_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Users (advocates, clerks, admins) - chamber-agnostic';

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.3 User Profiles (Personal Details - One per User)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS user_profiles;
CREATE TABLE user_profiles (
    profile_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL UNIQUE,
    address         TEXT NULL,
    country         CHAR(2) NULL,
    state           CHAR(4) NULL,
    city            VARCHAR(50) NULL,
    postal_code     VARCHAR(20) NULL,
    header_color    VARCHAR(20) DEFAULT '0 0% 100%',
    sidebar_color   VARCHAR(20) DEFAULT '0 0% 100%',
    primary_color   VARCHAR(20) DEFAULT '32.4 99% 63%',
    font_family     VARCHAR(50) DEFAULT 'Nunito, sans-serif',
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT fk_profiles_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_profiles_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='User personal details and preferences';

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.4 NEW: User ↔ Chamber Link (The Bridge Table)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS user_chamber_link;
CREATE TABLE user_chamber_link (
    link_id                 BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- Foreign Keys (Composite relationship)
    user_id                 BIGINT NOT NULL,
    chamber_id              BIGINT NOT NULL,
    
    -- Membership Details
    is_primary              BOOLEAN DEFAULT FALSE COMMENT 'User''s default/home chamber',
    joined_date             DATE NOT NULL DEFAULT (CURRENT_DATE),
    left_date               DATE NULL COMMENT 'NULL = still active',
    
    -- Chamber-Specific Overrides
    role_override           CHAR(4) NULL COMMENT 'Overrides global role_code for this chamber',
    display_name_override   VARCHAR(100) NULL COMMENT 'How user appears in this chamber',
    
    -- Status & Audit
    status_ind              BOOLEAN DEFAULT TRUE,
    created_date            TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by              BIGINT NULL,
    updated_date            TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by              BIGINT NULL,
    
    -- Constraints
    CONSTRAINT uk_user_chamber_active 
        UNIQUE KEY (user_id, chamber_id, left_date),
    CONSTRAINT fk_ucl_user 
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_ucl_chamber 
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_ucl_created_by 
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_ucl_updated_by 
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Indexes for common queries
    INDEX idx_ucl_user_primary (user_id, is_primary),
    INDEX idx_ucl_chamber_active (chamber_id, status_ind, left_date),
    INDEX idx_ucl_lookup (user_id, chamber_id, status_ind)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='User ↔ Chamber membership with contextual overrides';

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.5 Chamber Modules (Feature Access per Chamber)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS chamber_modules;
CREATE TABLE chamber_modules (
    chamber_module_id   INT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    module_code         CHAR(8) NOT NULL,
    is_active           BOOLEAN DEFAULT TRUE,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    CONSTRAINT uk_cmodule_chamber
        UNIQUE KEY (chamber_id, module_code),
    CONSTRAINT fk_cmodule_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_cmodule_module
        FOREIGN KEY (module_code) REFERENCES refm_modules(code) ON DELETE RESTRICT,
    CONSTRAINT fk_cmodule_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_cmodule_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Modules allocated per chamber';

-- =============================================================================
-- 4. SECURITY & PERMISSIONS (Roles per Chamber Context)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.1 Security Roles (Global Definitions)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS security_roles;
CREATE TABLE security_roles (
    role_id         INT AUTO_INCREMENT PRIMARY KEY,
    role_name       VARCHAR(80) NOT NULL,
    role_code       CHAR(4) NOT NULL,
    description     TEXT NULL,
    status_ind      BOOLEAN DEFAULT TRUE,
    is_deleted      BOOLEAN DEFAULT FALSE,
    deleted_date    TIMESTAMP NULL,
    deleted_by      BIGINT NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT uk_role_code
        UNIQUE KEY (role_code)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Roles';

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.2 Role Permissions (Role + Module + CRUD Flags)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS role_permissions;
CREATE TABLE role_permissions (
    permission_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    role_id           INT NOT NULL,
    chamber_module_id INT NOT NULL,
    allow_all_ind     BOOLEAN DEFAULT FALSE,
    read_ind          BOOLEAN DEFAULT TRUE,
    write_ind         BOOLEAN DEFAULT FALSE,
    create_ind        BOOLEAN DEFAULT FALSE,
    delete_ind        BOOLEAN DEFAULT FALSE,
    created_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by        BIGINT NULL,
    updated_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by        BIGINT NULL,
    CONSTRAINT uk_role_module
        UNIQUE KEY (role_id, chamber_module_id),
    CONSTRAINT fk_role_permissions_role
        FOREIGN KEY (role_id) REFERENCES security_roles(role_id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_module
        FOREIGN KEY (chamber_module_id) REFERENCES chamber_modules(chamber_module_id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_role_permissions_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Role-module permissions';

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.3 UPDATED: User Roles (Now References link_id, NOT user_id)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS user_roles;
CREATE TABLE user_roles (
    user_role_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    
    -- ✅ CHANGED: Now references user_chamber_link.link_id (contextual)
    link_id         BIGINT NOT NULL,
    role_id         INT NOT NULL,
    
    start_date      DATE NOT NULL DEFAULT (CURRENT_DATE),
    end_date        DATE NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    
    -- Constraints
    CONSTRAINT uk_user_role_active
        UNIQUE KEY (link_id, role_id, start_date),
    CONSTRAINT fk_user_roles_link
        FOREIGN KEY (link_id) REFERENCES user_chamber_link(link_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role
        FOREIGN KEY (role_id) REFERENCES security_roles(role_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_user_roles_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Role assignments per user-chamber context';

-- =============================================================================
-- 5. CORE BUSINESS TABLES (Cases & Hearings)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.1 Cases
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS cases;
CREATE TABLE cases (
    case_id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    case_number         VARCHAR(120) NOT NULL,
    court_id            INT NOT NULL,
    case_type_code      CHAR(4) NULL,
    filing_year         INT NULL,
    petitioner          TEXT NOT NULL,
    respondent          TEXT NOT NULL,
    aor_user_id         BIGINT NULL,
    case_summary        TEXT NULL,
    status_code         CHAR(4) DEFAULT 'AC',
    next_hearing_date   DATE NULL,
    last_hearing_date   DATE NULL,
    is_deleted          BOOLEAN DEFAULT FALSE,
    deleted_date        TIMESTAMP NULL,
    deleted_by          BIGINT NULL,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    CONSTRAINT uk_case_chamber_number
        UNIQUE KEY (chamber_id, case_number),
    CONSTRAINT fk_cases_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_cases_court
        FOREIGN KEY (court_id) REFERENCES refm_courts(court_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_type
        FOREIGN KEY (case_type_code) REFERENCES refm_case_types(code) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_status
        FOREIGN KEY (status_code) REFERENCES refm_case_status(code) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_aor
        FOREIGN KEY (aor_user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Legal cases';

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.2 Hearings
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS hearings;
CREATE TABLE hearings (
    hearing_id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    case_id             BIGINT NOT NULL,
    hearing_date        DATE NOT NULL,
    status_code         CHAR(4) DEFAULT 'UP',
    purpose             VARCHAR(255) NULL,
    notes               TEXT NULL,
    order_details       TEXT NULL,
    next_hearing_date   DATE NULL,
    is_deleted          BOOLEAN DEFAULT FALSE,
    deleted_date        TIMESTAMP NULL,
    deleted_by          BIGINT NULL,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    CONSTRAINT fk_hearings_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_hearings_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    CONSTRAINT fk_hearings_status
        FOREIGN KEY (status_code) REFERENCES refm_hearing_status(code) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Court hearings';

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.3 Case Notes (Internal Notes)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS case_notes;
CREATE TABLE case_notes (
    note_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    case_id         BIGINT NOT NULL,
    user_id         BIGINT NOT NULL,
    note_text       TEXT NOT NULL,
    is_private      BOOLEAN DEFAULT FALSE,
    is_deleted      BOOLEAN DEFAULT FALSE,
    deleted_date    TIMESTAMP NULL,
    deleted_by      BIGINT NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT fk_notes_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_notes_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    CONSTRAINT fk_notes_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_notes_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_notes_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_notes_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_notes_case (case_id),
    INDEX idx_notes_user (user_id),
    INDEX idx_notes_chamber_date (chamber_id, created_date DESC)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Private/internal notes on cases';

-- =============================================================================
-- 6. CLIENT MANAGEMENT (Paid Feature)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.1 Clients Master
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
    client_id           BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    
    -- Client Type & Name
    client_type         CHAR(1) NOT NULL COMMENT 'I=Individual, O=Organization',
    client_name         VARCHAR(200) NOT NULL,
    display_name        VARCHAR(200) NULL,
    
    -- Contact Information
    contact_person      VARCHAR(150) NULL COMMENT 'For organizations',
    email               VARCHAR(150) NULL,
    phone               VARCHAR(20) NULL,
    alternate_phone     VARCHAR(20) NULL,
    
    -- Address
    address_line1       VARCHAR(255) NULL,
    address_line2       VARCHAR(255) NULL,
    city                VARCHAR(80) NULL,
    state_code          CHAR(4) NULL,
    postal_code         VARCHAR(12) NULL,
    country_code        CHAR(2) DEFAULT 'IN',
    
    -- Identity Proof
    id_proof_type       VARCHAR(50) NULL COMMENT 'Aadhaar/PAN/Passport/etc',
    id_proof_number     VARCHAR(100) NULL,
    
    -- Client Metadata
    source_code         VARCHAR(20) NULL COMMENT 'REF=Referral, WEB=Website, WALK=Walk-in',
    referral_source     VARCHAR(150) NULL,
    client_since        DATE NULL,
    notes               TEXT NULL,
    
    -- Status & Audit
    status_ind          BOOLEAN DEFAULT TRUE,
    is_deleted          BOOLEAN DEFAULT FALSE,
    deleted_date        TIMESTAMP NULL,
    deleted_by          BIGINT NULL,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    
    CONSTRAINT fk_clients_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_clients_state
        FOREIGN KEY (state_code) REFERENCES refm_states(code) ON DELETE SET NULL,
    CONSTRAINT fk_clients_country
        FOREIGN KEY (country_code) REFERENCES refm_countries(code) ON DELETE RESTRICT,
    CONSTRAINT fk_clients_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_clients_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_clients_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    INDEX idx_clients_chamber (chamber_id),
    INDEX idx_clients_name (client_name),
    INDEX idx_clients_phone (phone),
    INDEX idx_clients_email (email)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Clients of chamber';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.2 Case ↔ Client Links (Many-to-Many)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS case_clients;
CREATE TABLE case_clients (
    case_client_id  BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    case_id         BIGINT NOT NULL,
    client_id       BIGINT NOT NULL,
    
    -- Role in this specific case
    party_role      CHAR(3) NOT NULL COMMENT 'PET=Petitioner, RES=Respondent, APP=Appellant, DEF=Defendant, WIT=Witness, AOR=Advocate on Record',
    
    -- Billing & Contact Priority
    is_primary      BOOLEAN DEFAULT FALSE COMMENT 'Primary client for billing/contact',
    engagement_type VARCHAR(20) NULL COMMENT 'RETAINER=Retainer, CASE=Case-wise, CONSUL=Consultation',
    
    -- Audit
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    
    CONSTRAINT uk_case_client
        UNIQUE KEY (case_id, client_id, party_role),
    CONSTRAINT fk_case_clients_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_case_clients_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    CONSTRAINT fk_case_clients_client
        FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_case_clients_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_case_clients_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    INDEX idx_case_clients_case (case_id),
    INDEX idx_case_clients_client (client_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Mapping between cases and clients';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.3 Client Billing
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_bills;
CREATE TABLE client_bills (
    bill_id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    case_id             BIGINT NULL,
    client_id           BIGINT NOT NULL,
    
    -- Bill Details
    bill_number         VARCHAR(50) NULL,
    bill_date           DATE NOT NULL,
    due_date            DATE NULL,
    
    -- Amounts
    amount              DECIMAL(12,2) NOT NULL,
    tax_amount          DECIMAL(12,2) DEFAULT 0,
    total_amount        DECIMAL(12,2) NOT NULL,
    paid_amount         DECIMAL(12,2) DEFAULT 0,
    balance_amount      DECIMAL(12,2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    
    -- Status
    status_code         CHAR(2) DEFAULT 'PN' COMMENT 'PN=Pending, PD=Paid, OV=Overdue, CN=Cancelled',
    
    -- Service Details
    service_description TEXT NULL,
    notes               TEXT NULL,
    
    -- Audit
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    
    CONSTRAINT fk_bills_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_bills_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE SET NULL,
    CONSTRAINT fk_bills_client
        FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_bills_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_bills_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    INDEX idx_bills_client (client_id),
    INDEX idx_bills_status (status_code),
    INDEX idx_bills_date (bill_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client billing records';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.4 Client Payments
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_payments;
CREATE TABLE client_payments (
    payment_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    bill_id         BIGINT NOT NULL,
    client_id       BIGINT NOT NULL,
    
    -- Payment Details
    payment_date    DATE NOT NULL,
    amount          DECIMAL(12,2) NOT NULL,
    
    -- Payment Method
    payment_mode    VARCHAR(20) NULL COMMENT 'CASH=Cash, UPI=UPI, NEFT=NEFT/IMPS, CHQ=Cheque, CARD=Card',
    reference_no    VARCHAR(100) NULL COMMENT 'Transaction ID / Cheque Number',
    bank_name       VARCHAR(100) NULL,
    
    -- Receipt
    receipt_number  VARCHAR(50) NULL,
    receipt_date    DATE NULL,
    notes           TEXT NULL,
    
    -- Audit
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    
    CONSTRAINT fk_payments_bill
        FOREIGN KEY (bill_id) REFERENCES client_bills(bill_id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_client
        FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_payments_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    INDEX idx_payments_client (client_id),
    INDEX idx_payments_date (payment_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Payments from clients';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.5 Document Custody Tracking
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_documents;
CREATE TABLE client_documents (
    document_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    client_id           BIGINT NOT NULL,
    case_id             BIGINT NULL,
    
    -- Document Details
    document_name       VARCHAR(255) NOT NULL,
    document_type       VARCHAR(50) NULL COMMENT 'ORIGINAL=Original, COPY=Copy, CERT=Certified, PDF=Digital',
    document_category   VARCHAR(50) NULL COMMENT 'ID=Identity, PROP=Property, COURT=Court Order, FIN=Financial',
    
    -- Custody Tracking
    received_date       DATE NULL,
    received_from       VARCHAR(150) NULL,
    returned_date       DATE NULL,
    returned_to         VARCHAR(150) NULL,
    custody_status      CHAR(1) DEFAULT 'H' COMMENT 'H=Held, R=Returned, L=Lost, D=Destroyed',
    
    -- Storage
    storage_location    VARCHAR(100) NULL COMMENT 'File rack number / Digital path',
    file_number         VARCHAR(50) NULL,
    notes               TEXT NULL,
    
    -- Audit
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    
    CONSTRAINT fk_doc_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_doc_client
        FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_doc_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE SET NULL,
    CONSTRAINT fk_doc_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_doc_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    INDEX idx_doc_client (client_id),
    INDEX idx_doc_case (case_id),
    INDEX idx_doc_custody (custody_status)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client documents in custody';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.6 Client Communications
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_communications;
CREATE TABLE client_communications (
    comm_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    client_id       BIGINT NOT NULL,
    case_id         BIGINT NULL,
    user_id         BIGINT NULL,
    
    -- Communication Details
    comm_type       CHAR(2) NOT NULL COMMENT 'EM=Email, SM=SMS, WH=WhatsApp, CL=Call, MT=Meeting',
    subject         VARCHAR(255) NULL,
    message_preview TEXT NULL,
    
    -- Status
    status_code     CHAR(2) DEFAULT 'PN' COMMENT 'PN=Pending, SN=Sent, DL=Delivered, RD=Read, FD=Failed',
    
    -- Timestamps
    scheduled_at    DATETIME NULL,
    sent_at         DATETIME NULL,
    delivered_at    DATETIME NULL,
    read_at         DATETIME NULL,
    
    -- Linked Email Log (if applicable)
    -- email_log_id    BIGINT NULL,
    notes           TEXT NULL,
    
    -- Audit
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    
    CONSTRAINT fk_comm_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_comm_client
        FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_comm_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE SET NULL,
    CONSTRAINT fk_comm_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    -- CONSTRAINT fk_comm_email_log
    --     FOREIGN KEY (email_log_id) REFERENCES email_log(email_id) ON DELETE SET NULL,
    CONSTRAINT fk_comm_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    
    INDEX idx_comm_client (client_id),
    INDEX idx_comm_case (case_id),
    INDEX idx_comm_type (comm_type),
    INDEX idx_comm_status (status_code)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client communications and notifications';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.7 Client Aliases (Conflict Checking)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_aliases;
CREATE TABLE client_aliases (
    alias_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id       BIGINT NOT NULL,
    alias_name      VARCHAR(200) NOT NULL,
    alias_type      VARCHAR(50) NULL COMMENT 'AKA=Also Known As, DBA=Doing Business As, OLD=Former Name',
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    CONSTRAINT fk_aliases_client
        FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_aliases_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_aliases_name (alias_name)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client alternate names for conflict checking';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.8 Client Relationships (Family/Corporate Links)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_relationships;
CREATE TABLE client_relationships (
    relationship_id     BIGINT AUTO_INCREMENT PRIMARY KEY,
    client_id_from      BIGINT NOT NULL,
    client_id_to        BIGINT NOT NULL,
    relationship_type   VARCHAR(50) NOT NULL COMMENT 'SPOUSE=Spouse, PRNT=Parent, CHLD=Child, SIBL=Sibling, DIR=Director, PART=Partner',
    is_active           BOOLEAN DEFAULT TRUE,
    notes               TEXT NULL,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    CONSTRAINT fk_rel_client_from
        FOREIGN KEY (client_id_from) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_client_to
        FOREIGN KEY (client_id_to) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_rel_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_rel_from (client_id_from),
    INDEX idx_rel_to (client_id_to)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client relationships (family/corporate)';

-- =============================================================================
-- 7. CONFIGURATION & UTILITY TABLES
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.1 Email Settings per Chamber
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS email_settings;
CREATE TABLE email_settings (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    from_email          VARCHAR(150) NOT NULL,
    smtp_host           VARCHAR(100) NOT NULL,
    smtp_port           SMALLINT UNSIGNED NOT NULL DEFAULT 587,
    smtp_user           VARCHAR(150) NOT NULL,
    smtp_password       VARCHAR(255) NOT NULL,
    encryption_code     CHAR(2) NOT NULL DEFAULT 'T',
    auth_required_ind   BOOLEAN DEFAULT TRUE,
    is_default          BOOLEAN DEFAULT FALSE,
    status_ind          BOOLEAN DEFAULT TRUE,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    CONSTRAINT uk_chamber_default
        UNIQUE KEY (chamber_id, is_default),
    CONSTRAINT fk_email_settings_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_email_settings_encryption
        FOREIGN KEY (encryption_code) REFERENCES refm_email_encryption(code) ON DELETE RESTRICT,
    CONSTRAINT fk_email_settings_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_email_settings_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='SMTP settings per chamber';

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.2 Custom Email Templates per Chamber
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS email_templates;
CREATE TABLE email_templates (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    code            CHAR(30) NOT NULL,
    subject         VARCHAR(255) NOT NULL,
    content         LONGTEXT NOT NULL,
    is_customized   BOOLEAN DEFAULT FALSE,
    enabled_ind     BOOLEAN DEFAULT TRUE,
    version         SMALLINT UNSIGNED DEFAULT 1,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT uk_chamber_template_version
        UNIQUE KEY (chamber_id, code, version),
    CONSTRAINT fk_email_templates_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_email_templates_code
        FOREIGN KEY (code) REFERENCES refm_email_templates(code) ON DELETE RESTRICT,
    CONSTRAINT fk_email_templates_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_email_templates_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Custom email templates per chamber';

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.3 Account Deletion Requests
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS delete_account_requests;
CREATE TABLE delete_account_requests (
    request_id      INT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    request_no      VARCHAR(30) NOT NULL UNIQUE,
    user_id         BIGINT NOT NULL,
    request_date    DATE NOT NULL,
    status_code     CHAR(1) DEFAULT 'P',
    notes           TEXT NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT fk_delete_req_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_delete_req_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_delete_req_status
        FOREIGN KEY (status_code) REFERENCES refm_user_deletion_status(code) ON DELETE RESTRICT,
    CONSTRAINT fk_delete_req_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_delete_req_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Account deletion requests';

-- =============================================================================
-- 8. LOGGING & AUDIT TABLES
-- =============================================================================

DROP TABLE IF EXISTS login_audit;
CREATE TABLE login_audit (
    login_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NULL,
    chamber_id      BIGINT NOT NULL,
    email           VARCHAR(120) NULL,
    ip_address      VARCHAR(45),
    user_agent      TEXT,
    status_ind      BOOLEAN NOT NULL DEFAULT TRUE,
    failure_reason  VARCHAR(255) NULL,
    login_time      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_login_time (login_time DESC),
    CONSTRAINT fk_login_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_login_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Login attempts log';

DROP TABLE IF EXISTS db_call_log;
CREATE TABLE db_call_log (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NULL,
    user_id         BIGINT NULL,
    timestamp       DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    duration_ms     DOUBLE NOT NULL,
    raw_query       LONGTEXT NOT NULL,
    params          JSON NULL,
    final_query     LONGTEXT NULL,
    repo            VARCHAR(255) NULL,
    error           LONGTEXT NULL,
    metadata_json   JSON NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    CONSTRAINT fk_db_log_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE SET NULL,
    CONSTRAINT fk_db_log_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_db_log_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='DB query log';

DROP TABLE IF EXISTS exception_log;
CREATE TABLE exception_log (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NULL,
    user_id         BIGINT NULL,
    timestamp       DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    exception_type  VARCHAR(255) NOT NULL,
    message         LONGTEXT NULL,
    stacktrace      LONGTEXT NULL,
    path            VARCHAR(500) NULL,
    method          VARCHAR(10) NULL,
    query_params    JSON NULL,
    request_body    LONGTEXT NULL,
    headers         JSON NULL,
    error_code      VARCHAR(50) NULL,
    metadata_json   JSON NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    CONSTRAINT fk_exc_log_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE SET NULL,
    CONSTRAINT fk_exc_log_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_exc_log_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Application errors log';

DROP TABLE IF EXISTS activity_log;
CREATE TABLE activity_log (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    user_id         BIGINT NULL,
    timestamp       DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    action          VARCHAR(255) NOT NULL,
    target          VARCHAR(255) NULL,
    metadata_json   JSON NULL,
    ip_address      VARCHAR(45) NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    CONSTRAINT fk_activity_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_activity_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_activity_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='User actions audit';

DROP TABLE IF EXISTS email_log;
CREATE TABLE email_log (
    email_id        BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    user_id         BIGINT NULL,
    template_code   CHAR(30) NULL,
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name  VARCHAR(120) NULL,
    subject         VARCHAR(500) NULL,
    body_preview    TEXT NULL,
    status_code     CHAR(2) DEFAULT 'P',
    sent_at         DATETIME(6) NULL,
    delivered_at    DATETIME(6) NULL,
    opened_at       DATETIME(6) NULL,
    error_message   TEXT NULL,
    retry_count     TINYINT UNSIGNED DEFAULT 0,
    next_retry_at   DATETIME NULL,
    metadata_json   JSON NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    CONSTRAINT fk_email_log_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_email_log_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_email_log_template
        FOREIGN KEY (template_code) REFERENCES refm_email_templates(code) ON DELETE SET NULL,
    CONSTRAINT fk_email_log_status
        FOREIGN KEY (status_code) REFERENCES refm_email_status(code) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Email delivery log';

-- =============================================================================
-- 9. POST-CREATION: Deferred Foreign Keys & Indexes
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.1 Restore Deferred FKs on chamber (created_by/updated_by/deleted_by → users)
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE chamber
    ADD CONSTRAINT fk_chamber_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_chamber_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_chamber_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.2 Performance Indexes
-- ─────────────────────────────────────────────────────────────────────────────

-- Cases: Common dashboard queries
CREATE INDEX idx_cases_status_hearing ON cases(status_code, next_hearing_date);
CREATE INDEX idx_cases_number ON cases(case_number);

-- Hearings: Calendar views
CREATE INDEX idx_hearings_date ON hearings(hearing_date);

-- Activity Log: Audit trails per chamber
CREATE INDEX idx_activity_chamber_time ON activity_log(chamber_id, timestamp DESC);

-- Email Log: Delivery monitoring
CREATE INDEX idx_email_log_status ON email_log(status_code, created_date);

-- Users: Login lookup
CREATE INDEX idx_users_email ON users(email);

-- User Chamber Links: Fast membership lookups
CREATE INDEX idx_ucl_user_active ON user_chamber_link(user_id, status_ind, left_date);
CREATE INDEX idx_ucl_chamber_users ON user_chamber_link(chamber_id, is_primary, status_ind);

-- User Roles: Permission resolution
CREATE INDEX idx_user_roles_link_role ON user_roles(link_id, role_id, end_date);

SELECT '✅ courtdiary database schema created successfully!' AS status;
