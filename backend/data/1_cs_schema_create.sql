-- =============================================================================
-- COURT DIARY — FULL SCHEMA (Production-Ready with Contextual Membership)
-- Design: Users are chamber-agnostic; membership via user_chamber_link
--         Roles are assigned per user-chamber context (link_id)
--         ALL entity tables use UUID v7 for security
--         Reference tables keep code-based PKs (refm_*)
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
-- 2. REFERENCE TABLES — TIER 0 (No foreign key dependencies)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.1  Geographic & Global
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_countries;
CREATE TABLE refm_countries (
    code          CHAR(2)      PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    phone_code    VARCHAR(8)   NULL,
    sort_order    INT          NOT NULL DEFAULT 0,
    status_ind    BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Countries';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.2  Subscription & Modules
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_plan_types;
CREATE TABLE refm_plan_types (
    code              CHAR(4)        PRIMARY KEY,
    description       VARCHAR(60)    NOT NULL,
    max_users         INT            NULL,
    max_cases         INT            NULL,
    price_monthly_amt DECIMAL(12,2)  DEFAULT 0,
    price_annual_amt  DECIMAL(12,2)  DEFAULT 0,
    currency_code     CHAR(3)        DEFAULT 'INR',
    sort_order        INT            NOT NULL,
    status_ind        BOOLEAN        NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Subscription plans';

DROP TABLE IF EXISTS refm_modules;
CREATE TABLE refm_modules (
    code          CHAR(8)      PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    description   TEXT         NULL,
    sort_order    INT          NOT NULL DEFAULT 0,
    status_ind    BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='System modules for permissions';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.3  Case & Hearing Statuses
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_case_status;
CREATE TABLE refm_case_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case status';

DROP TABLE IF EXISTS refm_hearing_status;
CREATE TABLE refm_hearing_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Hearing status';

DROP TABLE IF EXISTS refm_hearing_purpose;

CREATE TABLE refm_hearing_purpose (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Hearing purpose';

DROP TABLE IF EXISTS refm_case_types;
CREATE TABLE refm_case_types (
    code          CHAR(4)      PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    sort_order    INT          NOT NULL,
    status_ind    BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case types';

DROP TABLE IF EXISTS refm_client_type;
CREATE TABLE refm_client_type (
    code        CHAR(4)     PRIMARY KEY,
    description VARCHAR(60) NOT NULL,
    sort_order  INT         NOT NULL,
    status_ind  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client type master';
DROP TABLE IF EXISTS refm_engagement_type;

DROP TABLE IF EXISTS refm_party_type;
CREATE TABLE refm_party_type (
    code        CHAR(4)     PRIMARY KEY,
    description VARCHAR(60) NOT NULL,
    sort_order  INT         NOT NULL,
    status_ind  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='How is the client/party related to chamber';

DROP TABLE IF EXISTS refm_engagement_type;

CREATE TABLE refm_engagement_type (
    code        CHAR(4)     PRIMARY KEY,
    description VARCHAR(60) NOT NULL,
    sort_order  INT         NOT NULL,
    status_ind  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Engagement type master';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.4  Email & Communication
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_email_encryption;
CREATE TABLE refm_email_encryption (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Email encryption methods';

DROP TABLE IF EXISTS refm_email_status;
CREATE TABLE refm_email_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(40) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Email delivery status codes';

DROP TABLE IF EXISTS refm_email_templates;
CREATE TABLE refm_email_templates (
    code          CHAR(30)     PRIMARY KEY,
    subject       VARCHAR(255) NOT NULL,
    content       LONGTEXT     NOT NULL,
    category      VARCHAR(50)  NULL,
    description   VARCHAR(255) NULL,
    sort_order    INT          NOT NULL DEFAULT 100,
    status_ind    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='System default email templates';

DROP TABLE IF EXISTS refm_comm_status;
CREATE TABLE refm_comm_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Communication status codes';

DROP TABLE IF EXISTS refm_entity_type;
CREATE TABLE refm_entity_type (
    code        CHAR(4)     PRIMARY KEY,
    description VARCHAR(60) NOT NULL,
    sort_order  INT         NOT NULL,
    status_ind  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Entity type master for images';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.5  User & Auth Statuses
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_login_status;
CREATE TABLE refm_login_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(20) NOT NULL,
    sort_order    INT         NOT NULL
) ENGINE=InnoDB COMMENT='Login status codes';

DROP TABLE IF EXISTS refm_user_deletion_status;
CREATE TABLE refm_user_deletion_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Account deletion request statuses';

DROP TABLE IF EXISTS refm_invitation_status;
CREATE TABLE refm_invitation_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Invitation status codes';

-- ─────────────────────────────────────────────────────────────────────────────
-- 2.6  Billing, Party Roles & Collaboration Access
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_billing_status;
CREATE TABLE refm_billing_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Billing status codes';

DROP TABLE IF EXISTS refm_party_roles;
CREATE TABLE refm_party_roles (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    category      VARCHAR(30) NULL COMMENT 'PARTY=Main Party, REP=Representative, OTHR=Other',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Party roles in cases';

DROP TABLE IF EXISTS refm_aor_status;
CREATE TABLE refm_aor_status (
    code          CHAR(4)     PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7)     DEFAULT '#64748b',
    sort_order    INT         NOT NULL,
    status_ind    BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='AOR status codes';

DROP TABLE IF EXISTS refm_collab_access;
CREATE TABLE refm_collab_access (
    code          CHAR(4)      PRIMARY KEY,
    description   VARCHAR(50)  NOT NULL,
    permissions   VARCHAR(255) NULL COMMENT 'Comma-separated: view,edit,delete,share',
    color_code    CHAR(7)      DEFAULT '#64748b',
    sort_order    INT          NOT NULL,
    status_ind    BOOLEAN      NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Collaboration access levels';

-- =============================================================================
-- 3. REFERENCE TABLES — TIER 1 (FK to other REFM only)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.1  States  →  refm_countries
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_states;
CREATE TABLE refm_states (
    code          CHAR(2)      PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    country_code  CHAR(2)      NOT NULL,
    sort_order    INT          NOT NULL DEFAULT 0,
    status_ind    BOOLEAN      NOT NULL DEFAULT TRUE,
    CONSTRAINT fk_states_country
        FOREIGN KEY (country_code) REFERENCES refm_countries(code) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='States / Union Territories';

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.2  Courts  →  refm_states (Keep INT AUTO_INCREMENT - small lookup table)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_courts;
CREATE TABLE refm_courts (
    court_id      INT          AUTO_INCREMENT PRIMARY KEY,
    court_name    VARCHAR(150) NOT NULL,
    state_code    CHAR(4)      NOT NULL,
    court_type    VARCHAR(60)  NULL,
    address       TEXT         NULL,
    sort_order    INT          NOT NULL DEFAULT 0,
    status_ind    BOOLEAN      NOT NULL DEFAULT TRUE,
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    updated_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_courts_state
        FOREIGN KEY (state_code) REFERENCES refm_states(code) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Courts / benches';

-- =============================================================================
-- 4. CORE ENTITIES — TIER 2 (UUID v7 Primary Keys)
--    chamber  →  REFM only   (user FKs deferred — Section 11)
--    users    →  self only   (chamber-agnostic)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.1  Chamber (Law Firms)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS chamber;
CREATE TABLE chamber (
    chamber_id         CHAR(36)     PRIMARY KEY,  
    chamber_name       VARCHAR(150) NOT NULL,
    email              VARCHAR(120) NULL UNIQUE,
    phone              VARCHAR(20)  NULL,
    address_line1      VARCHAR(255) NULL,
    address_line2      VARCHAR(255) NULL,
    city               VARCHAR(80)  NULL,
    state_code         CHAR(2)      DEFAULT 'TN',
    postal_code        VARCHAR(12)  NULL,
    country_code       CHAR(2)      DEFAULT 'IN',
    plan_code          CHAR(4)      DEFAULT 'FREE',
    subscription_start DATE         NULL,
    subscription_end   DATE         NULL,
    status_ind         BOOLEAN      NOT NULL DEFAULT TRUE,
    deleted_ind         BOOLEAN      DEFAULT FALSE,
    deleted_date       TIMESTAMP    NULL,
    deleted_by         CHAR(36)     NULL,  
    created_date       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by         CHAR(36)     NULL,  
    updated_date       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by         CHAR(36)     NULL,  
    CONSTRAINT fk_chamber_state
        FOREIGN KEY (state_code)   REFERENCES refm_states(code)      ON DELETE RESTRICT,
    CONSTRAINT fk_chamber_country
        FOREIGN KEY (country_code) REFERENCES refm_countries(code)   ON DELETE RESTRICT,
    CONSTRAINT fk_chamber_plan
        FOREIGN KEY (plan_code)    REFERENCES refm_plan_types(code)  ON DELETE RESTRICT,
    INDEX idx_chamber_email (email),
    INDEX idx_chamber_status (status_ind, deleted_ind)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Law chamber / firm';

-- ─────────────────────────────────────────────────────────────────────────────
-- 4.2  Users (Chamber-agnostic)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id               CHAR(36)     PRIMARY KEY,  
    email                 VARCHAR(120) NOT NULL,
    password_hash         VARCHAR(255) NOT NULL,
    first_name            VARCHAR(60)  NOT NULL,
    last_name             VARCHAR(60)  NULL,
    phone                 VARCHAR(20)  NULL,
    status_ind            BOOLEAN      NOT NULL DEFAULT TRUE,
    deleted_ind           BOOLEAN      DEFAULT FALSE,
    deleted_date          TIMESTAMP    NULL,
    deleted_by            CHAR(36)     NULL,  
    email_verified_ind    BOOLEAN      DEFAULT FALSE,
    phone_verified_ind    BOOLEAN      DEFAULT FALSE,
    two_factor_ind        BOOLEAN      DEFAULT FALSE,
    google_auth_ind       BOOLEAN      DEFAULT FALSE,
    last_login_date       TIMESTAMP    NULL,
    password_changed_date TIMESTAMP    NULL,
    created_date          TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by            CHAR(36)     NULL,  
    updated_date          TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by            CHAR(36)     NULL,  
    CONSTRAINT uk_user_email
        UNIQUE KEY (email),
    INDEX idx_users_status (status_ind, deleted_ind)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Users (chamber-agnostic)';

-- =============================================================================
-- 5. TIER 3 — Bridge Tables (UUID v7)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.1  User Profiles  →  users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS user_profiles;
CREATE TABLE user_profiles (
    profile_id    CHAR(36)     PRIMARY KEY,  
    user_id       CHAR(36)     NOT NULL UNIQUE,  
    address       TEXT         NULL,
    country       CHAR(2)      NULL,
    state         CHAR(4)      NULL,
    city          VARCHAR(50)  NULL,
    postal_code   VARCHAR(20)  NULL,
    header_color  VARCHAR(20)  DEFAULT '0 0% 100%',
    sidebar_color VARCHAR(20)  DEFAULT '0 0% 100%',
    primary_color VARCHAR(20)  DEFAULT '32.4 99% 63%',
    font_family   VARCHAR(50)  DEFAULT 'Nunito, sans-serif',
    updated_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by    CHAR(36)     NULL,  
    CONSTRAINT fk_profiles_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_profiles_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='User personal details and preferences';

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.2  User ↔ Chamber Link  →  users, chamber
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS user_chamber_link;
CREATE TABLE user_chamber_link (
    link_id               CHAR(36)     PRIMARY KEY,  
    user_id               CHAR(36)     NOT NULL,  
    chamber_id            CHAR(36)     NOT NULL,  
    primary_ind            BOOLEAN      DEFAULT FALSE,
    joined_date           DATE         NOT NULL DEFAULT (CURRENT_DATE),
    left_date             DATE         NULL,
    status_ind            BOOLEAN      NOT NULL DEFAULT TRUE,
    created_date          TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by            CHAR(36)     NULL,  
    updated_date          TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by            CHAR(36)     NULL,  
    CONSTRAINT uk_user_chamber_active
        UNIQUE KEY (user_id, chamber_id, left_date),
    CONSTRAINT fk_ucl_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)     ON DELETE CASCADE,
    CONSTRAINT fk_ucl_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_ucl_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)     ON DELETE SET NULL,
    CONSTRAINT fk_ucl_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id)     ON DELETE SET NULL,
    INDEX idx_ucl_user_primary    (user_id, primary_ind),
    INDEX idx_ucl_chamber_active  (chamber_id, status_ind, left_date),
    INDEX idx_ucl_lookup          (user_id, chamber_id, status_ind)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='User ↔ Chamber membership';

-- ─────────────────────────────────────────────────────────────────────────────
-- 5.3  Chamber Modules  →  chamber, refm_modules, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS chamber_modules;
CREATE TABLE chamber_modules (
    chamber_module_id CHAR(36)     PRIMARY KEY,  
    chamber_id        CHAR(36)     NOT NULL,  
    module_code       CHAR(8)      NOT NULL,
    active_ind        BOOLEAN      DEFAULT TRUE,
    created_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by        CHAR(36)     NULL,  
    updated_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by        CHAR(36)     NULL,  
    CONSTRAINT uk_cmodule_chamber
        UNIQUE KEY (chamber_id, module_code),
    CONSTRAINT fk_cmodule_chamber
        FOREIGN KEY (chamber_id)  REFERENCES chamber(chamber_id)  ON DELETE CASCADE,
    CONSTRAINT fk_cmodule_module
        FOREIGN KEY (module_code) REFERENCES refm_modules(code)   ON DELETE RESTRICT,
    CONSTRAINT fk_cmodule_created_by
        FOREIGN KEY (created_by)  REFERENCES users(user_id)        ON DELETE SET NULL,
    CONSTRAINT fk_cmodule_updated_by
        FOREIGN KEY (updated_by)  REFERENCES users(user_id)        ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Modules allocated per chamber';

-- =============================================================================
-- 6. TIER 4 — Roles (INT for security_roles, UUID v7 for others)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.1  Security Roles  →  users (audit only) - Keep INT (small lookup table < 20 rows)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS security_roles;
CREATE TABLE security_roles (
    role_id      INT          AUTO_INCREMENT PRIMARY KEY,  -- Keep INT (small table)
    role_name    VARCHAR(80)  NOT NULL,
    description  TEXT         NULL,
    system_ind   BOOLEAN      NOT NULL DEFAULT TRUE,
    admin_ind    BOOLEAN      NOT NULL DEFAULT FALSE,
    status_ind   BOOLEAN      NOT NULL DEFAULT TRUE,
    deleted_ind  BOOLEAN      DEFAULT FALSE,
    deleted_date TIMESTAMP    NULL,
    deleted_by   CHAR(36)     NULL,  
    created_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by   CHAR(36)     NULL,  
    updated_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by   CHAR(36)     NULL,  
    CONSTRAINT uk_role_name
        UNIQUE KEY (role_name)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Master role templates';


-- ─────────────────────────────────────────────────────────────────────────────
-- 6.1b Chamber Roles (Chamber-Specific Instances)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS chamber_roles;
CREATE TABLE chamber_roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    chamber_id CHAR(36) NOT NULL,
    role_name VARCHAR(80) NOT NULL,
    description TEXT NULL,
	system_ind BOOLEAN NOT NULL DEFAULT FALSE,
    admin_ind  BOOLEAN NOT NULL DEFAULT FALSE,
    status_ind BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_ind BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP NULL,
    deleted_by CHAR(36) NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by CHAR(36) NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by CHAR(36) NULL,
    CONSTRAINT uk_chamber_role_name UNIQUE KEY (chamber_id, role_name),
    CONSTRAINT fk_croles_chamber FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_croles_created_by FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_croles_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_croles_chamber (chamber_id, status_ind)
) ENGINE=InnoDB COMMENT='Chamber-specific role instances';

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.2  User Roles for PK, INT for role_id FK
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS user_roles;
CREATE TABLE user_roles (
    user_role_id CHAR(36) PRIMARY KEY,
    link_id CHAR(36) NOT NULL,
    role_id INT NOT NULL,
    start_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    end_date DATE NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by CHAR(36) NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by CHAR(36) NULL,
    CONSTRAINT uk_user_role_active UNIQUE KEY (link_id, role_id, start_date),
    CONSTRAINT fk_user_roles_link FOREIGN KEY (link_id) REFERENCES user_chamber_link(link_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_chamber_role FOREIGN KEY (role_id) REFERENCES chamber_roles(role_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_created_by FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_user_roles_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Role assignments per user-chamber context';


-- =============================================================================
-- 7. TIER 5  —  Permissions (Depends on Tier 4)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.1  Role Permissions  →  security_roles, chamber_modules, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS role_permissions;
CREATE TABLE role_permissions (
    permission_id CHAR(36) PRIMARY KEY,
    role_id INT NOT NULL,           -- ← Changed
    chamber_module_id CHAR(36) NOT NULL,
    allow_all_ind BOOLEAN NOT NULL DEFAULT FALSE,
    read_ind BOOLEAN NOT NULL DEFAULT TRUE,
    write_ind BOOLEAN NOT NULL DEFAULT FALSE,
    create_ind BOOLEAN NOT NULL DEFAULT FALSE,
    delete_ind BOOLEAN NOT NULL DEFAULT FALSE,
    import_ind BOOLEAN NOT NULL DEFAULT FALSE,
    export_ind BOOLEAN NOT NULL DEFAULT FALSE,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by CHAR(36) NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by CHAR(36) NULL,
    CONSTRAINT uk_role_module UNIQUE KEY (role_id, chamber_module_id),
    CONSTRAINT fk_role_permissions_chamber_role FOREIGN KEY (role_id) REFERENCES chamber_roles(role_id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_module FOREIGN KEY (chamber_module_id) REFERENCES chamber_modules(chamber_module_id) ON DELETE CASCADE
) ENGINE=InnoDB COMMENT='Role-module permissions';


-- =============================================================================
-- 8. TIER 6  —  Core Business: Cases
--    →  chamber, refm_courts, refm_case_types, refm_case_status, users
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.1  Cases
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS cases;
CREATE TABLE cases (
    case_id           CHAR(36)     PRIMARY KEY,  
    chamber_id        CHAR(36)     NOT NULL,  
    case_number       VARCHAR(120) NOT NULL,
    court_id          INT          NOT NULL,
    case_type_code    CHAR(4)      NULL,
    filing_year       INT          NULL,
    petitioner        TEXT         NOT NULL,
    respondent        TEXT         NOT NULL,
    aor_user_id       CHAR(36)     NULL,  
    case_summary      TEXT         NULL,
    status_code       CHAR(4)      DEFAULT 'AC',
    next_hearing_date DATE         NULL,
    last_hearing_date DATE         NULL,
    deleted_ind        BOOLEAN      DEFAULT FALSE,
    deleted_date      TIMESTAMP    NULL,
    deleted_by        CHAR(36)     NULL,  
    created_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by        CHAR(36)     NULL,  
    updated_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by        CHAR(36)     NULL,  
    CONSTRAINT uk_case_chamber_number
        UNIQUE KEY (chamber_id, case_number),
    CONSTRAINT fk_cases_chamber
        FOREIGN KEY (chamber_id)     REFERENCES chamber(chamber_id)        ON DELETE CASCADE,
    CONSTRAINT fk_cases_court
        FOREIGN KEY (court_id)       REFERENCES refm_courts(court_id)      ON DELETE RESTRICT,
    CONSTRAINT fk_cases_type
        FOREIGN KEY (case_type_code) REFERENCES refm_case_types(code)      ON DELETE RESTRICT,
    CONSTRAINT fk_cases_status
        FOREIGN KEY (status_code)    REFERENCES refm_case_status(code)     ON DELETE RESTRICT,
    CONSTRAINT fk_cases_aor
        FOREIGN KEY (aor_user_id)    REFERENCES users(user_id)             ON DELETE SET NULL,
    INDEX idx_cases_chamber_status (chamber_id, status_code),
    INDEX idx_cases_next_hearing (next_hearing_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Legal cases';


-- =============================================================================
-- 9. TIER 7  —  Case Children: Hearings, Notes, AORs
--    →  cases, chamber, refm_hearing_status, users
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.2  Hearings  →  chamber, cases, refm_hearing_status
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS hearings;

CREATE TABLE hearings (
    hearing_id         CHAR(36)     PRIMARY KEY,  
    chamber_id         CHAR(36)     NOT NULL,  
    case_id            CHAR(36)     NOT NULL,  

    hearing_date       DATE         NOT NULL,

    status_code        CHAR(4)      DEFAULT 'HSUP',
    purpose_code       CHAR(4)      NULL,   -- 🔥 REPLACED purpose TEXT

    notes              TEXT         NULL,
    order_details      TEXT         NULL,

    next_hearing_date  DATE         NULL,

    deleted_ind        BOOLEAN      DEFAULT FALSE,
    deleted_date       TIMESTAMP    NULL,
    deleted_by         CHAR(36)     NULL,  

    created_date       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by         CHAR(36)     NULL,  

    updated_date       TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by         CHAR(36)     NULL,  

    -- 🔗 Foreign Keys
    CONSTRAINT fk_hearings_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_hearings_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_hearings_status
        FOREIGN KEY (status_code) REFERENCES refm_hearing_status(code)
        ON DELETE RESTRICT,

    CONSTRAINT fk_hearings_purpose   -- 🔥 NEW FK
        FOREIGN KEY (purpose_code) REFERENCES refm_hearing_purpose(code)
        ON DELETE RESTRICT

) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Court hearings';

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.3  Case Notes  →  chamber, cases, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS case_notes;
CREATE TABLE case_notes (
    note_id      CHAR(36)     PRIMARY KEY,  
    chamber_id   CHAR(36)     NOT NULL,  
    case_id      CHAR(36)     NOT NULL,  
    user_id      CHAR(36)     NOT NULL,  
    note_text    TEXT         NOT NULL,
    private_ind  BOOLEAN      DEFAULT FALSE,
    deleted_ind  BOOLEAN      DEFAULT FALSE,
    deleted_date TIMESTAMP    NULL,
    deleted_by   CHAR(36)     NULL,  
    created_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by   CHAR(36)     NULL,  
    updated_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by   CHAR(36)     NULL,  
    CONSTRAINT fk_notes_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_notes_case
        FOREIGN KEY (case_id)    REFERENCES cases(case_id)      ON DELETE CASCADE,
    CONSTRAINT fk_notes_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)      ON DELETE CASCADE,
    CONSTRAINT fk_notes_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users(user_id)      ON DELETE SET NULL,
    CONSTRAINT fk_notes_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)      ON DELETE SET NULL,
    CONSTRAINT fk_notes_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id)      ON DELETE SET NULL,
    INDEX idx_notes_case (case_id),
    INDEX idx_notes_user (user_id),
    INDEX idx_notes_chamber_date (chamber_id, created_date DESC)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Internal notes on cases';

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.4  Case AORs  →  cases, users, chamber
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS case_aors;
CREATE TABLE case_aors (
    case_aor_id      CHAR(36)     PRIMARY KEY,  
    case_id          CHAR(36)     NOT NULL,  
    user_id          CHAR(36)     NOT NULL,  
    chamber_id       CHAR(36)     NOT NULL,  
    primary_ind       BOOLEAN      DEFAULT FALSE,
    appointment_date DATE         NULL,
    withdrawal_date  DATE         NULL,
    status_code      CHAR(4)      DEFAULT 'CSAC',
    notes            TEXT         NULL,
    created_date     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by       CHAR(36)     NULL,  
    CONSTRAINT fk_aor_case
        FOREIGN KEY (case_id)    REFERENCES cases(case_id)       ON DELETE CASCADE,
    CONSTRAINT fk_aor_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)       ON DELETE CASCADE,
    CONSTRAINT fk_aor_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)  ON DELETE CASCADE,
    CONSTRAINT fk_aor_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)       ON DELETE SET NULL,
    UNIQUE KEY uk_case_aor (case_id, user_id, status_code),
    INDEX idx_aor_case (case_id),
    INDEX idx_aor_user (user_id),
    INDEX idx_aor_status (status_code)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Multiple AORs per case';

-- =============================================================================
-- 8. TIER 6 — Client Management (Paid Feature)
--     →  chamber, cases, refm_states, refm_countries, users
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 8.1  Clients  →  chamber, refm_states, refm_countries, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS clients;
CREATE TABLE clients (
    client_id       CHAR(36)     PRIMARY KEY,  
    chamber_id      CHAR(36)     NOT NULL,  
    client_type_code  CHAR(4)      NOT NULL,
	party_type_code  CHAR(4)      NOT NULL,
    client_name     VARCHAR(200) NOT NULL,
    display_name    VARCHAR(200) NULL,
    contact_person  VARCHAR(150) NULL,
    email           VARCHAR(150) NULL,
    phone           VARCHAR(20)  NULL,
    alternate_phone VARCHAR(20)  NULL,
    address_line1   VARCHAR(255) NULL,
    address_line2   VARCHAR(255) NULL,
    city            VARCHAR(80)  NULL,
    state_code      CHAR(4)      NULL,
    postal_code     VARCHAR(12)  NULL,
    country_code    CHAR(2)      DEFAULT 'IN',
    id_proof_type   VARCHAR(50)  NULL,
    id_proof_number VARCHAR(100) NULL,
    source_code     VARCHAR(20)  NULL,
    referral_source VARCHAR(150) NULL,
    client_since    DATE         NULL,
    notes           TEXT         NULL,
    deleted_ind     BOOLEAN      DEFAULT FALSE,
    deleted_date    TIMESTAMP    NULL,
    deleted_by      CHAR(36)     NULL,  
    created_date    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by      CHAR(36)     NULL,  
    updated_date    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      CHAR(36)     NULL,  
    CONSTRAINT fk_clients_chamber
        FOREIGN KEY (chamber_id)  REFERENCES chamber(chamber_id)     ON DELETE CASCADE,
    CONSTRAINT fk_clients_type
        FOREIGN KEY (client_type_code) REFERENCES refm_client_type(code)  ON DELETE RESTRICT,
    CONSTRAINT fk_party_type
        FOREIGN KEY (party_type_code) REFERENCES refm_party_type(code)  ON DELETE RESTRICT,
    CONSTRAINT fk_clients_state
        FOREIGN KEY (state_code)  REFERENCES refm_states(code)       ON DELETE SET NULL,
    CONSTRAINT fk_clients_country
        FOREIGN KEY (country_code) REFERENCES refm_countries(code)   ON DELETE RESTRICT,
    CONSTRAINT fk_clients_deleted_by
        FOREIGN KEY (deleted_by)  REFERENCES users(user_id)          ON DELETE SET NULL,
    CONSTRAINT fk_clients_created_by
        FOREIGN KEY (created_by)  REFERENCES users(user_id)          ON DELETE SET NULL,
    CONSTRAINT fk_clients_updated_by
        FOREIGN KEY (updated_by)  REFERENCES users(user_id)          ON DELETE SET NULL,
    INDEX idx_clients_chamber (chamber_id),
    INDEX idx_clients_name (client_name),
    INDEX idx_clients_phone (phone),
    INDEX idx_clients_email (email)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Clients of chamber';

-- ─────────────────────────────────────────────────────────────────────────────
-- 8.2  Case Clients ↔ Client Link  →  chamber, cases, clients, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS case_clients;
CREATE TABLE case_clients (
    case_client_id  CHAR(36)     PRIMARY KEY,  
    chamber_id      CHAR(36)     NOT NULL,  
    case_id         CHAR(36)     NOT NULL,  
    client_id       CHAR(36)     NOT NULL,  
    party_role_code      CHAR(4)      NOT NULL,
    primary_ind     BOOLEAN      DEFAULT FALSE,
    engagement_type_code CHAR(4)      NULL,
    created_date    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by      CHAR(36)     NULL,  
    updated_date    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      CHAR(36)     NULL,  
    CONSTRAINT uk_case_client
        UNIQUE KEY (case_id, client_id, party_role_code),
    CONSTRAINT fk_case_clients_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)   ON DELETE CASCADE,
    CONSTRAINT fk_case_clients_case
        FOREIGN KEY (case_id)    REFERENCES cases(case_id)        ON DELETE CASCADE,
    CONSTRAINT fk_case_clients_client
        FOREIGN KEY (client_id)  REFERENCES clients(client_id)    ON DELETE CASCADE,
    CONSTRAINT fk_case_clients_party_role
        FOREIGN KEY (party_role_code) REFERENCES refm_party_roles(code) ON DELETE RESTRICT,
    CONSTRAINT fk_case_clients_engagement
        FOREIGN KEY (engagement_type_code) REFERENCES refm_engagement_type(code) ON DELETE RESTRICT,
    CONSTRAINT fk_case_clients_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)        ON DELETE SET NULL,
    CONSTRAINT fk_case_clients_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id)        ON DELETE SET NULL,
    INDEX idx_case_clients_case (case_id),
    INDEX idx_case_clients_client (client_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case ↔ Client mapping';

-- ─────────────────────────────────────────────────────────────────────────────
-- 8.3  Client Bills  →  chamber, cases, clients, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_bills;
CREATE TABLE client_bills (
    bill_id             CHAR(36)     PRIMARY KEY,  
    chamber_id          CHAR(36)     NOT NULL,  
    case_id             CHAR(36)     NULL,  
    client_id           CHAR(36)     NOT NULL,  
    bill_number         VARCHAR(50)  NULL,
    bill_date           DATE         NOT NULL,
    due_date            DATE         NULL,
    amount              DECIMAL(12,2) NOT NULL,
    tax_amount          DECIMAL(12,2) DEFAULT 0,
    total_amount        DECIMAL(12,2) NOT NULL,
    paid_amount         DECIMAL(12,2) DEFAULT 0,
    balance_amount      DECIMAL(12,2) GENERATED ALWAYS AS (total_amount - paid_amount) STORED,
    status_code         CHAR(4)      DEFAULT 'BSPN',
    service_description TEXT         NULL,
    notes               TEXT         NULL,
    created_date        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by          CHAR(36)     NULL,  
    updated_date        TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          CHAR(36)     NULL,  
    CONSTRAINT fk_bills_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)   ON DELETE CASCADE,
    CONSTRAINT fk_bills_case
        FOREIGN KEY (case_id)    REFERENCES cases(case_id)        ON DELETE SET NULL,
    CONSTRAINT fk_bills_client
        FOREIGN KEY (client_id)  REFERENCES clients(client_id)    ON DELETE CASCADE,
    CONSTRAINT fk_bills_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)        ON DELETE SET NULL,
    CONSTRAINT fk_bills_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id)        ON DELETE SET NULL,
    CONSTRAINT fk_bills_status_by
        FOREIGN KEY (status_code) REFERENCES refm_billing_status(code)        ON DELETE SET NULL,
    INDEX idx_bills_client (client_id),
    INDEX idx_bills_status (status_code),
    INDEX idx_bills_date (bill_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client billing records';

-- ─────────────────────────────────────────────────────────────────────────────
-- 8.4  Client Payments  →  client_bills, clients, chamber, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_payments;
CREATE TABLE client_payments (
    payment_id     CHAR(36)     PRIMARY KEY,  
    chamber_id     CHAR(36)     NOT NULL,  
    bill_id        CHAR(36)     NOT NULL,  
    client_id      CHAR(36)     NOT NULL,  
    payment_date   DATE         NOT NULL,
    amount         DECIMAL(12,2) NOT NULL,
    payment_mode   VARCHAR(20)   NULL COMMENT 'CASH, UPI, NEFT, CHQ, CARD',
    reference_no   VARCHAR(100) NULL,
    bank_name      VARCHAR(100) NULL,
    receipt_number VARCHAR(50)  NULL,
    receipt_date   DATE         NULL,
    notes          TEXT         NULL,
    created_date   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by     CHAR(36)     NULL,  
    updated_date   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by     CHAR(36)     NULL,  
    CONSTRAINT fk_payments_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)       ON DELETE CASCADE,
    CONSTRAINT fk_payments_bill
        FOREIGN KEY (bill_id)    REFERENCES client_bills(bill_id)     ON DELETE CASCADE,
    CONSTRAINT fk_payments_client
        FOREIGN KEY (client_id)  REFERENCES clients(client_id)        ON DELETE CASCADE,
    CONSTRAINT fk_payments_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)            ON DELETE SET NULL,
    CONSTRAINT fk_payments_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id)            ON DELETE SET NULL,
    INDEX idx_payments_client (client_id),
    INDEX idx_payments_date (payment_date)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Payments from clients';

-- ─────────────────────────────────────────────────────────────────────────────
-- 8.5  Client Documents  →  chamber, clients, cases, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_documents;
CREATE TABLE client_documents (
    document_id       CHAR(36)     PRIMARY KEY,  
    chamber_id        CHAR(36)     NOT NULL,  
    client_id         CHAR(36)     NOT NULL,  
    case_id           CHAR(36)     NULL,  
    document_name     VARCHAR(255) NOT NULL,
    document_type     VARCHAR(50)  NULL,
    document_category VARCHAR(50)  NULL,
    received_date     DATE         NULL,
    received_from     VARCHAR(150) NULL,
    returned_date     DATE         NULL,
    returned_to       VARCHAR(150) NULL,
    custody_status    CHAR(1)      DEFAULT 'H',
    storage_location  VARCHAR(100) NULL,
    file_number       VARCHAR(50)  NULL,
    notes             TEXT         NULL,
    created_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by        CHAR(36)     NULL,  
    updated_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by        CHAR(36)     NULL,  
    CONSTRAINT fk_doc_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)   ON DELETE CASCADE,
    CONSTRAINT fk_doc_client
        FOREIGN KEY (client_id)  REFERENCES clients(client_id)    ON DELETE CASCADE,
    CONSTRAINT fk_doc_case
        FOREIGN KEY (case_id)    REFERENCES cases(case_id)        ON DELETE SET NULL,
    CONSTRAINT fk_doc_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)        ON DELETE SET NULL,
    CONSTRAINT fk_doc_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id)        ON DELETE SET NULL,
    INDEX idx_doc_client (client_id),
    INDEX idx_doc_case (case_id),
    INDEX idx_doc_custody (custody_status)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client documents in custody';

-- ─────────────────────────────────────────────────────────────────────────────
-- 8.6  Client Communications  →  chamber, clients, cases, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS client_communications;
CREATE TABLE client_communications (
    comm_id         CHAR(36)     PRIMARY KEY,  
    chamber_id      CHAR(36)     NOT NULL,  
    client_id       CHAR(36)     NOT NULL,  
    case_id         CHAR(36)     NULL,  
    user_id         CHAR(36)     NULL,  
    comm_type       CHAR(4)      NOT NULL,
    subject         VARCHAR(255) NULL,
    message_preview TEXT         NULL,
    status_code     CHAR(4)      DEFAULT 'CSPN',
    scheduled_at    DATETIME     NULL,
    sent_at        DATETIME     NULL,
    delivered_at    DATETIME     NULL,
    read_at         DATETIME     NULL,
    notes           TEXT         NULL,
    created_date    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by      CHAR(36)     NULL,  
    CONSTRAINT fk_comm_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)   ON DELETE CASCADE,
    CONSTRAINT fk_comm_client
        FOREIGN KEY (client_id)  REFERENCES clients(client_id)    ON DELETE CASCADE,
    CONSTRAINT fk_comm_case
        FOREIGN KEY (case_id)    REFERENCES cases(case_id)        ON DELETE SET NULL,
    CONSTRAINT fk_comm_status_code
        FOREIGN KEY (status_code)    REFERENCES refm_comm_status(code)        ON DELETE SET NULL,
    CONSTRAINT fk_comm_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)        ON DELETE SET NULL,
    CONSTRAINT fk_comm_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)        ON DELETE SET NULL,
    INDEX idx_comm_client (client_id),
    INDEX idx_comm_case (case_id),
    INDEX idx_comm_type (comm_type),
    INDEX idx_comm_status (status_code)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Client communications';


DROP TABLE IF EXISTS profile_images;
CREATE TABLE profile_images (
    image_id      CHAR(36)     PRIMARY KEY,
    user_id       CHAR(36)     NULL,       -- FK to users
    client_id     CHAR(36)     NULL,       -- FK to clients
    image_data    LONGTEXT     NOT NULL,   -- base64 string
    description   VARCHAR(255) NULL,
    deleted_ind   BOOLEAN      DEFAULT FALSE,
    deleted_date  TIMESTAMP    NULL,
    deleted_by    CHAR(36)     NULL,
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by    CHAR(36)     NULL,
    updated_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by    CHAR(36)     NULL,
    CONSTRAINT fk_profile_images_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_profile_images_client
        FOREIGN KEY (client_id) REFERENCES clients(client_id) ON DELETE CASCADE,
    CONSTRAINT fk_profile_images_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_profile_images_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_profile_images_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL,
    INDEX idx_profile_images_user (user_id),
    INDEX idx_profile_images_client (client_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Profile images for users and clients';


-- =============================================================================
-- 9. TIER 7 — Configuration & Utility
--     →  chamber, refm_*, users
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.1  Email Settings  →  chamber, refm_email_encryption, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS email_settings;
CREATE TABLE email_settings (
    id                INT       AUTO_INCREMENT PRIMARY KEY,
    chamber_id        CHAR(36)  NOT NULL,  
    from_email        VARCHAR(150) NOT NULL,
    smtp_host         VARCHAR(100) NOT NULL,
    smtp_port         SMALLINT UNSIGNED NOT NULL DEFAULT 587,
    smtp_user         VARCHAR(150) NOT NULL,
    smtp_password     VARCHAR(255) NOT NULL,
    encryption_code   CHAR(4)   NOT NULL DEFAULT 'EETL',
    auth_required_ind BOOLEAN   DEFAULT TRUE,
    default_ind        BOOLEAN   DEFAULT FALSE,
    status_ind        BOOLEAN   NOT NULL DEFAULT TRUE,
    created_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by        CHAR(36)  NULL,  
    updated_date      TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by        CHAR(36)  NULL,  
    CONSTRAINT uk_chamber_default
        UNIQUE KEY (chamber_id, default_ind),
    CONSTRAINT fk_email_settings_chamber
        FOREIGN KEY (chamber_id)      REFERENCES chamber(chamber_id)           ON DELETE CASCADE,
    CONSTRAINT fk_email_settings_encryption
        FOREIGN KEY (encryption_code) REFERENCES refm_email_encryption(code)  ON DELETE RESTRICT,
    CONSTRAINT fk_email_settings_created_by
        FOREIGN KEY (created_by)      REFERENCES users(user_id)               ON DELETE SET NULL,
    CONSTRAINT fk_email_settings_updated_by
        FOREIGN KEY (updated_by)      REFERENCES users(user_id)               ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='SMTP settings per chamber';

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.2  Email Templates (Custom)  →  chamber, refm_email_templates, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS email_templates;
CREATE TABLE email_templates (
    id            INT       AUTO_INCREMENT PRIMARY KEY,
    chamber_id    CHAR(36)  NOT NULL,  
    code          CHAR(30)  NOT NULL,
    subject       VARCHAR(255) NOT NULL,
    content       LONGTEXT  NOT NULL,
    customized_ind BOOLEAN   DEFAULT FALSE,
    enabled_ind   BOOLEAN   DEFAULT TRUE,
    version       SMALLINT UNSIGNED DEFAULT 1,
    created_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by    CHAR(36)  NULL,  
    updated_date  TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by    CHAR(36)  NULL,  
    CONSTRAINT uk_chamber_template_version
        UNIQUE KEY (chamber_id, code, version),
    CONSTRAINT fk_email_templates_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)         ON DELETE CASCADE,
    CONSTRAINT fk_email_templates_code
        FOREIGN KEY (code)       REFERENCES refm_email_templates(code)  ON DELETE RESTRICT,
    CONSTRAINT fk_email_templates_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)             ON DELETE SET NULL,
    CONSTRAINT fk_email_templates_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id)             ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Custom email templates per chamber';

-- ─────────────────────────────────────────────────────────────────────────────
-- 9.3  Delete Account Requests  →  chamber, users, refm_user_deletion_status
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS delete_account_requests;
CREATE TABLE delete_account_requests (
    request_id   INT          AUTO_INCREMENT PRIMARY KEY,
    chamber_id   CHAR(36)     NOT NULL,  
    request_no   VARCHAR(30)  NOT NULL UNIQUE,
    user_id      CHAR(36)     NOT NULL,  
    request_date DATE         NOT NULL,
    status_code  CHAR(4)      DEFAULT 'DSPN',
    notes        TEXT         NULL,
    created_date TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by   CHAR(36)     NULL,  
    updated_date TIMESTAMP    NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    updated_by   CHAR(36)     NULL,  
    CONSTRAINT fk_delete_req_chamber
        FOREIGN KEY (chamber_id)  REFERENCES chamber(chamber_id)               ON DELETE CASCADE,
    CONSTRAINT fk_delete_req_user
        FOREIGN KEY (user_id)     REFERENCES users(user_id)                    ON DELETE CASCADE,
    CONSTRAINT fk_delete_req_status
        FOREIGN KEY (status_code) REFERENCES refm_user_deletion_status(code)  ON DELETE RESTRICT,
    CONSTRAINT fk_delete_req_created_by
        FOREIGN KEY (created_by)  REFERENCES users(user_id)                   ON DELETE SET NULL,
    CONSTRAINT fk_delete_req_updated_by
        FOREIGN KEY (updated_by)  REFERENCES users(user_id)                   ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Account deletion requests';


-- =============================================================================
-- 10. TIER 10  —  Multi-Chamber Collaboration & Invitations
--     →  cases, chamber, security_roles, users
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.1  Case Collaborations  →  cases, chamber, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS case_collaborations;
CREATE TABLE case_collaborations (
    collaboration_id        CHAR(36)     PRIMARY KEY,  
    case_id                 CHAR(36)     NOT NULL,  
    owner_chamber_id        CHAR(36)     NOT NULL,  
    collaborator_chamber_id CHAR(36)     NOT NULL,  
    access_level            CHAR(4)      DEFAULT 'CARO',
    invited_by              CHAR(36)     NULL,  
    invited_date            TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    accepted_date           TIMESTAMP    NULL,
    status_code             CHAR(4)      DEFAULT 'PN',
    notes                   TEXT         NULL,
    created_date            TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by              CHAR(36)     NULL,  
    updated_date            TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by              CHAR(36)     NULL,  
    CONSTRAINT fk_collab_case
        FOREIGN KEY (case_id)                 REFERENCES cases(case_id)         ON DELETE CASCADE,
    CONSTRAINT fk_collab_owner
        FOREIGN KEY (owner_chamber_id)        REFERENCES chamber(chamber_id)    ON DELETE CASCADE,
    CONSTRAINT fk_collab_collaborator
        FOREIGN KEY (collaborator_chamber_id) REFERENCES chamber(chamber_id)    ON DELETE CASCADE,
    CONSTRAINT fk_collab_access_level
        FOREIGN KEY (access_level) REFERENCES refm_collab_access(code)    ON DELETE CASCADE,
    CONSTRAINT fk_collab_invited_by
        FOREIGN KEY (invited_by)              REFERENCES users(user_id)         ON DELETE SET NULL,
    CONSTRAINT fk_collab_created_by
        FOREIGN KEY (created_by)              REFERENCES users(user_id)         ON DELETE SET NULL,
    CONSTRAINT fk_collab_updated_by
        FOREIGN KEY (updated_by)              REFERENCES users(user_id)         ON DELETE SET NULL,
    UNIQUE KEY uk_case_collaboration (case_id, collaborator_chamber_id),
    INDEX idx_collab_case (case_id),
    INDEX idx_collab_chamber (collaborator_chamber_id),
    INDEX idx_collab_status (status_code)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case collaboration between chambers';

-- ─────────────────────────────────────────────────────────────────────────────
-- 10.2  User Invitations  →  chamber, security_roles, users
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS user_invitations;
CREATE TABLE user_invitations (
    invitation_id CHAR(36)     PRIMARY KEY,  
    chamber_id    CHAR(36)     NOT NULL,  
    email         VARCHAR(150) NOT NULL,
    role_id       INT          NULL,  -- INT FK to security_roles
    invited_by    CHAR(36)     NOT NULL,  
    invited_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    expires_date  DATE         NULL,
    status_code   CHAR(4)      DEFAULT 'PN',
    message       TEXT         NULL,
    accepted_date TIMESTAMP    NULL,
    accepted_by   CHAR(36)     NULL,  
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by    CHAR(36)     NULL,  
    CONSTRAINT fk_inv_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)       ON DELETE CASCADE,
    CONSTRAINT fk_inv_role
        FOREIGN KEY (role_id)    REFERENCES security_roles(role_id)   ON DELETE SET NULL,
    CONSTRAINT fk_inv_invited_by
        FOREIGN KEY (invited_by) REFERENCES users(user_id)            ON DELETE CASCADE,
    CONSTRAINT fk_inv_accepted_by
        FOREIGN KEY (accepted_by) REFERENCES users(user_id)           ON DELETE SET NULL,
    CONSTRAINT fk_inv_created_by
        FOREIGN KEY (created_by)  REFERENCES users(user_id)           ON DELETE SET NULL,
    UNIQUE KEY uk_invitation_email_chamber (chamber_id, email, status_code),
    INDEX idx_inv_email (email),
    INDEX idx_inv_status (status_code),
    INDEX idx_inv_chamber (chamber_id)
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Pending user invitations';

-- =============================================================================
-- 11. TIER 11  —  Logging & Audit
--     →  chamber, users, refm_login_status, refm_email_templates, refm_email_status
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.1  Login Audit
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS login_audit;
CREATE TABLE login_audit (
    login_id       CHAR(36)     PRIMARY KEY,  
    user_id        CHAR(36)     NULL,  
    chamber_id     CHAR(36)     NOT NULL,  
    email          VARCHAR(120) NULL,
    status_code    CHAR(4)      NULL,
    failure_reason VARCHAR(255) NULL,
    login_time     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    ip_address     VARCHAR(45)  NULL,
    user_agent     TEXT         NULL,
    CONSTRAINT fk_login_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)             ON DELETE SET NULL,
    CONSTRAINT fk_login_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id)        ON DELETE CASCADE,
    CONSTRAINT fk_login_status
        FOREIGN KEY (status_code) REFERENCES refm_login_status(code)  ON DELETE SET NULL,
    INDEX idx_login_time (login_time DESC)
) ENGINE=InnoDB COMMENT='Login attempts log';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.2  DB Call Log
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS db_call_log;
CREATE TABLE db_call_log (
    id            CHAR(36)     PRIMARY KEY,  
    chamber_id    CHAR(36)     NULL,  
    user_id       CHAR(36)     NULL,  
    timestamp     DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    duration_ms   DOUBLE       NOT NULL,
    raw_query     LONGTEXT     NOT NULL,
    params        JSON         NULL,
    final_query   LONGTEXT     NULL,
    repo          VARCHAR(255) NULL,
    error         LONGTEXT     NULL,
    metadata_json JSON         NULL,
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by    CHAR(36)     NULL,  
    CONSTRAINT fk_db_log_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE SET NULL,
    CONSTRAINT fk_db_log_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)      ON DELETE SET NULL,
    CONSTRAINT fk_db_log_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)      ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='DB query log';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.3  Exception Log
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS exception_log;
CREATE TABLE exception_log (
    id             CHAR(36)     PRIMARY KEY,  
    chamber_id     CHAR(36)     NULL,  
    user_id        CHAR(36)     NULL,  
    timestamp      DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    exception_type VARCHAR(255) NOT NULL,
    message        LONGTEXT     NULL,
    stacktrace     LONGTEXT     NULL,
    path           VARCHAR(500) NULL,
    method         VARCHAR(10)  NULL,
    query_params   JSON         NULL,
    request_body   LONGTEXT     NULL,
    headers        JSON         NULL,
    error_code     VARCHAR(50)  NULL,
    metadata_json  JSON         NULL,
    created_date   TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by     CHAR(36)     NULL,  
    CONSTRAINT fk_exc_log_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE SET NULL,
    CONSTRAINT fk_exc_log_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)      ON DELETE SET NULL,
    CONSTRAINT fk_exc_log_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)      ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Application errors log';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.4  Activity Log
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS activity_log;
CREATE TABLE activity_log (
    id            CHAR(36)     PRIMARY KEY,  
    chamber_id    CHAR(36)     NOT NULL,  
    user_id       CHAR(36)     NULL,  
    timestamp     DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    action        VARCHAR(255) NOT NULL,
    target        VARCHAR(255) NULL,
    metadata_json JSON         NULL,
    ip_address    VARCHAR(45)  NULL,
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by    CHAR(36)     NULL,  
    CONSTRAINT fk_activity_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_activity_user
        FOREIGN KEY (user_id)    REFERENCES users(user_id)      ON DELETE SET NULL,
    CONSTRAINT fk_activity_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id)      ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='User actions audit';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.5  Email Log
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS email_log;
CREATE TABLE email_log (
    email_id        CHAR(36)     PRIMARY KEY,  
    chamber_id      CHAR(36)     NOT NULL,  
    user_id         CHAR(36)     NULL,  
    template_code   CHAR(30)     NULL,
    recipient_email VARCHAR(255) NOT NULL,
    recipient_name  VARCHAR(120) NULL,
    subject         VARCHAR(500) NULL,
    body_preview    TEXT         NULL,
    status_code     CHAR(4)      DEFAULT 'ESPN',
    sent_at         DATETIME(6)  NULL,
    delivered_at    DATETIME(6)  NULL,
    opened_at       DATETIME(6)  NULL,
    error_message   TEXT         NULL,
    retry_count     TINYINT UNSIGNED DEFAULT 0,
    next_retry_at   DATETIME     NULL,
    metadata_json   JSON         NULL,
    created_date    TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by      CHAR(36)     NULL,  
    CONSTRAINT fk_email_log_chamber
        FOREIGN KEY (chamber_id)    REFERENCES chamber(chamber_id)           ON DELETE CASCADE,
    CONSTRAINT fk_email_log_user
        FOREIGN KEY (user_id)       REFERENCES users(user_id)               ON DELETE SET NULL,
    CONSTRAINT fk_email_log_template
        FOREIGN KEY (template_code) REFERENCES refm_email_templates(code)  ON DELETE SET NULL,
    CONSTRAINT fk_email_log_status
        FOREIGN KEY (status_code)   REFERENCES refm_email_status(code)     ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Email delivery log';

-- =============================================================================
-- 12.  —  Deferred Foreign Keys & Performance Indexes
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 14.1  Restore chamber audit FKs (deferred from Section 4.1)
-- ─────────────────────────────────────────────────────────────────────────────

ALTER TABLE chamber
    ADD CONSTRAINT fk_chamber_created_by
        FOREIGN KEY (created_by)  REFERENCES users(user_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_chamber_updated_by
        FOREIGN KEY (updated_by)  REFERENCES users(user_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_chamber_deleted_by
        FOREIGN KEY (deleted_by)  REFERENCES users(user_id) ON DELETE SET NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- 14.2  Performance Indexes
-- ─────────────────────────────────────────────────────────────────────────────

-- Cases
CREATE INDEX idx_cases_status_hearing ON cases(status_code, next_hearing_date);
CREATE INDEX idx_cases_number ON cases(case_number);

-- Hearings
CREATE INDEX idx_hearings_date ON hearings(hearing_date);

-- Users
CREATE INDEX idx_users_email ON users(email);

-- User Chamber Links
CREATE INDEX idx_ucl_user_active ON user_chamber_link(user_id, status_ind, left_date);
CREATE INDEX idx_ucl_chamber_users ON user_chamber_link(chamber_id, primary_ind, status_ind);

-- User Roles
CREATE INDEX idx_user_roles_link_role ON user_roles(link_id, role_id, end_date);

-- Activity Log
CREATE INDEX idx_activity_chamber_time ON activity_log(chamber_id, timestamp DESC);

-- Email Log
CREATE INDEX idx_email_log_status      ON email_log(status_code, created_date);

SELECT '✅ Court Diary schema with UUID v7 created successfully!' AS status_message;

-- ===========================================================================
-- END OF SCHEMA & SEED DATA
-- ===========================================================================