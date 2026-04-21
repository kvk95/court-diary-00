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
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='System modules for permissions';DROP TABLE IF EXISTS refm_ticket_status;

CREATE TABLE refm_ticket_status (
    code CHAR(4) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    sort_order INT NOT NULL DEFAULT 0,
    status_ind BOOLEAN NOT NULL DEFAULT TRUE,
    color_code VARCHAR(7) NULL DEFAULT '#6B7280' COMMENT 'Hex color for UI display'
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Reference table for Support Ticket Status';

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

DROP TABLE IF EXISTS refm_party_type;
CREATE TABLE refm_party_type (
    code        CHAR(4)     PRIMARY KEY,
    description VARCHAR(60) NOT NULL,
    sort_order  INT         NOT NULL,
    status_ind  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='How is the client/party related to chamber';

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

DROP TABLE IF EXISTS refm_email_templates;
CREATE TABLE refm_email_templates (
    code          CHAR(4)     PRIMARY KEY,
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

DROP TABLE IF EXISTS refm_img_upload_for;
CREATE TABLE refm_img_upload_for (
    code        CHAR(4)     PRIMARY KEY,
    description VARCHAR(60) NOT NULL,
    sort_order  INT         NOT NULL,
    status_ind  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Entity type master for images';

DROP TABLE IF EXISTS refm_proof_type;
CREATE TABLE refm_proof_type (
    code        CHAR(4)     PRIMARY KEY,
    description VARCHAR(60) NOT NULL,
    sort_order  INT         NOT NULL,
    status_ind  BOOLEAN     NOT NULL DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='type of id proof';

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
-- 3.2  refm_court_type
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS refm_court_type;
CREATE TABLE refm_court_type (
    court_code VARCHAR(4) PRIMARY KEY,
    description VARCHAR(50)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.3  refm_announcement
-- ─────────────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS refm_announcement_type;
CREATE TABLE refm_announcement_type (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50)
);

DROP TABLE IF EXISTS refm_announcement_audience;
CREATE TABLE refm_announcement_audience (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50)
);

DROP TABLE IF EXISTS refm_announcement_status;
CREATE TABLE refm_announcement_status (
    code VARCHAR(20) PRIMARY KEY,
    name VARCHAR(50)
);

-- ─────────────────────────────────────────────────────────────────────────────
-- 3.4  Courts  →  refm_court_type
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS courts;

CREATE TABLE courts (
    court_code VARCHAR(12) PRIMARY KEY,
    court_name VARCHAR(255) NOT NULL,
    state_code CHAR(2)      NULL,
    court_type_code VARCHAR(4) NOT NULL,
    parent_court_code VARCHAR(12) NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_courts_state
        FOREIGN KEY (state_code)   REFERENCES refm_states(code)      ON DELETE RESTRICT,
    CONSTRAINT fk_courts_type_code
		FOREIGN KEY (court_type_code) REFERENCES refm_court_type(court_code),
    CONSTRAINT code
		FOREIGN KEY (parent_court_code) REFERENCES courts(court_code)
);

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
    plan_code          CHAR(4)      DEFAULT 'PTFR',
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
	advocate_ind		  BOOLEAN      NOT NULL DEFAULT FALSE,
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
    chamber_module_id CHAR(36) PRIMARY KEY,

    chamber_id CHAR(36) NOT NULL,
    module_code CHAR(8) NOT NULL,

    active_ind BOOLEAN NOT NULL DEFAULT TRUE,
    deleted_ind BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP NULL,
    deleted_by CHAR(36) NULL,

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by CHAR(36) NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by CHAR(36) NULL,

    -- Constraints
    UNIQUE KEY uk_chamber_module (chamber_id, module_code),

    CONSTRAINT fk_cmodules_chamber
        FOREIGN KEY (chamber_id)
        REFERENCES chamber(chamber_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cmodules_module
        FOREIGN KEY (module_code)
        REFERENCES refm_modules(code)
        ON DELETE RESTRICT,

    -- 🔥 Audit FKs
    CONSTRAINT fk_cmodules_created_by 
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,

    CONSTRAINT fk_cmodules_updated_by 
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,

    CONSTRAINT fk_cmodules_deleted_by 
        FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL

) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Modules enabled per chamber';

-- =============================================================================
-- 6. TIER 4 — Roles (INT for security_roles, UUID v7 for others)
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 6.1  Security Roles  →  users (audit only) - Keep INT (small lookup table < 20 rows)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS security_roles;

CREATE TABLE security_roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,

    role_code VARCHAR(20) NOT NULL UNIQUE,
    role_name VARCHAR(80) NOT NULL,
    description TEXT NULL,

    system_ind BOOLEAN NOT NULL DEFAULT TRUE,
    admin_ind  BOOLEAN NOT NULL DEFAULT FALSE,
    status_ind BOOLEAN NOT NULL DEFAULT TRUE,

    deleted_ind BOOLEAN DEFAULT FALSE,
    deleted_date TIMESTAMP NULL,
    deleted_by CHAR(36) NULL,

    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by CHAR(36) NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by CHAR(36) NULL,

    CONSTRAINT uk_role_name UNIQUE (role_name),

    -- 🔥 AUDIT FKs
    CONSTRAINT fk_sroles_created_by FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_sroles_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_sroles_deleted_by FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL

) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Master role templates';


-- ─────────────────────────────────────────────────────────────────────────────
-- 6.1b Chamber Roles (Chamber-Specific Instances)
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS chamber_roles;

CREATE TABLE chamber_roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,

    chamber_id CHAR(36) NOT NULL,
    security_role_id INT NULL,
	role_code VARCHAR(20) NOT NULL,
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

    CONSTRAINT uk_chamber_role UNIQUE (chamber_id, role_name, role_code),

    CONSTRAINT fk_croles_security_role
        FOREIGN KEY (security_role_id)
        REFERENCES security_roles(role_id)
        ON DELETE SET NULL,

    -- 🔥 AUDIT FKs
    CONSTRAINT fk_croles_created_by FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_croles_updated_by FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_croles_deleted_by FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL

) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Chamber-specific roles';

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
-- 7.1  Role Permissions  →  security_roles, chamber_modules,role_permission_master, users
-- ─────────────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS role_permission_master;

CREATE TABLE role_permission_master (
    id INT AUTO_INCREMENT PRIMARY KEY,

    security_role_id INT NOT NULL,   -- ✅ FIXED

    module_code CHAR(8) NOT NULL,

    allow_all_ind BOOLEAN DEFAULT FALSE,
    read_ind BOOLEAN DEFAULT TRUE,
    write_ind BOOLEAN DEFAULT FALSE,
    create_ind BOOLEAN DEFAULT FALSE,
    delete_ind BOOLEAN DEFAULT FALSE,
    import_ind BOOLEAN DEFAULT FALSE,
    export_ind BOOLEAN DEFAULT FALSE,

    CONSTRAINT fk_rpm_role
        FOREIGN KEY (security_role_id)
        REFERENCES security_roles(role_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_rpm_module
        FOREIGN KEY (module_code)
        REFERENCES refm_modules(code)
        ON DELETE RESTRICT,

    UNIQUE KEY uk_rpm (security_role_id, module_code)

) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Default permissions per global role';

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.2  Role Permissions  →  security_roles, chamber_modules, users
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
--    →  chamber, courts, refm_case_types, refm_case_status, users
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 7.1  Cases
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS cases;

CREATE TABLE cases (
    case_id           CHAR(36)     PRIMARY KEY,

    chamber_id        CHAR(36)     NOT NULL,
    case_number       VARCHAR(120) NOT NULL,

    court_code        VARCHAR(12)  NOT NULL,

    case_type_code    CHAR(4)      NULL,
    filing_year       INT          NULL,

    petitioner        TEXT         NOT NULL,
    respondent        TEXT         NOT NULL,
    case_summary      TEXT         NULL,

    status_code       CHAR(4)      DEFAULT 'AC',

    next_hearing_date DATE         NULL,
    last_hearing_date DATE         NULL,

    deleted_ind       BOOLEAN      DEFAULT FALSE,
    deleted_date      TIMESTAMP    NULL,
    deleted_by        CHAR(36)     NULL,

    created_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    created_by        CHAR(36)     NULL,

    updated_date      TIMESTAMP    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by        CHAR(36)     NULL,

    CONSTRAINT uk_case_chamber_number
        UNIQUE KEY (chamber_id, case_number),

    CONSTRAINT fk_cases_chamber
        FOREIGN KEY (chamber_id)
        REFERENCES chamber(chamber_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_cases_court
        FOREIGN KEY (court_code)
        REFERENCES courts(court_code)
        ON DELETE RESTRICT,

    CONSTRAINT fk_cases_type
        FOREIGN KEY (case_type_code)
        REFERENCES refm_case_types(code)
        ON DELETE RESTRICT,

    CONSTRAINT fk_cases_status
        FOREIGN KEY (status_code)
        REFERENCES refm_case_status(code)
        ON DELETE RESTRICT,

    INDEX idx_cases_chamber_status (chamber_id, status_code),
    INDEX idx_cases_next_hearing (next_hearing_date),
    INDEX idx_cases_court (court_code)
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
    id_proof_code   CHAR(4)  NULL,
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
    CONSTRAINT fk_clients_id_proof_code
        FOREIGN KEY (id_proof_code) REFERENCES refm_proof_type(code)  ON DELETE RESTRICT,
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
	image_upload_code CHAR(4)   NOT NULL,
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
    CONSTRAINT fk_profile_images_upload_code
        FOREIGN KEY (image_upload_code) REFERENCES refm_img_upload_for(code)  ON DELETE RESTRICT,
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
-- 11. TIER 11  —  Logging & Audit
--     →  chamber, users, audit
-- =============================================================================

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.1  Login Audit
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS login_audit;
CREATE TABLE login_audit (
    login_id       CHAR(36)     PRIMARY KEY,   
    email          VARCHAR(120) NULL,
    status_code    CHAR(4)      NULL,
    failure_reason VARCHAR(255) NULL,
    login_time     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    user_agent     TEXT         NULL,
    actor_user_id        CHAR(36)     NULL,  
    actor_chamber_id     CHAR(36)     NULL,
    ip_address     VARCHAR(45)  NULL, 
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_login_user
        FOREIGN KEY (actor_user_id)    REFERENCES users(user_id)             ON DELETE CASCADE,
    CONSTRAINT fk_login_chamber
        FOREIGN KEY (actor_chamber_id) REFERENCES chamber(chamber_id)        ON DELETE CASCADE,
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
    timestamp     DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    duration_ms   DOUBLE       NOT NULL,
    raw_query     LONGTEXT     NOT NULL,
    params        JSON         NULL,
    final_query   LONGTEXT     NULL,
    repo          VARCHAR(255) NULL,
    error         LONGTEXT     NULL,
    metadata_json JSON         NULL,
    actor_user_id        CHAR(36)     NULL,  
    actor_chamber_id     CHAR(36)     NULL, 
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_db_log_chamber
        FOREIGN KEY (actor_chamber_id) REFERENCES chamber(chamber_id) ON DELETE SET NULL,
    CONSTRAINT fk_db_log_user
        FOREIGN KEY (actor_user_id)    REFERENCES users(user_id)      ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='DB query log';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.3  Exception Log
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS exception_log;
CREATE TABLE exception_log (
    id             CHAR(36)     PRIMARY KEY,  
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
    actor_user_id        CHAR(36)     NULL,  
    actor_chamber_id     CHAR(36)     NULL, 
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_exc_log_chamber
        FOREIGN KEY (actor_chamber_id) REFERENCES chamber(chamber_id) ON DELETE SET NULL,
    CONSTRAINT fk_exc_log_user
        FOREIGN KEY (actor_user_id)    REFERENCES users(user_id)      ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Application errors log';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.4  Activity Log
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS activity_log;
CREATE TABLE activity_log (
    id            CHAR(36)     PRIMARY KEY, 
    timestamp     DATETIME(6)  NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    action        VARCHAR(255) NOT NULL,
    target        VARCHAR(255) NULL,
    metadata_json JSON         NULL,
    ip_address    VARCHAR(45)  NULL,  
    actor_chamber_id    CHAR(36)     NULL,  
    actor_user_id       CHAR(36)     NULL, 
    created_date  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_activity_chamber
        FOREIGN KEY (actor_chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_activity_user
        FOREIGN KEY (actor_user_id)    REFERENCES users(user_id)      ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='User actions audit';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.5  Email link
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS email_link;

CREATE TABLE email_link (
    link_id          CHAR(36) PRIMARY KEY,

    user_id          CHAR(36) NOT NULL,
    recipient_email  VARCHAR(120) NOT NULL,

    template_code    CHAR(4) NOT NULL,

    link_url         VARCHAR(1000),

    is_used          BOOLEAN DEFAULT FALSE,
    expiry_date      TIMESTAMP NULL,

    created_date     TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT fk_email_link_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id)
        ON DELETE CASCADE,

    CONSTRAINT fk_email_link_template
        FOREIGN KEY (template_code)
        REFERENCES refm_email_templates(code)
        ON DELETE RESTRICT

) ENGINE=InnoDB;

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.6  Global Settings
-- ─────────────────────────────────────────────────────────────────────────────
DROP TABLE IF EXISTS global_settings;

CREATE TABLE global_settings (
    settings_id     TINYINT PRIMARY KEY DEFAULT 1,

    -- 🎨 Branding
    platform_name   VARCHAR(150) NOT NULL,
    company_name    VARCHAR(150) NOT NULL,
    support_email   VARCHAR(150) NOT NULL,
    primary_color   VARCHAR(20)  NOT NULL,

    -- 📧 Email (SMTP)
    smtp_host       VARCHAR(255) NULL,
	smtp_user_name  VARCHAR(255) NULL,
	smtp_password   VARCHAR(255) NULL,
	smtp_use_tls    BOOLEAN DEFAULT TRUE,
    smtp_port       INT NULL,

    -- 📱 SMS
    sms_provider    VARCHAR(100) NULL,
    sms_api_key     TEXT NULL,

    -- ⚙️ Maintenance
    maintenance_enabled BOOLEAN DEFAULT FALSE,
    maintenance_start   TIMESTAMP NULL,
    maintenance_end     TIMESTAMP NULL,

    -- 🚀 Feature Flags
    allow_user_registration   BOOLEAN DEFAULT TRUE,
    enable_case_collaboration BOOLEAN DEFAULT TRUE,
    enable_reports_module     BOOLEAN DEFAULT TRUE,
    enable_api_rate_limit     BOOLEAN DEFAULT TRUE,

    -- 🧾 AUDIT
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      CHAR(36) NULL,

    updated_date    TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    updated_by      CHAR(36) NULL,

    -- 🔗 FK
    CONSTRAINT fk_global_settings_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_global_settings_updated_by
        FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    -- 🔒 Singleton enforcement
    CONSTRAINT chk_single_row CHECK (settings_id = 1)
) ENGINE=InnoDB COMMENT='Global platform configuration';

-- ─────────────────────────────────────────────────────────────────────────────
-- 11.7  Support Ticket
-- ─────────────────────────────────────────────────────────────────────────────

DROP TABLE IF EXISTS support_tickets;

CREATE TABLE support_tickets (
    ticket_id CHAR(36) PRIMARY KEY,
    chamber_id CHAR(36) NOT NULL,
    
    -- Ticket Identification
    ticket_number VARCHAR(50) NOT NULL,
    subject VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    
    -- Module Reference (which module the ticket belongs to)
    module_code CHAR(8) NULL,
    
    -- Status (using new refm_ticket_status)
    status_code CHAR(4) NOT NULL DEFAULT 'OPEN',
    
    -- Priority & Severity
    priority_code CHAR(4) NULL DEFAULT 'MEDI' COMMENT 'LOW, MEDI, HIGH, URGT',
    
    -- Assignment
    assigned_to CHAR(36) NULL,           -- user_id
    reported_by CHAR(36) NOT NULL,       -- user_id who raised the ticket
    
    -- Dates
    reported_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    assigned_date TIMESTAMP NULL,
    resolved_date TIMESTAMP NULL,
    due_date DATE NULL,
    
    -- Soft Delete & Audit
    deleted_ind BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_date TIMESTAMP NULL,
    deleted_by CHAR(36) NULL,
    
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by CHAR(36) NULL,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by CHAR(36) NULL,

    -- Constraints
    CONSTRAINT uk_ticket_chamber_number 
        UNIQUE KEY (chamber_id, ticket_number),
    
    CONSTRAINT fk_support_tickets_chamber
        FOREIGN KEY (chamber_id) REFERENCES chamber(chamber_id) ON DELETE CASCADE,
    
    CONSTRAINT fk_support_tickets_module
        FOREIGN KEY (module_code) REFERENCES refm_modules(code) ON DELETE SET NULL,
    
    CONSTRAINT fk_support_tickets_status
        FOREIGN KEY (status_code) REFERENCES refm_ticket_status(code) ON DELETE RESTRICT,
    
    CONSTRAINT fk_support_tickets_reported_by
        FOREIGN KEY (reported_by) REFERENCES users(user_id) ON DELETE RESTRICT,
    
    CONSTRAINT fk_support_tickets_assigned_to
        FOREIGN KEY (assigned_to) REFERENCES users(user_id) ON DELETE SET NULL,
    
    -- Indexes for performance
    INDEX idx_tickets_chamber_status (chamber_id, status_code),
    INDEX idx_tickets_reported_by (reported_by),
    INDEX idx_tickets_assigned_to (assigned_to),
    INDEX idx_tickets_module (module_code),
    INDEX idx_tickets_reported_date (reported_date DESC),
    INDEX idx_tickets_due_date (due_date)
    
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Support Ticket Management System';

DROP TABLE IF EXISTS contact_messages;

CREATE TABLE contact_messages (
    message_id      BIGINT PRIMARY KEY AUTO_INCREMENT,

    full_name       VARCHAR(150) NOT NULL,
    email           VARCHAR(150) NOT NULL,
    subject         VARCHAR(255),
    message         TEXT NOT NULL,
    
    status_code     CHAR(4) NOT NULL DEFAULT 'OPEN',

    chamber_id      CHAR(36) NULL,
    audit_user_id   CHAR(36) NULL,

    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    deleted_ind     BOOLEAN DEFAULT FALSE,
    deleted_date    TIMESTAMP NULL,
    deleted_by      CHAR(36) NULL,

    CONSTRAINT fk_contact_messages_status
        FOREIGN KEY (status_code)
        REFERENCES refm_ticket_status(code)
        ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='contact messages';

DROP TABLE IF EXISTS announcements;

CREATE TABLE announcements (
    announcement_id CHAR(36) PRIMARY KEY,

    title           VARCHAR(255) NOT NULL,
    content         TEXT NOT NULL,

    type_code       VARCHAR(20) NOT NULL,
    audience_code   VARCHAR(20) NOT NULL,
    status_code     VARCHAR(20) NOT NULL,

    scheduled_at    TIMESTAMP NULL,
    expires_at      TIMESTAMP NULL,

    -- ✅ AUDIT
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      CHAR(36) NULL,

    updated_date    TIMESTAMP NULL DEFAULT NULL ON UPDATE CURRENT_TIMESTAMP,
    updated_by      CHAR(36) NULL,
	
	deleted_ind BOOLEAN DEFAULT FALSE,
	deleted_date TIMESTAMP NULL,
	deleted_by CHAR(36) NULL,

    -- 🔗 FK: USERS (audit)
    CONSTRAINT fk_ann_created_by
        FOREIGN KEY (created_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    CONSTRAINT fk_ann_updated_by
        FOREIGN KEY (updated_by)
        REFERENCES users(user_id)
        ON DELETE SET NULL,

    -- 🔗 FK: TYPE
    CONSTRAINT fk_ann_type
        FOREIGN KEY (type_code)
        REFERENCES refm_announcement_type(code)
        ON DELETE RESTRICT,

    -- 🔗 FK: AUDIENCE
    CONSTRAINT fk_ann_audience
        FOREIGN KEY (audience_code)
        REFERENCES refm_announcement_audience(code)
        ON DELETE RESTRICT,

    -- 🔗 FK: STATUS
    CONSTRAINT fk_ann_status
        FOREIGN KEY (status_code)
        REFERENCES refm_announcement_status(code)
        ON DELETE RESTRICT,
		
	CONSTRAINT fk_ann_deleted_by
		FOREIGN KEY (deleted_by)
		REFERENCES users(user_id)
		ON DELETE SET NULL,

    -- ✅ VALIDATION CHECKS
    CONSTRAINT chk_schedule_dates
        CHECK (
            scheduled_at IS NULL 
            OR expires_at IS NULL 
            OR scheduled_at < expires_at
        ),
		
	INDEX idx_ann_status (status_code),
	INDEX idx_ann_schedule (scheduled_at),
	INDEX idx_ann_expiry (expires_at)

) ENGINE=InnoDB ROW_FORMAT=DYNAMIC 
COMMENT='System announcements & notifications';


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
CREATE INDEX idx_activity_chamber_time ON activity_log(actor_chamber_id, timestamp DESC);


SELECT '✅ Court Diary schema with UUID v7 created successfully!' AS status_message;

-- ===========================================================================
-- END OF SCHEMA & SEED DATA
-- ===========================================================================