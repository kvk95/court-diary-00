-- =============================================================================
-- COURT DIARY - FULL SCHEMA (Corrected & Production-Ready)
-- Unified style aligned with NYABUY POS conventions
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
-- 1. PURE REFERENCE / LOOKUP TABLES
-- (No or minimal dependencies)
-- =============================================================================

DROP TABLE IF EXISTS refm_countries;
CREATE TABLE refm_countries (
    code          CHAR(2) PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    phone_code    VARCHAR(8) NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Countries';

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

DROP TABLE IF EXISTS refm_hearing_status;
CREATE TABLE refm_hearing_status (
    code          CHAR(4) PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Hearing status';

DROP TABLE IF EXISTS refm_case_status;
CREATE TABLE refm_case_status (
    code          CHAR(4) PRIMARY KEY,
    description   VARCHAR(60) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case status';

DROP TABLE IF EXISTS refm_case_types;
CREATE TABLE refm_case_types (
    code          CHAR(4) PRIMARY KEY,
    description   VARCHAR(100) NOT NULL,
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Case types';

DROP TABLE IF EXISTS refm_modules;
CREATE TABLE refm_modules (
    code          CHAR(8) PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    description   TEXT NULL,
    sort_order    INT NOT NULL DEFAULT 0,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='System modules for permissions';

DROP TABLE IF EXISTS refm_plan_types;
CREATE TABLE refm_plan_types (
    code             CHAR(4) PRIMARY KEY,
    description      VARCHAR(60) NOT NULL,
    max_users        INT NULL,
    max_cases        INT NULL,
    price_monthly_amt DECIMAL(12,2) DEFAULT 0,
    price_annual_amt  DECIMAL(12,2) DEFAULT 0,
    currency_code    CHAR(3) DEFAULT 'INR',
    sort_order       INT NOT NULL,
    status_ind       BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Subscription plans';

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

DROP TABLE IF EXISTS refm_user_deletion_status;
CREATE TABLE refm_user_deletion_status (
    code          CHAR(1) PRIMARY KEY,
    description   VARCHAR(50) NOT NULL,
    color_code    CHAR(7) DEFAULT '#64748b',
    sort_order    INT NOT NULL,
    status_ind    BOOLEAN DEFAULT TRUE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Account deletion request statuses';


-- =============================================================================
-- 2. DEPENDENT REFERENCE TABLES
-- =============================================================================

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


-- =============================================================================
-- 3. CORE ENTITIES
-- NOTE: FKs to 'users' are deferred to Section 8 to avoid DDL order errors.
-- =============================================================================

DROP TABLE IF EXISTS chambers;
CREATE TABLE chambers (
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
    CONSTRAINT fk_chambers_state
        FOREIGN KEY (state_code) REFERENCES refm_states(code) ON DELETE RESTRICT,
    CONSTRAINT fk_chambers_country
        FOREIGN KEY (country_code) REFERENCES refm_countries(code) ON DELETE RESTRICT,
    CONSTRAINT fk_chambers_plan
        FOREIGN KEY (plan_code) REFERENCES refm_plan_types(code) ON DELETE RESTRICT
    -- FKs to users(user_id) for created_by/updated_by/deleted_by added in Section 8
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Law chamber / firm';

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    user_id             BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id          BIGINT NOT NULL,
    email               VARCHAR(120) NOT NULL,
    password_hash       VARCHAR(255) NOT NULL,
    first_name          VARCHAR(60) NOT NULL,
    last_name           VARCHAR(60) NULL,
    phone               VARCHAR(20) NULL,
    role_code           CHAR(4) DEFAULT 'MEMB',
    status_ind          BOOLEAN DEFAULT TRUE,
    is_deleted          BOOLEAN DEFAULT FALSE,
    deleted_date        TIMESTAMP NULL,
    deleted_by          BIGINT NULL,
    email_verified_ind  BOOLEAN DEFAULT FALSE,
    phone_verified_ind  BOOLEAN DEFAULT FALSE,
    two_factor_ind      BOOLEAN DEFAULT FALSE,
    google_auth_ind     BOOLEAN DEFAULT FALSE,
    last_login_date     TIMESTAMP NULL,
    password_changed_date TIMESTAMP NULL,
    created_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by          BIGINT NULL,
    updated_date        TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by          BIGINT NULL,
    CONSTRAINT uk_user_chamber_email
        UNIQUE KEY (chamber_id, email),
    CONSTRAINT fk_users_chamber
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_users_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_users_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Users (advocates, clerks, admins)';


-- =============================================================================
-- 4. SECURITY & PERMISSIONS
-- =============================================================================

DROP TABLE IF EXISTS security_roles;
CREATE TABLE security_roles (
    role_id         INT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
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
    CONSTRAINT uk_role_chamber_code
        UNIQUE KEY (chamber_id, role_code),
    CONSTRAINT fk_roles_chamber
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Roles per chamber';

DROP TABLE IF EXISTS user_roles;
CREATE TABLE user_roles (
    user_role_id    BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id         BIGINT NOT NULL,
    role_id         INT NOT NULL,
    start_date      DATE NOT NULL DEFAULT (CURRENT_DATE),
    end_date        DATE NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT uk_user_role_active
        UNIQUE KEY (user_id, role_id, start_date),
    CONSTRAINT fk_user_roles_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_user_roles_role
        FOREIGN KEY (role_id) REFERENCES security_roles(role_id) ON DELETE CASCADE
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='User ↔ Role mapping';

DROP TABLE IF EXISTS role_permissions;
CREATE TABLE role_permissions (
    permission_id   BIGINT AUTO_INCREMENT PRIMARY KEY,
    role_id         INT NOT NULL,
    module_code     CHAR(8) NOT NULL,
    allow_all_ind   BOOLEAN DEFAULT FALSE,
    read_ind        BOOLEAN DEFAULT TRUE,
    write_ind       BOOLEAN DEFAULT FALSE,
    create_ind      BOOLEAN DEFAULT FALSE,
    delete_ind      BOOLEAN DEFAULT FALSE,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT uk_role_module
        UNIQUE KEY (role_id, module_code),
    CONSTRAINT fk_role_permissions_role
        FOREIGN KEY (role_id) REFERENCES security_roles(role_id) ON DELETE CASCADE,
    CONSTRAINT fk_role_permissions_module
        FOREIGN KEY (module_code) REFERENCES refm_modules(code) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Role-module permissions';


-- =============================================================================
-- 5. CORE BUSINESS TABLES
-- =============================================================================

DROP TABLE IF EXISTS cases;
CREATE TABLE cases (
    case_id         BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    case_number     VARCHAR(120) NOT NULL,
    court_id        INT NOT NULL,
    case_type_code  CHAR(4) NULL,
    filing_year     INT NULL,
    petitioner      TEXT NOT NULL,
    respondent      TEXT NOT NULL,
    aor_user_id     BIGINT NULL,
    case_summary    TEXT NULL,
    status_code     CHAR(4) DEFAULT 'AC',
    next_hearing_date DATE NULL,
    last_hearing_date DATE NULL,
    is_deleted      BOOLEAN DEFAULT FALSE,
    deleted_date    TIMESTAMP NULL,
    deleted_by      BIGINT NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT uk_case_chamber_number
        UNIQUE KEY (chamber_id, case_number),
    CONSTRAINT fk_cases_chamber
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_cases_court
        FOREIGN KEY (court_id) REFERENCES refm_courts(court_id) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_type
        FOREIGN KEY (case_type_code) REFERENCES refm_case_types(code) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_status
        FOREIGN KEY (status_code) REFERENCES refm_case_status(code) ON DELETE RESTRICT,
    CONSTRAINT fk_cases_aor
        FOREIGN KEY (aor_user_id) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Legal cases';

DROP TABLE IF EXISTS hearings;
CREATE TABLE hearings (
    hearing_id      BIGINT AUTO_INCREMENT PRIMARY KEY,
    chamber_id      BIGINT NOT NULL,
    case_id         BIGINT NOT NULL,
    hearing_date    DATE NOT NULL,
    status_code     CHAR(4) DEFAULT 'UP',
    purpose         VARCHAR(255) NULL,
    notes           TEXT NULL,
    order_details   TEXT NULL,
    next_hearing_date DATE NULL,
    is_deleted      BOOLEAN DEFAULT FALSE,
    deleted_date    TIMESTAMP NULL,
    deleted_by      BIGINT NULL,
    created_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by      BIGINT NULL,
    updated_date    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    updated_by      BIGINT NULL,
    CONSTRAINT fk_hearings_chamber
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_hearings_case
        FOREIGN KEY (case_id) REFERENCES cases(case_id) ON DELETE CASCADE,
    CONSTRAINT fk_hearings_status
        FOREIGN KEY (status_code) REFERENCES refm_hearing_status(code) ON DELETE RESTRICT
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Court hearings';


-- =============================================================================
-- 6. CONFIGURATION & UTILITY TABLES
-- =============================================================================

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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_email_settings_encryption
        FOREIGN KEY (encryption_code) REFERENCES refm_email_encryption(code) ON DELETE RESTRICT,
    CONSTRAINT fk_email_settings_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_email_settings_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='SMTP settings per chamber';

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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_email_templates_code
        FOREIGN KEY (code) REFERENCES refm_email_templates(code) ON DELETE RESTRICT,
    CONSTRAINT fk_email_templates_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_email_templates_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL
) ENGINE=InnoDB ROW_FORMAT=DYNAMIC COMMENT='Custom email templates per chamber';

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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
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
-- 7. LOGGING & AUDIT
-- (Depend on users & chambers)
-- =============================================================================

-- =============================================================================
-- 7. LOGGING & AUDIT
-- (Depend on users & chambers)
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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE
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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE SET NULL,
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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE SET NULL,
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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
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
        FOREIGN KEY (chamber_id) REFERENCES chambers(chamber_id) ON DELETE CASCADE,
    CONSTRAINT fk_email_log_user
        FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE SET NULL,
    CONSTRAINT fk_email_log_template
        FOREIGN KEY (template_code) REFERENCES refm_email_templates(code) ON DELETE SET NULL,
    CONSTRAINT fk_email_log_status
        FOREIGN KEY (status_code) REFERENCES refm_email_status(code) ON DELETE SET NULL
) ENGINE=InnoDB COMMENT='Email delivery log';


-- =============================================================================
-- 8. POST-CREATION CONSTRAINTS & INDEXES
-- (Resolves circular dependencies and adds performance indexes)
-- =============================================================================

-- 8.1 Restore Deferred Foreign Keys on Chambers
-- (chambers.created_by/updated_by/deleted_by reference users, which didn't exist during chambers creation)
ALTER TABLE chambers
    ADD CONSTRAINT fk_chambers_created_by
        FOREIGN KEY (created_by) REFERENCES users(user_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_chambers_updated_by
        FOREIGN KEY (updated_by) REFERENCES users(user_id) ON DELETE SET NULL,
    ADD CONSTRAINT fk_chambers_deleted_by
        FOREIGN KEY (deleted_by) REFERENCES users(user_id) ON DELETE SET NULL;

-- 8.2 Performance Indexes

-- Cases: Common dashboard queries (Status + Date)
CREATE INDEX idx_cases_status_hearing ON cases(status_code, next_hearing_date);

-- Cases: Search by case number (partial match support if needed later)
CREATE INDEX idx_cases_number ON cases(case_number);

-- Hearings: Calendar views
CREATE INDEX idx_hearings_date ON hearings(hearing_date);

-- Activity Log: Audit trails per chamber
CREATE INDEX idx_activity_chamber_time ON activity_log(chamber_id, timestamp DESC);

-- Email Log: Delivery monitoring
CREATE INDEX idx_email_log_status ON email_log(status_code, created_date);

-- Users: Login lookup (if email is searched globally)
CREATE INDEX idx_users_email ON users(email);

SELECT '✅ courtdiary database created successfully!' AS status;

-- ===========================================================
-- END OF SCHEMA
-- ===========================================================