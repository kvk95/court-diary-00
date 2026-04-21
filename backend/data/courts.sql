-- ─────────────────────────────────────────────────────────────────────────────
-- 15.1  Geographic
-- ─────────────────────────────────────────────────────────────────────────────

INSERT IGNORE INTO refm_countries (code, description, phone_code, sort_order) VALUES
('IN  ', 'India', '+91', 1);

-- =============================================================================
-- 16. SEED DATA — TIER 1  (REFM with FK to other REFM)
-- =============================================================================

INSERT INTO refm_states (code, description, country_code, sort_order) 
SELECT code, description, country_code, sort_order FROM (
  VALUES 
    -- 28 STATES ─────────────────────────────────────────────
    ROW('AP', 'Andhra Pradesh',              'IN', 1),
    ROW('AR', 'Arunachal Pradesh',           'IN', 2),
    ROW('AS', 'Assam',                       'IN', 3),
    ROW('BR', 'Bihar',                       'IN', 4),
    ROW('CG', 'Chhattisgarh',                'IN', 5),
    ROW('GA', 'Goa',                         'IN', 6),
    ROW('GJ', 'Gujarat',                     'IN', 7),
    ROW('HR', 'Haryana',                     'IN', 8),
    ROW('HP', 'Himachal Pradesh',            'IN', 9),
    ROW('JH', 'Jharkhand',                   'IN', 10),
    ROW('KA', 'Karnataka',                   'IN', 11),
    ROW('KL', 'Kerala',                      'IN', 12),
    ROW('MP', 'Madhya Pradesh',              'IN', 13),
    ROW('MH', 'Maharashtra',                 'IN', 14),
    ROW('MN', 'Manipur',                     'IN', 15),
    ROW('ML', 'Meghalaya',                   'IN', 16),
    ROW('MZ', 'Mizoram',                     'IN', 17),
    ROW('NL', 'Nagaland',                    'IN', 18),
    ROW('OD', 'Odisha',                      'IN', 19),
    ROW('PB', 'Punjab',                      'IN', 20),
    ROW('RJ', 'Rajasthan',                   'IN', 21),
    ROW('SK', 'Sikkim',                      'IN', 22),
    ROW('TN', 'Tamil Nadu',                  'IN', 23),
    ROW('TS', 'Telangana',                   'IN', 24),
    ROW('TR', 'Tripura',                     'IN', 25),
    ROW('UP', 'Uttar Pradesh',               'IN', 26),
    ROW('UK', 'Uttarakhand',                 'IN', 27),
    ROW('WB', 'West Bengal',                 'IN', 28),
    
    -- 8 UNION TERRITORIES ───────────────────────────────────
    ROW('AN', 'Andaman & Nicobar Islands',   'IN', 29),
    ROW('CH', 'Chandigarh',                  'IN', 30),
    ROW('DN', 'Dadra & Nagar Haveli and Daman & Diu', 'IN', 31),
    ROW('DL', 'Delhi (NCT)',                 'IN', 32),
    ROW('JK', 'Jammu & Kashmir',             'IN', 33),
    ROW('LA', 'Ladakh',                      'IN', 34),
    ROW('LD', 'Lakshadweep',                 'IN', 35),
    ROW('PY', 'Puducherry',                  'IN', 36)
) AS new_states(code, description, country_code, sort_order)
WHERE NOT EXISTS (
    SELECT 1 FROM refm_states r WHERE r.code = new_states.code
);

INSERT INTO refm_court_type (court_code, description) VALUES 
('HIGH', 'High Court'),
('TRIB', 'Tribunal'),
('SPEC', 'Special Court'),
('MAGI', 'Magistrate'),
('CIVI', 'Civil Court'),
('DIST', 'District Court'),
('FAMI', 'Family Court'),
('SUPR', 'Supreme Court');


-- ============================================================
--  indian_courts.sql
--  Complete court reference data for India
--  Covers: Supreme Court, 25 High Courts, District Courts
--          across all States and Union Territories
--  State codes: 2-char ISO 3166-2:IN abbreviations
--  sort_order: HC=10, City Civil=20, District=30-xxx, Family=500,
--              Magistrate=600, Tribunal=700
--  Generated: April 2026
-- ============================================================

-- ============================================================
--  SUPREME COURT OF INDIA
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES 
('SUPR001', 'Supreme Court of India', 'DL', 'SUPR', NULL);

-- ============================================================
--  ANDHRA PRADESH  (AP)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES 
('HCAP001', 'Andhra Pradesh High Court', 'AP', 'HIGH', NULL),
('DCAP020', 'Principal District Court, Anantapur', 'AP', 'DIST', 'HCAP001'),
('DCAP030', 'Principal District Court, Chittoor', 'AP', 'DIST', 'HCAP001'),
('DCAP040', 'Principal District Court, East Godavari', 'AP', 'DIST', 'HCAP001'),
('DCAP050', 'Principal District Court, Guntur', 'AP', 'DIST', 'HCAP001'),
('DCAP060', 'Principal District Court, Krishna', 'AP', 'DIST', 'HCAP001'),
('DCAP070', 'Principal District Court, Kurnool', 'AP', 'DIST', 'HCAP001'),
('DCAP080', 'Principal District Court, Nellore', 'AP', 'DIST', 'HCAP001'),
('DCAP090', 'Principal District Court, Prakasam', 'AP', 'DIST', 'HCAP001'),
('DCAP100', 'Principal District Court, Srikakulam', 'AP', 'DIST', 'HCAP001'),
('DCAP110', 'Principal District Court, Visakhapatnam', 'AP', 'DIST', 'HCAP001'),
('DCAP120', 'Principal District Court, Vizianagaram', 'AP', 'DIST', 'HCAP001'),
('DCAP130', 'Principal District Court, West Godavari', 'AP', 'DIST', 'HCAP001'),
('DCAP140', 'Principal District Court, YSR Kadapa', 'AP', 'DIST', 'HCAP001'),
('FCAP500', 'Family Court, Vijayawada', 'AP', 'FAMI', 'HCAP001'),
('FCAP510', 'Family Court, Visakhapatnam', 'AP', 'FAMI', 'HCAP001');

-- ============================================================
--  ARUNACHAL PRADESH  (AR)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES 
('HCAR001', 'Gauhati High Court – Itanagar Permanent Bench', 'AR', 'HIGH', NULL),
('DCAR020', 'District & Sessions Court, Itanagar', 'AR', 'DIST', 'HCAR001'),
('DCAR030', 'District & Sessions Court, Naharlagun', 'AR', 'DIST', 'HCAR001'),
('DCAR040', 'District & Sessions Court, Pasighat', 'AR', 'DIST', 'HCAR001'),
('DCAR050', 'District & Sessions Court, Tezpur (Sonitpur)', 'AR', 'DIST', 'HCAR001');

-- ============================================================
--  ASSAM  (AS)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES 
('HCAS001', 'Gauhati High Court', 'AS', 'HIGH', NULL),
('DCAS020', 'District & Sessions Court, Baksa', 'AS', 'DIST', 'HCAS001'),
('DCAS030', 'District & Sessions Court, Barpeta', 'AS', 'DIST', 'HCAS001'),
('DCAS040', 'District & Sessions Court, Biswanath', 'AS', 'DIST', 'HCAS001'),
('DCAS050', 'District & Sessions Court, Bongaigaon', 'AS', 'DIST', 'HCAS001'),
('DCAS060', 'District & Sessions Court, Cachar', 'AS', 'DIST', 'HCAS001'),
('DCAS070', 'District & Sessions Court, Charaideo', 'AS', 'DIST', 'HCAS001'),
('DCAS080', 'District & Sessions Court, Chirang', 'AS', 'DIST', 'HCAS001'),
('DCAS090', 'District & Sessions Court, Darrang', 'AS', 'DIST', 'HCAS001'),
('DCAS100', 'District & Sessions Court, Dhemaji', 'AS', 'DIST', 'HCAS001'),
('DCAS110', 'District & Sessions Court, Dhubri', 'AS', 'DIST', 'HCAS001'),
('DCAS120', 'District & Sessions Court, Dibrugarh', 'AS', 'DIST', 'HCAS001'),
('DCAS130', 'District & Sessions Court, Dima Hasao', 'AS', 'DIST', 'HCAS001'),
('DCAS140', 'District & Sessions Court, Goalpara', 'AS', 'DIST', 'HCAS001'),
('DCAS150', 'District & Sessions Court, Golaghat', 'AS', 'DIST', 'HCAS001'),
('DCAS160', 'District & Sessions Court, Hailakandi', 'AS', 'DIST', 'HCAS001'),
('DCAS170', 'District & Sessions Court, Hojai', 'AS', 'DIST', 'HCAS001'),
('DCAS180', 'District & Sessions Court, Jorhat', 'AS', 'DIST', 'HCAS001'),
('DCAS190', 'District & Sessions Court, Kamrup', 'AS', 'DIST', 'HCAS001'),
('DCAS200', 'District & Sessions Court, Kamrup Metro (Guwahati)', 'AS', 'DIST', 'HCAS001'),
('DCAS210', 'District & Sessions Court, Karbi Anglong', 'AS', 'DIST', 'HCAS001'),
('DCAS220', 'District & Sessions Court, Karimganj', 'AS', 'DIST', 'HCAS001'),
('DCAS230', 'District & Sessions Court, Kokrajhar', 'AS', 'DIST', 'HCAS001'),
('DCAS240', 'District & Sessions Court, Lakhimpur', 'AS', 'DIST', 'HCAS001'),
('DCAS250', 'District & Sessions Court, Majuli', 'AS', 'DIST', 'HCAS001'),
('DCAS260', 'District & Sessions Court, Morigaon', 'AS', 'DIST', 'HCAS001'),
('DCAS270', 'District & Sessions Court, Nagaon', 'AS', 'DIST', 'HCAS001'),
('DCAS280', 'District & Sessions Court, Nalbari', 'AS', 'DIST', 'HCAS001'),
('DCAS290', 'District & Sessions Court, Sivasagar', 'AS', 'DIST', 'HCAS001'),
('DCAS300', 'District & Sessions Court, Sonitpur', 'AS', 'DIST', 'HCAS001'),
('DCAS310', 'District & Sessions Court, South Salmara', 'AS', 'DIST', 'HCAS001'),
('DCAS320', 'District & Sessions Court, Tinsukia', 'AS', 'DIST', 'HCAS001'),
('DCAS330', 'District & Sessions Court, Udalguri', 'AS', 'DIST', 'HCAS001'),
('DCAS340', 'District & Sessions Court, West Karbi Anglong', 'AS', 'DIST', 'HCAS001'),
('FCAS500', 'Family Court, Guwahati', 'AS', 'FAMI', 'HCAS001');

-- ============================================================
--  BIHAR  (BR)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES 
('HCBR001', 'Patna High Court', 'BR', 'HIGH', NULL),
('DCBR020', 'District & Sessions Court, Araria', 'BR', 'DIST', 'HCBR001'),
('DCBR030', 'District & Sessions Court, Aurangabad', 'BR', 'DIST', 'HCBR001'),
('DCBR040', 'District & Sessions Court, Banka', 'BR', 'DIST', 'HCBR001'),
('DCBR050', 'District & Sessions Court, Begusarai', 'BR', 'DIST', 'HCBR001'),
('DCBR060', 'District & Sessions Court, Bhagalpur', 'BR', 'DIST', 'HCBR001'),
('DCBR070', 'District & Sessions Court, Bhojpur', 'BR', 'DIST', 'HCBR001'),
('DCBR080', 'District & Sessions Court, Buxar', 'BR', 'DIST', 'HCBR001'),
('DCBR090', 'District & Sessions Court, Darbhanga', 'BR', 'DIST', 'HCBR001'),
('DCBR100', 'District & Sessions Court, East Champaran', 'BR', 'DIST', 'HCBR001'),
('DCBR110', 'District & Sessions Court, Gaya', 'BR', 'DIST', 'HCBR001'),
('DCBR120', 'District & Sessions Court, Gopalganj', 'BR', 'DIST', 'HCBR001'),
('DCBR130', 'District & Sessions Court, Jamui', 'BR', 'DIST', 'HCBR001'),
('DCBR140', 'District & Sessions Court, Jehanabad', 'BR', 'DIST', 'HCBR001'),
('DCBR150', 'District & Sessions Court, Kaimur', 'BR', 'DIST', 'HCBR001'),
('DCBR160', 'District & Sessions Court, Katihar', 'BR', 'DIST', 'HCBR001'),
('DCBR170', 'District & Sessions Court, Khagaria', 'BR', 'DIST', 'HCBR001'),
('DCBR180', 'District & Sessions Court, Kishanganj', 'BR', 'DIST', 'HCBR001'),
('DCBR190', 'District & Sessions Court, Lakhisarai', 'BR', 'DIST', 'HCBR001'),
('DCBR200', 'District & Sessions Court, Madhepura', 'BR', 'DIST', 'HCBR001'),
('DCBR210', 'District & Sessions Court, Madhubani', 'BR', 'DIST', 'HCBR001'),
('DCBR220', 'District & Sessions Court, Munger', 'BR', 'DIST', 'HCBR001'),
('DCBR230', 'District & Sessions Court, Muzaffarpur', 'BR', 'DIST', 'HCBR001'),
('DCBR240', 'District & Sessions Court, Nalanda', 'BR', 'DIST', 'HCBR001'),
('DCBR250', 'District & Sessions Court, Nawada', 'BR', 'DIST', 'HCBR001'),
('DCBR260', 'District & Sessions Court, Patna', 'BR', 'DIST', 'HCBR001'),
('DCBR270', 'District & Sessions Court, Purnea', 'BR', 'DIST', 'HCBR001'),
('DCBR280', 'District & Sessions Court, Rohtas', 'BR', 'DIST', 'HCBR001'),
('DCBR290', 'District & Sessions Court, Saharsa', 'BR', 'DIST', 'HCBR001'),
('DCBR300', 'District & Sessions Court, Samastipur', 'BR', 'DIST', 'HCBR001'),
('DCBR310', 'District & Sessions Court, Saran', 'BR', 'DIST', 'HCBR001'),
('DCBR320', 'District & Sessions Court, Sheikhpura', 'BR', 'DIST', 'HCBR001'),
('DCBR330', 'District & Sessions Court, Sheohar', 'BR', 'DIST', 'HCBR001'),
('DCBR340', 'District & Sessions Court, Sitamarhi', 'BR', 'DIST', 'HCBR001'),
('DCBR350', 'District & Sessions Court, Siwan', 'BR', 'DIST', 'HCBR001'),
('DCBR360', 'District & Sessions Court, Supaul', 'BR', 'DIST', 'HCBR001'),
('DCBR370', 'District & Sessions Court, Vaishali', 'BR', 'DIST', 'HCBR001'),
('DCBR380', 'District & Sessions Court, West Champaran', 'BR', 'DIST', 'HCBR001'),
('FCBR500', 'Family Court, Patna', 'BR', 'FAMI', 'HCBR001');

-- ============================================================
--  CHHATTISGARH  (CG)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCCG001', 'Chhattisgarh High Court', 'CG', 'HIGH', NULL),
('DCCG020', 'District & Sessions Court, Balod', 'CG', 'DIST', 'HCCG001'),
('DCCG030', 'District & Sessions Court, Baloda Bazar', 'CG', 'DIST', 'HCCG001'),
('DCCG040', 'District & Sessions Court, Balrampur', 'CG', 'DIST', 'HCCG001'),
('DCCG050', 'District & Sessions Court, Bastar', 'CG', 'DIST', 'HCCG001'),
('DCCG060', 'District & Sessions Court, Bemetara', 'CG', 'DIST', 'HCCG001'),
('DCCG070', 'District & Sessions Court, Bijapur', 'CG', 'DIST', 'HCCG001'),
('DCCG080', 'District & Sessions Court, Bilaspur', 'CG', 'DIST', 'HCCG001'),
('DCCG090', 'District & Sessions Court, Dantewada', 'CG', 'DIST', 'HCCG001'),
('DCCG100', 'District & Sessions Court, Dhamtari', 'CG', 'DIST', 'HCCG001'),
('DCCG110', 'District & Sessions Court, Durg', 'CG', 'DIST', 'HCCG001'),
('DCCG120', 'District & Sessions Court, Gariaband', 'CG', 'DIST', 'HCCG001'),
('DCCG130', 'District & Sessions Court, Gaurela-Pendra-Marwahi', 'CG', 'DIST', 'HCCG001'),
('DCCG140', 'District & Sessions Court, Janjgir-Champa', 'CG', 'DIST', 'HCCG001'),
('DCCG150', 'District & Sessions Court, Jashpur', 'CG', 'DIST', 'HCCG001'),
('DCCG160', 'District & Sessions Court, Kabirdham', 'CG', 'DIST', 'HCCG001'),
('DCCG170', 'District & Sessions Court, Kanker', 'CG', 'DIST', 'HCCG001'),
('DCCG180', 'District & Sessions Court, Kondagaon', 'CG', 'DIST', 'HCCG001'),
('DCCG190', 'District & Sessions Court, Korba', 'CG', 'DIST', 'HCCG001'),
('DCCG200', 'District & Sessions Court, Koriya', 'CG', 'DIST', 'HCCG001'),
('DCCG210', 'District & Sessions Court, Mahasamund', 'CG', 'DIST', 'HCCG001'),
('DCCG220', 'District & Sessions Court, Mungeli', 'CG', 'DIST', 'HCCG001'),
('DCCG230', 'District & Sessions Court, Narayanpur', 'CG', 'DIST', 'HCCG001'),
('DCCG240', 'District & Sessions Court, Raigarh', 'CG', 'DIST', 'HCCG001'),
('DCCG250', 'District & Sessions Court, Raipur', 'CG', 'DIST', 'HCCG001'),
('DCCG260', 'District & Sessions Court, Rajnandgaon', 'CG', 'DIST', 'HCCG001'),
('DCCG270', 'District & Sessions Court, Sukma', 'CG', 'DIST', 'HCCG001'),
('DCCG280', 'District & Sessions Court, Surajpur', 'CG', 'DIST', 'HCCG001'),
('DCCG290', 'District & Sessions Court, Surguja', 'CG', 'DIST', 'HCCG001'),
('FCCG500', 'Family Court, Raipur', 'CG', 'FAMI', 'HCCG001');

-- ============================================================
--  GOA  (GA)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCGA001', 'Bombay High Court – Goa Bench', 'GA', 'HIGH', NULL),
('DCGA020', 'District & Sessions Court, North Goa', 'GA', 'DIST', 'HCGA001'),
('DCGA030', 'District & Sessions Court, South Goa', 'GA', 'DIST', 'HCGA001'),
('FCGA500', 'Family Court, Panaji', 'GA', 'FAMI', 'HCGA001');

-- ============================================================
--  GUJARAT  (GJ)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCGJ001', 'Gujarat High Court', 'GJ', 'HIGH', NULL),
('CIVIGJ020', 'City Civil & Sessions Court, Ahmedabad', 'GJ', 'CIVI', 'HCGJ001'),
('MAGIGJ025', 'Chief Judicial Magistrate Court, Ahmedabad', 'GJ', 'MAGI', 'HCGJ001'),
('CIVIGJ028', 'Small Causes Court, Ahmedabad', 'GJ', 'CIVI', 'HCGJ001'),
('DCGJ030', 'District Court, Ahmedabad Rural', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ040', 'District Court, Amreli', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ050', 'District Court, Anand', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ060', 'District Court, Aravalli', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ070', 'District Court, Banaskantha', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ080', 'District Court, Bharuch', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ090', 'District Court, Bhavnagar', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ100', 'District Court, Botad', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ110', 'District Court, Chhota Udepur', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ120', 'District Court, Dahod', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ130', 'District Court, Dang', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ140', 'District Court, Devbhumi Dwarka', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ150', 'District Court, Gandhinagar', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ160', 'District Court, Gir Somnath', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ170', 'District Court, Jamnagar', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ180', 'District Court, Junagadh', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ190', 'District Court, Kheda', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ200', 'District Court, Kutch', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ210', 'District Court, Mahisagar', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ220', 'District Court, Mehsana', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ230', 'District Court, Morbi', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ240', 'District Court, Narmada', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ250', 'District Court, Navsari', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ260', 'District Court, Panchmahals', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ270', 'District Court, Patan', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ280', 'District Court, Porbandar', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ290', 'District Court, Rajkot', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ300', 'District Court, Sabarkantha', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ310', 'District Court, Surat', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ320', 'District Court, Surendranagar', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ330', 'District Court, Tapi', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ340', 'District Court, Vadodara', 'GJ', 'DIST', 'HCGJ001'),
('DCGJ350', 'District Court, Valsad', 'GJ', 'DIST', 'HCGJ001'),
('FCGJ500', 'Family Court, Ahmedabad', 'GJ', 'FAMI', 'HCGJ001'),
('FCGJ510', 'Family Court, Surat', 'GJ', 'FAMI', 'HCGJ001'),
('FCGJ520', 'Family Court, Vadodara', 'GJ', 'FAMI', 'HCGJ001');

-- ============================================================
--  HARYANA  (HR)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCHR001', 'Punjab & Haryana High Court', 'HR', 'HIGH', NULL),
('DCHR020', 'District & Sessions Court, Ambala', 'HR', 'DIST', 'HCHR001'),
('DCHR030', 'District & Sessions Court, Bhiwani', 'HR', 'DIST', 'HCHR001'),
('DCHR040', 'District & Sessions Court, Charkhi Dadri', 'HR', 'DIST', 'HCHR001'),
('DCHR050', 'District & Sessions Court, Faridabad', 'HR', 'DIST', 'HCHR001'),
('DCHR060', 'District & Sessions Court, Fatehabad', 'HR', 'DIST', 'HCHR001'),
('DCHR070', 'District & Sessions Court, Gurugram', 'HR', 'DIST', 'HCHR001'),
('DCHR080', 'District & Sessions Court, Hisar', 'HR', 'DIST', 'HCHR001'),
('DCHR090', 'District & Sessions Court, Jhajjar', 'HR', 'DIST', 'HCHR001'),
('DCHR100', 'District & Sessions Court, Jind', 'HR', 'DIST', 'HCHR001'),
('DCHR110', 'District & Sessions Court, Kaithal', 'HR', 'DIST', 'HCHR001'),
('DCHR120', 'District & Sessions Court, Karnal', 'HR', 'DIST', 'HCHR001'),
('DCHR130', 'District & Sessions Court, Kurukshetra', 'HR', 'DIST', 'HCHR001'),
('DCHR140', 'District & Sessions Court, Mahendragarh', 'HR', 'DIST', 'HCHR001'),
('DCHR150', 'District & Sessions Court, Nuh', 'HR', 'DIST', 'HCHR001'),
('DCHR160', 'District & Sessions Court, Palwal', 'HR', 'DIST', 'HCHR001'),
('DCHR170', 'District & Sessions Court, Panchkula', 'HR', 'DIST', 'HCHR001'),
('DCHR180', 'District & Sessions Court, Panipat', 'HR', 'DIST', 'HCHR001'),
('DCHR190', 'District & Sessions Court, Rewari', 'HR', 'DIST', 'HCHR001'),
('DCHR200', 'District & Sessions Court, Rohtak', 'HR', 'DIST', 'HCHR001'),
('DCHR210', 'District & Sessions Court, Sirsa', 'HR', 'DIST', 'HCHR001'),
('DCHR220', 'District & Sessions Court, Sonipat', 'HR', 'DIST', 'HCHR001'),
('DCHR230', 'District & Sessions Court, Yamunanagar', 'HR', 'DIST', 'HCHR001'),
('FCHR500', 'Family Court, Gurugram', 'HR', 'FAMI', 'HCHR001'),
('FCHR510', 'Family Court, Faridabad', 'HR', 'FAMI', 'HCHR001');

-- ============================================================
--  HIMACHAL PRADESH  (HP)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCHP001', 'Himachal Pradesh High Court', 'HP', 'HIGH', NULL),
('DCHP020', 'District & Sessions Court, Bilaspur', 'HP', 'DIST', 'HCHP001'),
('DCHP030', 'District & Sessions Court, Chamba', 'HP', 'DIST', 'HCHP001'),
('DCHP040', 'District & Sessions Court, Hamirpur', 'HP', 'DIST', 'HCHP001'),
('DCHP050', 'District & Sessions Court, Kangra', 'HP', 'DIST', 'HCHP001'),
('DCHP060', 'District & Sessions Court, Kinnaur', 'HP', 'DIST', 'HCHP001'),
('DCHP070', 'District & Sessions Court, Kullu', 'HP', 'DIST', 'HCHP001'),
('DCHP080', 'District & Sessions Court, Lahaul & Spiti', 'HP', 'DIST', 'HCHP001'),
('DCHP090', 'District & Sessions Court, Mandi', 'HP', 'DIST', 'HCHP001'),
('DCHP100', 'District & Sessions Court, Shimla', 'HP', 'DIST', 'HCHP001'),
('DCHP110', 'District & Sessions Court, Sirmaur', 'HP', 'DIST', 'HCHP001'),
('DCHP120', 'District & Sessions Court, Solan', 'HP', 'DIST', 'HCHP001'),
('DCHP130', 'District & Sessions Court, Una', 'HP', 'DIST', 'HCHP001');

-- ============================================================
--  JHARKHAND  (JH)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCJH001', 'Jharkhand High Court', 'JH', 'HIGH', NULL),
('CIVIJH015', 'Civil Court, Dhanbad', 'JH', 'CIVI', 'HCJH001'),
('CIVIJH016', 'Civil Court, Ranchi', 'JH', 'CIVI', 'HCJH001'),
('DCJH020', 'District & Sessions Court, Bokaro', 'JH', 'DIST', 'HCJH001'),
('DCJH030', 'District & Sessions Court, Chatra', 'JH', 'DIST', 'HCJH001'),
('DCJH040', 'District & Sessions Court, Deoghar', 'JH', 'DIST', 'HCJH001'),
('DCJH050', 'District & Sessions Court, Dhanbad', 'JH', 'DIST', 'HCJH001'),
('DCJH060', 'District & Sessions Court, Dumka', 'JH', 'DIST', 'HCJH001'),
('DCJH070', 'District & Sessions Court, East Singhbhum', 'JH', 'DIST', 'HCJH001'),
('DCJH080', 'District & Sessions Court, Garhwa', 'JH', 'DIST', 'HCJH001'),
('DCJH090', 'District & Sessions Court, Giridih', 'JH', 'DIST', 'HCJH001'),
('DCJH100', 'District & Sessions Court, Godda', 'JH', 'DIST', 'HCJH001'),
('DCJH110', 'District & Sessions Court, Gumla', 'JH', 'DIST', 'HCJH001'),
('DCJH120', 'District & Sessions Court, Hazaribagh', 'JH', 'DIST', 'HCJH001'),
('DCJH130', 'District & Sessions Court, Jamtara', 'JH', 'DIST', 'HCJH001'),
('DCJH140', 'District & Sessions Court, Khunti', 'JH', 'DIST', 'HCJH001'),
('DCJH150', 'District & Sessions Court, Koderma', 'JH', 'DIST', 'HCJH001'),
('DCJH160', 'District & Sessions Court, Latehar', 'JH', 'DIST', 'HCJH001'),
('DCJH170', 'District & Sessions Court, Lohardaga', 'JH', 'DIST', 'HCJH001'),
('DCJH180', 'District & Sessions Court, Pakur', 'JH', 'DIST', 'HCJH001'),
('DCJH190', 'District & Sessions Court, Palamu', 'JH', 'DIST', 'HCJH001'),
('DCJH200', 'District & Sessions Court, Ramgarh', 'JH', 'DIST', 'HCJH001'),
('DCJH210', 'District & Sessions Court, Ranchi', 'JH', 'DIST', 'HCJH001'),
('DCJH220', 'District & Sessions Court, Sahebganj', 'JH', 'DIST', 'HCJH001'),
('DCJH230', 'District & Sessions Court, Seraikela-Kharsawan', 'JH', 'DIST', 'HCJH001'),
('DCJH240', 'District & Sessions Court, Simdega', 'JH', 'DIST', 'HCJH001'),
('DCJH250', 'District & Sessions Court, West Singhbhum', 'JH', 'DIST', 'HCJH001'),
('FCJH500', 'Family Court, Ranchi', 'JH', 'FAMI', 'HCJH001');

-- ============================================================
--  KARNATAKA  (KA)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCKA001', 'Karnataka High Court', 'KA', 'HIGH', NULL),
('CIVIKA015', 'City Civil & Sessions Court, Bengaluru', 'KA', 'CIVI', 'HCKA001'),
('DCKA020', 'District & Sessions Court, Bagalkot', 'KA', 'DIST', 'HCKA001'),
('DCKA030', 'District & Sessions Court, Ballari', 'KA', 'DIST', 'HCKA001'),
('DCKA040', 'District & Sessions Court, Belagavi', 'KA', 'DIST', 'HCKA001'),
('DCKA050', 'District & Sessions Court, Bengaluru Rural', 'KA', 'DIST', 'HCKA001'),
('DCKA060', 'District & Sessions Court, Bengaluru Urban', 'KA', 'DIST', 'HCKA001'),
('DCKA070', 'District & Sessions Court, Bidar', 'KA', 'DIST', 'HCKA001'),
('DCKA080', 'District & Sessions Court, Chamarajanagar', 'KA', 'DIST', 'HCKA001'),
('DCKA090', 'District & Sessions Court, Chikkaballapur', 'KA', 'DIST', 'HCKA001'),
('DCKA100', 'District & Sessions Court, Chikkamagaluru', 'KA', 'DIST', 'HCKA001'),
('DCKA110', 'District & Sessions Court, Chitradurga', 'KA', 'DIST', 'HCKA001'),
('DCKA120', 'District & Sessions Court, Dakshina Kannada', 'KA', 'DIST', 'HCKA001'),
('DCKA130', 'District & Sessions Court, Davanagere', 'KA', 'DIST', 'HCKA001'),
('DCKA140', 'District & Sessions Court, Dharwad', 'KA', 'DIST', 'HCKA001'),
('DCKA150', 'District & Sessions Court, Gadag', 'KA', 'DIST', 'HCKA001'),
('DCKA160', 'District & Sessions Court, Hassan', 'KA', 'DIST', 'HCKA001'),
('DCKA170', 'District & Sessions Court, Haveri', 'KA', 'DIST', 'HCKA001'),
('DCKA180', 'District & Sessions Court, Kalaburagi', 'KA', 'DIST', 'HCKA001'),
('DCKA190', 'District & Sessions Court, Kodagu', 'KA', 'DIST', 'HCKA001'),
('DCKA200', 'District & Sessions Court, Kolar', 'KA', 'DIST', 'HCKA001'),
('DCKA210', 'District & Sessions Court, Koppal', 'KA', 'DIST', 'HCKA001'),
('DCKA220', 'District & Sessions Court, Mandya', 'KA', 'DIST', 'HCKA001'),
('DCKA230', 'District & Sessions Court, Mysuru', 'KA', 'DIST', 'HCKA001'),
('DCKA240', 'District & Sessions Court, Raichur', 'KA', 'DIST', 'HCKA001'),
('DCKA250', 'District & Sessions Court, Ramanagara', 'KA', 'DIST', 'HCKA001'),
('DCKA260', 'District & Sessions Court, Shivamogga', 'KA', 'DIST', 'HCKA001'),
('DCKA270', 'District & Sessions Court, Tumakuru', 'KA', 'DIST', 'HCKA001'),
('DCKA280', 'District & Sessions Court, Udupi', 'KA', 'DIST', 'HCKA001'),
('DCKA290', 'District & Sessions Court, Uttara Kannada', 'KA', 'DIST', 'HCKA001'),
('DCKA300', 'District & Sessions Court, Vijayapura', 'KA', 'DIST', 'HCKA001'),
('DCKA310', 'District & Sessions Court, Vijayanagara', 'KA', 'DIST', 'HCKA001'),
('DCKA320', 'District & Sessions Court, Yadgir', 'KA', 'DIST', 'HCKA001'),
('FCKA500', 'Family Court, Bengaluru', 'KA', 'FAMI', 'HCKA001'),
('FCKA510', 'Family Court, Mysuru', 'KA', 'FAMI', 'HCKA001');

-- ============================================================
--  KERALA  (KL)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCKL001', 'Kerala High Court', 'KL', 'HIGH', NULL),
('DCKL020', 'District & Sessions Court, Alappuzha', 'KL', 'DIST', 'HCKL001'),
('DCKL030', 'District & Sessions Court, Ernakulam', 'KL', 'DIST', 'HCKL001'),
('DCKL040', 'District & Sessions Court, Idukki', 'KL', 'DIST', 'HCKL001'),
('DCKL050', 'District & Sessions Court, Kannur', 'KL', 'DIST', 'HCKL001'),
('DCKL060', 'District & Sessions Court, Kasaragod', 'KL', 'DIST', 'HCKL001'),
('DCKL070', 'District & Sessions Court, Kollam', 'KL', 'DIST', 'HCKL001'),
('DCKL080', 'District & Sessions Court, Kottayam', 'KL', 'DIST', 'HCKL001'),
('DCKL090', 'District & Sessions Court, Kozhikode', 'KL', 'DIST', 'HCKL001'),
('DCKL100', 'District & Sessions Court, Malappuram', 'KL', 'DIST', 'HCKL001'),
('DCKL110', 'District & Sessions Court, Palakkad', 'KL', 'DIST', 'HCKL001'),
('DCKL120', 'District & Sessions Court, Pathanamthitta', 'KL', 'DIST', 'HCKL001'),
('DCKL130', 'District & Sessions Court, Thiruvananthapuram', 'KL', 'DIST', 'HCKL001'),
('DCKL140', 'District & Sessions Court, Thrissur', 'KL', 'DIST', 'HCKL001'),
('DCKL150', 'District & Sessions Court, Wayanad', 'KL', 'DIST', 'HCKL001'),
('FCKL500', 'Family Court, Ernakulam', 'KL', 'FAMI', 'HCKL001'),
('FCKL510', 'Family Court, Thiruvananthapuram', 'KL', 'FAMI', 'HCKL001'),
('FCKL520', 'Family Court, Kozhikode', 'KL', 'FAMI', 'HCKL001');

-- ============================================================
--  MADHYA PRADESH  (MP)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCMP001', 'Madhya Pradesh High Court', 'MP', 'HIGH', NULL),
('DCMP020', 'District & Sessions Court, Alirajpur', 'MP', 'DIST', 'HCMP001'),
('DCMP030', 'District & Sessions Court, Anuppur', 'MP', 'DIST', 'HCMP001'),
('DCMP040', 'District & Sessions Court, Ashoknagar', 'MP', 'DIST', 'HCMP001'),
('DCMP050', 'District & Sessions Court, Balaghat', 'MP', 'DIST', 'HCMP001'),
('DCMP060', 'District & Sessions Court, Barwani', 'MP', 'DIST', 'HCMP001'),
('DCMP070', 'District & Sessions Court, Betul', 'MP', 'DIST', 'HCMP001'),
('DCMP080', 'District & Sessions Court, Bhind', 'MP', 'DIST', 'HCMP001'),
('DCMP090', 'District & Sessions Court, Bhopal', 'MP', 'DIST', 'HCMP001'),
('DCMP100', 'District & Sessions Court, Burhanpur', 'MP', 'DIST', 'HCMP001'),
('DCMP110', 'District & Sessions Court, Chhatarpur', 'MP', 'DIST', 'HCMP001'),
('DCMP120', 'District & Sessions Court, Chhindwara', 'MP', 'DIST', 'HCMP001'),
('DCMP130', 'District & Sessions Court, Damoh', 'MP', 'DIST', 'HCMP001'),
('DCMP140', 'District & Sessions Court, Datia', 'MP', 'DIST', 'HCMP001'),
('DCMP150', 'District & Sessions Court, Dewas', 'MP', 'DIST', 'HCMP001'),
('DCMP160', 'District & Sessions Court, Dhar', 'MP', 'DIST', 'HCMP001'),
('DCMP170', 'District & Sessions Court, Dindori', 'MP', 'DIST', 'HCMP001'),
('DCMP180', 'District & Sessions Court, Guna', 'MP', 'DIST', 'HCMP001'),
('DCMP190', 'District & Sessions Court, Gwalior', 'MP', 'DIST', 'HCMP001'),
('DCMP200', 'District & Sessions Court, Harda', 'MP', 'DIST', 'HCMP001'),
('DCMP210', 'District & Sessions Court, Hoshangabad', 'MP', 'DIST', 'HCMP001'),
('DCMP220', 'District & Sessions Court, Indore', 'MP', 'DIST', 'HCMP001'),
('DCMP230', 'District & Sessions Court, Jabalpur', 'MP', 'DIST', 'HCMP001'),
('DCMP240', 'District & Sessions Court, Jhabua', 'MP', 'DIST', 'HCMP001'),
('DCMP250', 'District & Sessions Court, Katni', 'MP', 'DIST', 'HCMP001'),
('DCMP260', 'District & Sessions Court, Khandwa', 'MP', 'DIST', 'HCMP001'),
('DCMP270', 'District & Sessions Court, Khargone', 'MP', 'DIST', 'HCMP001'),
('DCMP280', 'District & Sessions Court, Mandla', 'MP', 'DIST', 'HCMP001'),
('DCMP290', 'District & Sessions Court, Mandsaur', 'MP', 'DIST', 'HCMP001'),
('DCMP300', 'District & Sessions Court, Morena', 'MP', 'DIST', 'HCMP001'),
('DCMP310', 'District & Sessions Court, Narsinghpur', 'MP', 'DIST', 'HCMP001'),
('DCMP320', 'District & Sessions Court, Neemuch', 'MP', 'DIST', 'HCMP001'),
('DCMP325', 'District & Sessions Court, Niwari', 'MP', 'DIST', 'HCMP001'),
('DCMP330', 'District & Sessions Court, Panna', 'MP', 'DIST', 'HCMP001'),
('DCMP340', 'District & Sessions Court, Raisen', 'MP', 'DIST', 'HCMP001'),
('DCMP350', 'District & Sessions Court, Rajgarh', 'MP', 'DIST', 'HCMP001'),
('DCMP360', 'District & Sessions Court, Ratlam', 'MP', 'DIST', 'HCMP001'),
('DCMP370', 'District & Sessions Court, Rewa', 'MP', 'DIST', 'HCMP001'),
('DCMP380', 'District & Sessions Court, Sagar', 'MP', 'DIST', 'HCMP001'),
('DCMP390', 'District & Sessions Court, Satna', 'MP', 'DIST', 'HCMP001'),
('DCMP400', 'District & Sessions Court, Sehore', 'MP', 'DIST', 'HCMP001'),
('DCMP410', 'District & Sessions Court, Seoni', 'MP', 'DIST', 'HCMP001'),
('DCMP420', 'District & Sessions Court, Shahdol', 'MP', 'DIST', 'HCMP001'),
('DCMP430', 'District & Sessions Court, Shajapur', 'MP', 'DIST', 'HCMP001'),
('DCMP440', 'District & Sessions Court, Sheopur', 'MP', 'DIST', 'HCMP001'),
('DCMP450', 'District & Sessions Court, Shivpuri', 'MP', 'DIST', 'HCMP001'),
('DCMP460', 'District & Sessions Court, Sidhi', 'MP', 'DIST', 'HCMP001'),
('DCMP470', 'District & Sessions Court, Singrauli', 'MP', 'DIST', 'HCMP001'),
('DCMP480', 'District & Sessions Court, Tikamgarh', 'MP', 'DIST', 'HCMP001'),
('DCMP490', 'District & Sessions Court, Ujjain', 'MP', 'DIST', 'HCMP001'),
('DCMP500', 'District & Sessions Court, Umaria', 'MP', 'DIST', 'HCMP001'),
('DCMP510', 'District & Sessions Court, Vidisha', 'MP', 'DIST', 'HCMP001'),
('FCMP600', 'Family Court, Bhopal', 'MP', 'FAMI', 'HCMP001'),
('FCMP610', 'Family Court, Indore', 'MP', 'FAMI', 'HCMP001'),
('FCMP620', 'Family Court, Jabalpur', 'MP', 'FAMI', 'HCMP001');

-- ============================================================
--  MAHARASHTRA  (MH)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCMH001', 'Bombay High Court', 'MH', 'HIGH', NULL),
('HCMH002', 'Bombay High Court – Aurangabad Bench', 'MH', 'HIGH', 'HCMH001'),
('HCMH003', 'Bombay High Court – Nagpur Bench', 'MH', 'HIGH', 'HCMH001'),
('CIVIMH015', 'City Civil & Sessions Court, Mumbai', 'MH', 'CIVI', 'HCMH001'),
('CIVIMH016', 'Small Causes Court, Mumbai', 'MH', 'CIVI', 'HCMH001'),
('MAGIMH017', 'Chief Metropolitan Magistrate Court, Mumbai', 'MH', 'MAGI', 'HCMH001'),
('DCMH020', 'District & Sessions Court, Ahmadnagar', 'MH', 'DIST', 'HCMH001'),
('DCMH030', 'District & Sessions Court, Akola', 'MH', 'DIST', 'HCMH001'),
('DCMH040', 'District & Sessions Court, Amravati', 'MH', 'DIST', 'HCMH001'),
('DCMH050', 'District & Sessions Court, Aurangabad', 'MH', 'DIST', 'HCMH001'),
('DCMH060', 'District & Sessions Court, Beed', 'MH', 'DIST', 'HCMH001'),
('DCMH070', 'District & Sessions Court, Bhandara', 'MH', 'DIST', 'HCMH001'),
('DCMH080', 'District & Sessions Court, Buldhana', 'MH', 'DIST', 'HCMH001'),
('DCMH090', 'District & Sessions Court, Chandrapur', 'MH', 'DIST', 'HCMH001'),
('DCMH100', 'District & Sessions Court, Dhule', 'MH', 'DIST', 'HCMH001'),
('DCMH110', 'District & Sessions Court, Gadchiroli', 'MH', 'DIST', 'HCMH001'),
('DCMH120', 'District & Sessions Court, Gondia', 'MH', 'DIST', 'HCMH001'),
('DCMH130', 'District & Sessions Court, Hingoli', 'MH', 'DIST', 'HCMH001'),
('DCMH140', 'District & Sessions Court, Jalgaon', 'MH', 'DIST', 'HCMH001'),
('DCMH150', 'District & Sessions Court, Jalna', 'MH', 'DIST', 'HCMH001'),
('DCMH160', 'District & Sessions Court, Kolhapur', 'MH', 'DIST', 'HCMH001'),
('DCMH170', 'District & Sessions Court, Latur', 'MH', 'DIST', 'HCMH001'),
('DCMH175', 'District & Sessions Court, Mumbai Suburban', 'MH', 'DIST', 'HCMH001'),
('DCMH180', 'District & Sessions Court, Nagpur', 'MH', 'DIST', 'HCMH001'),
('DCMH190', 'District & Sessions Court, Nanded', 'MH', 'DIST', 'HCMH001'),
('DCMH200', 'District & Sessions Court, Nandurbar', 'MH', 'DIST', 'HCMH001'),
('DCMH210', 'District & Sessions Court, Nashik', 'MH', 'DIST', 'HCMH001'),
('DCMH220', 'District & Sessions Court, Osmanabad', 'MH', 'DIST', 'HCMH001'),
('DCMH230', 'District & Sessions Court, Parbhani', 'MH', 'DIST', 'HCMH001'),
('DCMH240', 'District & Sessions Court, Pune', 'MH', 'DIST', 'HCMH001'),
('DCMH250', 'District & Sessions Court, Raigad', 'MH', 'DIST', 'HCMH001'),
('DCMH260', 'District & Sessions Court, Ratnagiri', 'MH', 'DIST', 'HCMH001'),
('DCMH270', 'District & Sessions Court, Sangli', 'MH', 'DIST', 'HCMH001'),
('DCMH280', 'District & Sessions Court, Satara', 'MH', 'DIST', 'HCMH001'),
('DCMH290', 'District & Sessions Court, Sindhudurg', 'MH', 'DIST', 'HCMH001'),
('DCMH300', 'District & Sessions Court, Solapur', 'MH', 'DIST', 'HCMH001'),
('DCMH310', 'District & Sessions Court, Thane', 'MH', 'DIST', 'HCMH001'),
('DCMH320', 'District & Sessions Court, Wardha', 'MH', 'DIST', 'HCMH001'),
('DCMH330', 'District & Sessions Court, Washim', 'MH', 'DIST', 'HCMH001'),
('DCMH340', 'District & Sessions Court, Yavatmal', 'MH', 'DIST', 'HCMH001'),
('FCMH500', 'Family Court, Mumbai', 'MH', 'FAMI', 'HCMH001'),
('FCMH510', 'Family Court, Pune', 'MH', 'FAMI', 'HCMH001'),
('FCMH520', 'Family Court, Nagpur', 'MH', 'FAMI', 'HCMH001'),
('FCMH530', 'Family Court, Aurangabad', 'MH', 'FAMI', 'HCMH001'),
('TRIBMH700', 'Motor Accident Claims Tribunal, Mumbai', 'MH', 'TRIB', 'HCMH001');

-- ============================================================
-- MANIPUR (MN)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCMN001', 'Manipur High Court', 'MN', 'HIGH', NULL),
('DCMN020', 'District & Sessions Court, Bishnupur', 'MN', 'DIST', 'HCMN001'),
('DCMN030', 'District & Sessions Court, Chandel', 'MN', 'DIST', 'HCMN001'),
('DCMN040', 'District & Sessions Court, Churachandpur', 'MN', 'DIST', 'HCMN001'),
('DCMN050', 'District & Sessions Court, Imphal East', 'MN', 'DIST', 'HCMN001'),
('DCMN060', 'District & Sessions Court, Imphal West', 'MN', 'DIST', 'HCMN001'),
('DCMN070', 'District & Sessions Court, Jiribam', 'MN', 'DIST', 'HCMN001'),
('DCMN080', 'District & Sessions Court, Kakching', 'MN', 'DIST', 'HCMN001'),
('DCMN090', 'District & Sessions Court, Kamjong', 'MN', 'DIST', 'HCMN001'),
('DCMN100', 'District & Sessions Court, Kangpokpi', 'MN', 'DIST', 'HCMN001'),
('DCMN110', 'District & Sessions Court, Noney', 'MN', 'DIST', 'HCMN001'),
('DCMN120', 'District & Sessions Court, Pherzawl', 'MN', 'DIST', 'HCMN001'),
('DCMN130', 'District & Sessions Court, Senapati', 'MN', 'DIST', 'HCMN001'),
('DCMN140', 'District & Sessions Court, Tamenglong', 'MN', 'DIST', 'HCMN001'),
('DCMN150', 'District & Sessions Court, Tengnoupal', 'MN', 'DIST', 'HCMN001'),
('DCMN160', 'District & Sessions Court, Thoubal', 'MN', 'DIST', 'HCMN001'),
('DCMN170', 'District & Sessions Court, Ukhrul', 'MN', 'DIST', 'HCMN001');

-- ============================================================
-- MEGHALAYA (ML)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCML001', 'Meghalaya High Court', 'ML', 'HIGH', NULL),
('DCML020', 'District & Sessions Court, East Garo Hills', 'ML', 'DIST', 'HCML001'),
('DCML030', 'District & Sessions Court, East Jaintia Hills', 'ML', 'DIST', 'HCML001'),
('DCML040', 'District & Sessions Court, East Khasi Hills', 'ML', 'DIST', 'HCML001'),
('DCML050', 'District & Sessions Court, North Garo Hills', 'ML', 'DIST', 'HCML001'),
('DCML060', 'District & Sessions Court, Ri Bhoi', 'ML', 'DIST', 'HCML001'),
('DCML070', 'District & Sessions Court, South Garo Hills', 'ML', 'DIST', 'HCML001'),
('DCML080', 'District & Sessions Court, South West Garo Hills', 'ML', 'DIST', 'HCML001'),
('DCML090', 'District & Sessions Court, South West Khasi Hills', 'ML', 'DIST', 'HCML001'),
('DCML100', 'District & Sessions Court, West Garo Hills', 'ML', 'DIST', 'HCML001'),
('DCML110', 'District & Sessions Court, West Jaintia Hills', 'ML', 'DIST', 'HCML001'),
('DCML120', 'District & Sessions Court, West Khasi Hills', 'ML', 'DIST', 'HCML001');

-- ============================================================
--  MIZORAM  (MZ)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCMZ001', 'Gauhati High Court – Mizoram Bench', 'MZ', 'HIGH', NULL),
('DCMZ020', 'District & Sessions Court, Aizawl', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ030', 'District & Sessions Court, Champhai', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ040', 'District & Sessions Court, Hnahthial', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ050', 'District & Sessions Court, Khawzawl', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ060', 'District & Sessions Court, Kolasib', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ070', 'District & Sessions Court, Lawngtlai', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ080', 'District & Sessions Court, Lunglei', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ090', 'District & Sessions Court, Mamit', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ100', 'District & Sessions Court, Saiha', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ110', 'District & Sessions Court, Saitual', 'MZ', 'DIST', 'HCMZ001'),
('DCMZ120', 'District & Sessions Court, Serchhip', 'MZ', 'DIST', 'HCMZ001');

-- ============================================================
--  NAGALAND  (NL)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCNL001', 'Gauhati High Court – Nagaland Bench', 'NL', 'HIGH', NULL),
('DCNL020', 'District & Sessions Court, Chumoukedima', 'NL', 'DIST', 'HCNL001'),
('DCNL030', 'District & Sessions Court, Dimapur', 'NL', 'DIST', 'HCNL001'),
('DCNL040', 'District & Sessions Court, Kiphire', 'NL', 'DIST', 'HCNL001'),
('DCNL050', 'District & Sessions Court, Kohima', 'NL', 'DIST', 'HCNL001'),
('DCNL060', 'District & Sessions Court, Longleng', 'NL', 'DIST', 'HCNL001'),
('DCNL070', 'District & Sessions Court, Mokokchung', 'NL', 'DIST', 'HCNL001'),
('DCNL080', 'District & Sessions Court, Mon', 'NL', 'DIST', 'HCNL001'),
('DCNL090', 'District & Sessions Court, Niuland', 'NL', 'DIST', 'HCNL001'),
('DCNL100', 'District & Sessions Court, Noklak', 'NL', 'DIST', 'HCNL001'),
('DCNL110', 'District & Sessions Court, Peren', 'NL', 'DIST', 'HCNL001'),
('DCNL120', 'District & Sessions Court, Phek', 'NL', 'DIST', 'HCNL001'),
('DCNL130', 'District & Sessions Court, Shamator', 'NL', 'DIST', 'HCNL001'),
('DCNL140', 'District & Sessions Court, Tseminyü', 'NL', 'DIST', 'HCNL001'),
('DCNL150', 'District & Sessions Court, Tuensang', 'NL', 'DIST', 'HCNL001'),
('DCNL160', 'District & Sessions Court, Wokha', 'NL', 'DIST', 'HCNL001'),
('DCNL170', 'District & Sessions Court, Zunheboto', 'NL', 'DIST', 'HCNL001');

-- ============================================================
--  ODISHA  (OD)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCOD001', 'Orissa High Court', 'OD', 'HIGH', NULL),
('DCOD020', 'District & Sessions Court, Angul', 'OD', 'DIST', 'HCOD001'),
('DCOD030', 'District & Sessions Court, Balangir', 'OD', 'DIST', 'HCOD001'),
('DCOD040', 'District & Sessions Court, Balasore', 'OD', 'DIST', 'HCOD001'),
('DCOD050', 'District & Sessions Court, Bargarh', 'OD', 'DIST', 'HCOD001'),
('DCOD060', 'District & Sessions Court, Bhadrak', 'OD', 'DIST', 'HCOD001'),
('DCOD070', 'District & Sessions Court, Boudh', 'OD', 'DIST', 'HCOD001'),
('DCOD080', 'District & Sessions Court, Cuttack', 'OD', 'DIST', 'HCOD001'),
('DCOD090', 'District & Sessions Court, Debagarh', 'OD', 'DIST', 'HCOD001'),
('DCOD100', 'District & Sessions Court, Dhenkanal', 'OD', 'DIST', 'HCOD001'),
('DCOD110', 'District & Sessions Court, Gajapati', 'OD', 'DIST', 'HCOD001'),
('DCOD120', 'District & Sessions Court, Ganjam', 'OD', 'DIST', 'HCOD001'),
('DCOD130', 'District & Sessions Court, Jagatsinghpur', 'OD', 'DIST', 'HCOD001'),
('DCOD140', 'District & Sessions Court, Jajpur', 'OD', 'DIST', 'HCOD001'),
('DCOD150', 'District & Sessions Court, Jharsuguda', 'OD', 'DIST', 'HCOD001'),
('DCOD160', 'District & Sessions Court, Kalahandi', 'OD', 'DIST', 'HCOD001'),
('DCOD170', 'District & Sessions Court, Kandhamal', 'OD', 'DIST', 'HCOD001'),
('DCOD180', 'District & Sessions Court, Kendrapara', 'OD', 'DIST', 'HCOD001'),
('DCOD190', 'District & Sessions Court, Kendujhar', 'OD', 'DIST', 'HCOD001'),
('DCOD200', 'District & Sessions Court, Khordha', 'OD', 'DIST', 'HCOD001'),
('DCOD210', 'District & Sessions Court, Koraput', 'OD', 'DIST', 'HCOD001'),
('DCOD220', 'District & Sessions Court, Malkangiri', 'OD', 'DIST', 'HCOD001'),
('DCOD230', 'District & Sessions Court, Mayurbhanj', 'OD', 'DIST', 'HCOD001'),
('DCOD240', 'District & Sessions Court, Nabarangpur', 'OD', 'DIST', 'HCOD001'),
('DCOD250', 'District & Sessions Court, Nayagarh', 'OD', 'DIST', 'HCOD001'),
('DCOD260', 'District & Sessions Court, Nuapada', 'OD', 'DIST', 'HCOD001'),
('DCOD270', 'District & Sessions Court, Puri', 'OD', 'DIST', 'HCOD001'),
('DCOD280', 'District & Sessions Court, Rayagada', 'OD', 'DIST', 'HCOD001'),
('DCOD290', 'District & Sessions Court, Sambalpur', 'OD', 'DIST', 'HCOD001'),
('DCOD300', 'District & Sessions Court, Subarnapur', 'OD', 'DIST', 'HCOD001'),
('DCOD310', 'District & Sessions Court, Sundargarh', 'OD', 'DIST', 'HCOD001'),
('FCOD500', 'Family Court, Bhubaneswar', 'OD', 'FAMI', 'HCOD001'),
('FCOD510', 'Family Court, Cuttack', 'OD', 'FAMI', 'HCOD001');

-- ============================================================
--  PUNJAB  (PB)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCPB001', 'Punjab & Haryana High Court', 'PB', 'HIGH', NULL),
('DCPB020', 'District & Sessions Court, Amritsar', 'PB', 'DIST', 'HCPB001'),
('DCPB030', 'District & Sessions Court, Barnala', 'PB', 'DIST', 'HCPB001'),
('DCPB040', 'District & Sessions Court, Bathinda', 'PB', 'DIST', 'HCPB001'),
('DCPB050', 'District & Sessions Court, Faridkot', 'PB', 'DIST', 'HCPB001'),
('DCPB060', 'District & Sessions Court, Fatehgarh Sahib', 'PB', 'DIST', 'HCPB001'),
('DCPB070', 'District & Sessions Court, Fazilka', 'PB', 'DIST', 'HCPB001'),
('DCPB080', 'District & Sessions Court, Ferozepur', 'PB', 'DIST', 'HCPB001'),
('DCPB090', 'District & Sessions Court, Gurdaspur', 'PB', 'DIST', 'HCPB001'),
('DCPB100', 'District & Sessions Court, Hoshiarpur', 'PB', 'DIST', 'HCPB001'),
('DCPB110', 'District & Sessions Court, Jalandhar', 'PB', 'DIST', 'HCPB001'),
('DCPB120', 'District & Sessions Court, Kapurthala', 'PB', 'DIST', 'HCPB001'),
('DCPB130', 'District & Sessions Court, Ludhiana', 'PB', 'DIST', 'HCPB001'),
('DCPB140', 'District & Sessions Court, Mansa', 'PB', 'DIST', 'HCPB001'),
('DCPB150', 'District & Sessions Court, Moga', 'PB', 'DIST', 'HCPB001'),
('DCPB160', 'District & Sessions Court, Mohali', 'PB', 'DIST', 'HCPB001'),
('DCPB170', 'District & Sessions Court, Muktsar', 'PB', 'DIST', 'HCPB001'),
('DCPB180', 'District & Sessions Court, Nawanshahr', 'PB', 'DIST', 'HCPB001'),
('DCPB190', 'District & Sessions Court, Pathankot', 'PB', 'DIST', 'HCPB001'),
('DCPB200', 'District & Sessions Court, Patiala', 'PB', 'DIST', 'HCPB001'),
('DCPB210', 'District & Sessions Court, Rupnagar', 'PB', 'DIST', 'HCPB001'),
('DCPB220', 'District & Sessions Court, Sangrur', 'PB', 'DIST', 'HCPB001'),
('DCPB230', 'District & Sessions Court, Tarn Taran', 'PB', 'DIST', 'HCPB001'),
('FCPB500', 'Family Court, Ludhiana', 'PB', 'FAMI', 'HCPB001'),
('FCPB510', 'Family Court, Amritsar', 'PB', 'FAMI', 'HCPB001');

-- ============================================================
--  RAJASTHAN  (RJ)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCRJ001', 'Rajasthan High Court', 'RJ', 'HIGH', NULL),
('HCRJ002', 'Rajasthan High Court – Jaipur Bench', 'RJ', 'HIGH', 'HCRJ001'),
('DCRJ020', 'District & Sessions Court, Ajmer', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ030', 'District & Sessions Court, Alwar', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ035', 'District & Sessions Court, Balotra', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ040', 'District & Sessions Court, Banswara', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ050', 'District & Sessions Court, Baran', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ060', 'District & Sessions Court, Barmer', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ065', 'District & Sessions Court, Beawar', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ070', 'District & Sessions Court, Bharatpur', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ080', 'District & Sessions Court, Bhilwara', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ090', 'District & Sessions Court, Bikaner', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ100', 'District & Sessions Court, Bundi', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ110', 'District & Sessions Court, Chittorgarh', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ120', 'District & Sessions Court, Churu', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ130', 'District & Sessions Court, Dausa', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ140', 'District & Sessions Court, Dholpur', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ150', 'District & Sessions Court, Dungarpur', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ160', 'District & Sessions Court, Ganganagar', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ170', 'District & Sessions Court, Hanumangarh', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ180', 'District & Sessions Court, Jaipur', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ190', 'District & Sessions Court, Jaisalmer', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ200', 'District & Sessions Court, Jalore', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ210', 'District & Sessions Court, Jhalawar', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ220', 'District & Sessions Court, Jhunjhunu', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ230', 'District & Sessions Court, Jodhpur', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ240', 'District & Sessions Court, Karauli', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ250', 'District & Sessions Court, Kota', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ260', 'District & Sessions Court, Nagaur', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ270', 'District & Sessions Court, Pali', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ280', 'District & Sessions Court, Pratapgarh', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ290', 'District & Sessions Court, Rajsamand', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ300', 'District & Sessions Court, Sawai Madhopur', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ310', 'District & Sessions Court, Sikar', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ320', 'District & Sessions Court, Sirohi', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ330', 'District & Sessions Court, Tonk', 'RJ', 'DIST', 'HCRJ001'),
('DCRJ340', 'District & Sessions Court, Udaipur', 'RJ', 'DIST', 'HCRJ001'),
('FCRJ500', 'Family Court, Jaipur', 'RJ', 'FAMI', 'HCRJ001'),
('FCRJ510', 'Family Court, Jodhpur', 'RJ', 'FAMI', 'HCRJ001');

-- ============================================================
--  SIKKIM  (SK)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCSK001', 'Sikkim High Court', 'SK', 'HIGH', NULL),
('DCSK020', 'District & Sessions Court, East Sikkim', 'SK', 'DIST', 'HCSK001'),
('DCSK030', 'District & Sessions Court, North Sikkim', 'SK', 'DIST', 'HCSK001'),
('DCSK035', 'District & Sessions Court, Pakyong', 'SK', 'DIST', 'HCSK001'),
('DCSK040', 'District & Sessions Court, Soreng', 'SK', 'DIST', 'HCSK001'),
('DCSK050', 'District & Sessions Court, South Sikkim', 'SK', 'DIST', 'HCSK001'),
('DCSK060', 'District & Sessions Court, West Sikkim', 'SK', 'DIST', 'HCSK001');

-- ============================================================
--  TAMIL NADU  (TN)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCTN001', 'Madras High Court', 'TN', 'HIGH', NULL),
('HCTN002', 'Madras High Court – Madurai Bench', 'TN', 'HIGH', 'HCTN001'),
('CIVITN015', 'City Civil Court, Chennai', 'TN', 'CIVI', 'HCTN001'),
('CIVITN016', 'Small Causes Court, Chennai', 'TN', 'CIVI', 'HCTN001'),
('DCTN020', 'Principal District Court, Ariyalur', 'TN', 'DIST', 'HCTN001'),
('DCTN030', 'Principal District Court, Chengalpattu', 'TN', 'DIST', 'HCTN001'),
('DCTN040', 'Principal District Court, Chennai', 'TN', 'DIST', 'HCTN001'),
('DCTN050', 'Principal District Court, Coimbatore', 'TN', 'DIST', 'HCTN001'),
('DCTN060', 'Principal District Court, Cuddalore', 'TN', 'DIST', 'HCTN001'),
('DCTN070', 'Principal District Court, Dharmapuri', 'TN', 'DIST', 'HCTN001'),
('DCTN080', 'Principal District Court, Dindigul', 'TN', 'DIST', 'HCTN001'),
('DCTN090', 'Principal District Court, Erode', 'TN', 'DIST', 'HCTN001'),
('DCTN100', 'Principal District Court, Kallakurichi', 'TN', 'DIST', 'HCTN001'),
('DCTN110', 'Principal District Court, Kanchipuram', 'TN', 'DIST', 'HCTN001'),
('DCTN120', 'Principal District Court, Kanyakumari', 'TN', 'DIST', 'HCTN001'),
('DCTN130', 'Principal District Court, Karur', 'TN', 'DIST', 'HCTN001'),
('DCTN140', 'Principal District Court, Krishnagiri', 'TN', 'DIST', 'HCTN001'),
('DCTN150', 'Principal District Court, Madurai', 'TN', 'DIST', 'HCTN001'),
('DCTN160', 'Principal District Court, Mayiladuthurai', 'TN', 'DIST', 'HCTN001'),
('DCTN170', 'Principal District Court, Nagapattinam', 'TN', 'DIST', 'HCTN001'),
('DCTN180', 'Principal District Court, Namakkal', 'TN', 'DIST', 'HCTN001'),
('DCTN190', 'Principal District Court, Nilgiris', 'TN', 'DIST', 'HCTN001'),
('DCTN200', 'Principal District Court, Perambalur', 'TN', 'DIST', 'HCTN001'),
('DCTN210', 'Principal District Court, Pudukkottai', 'TN', 'DIST', 'HCTN001'),
('DCTN220', 'Principal District Court, Ramanathapuram', 'TN', 'DIST', 'HCTN001'),
('DCTN230', 'Principal District Court, Ranipet', 'TN', 'DIST', 'HCTN001'),
('DCTN240', 'Principal District Court, Salem', 'TN', 'DIST', 'HCTN001'),
('DCTN250', 'Principal District Court, Sivaganga', 'TN', 'DIST', 'HCTN001'),
('DCTN260', 'Principal District Court, Tenkasi', 'TN', 'DIST', 'HCTN001'),
('DCTN270', 'Principal District Court, Thanjavur', 'TN', 'DIST', 'HCTN001'),
('DCTN280', 'Principal District Court, Theni', 'TN', 'DIST', 'HCTN001'),
('DCTN290', 'Principal District Court, Thoothukudi', 'TN', 'DIST', 'HCTN001'),
('DCTN300', 'Principal District Court, Tiruchirappalli', 'TN', 'DIST', 'HCTN001'),
('DCTN310', 'Principal District Court, Tirunelveli', 'TN', 'DIST', 'HCTN001'),
('DCTN320', 'Principal District Court, Tirupathur', 'TN', 'DIST', 'HCTN001'),
('DCTN330', 'Principal District Court, Tiruppur', 'TN', 'DIST', 'HCTN001'),
('DCTN340', 'Principal District Court, Tiruvallur', 'TN', 'DIST', 'HCTN001'),
('DCTN350', 'Principal District Court, Tiruvannamalai', 'TN', 'DIST', 'HCTN001'),
('DCTN360', 'Principal District Court, Tiruvarur', 'TN', 'DIST', 'HCTN001'),
('DCTN370', 'Principal District Court, Vellore', 'TN', 'DIST', 'HCTN001'),
('DCTN380', 'Principal District Court, Villuppuram', 'TN', 'DIST', 'HCTN001'),
('DCTN390', 'Principal District Court, Virudhunagar', 'TN', 'DIST', 'HCTN001'),
('FCTN500', 'Family Court, Chennai', 'TN', 'FAMI', 'HCTN001'),
('FCTN510', 'Family Court, Coimbatore', 'TN', 'FAMI', 'HCTN001'),
('FCTN520', 'Family Court, Madurai', 'TN', 'FAMI', 'HCTN001'),
('FCTN530', 'Family Court, Salem', 'TN', 'FAMI', 'HCTN001'),
('FCTN540', 'Family Court, Tiruchirappalli', 'TN', 'FAMI', 'HCTN001'),
('MAGITN600', 'JM Court, Saidapet', 'TN', 'MAGI', 'HCTN001'),
('MAGITN610', 'JM Court, Egmore', 'TN', 'MAGI', 'HCTN001'),
('MAGITN620', 'Chief Metropolitan Magistrate Court, Chennai', 'TN', 'MAGI', 'HCTN001'),
('TRIBTN700', 'Motor Accident Claims Tribunal, Chennai', 'TN', 'TRIB', 'HCTN001');

-- ============================================================
--  TELANGANA  (TS)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCTS001', 'Telangana High Court', 'TS', 'HIGH', NULL),
('CIVITS015', 'City Civil Court, Hyderabad', 'TS', 'CIVI', 'HCTS001'),
('CIVITS016', 'City Small Causes Court, Hyderabad', 'TS', 'CIVI', 'HCTS001'),
('SPECTS018', 'CBI Court, Hyderabad', 'TS', 'SPEC', 'HCTS001'),
('DCTS020', 'District & Sessions Court, Adilabad', 'TS', 'DIST', 'HCTS001'),
('DCTS030', 'District & Sessions Court, Bhadradri Kothagudem', 'TS', 'DIST', 'HCTS001'),
('DCTS040', 'District & Sessions Court, Hanumakonda', 'TS', 'DIST', 'HCTS001'),
('DCTS050', 'District & Sessions Court, Hyderabad', 'TS', 'DIST', 'HCTS001'),
('DCTS060', 'District & Sessions Court, Jagtial', 'TS', 'DIST', 'HCTS001'),
('DCTS070', 'District & Sessions Court, Jangaon', 'TS', 'DIST', 'HCTS001'),
('DCTS080', 'District & Sessions Court, Jayashankar Bhupalpally', 'TS', 'DIST', 'HCTS001'),
('DCTS090', 'District & Sessions Court, Jogulamba Gadwal', 'TS', 'DIST', 'HCTS001'),
('DCTS100', 'District & Sessions Court, Kamareddy', 'TS', 'DIST', 'HCTS001'),
('DCTS110', 'District & Sessions Court, Karimnagar', 'TS', 'DIST', 'HCTS001'),
('DCTS120', 'District & Sessions Court, Khammam', 'TS', 'DIST', 'HCTS001'),
('DCTS130', 'District & Sessions Court, Komaram Bheem Asifabad', 'TS', 'DIST', 'HCTS001'),
('DCTS140', 'District & Sessions Court, Mahabubabad', 'TS', 'DIST', 'HCTS001'),
('DCTS150', 'District & Sessions Court, Mahabubnagar', 'TS', 'DIST', 'HCTS001'),
('DCTS160', 'District & Sessions Court, Mancherial', 'TS', 'DIST', 'HCTS001'),
('DCTS170', 'District & Sessions Court, Medak', 'TS', 'DIST', 'HCTS001'),
('DCTS180', 'District & Sessions Court, Medchal-Malkajgiri', 'TS', 'DIST', 'HCTS001'),
('DCTS190', 'District & Sessions Court, Mulugu', 'TS', 'DIST', 'HCTS001'),
('DCTS200', 'District & Sessions Court, Nagarkurnool', 'TS', 'DIST', 'HCTS001'),
('DCTS210', 'District & Sessions Court, Nalgonda', 'TS', 'DIST', 'HCTS001'),
('DCTS220', 'District & Sessions Court, Narayanpet', 'TS', 'DIST', 'HCTS001'),
('DCTS230', 'District & Sessions Court, Nirmal', 'TS', 'DIST', 'HCTS001'),
('DCTS240', 'District & Sessions Court, Nizamabad', 'TS', 'DIST', 'HCTS001'),
('DCTS250', 'District & Sessions Court, Peddapalli', 'TS', 'DIST', 'HCTS001'),
('DCTS260', 'District & Sessions Court, Rajanna Sircilla', 'TS', 'DIST', 'HCTS001'),
('DCTS270', 'District & Sessions Court, Rangareddy', 'TS', 'DIST', 'HCTS001'),
('DCTS280', 'District & Sessions Court, Sangareddy', 'TS', 'DIST', 'HCTS001'),
('DCTS290', 'District & Sessions Court, Siddipet', 'TS', 'DIST', 'HCTS001'),
('DCTS300', 'District & Sessions Court, Suryapet', 'TS', 'DIST', 'HCTS001'),
('DCTS310', 'District & Sessions Court, Vikarabad', 'TS', 'DIST', 'HCTS001'),
('DCTS320', 'District & Sessions Court, Wanaparthy', 'TS', 'DIST', 'HCTS001'),
('DCTS330', 'District & Sessions Court, Warangal', 'TS', 'DIST', 'HCTS001'),
('DCTS340', 'District & Sessions Court, Yadadri Bhuvanagiri', 'TS', 'DIST', 'HCTS001'),
('FCTS500', 'Family Court, Hyderabad', 'TS', 'FAMI', 'HCTS001'),
('FCTS510', 'Family Court, Warangal', 'TS', 'FAMI', 'HCTS001');

-- ============================================================
--  TRIPURA  (TR)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCTR001', 'Tripura High Court', 'TR', 'HIGH', NULL),
('DCTR020', 'District & Sessions Court, Dhalai', 'TR', 'DIST', 'HCTR001'),
('DCTR030', 'District & Sessions Court, Gomati', 'TR', 'DIST', 'HCTR001'),
('DCTR040', 'District & Sessions Court, Khowai', 'TR', 'DIST', 'HCTR001'),
('DCTR050', 'District & Sessions Court, North Tripura', 'TR', 'DIST', 'HCTR001'),
('DCTR060', 'District & Sessions Court, Sepahijala', 'TR', 'DIST', 'HCTR001'),
('DCTR070', 'District & Sessions Court, South Tripura', 'TR', 'DIST', 'HCTR001'),
('DCTR080', 'District & Sessions Court, Unakoti', 'TR', 'DIST', 'HCTR001'),
('DCTR090', 'District & Sessions Court, West Tripura', 'TR', 'DIST', 'HCTR001'),
('FCTR500', 'Family Court, Agartala', 'TR', 'FAMI', 'HCTR001');

-- ============================================================
--  UTTAR PRADESH  (UP)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCUP001', 'Allahabad High Court', 'UP', 'HIGH', NULL),
('HCUP002', 'Allahabad High Court – Lucknow Bench', 'UP', 'HIGH', 'HCUP001'),
('DCUP020', 'District & Sessions Court, Agra', 'UP', 'DIST', 'HCUP001'),
('DCUP030', 'District & Sessions Court, Aligarh', 'UP', 'DIST', 'HCUP001'),
('DCUP040', 'District & Sessions Court, Ambedkar Nagar', 'UP', 'DIST', 'HCUP001'),
('DCUP050', 'District & Sessions Court, Amethi', 'UP', 'DIST', 'HCUP001'),
('DCUP060', 'District & Sessions Court, Amroha', 'UP', 'DIST', 'HCUP001'),
('DCUP070', 'District & Sessions Court, Auraiya', 'UP', 'DIST', 'HCUP001'),
('DCUP080', 'District & Sessions Court, Ayodhya', 'UP', 'DIST', 'HCUP001'),
('DCUP090', 'District & Sessions Court, Azamgarh', 'UP', 'DIST', 'HCUP001'),
('DCUP100', 'District & Sessions Court, Baghpat', 'UP', 'DIST', 'HCUP001'),
('DCUP110', 'District & Sessions Court, Bahraich', 'UP', 'DIST', 'HCUP001'),
('DCUP120', 'District & Sessions Court, Ballia', 'UP', 'DIST', 'HCUP001'),
('DCUP130', 'District & Sessions Court, Balrampur', 'UP', 'DIST', 'HCUP001'),
('DCUP140', 'District & Sessions Court, Banda', 'UP', 'DIST', 'HCUP001'),
('DCUP150', 'District & Sessions Court, Barabanki', 'UP', 'DIST', 'HCUP001'),
('DCUP160', 'District & Sessions Court, Bareilly', 'UP', 'DIST', 'HCUP001'),
('DCUP170', 'District & Sessions Court, Basti', 'UP', 'DIST', 'HCUP001'),
('DCUP180', 'District & Sessions Court, Bhadohi', 'UP', 'DIST', 'HCUP001'),
('DCUP190', 'District & Sessions Court, Bijnor', 'UP', 'DIST', 'HCUP001'),
('DCUP200', 'District & Sessions Court, Budaun', 'UP', 'DIST', 'HCUP001'),
('DCUP210', 'District & Sessions Court, Bulandshahar', 'UP', 'DIST', 'HCUP001'),
('DCUP220', 'District & Sessions Court, Chandauli', 'UP', 'DIST', 'HCUP001'),
('DCUP230', 'District & Sessions Court, Chitrakoot', 'UP', 'DIST', 'HCUP001'),
('DCUP240', 'District & Sessions Court, Deoria', 'UP', 'DIST', 'HCUP001'),
('DCUP250', 'District & Sessions Court, Etah', 'UP', 'DIST', 'HCUP001'),
('DCUP260', 'District & Sessions Court, Etawah', 'UP', 'DIST', 'HCUP001'),
('DCUP270', 'District & Sessions Court, Farrukhabad', 'UP', 'DIST', 'HCUP001'),
('DCUP280', 'District & Sessions Court, Fatehpur', 'UP', 'DIST', 'HCUP001'),
('DCUP290', 'District & Sessions Court, Firozabad', 'UP', 'DIST', 'HCUP001'),
('DCUP300', 'District & Sessions Court, Gautam Budh Nagar', 'UP', 'DIST', 'HCUP001'),
('DCUP310', 'District & Sessions Court, Ghaziabad', 'UP', 'DIST', 'HCUP001'),
('DCUP320', 'District & Sessions Court, Ghazipur', 'UP', 'DIST', 'HCUP001'),
('DCUP330', 'District & Sessions Court, Gonda', 'UP', 'DIST', 'HCUP001'),
('DCUP340', 'District & Sessions Court, Gorakhpur', 'UP', 'DIST', 'HCUP001'),
('DCUP350', 'District & Sessions Court, Hamirpur', 'UP', 'DIST', 'HCUP001'),
('DCUP360', 'District & Sessions Court, Hapur', 'UP', 'DIST', 'HCUP001'),
('DCUP370', 'District & Sessions Court, Hardoi', 'UP', 'DIST', 'HCUP001'),
('DCUP380', 'District & Sessions Court, Hathras', 'UP', 'DIST', 'HCUP001'),
('DCUP390', 'District & Sessions Court, Jalaun', 'UP', 'DIST', 'HCUP001'),
('DCUP400', 'District & Sessions Court, Jaunpur', 'UP', 'DIST', 'HCUP001'),
('DCUP410', 'District & Sessions Court, Jhansi', 'UP', 'DIST', 'HCUP001'),
('DCUP420', 'District & Sessions Court, Kannauj', 'UP', 'DIST', 'HCUP001'),
('DCUP430', 'District & Sessions Court, Kanpur Dehat', 'UP', 'DIST', 'HCUP001'),
('DCUP440', 'District & Sessions Court, Kanpur Nagar', 'UP', 'DIST', 'HCUP001'),
('DCUP450', 'District & Sessions Court, Kasganj', 'UP', 'DIST', 'HCUP001'),
('DCUP460', 'District & Sessions Court, Kaushambi', 'UP', 'DIST', 'HCUP001'),
('DCUP470', 'District & Sessions Court, Kheri', 'UP', 'DIST', 'HCUP001'),
('DCUP480', 'District & Sessions Court, Kushinagar', 'UP', 'DIST', 'HCUP001'),
('DCUP490', 'District & Sessions Court, Lalitpur', 'UP', 'DIST', 'HCUP001'),
('DCUP500', 'District & Sessions Court, Lucknow', 'UP', 'DIST', 'HCUP001'),
('DCUP510', 'District & Sessions Court, Maharajganj', 'UP', 'DIST', 'HCUP001'),
('DCUP520', 'District & Sessions Court, Mahoba', 'UP', 'DIST', 'HCUP001'),
('DCUP530', 'District & Sessions Court, Mainpuri', 'UP', 'DIST', 'HCUP001'),
('DCUP540', 'District & Sessions Court, Mathura', 'UP', 'DIST', 'HCUP001'),
('DCUP550', 'District & Sessions Court, Mau', 'UP', 'DIST', 'HCUP001'),
('DCUP560', 'District & Sessions Court, Meerut', 'UP', 'DIST', 'HCUP001'),
('DCUP570', 'District & Sessions Court, Mirzapur', 'UP', 'DIST', 'HCUP001'),
('DCUP580', 'District & Sessions Court, Moradabad', 'UP', 'DIST', 'HCUP001'),
('DCUP590', 'District & Sessions Court, Muzaffarnagar', 'UP', 'DIST', 'HCUP001'),
('DCUP600', 'District & Sessions Court, Pilibhit', 'UP', 'DIST', 'HCUP001'),
('DCUP610', 'District & Sessions Court, Pratapgarh', 'UP', 'DIST', 'HCUP001'),
('DCUP620', 'District & Sessions Court, Prayagraj', 'UP', 'DIST', 'HCUP001'),
('DCUP630', 'District & Sessions Court, Rae Bareli', 'UP', 'DIST', 'HCUP001'),
('DCUP640', 'District & Sessions Court, Rampur', 'UP', 'DIST', 'HCUP001'),
('DCUP650', 'District & Sessions Court, Saharanpur', 'UP', 'DIST', 'HCUP001'),
('DCUP655', 'District & Sessions Court, Sambhal', 'UP', 'DIST', 'HCUP001'),
('DCUP660', 'District & Sessions Court, Sant Kabir Nagar', 'UP', 'DIST', 'HCUP001'),
('DCUP670', 'District & Sessions Court, Shahjahanpur', 'UP', 'DIST', 'HCUP001'),
('DCUP680', 'District & Sessions Court, Shamli', 'UP', 'DIST', 'HCUP001'),
('DCUP690', 'District & Sessions Court, Shravasti', 'UP', 'DIST', 'HCUP001'),
('DCUP700', 'District & Sessions Court, Siddharthnagar', 'UP', 'DIST', 'HCUP001'),
('DCUP710', 'District & Sessions Court, Sitapur', 'UP', 'DIST', 'HCUP001'),
('DCUP720', 'District & Sessions Court, Sonbhadra', 'UP', 'DIST', 'HCUP001'),
('DCUP730', 'District & Sessions Court, Sultanpur', 'UP', 'DIST', 'HCUP001'),
('DCUP740', 'District & Sessions Court, Unnao', 'UP', 'DIST', 'HCUP001'),
('DCUP750', 'District & Sessions Court, Varanasi', 'UP', 'DIST', 'HCUP001'),
('FCUP800', 'Family Court, Lucknow', 'UP', 'FAMI', 'HCUP001'),
('FCUP810', 'Family Court, Kanpur Nagar', 'UP', 'FAMI', 'HCUP001'),
('FCUP820', 'Family Court, Agra', 'UP', 'FAMI', 'HCUP001'),
('FCUP830', 'Family Court, Varanasi', 'UP', 'FAMI', 'HCUP001');

-- ============================================================
--  UTTARAKHAND  (UK)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCUK001', 'Uttarakhand High Court', 'UK', 'HIGH', NULL),
('DCUK020', 'District & Sessions Court, Almora', 'UK', 'DIST', 'HCUK001'),
('DCUK030', 'District & Sessions Court, Bageshwar', 'UK', 'DIST', 'HCUK001'),
('DCUK040', 'District & Sessions Court, Chamoli', 'UK', 'DIST', 'HCUK001'),
('DCUK050', 'District & Sessions Court, Champawat', 'UK', 'DIST', 'HCUK001'),
('DCUK060', 'District & Sessions Court, Dehradun', 'UK', 'DIST', 'HCUK001'),
('DCUK070', 'District & Sessions Court, Haridwar', 'UK', 'DIST', 'HCUK001'),
('DCUK080', 'District & Sessions Court, Nainital', 'UK', 'DIST', 'HCUK001'),
('DCUK090', 'District & Sessions Court, Pauri Garhwal', 'UK', 'DIST', 'HCUK001'),
('DCUK100', 'District & Sessions Court, Pithoragarh', 'UK', 'DIST', 'HCUK001'),
('DCUK110', 'District & Sessions Court, Rudraprayag', 'UK', 'DIST', 'HCUK001'),
('DCUK120', 'District & Sessions Court, Tehri Garhwal', 'UK', 'DIST', 'HCUK001'),
('DCUK130', 'District & Sessions Court, Udham Singh Nagar', 'UK', 'DIST', 'HCUK001'),
('DCUK140', 'District & Sessions Court, Uttarkashi', 'UK', 'DIST', 'HCUK001'),
('FCUK500', 'Family Court, Dehradun', 'UK', 'FAMI', 'HCUK001');

-- ============================================================
--  WEST BENGAL  (WB)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCWB001', 'Calcutta High Court', 'WB', 'HIGH', NULL),
('CIVIWB015', 'City Civil Court, Kolkata', 'WB', 'CIVI', 'HCWB001'),
('CIVIWB016', 'Small Causes Court, Kolkata', 'WB', 'CIVI', 'HCWB001'),
('DCWB020', 'District & Sessions Court, Alipurduar', 'WB', 'DIST', 'HCWB001'),
('DCWB030', 'District & Sessions Court, Bankura', 'WB', 'DIST', 'HCWB001'),
('DCWB040', 'District & Sessions Court, Birbhum', 'WB', 'DIST', 'HCWB001'),
('DCWB050', 'District & Sessions Court, Cooch Behar', 'WB', 'DIST', 'HCWB001'),
('DCWB060', 'District & Sessions Court, Dakshin Dinajpur', 'WB', 'DIST', 'HCWB001'),
('DCWB070', 'District & Sessions Court, Darjeeling', 'WB', 'DIST', 'HCWB001'),
('DCWB080', 'District & Sessions Court, Hooghly', 'WB', 'DIST', 'HCWB001'),
('DCWB090', 'District & Sessions Court, Howrah', 'WB', 'DIST', 'HCWB001'),
('DCWB100', 'District & Sessions Court, Jalpaiguri', 'WB', 'DIST', 'HCWB001'),
('DCWB110', 'District & Sessions Court, Jhargram', 'WB', 'DIST', 'HCWB001'),
('DCWB120', 'District & Sessions Court, Kalimpong', 'WB', 'DIST', 'HCWB001'),
('DCWB130', 'District & Sessions Court, Kolkata', 'WB', 'DIST', 'HCWB001'),
('DCWB140', 'District & Sessions Court, Maldah', 'WB', 'DIST', 'HCWB001'),
('DCWB150', 'District & Sessions Court, Murshidabad', 'WB', 'DIST', 'HCWB001'),
('DCWB160', 'District & Sessions Court, Nadia', 'WB', 'DIST', 'HCWB001'),
('DCWB170', 'District & Sessions Court, North 24 Parganas', 'WB', 'DIST', 'HCWB001'),
('DCWB180', 'District & Sessions Court, Paschim Bardhaman', 'WB', 'DIST', 'HCWB001'),
('DCWB190', 'District & Sessions Court, Paschim Medinipur', 'WB', 'DIST', 'HCWB001'),
('DCWB200', 'District & Sessions Court, Purba Bardhaman', 'WB', 'DIST', 'HCWB001'),
('DCWB210', 'District & Sessions Court, Purba Medinipur', 'WB', 'DIST', 'HCWB001'),
('DCWB220', 'District & Sessions Court, Purulia', 'WB', 'DIST', 'HCWB001'),
('DCWB230', 'District & Sessions Court, South 24 Parganas', 'WB', 'DIST', 'HCWB001'),
('DCWB240', 'District & Sessions Court, Uttar Dinajpur', 'WB', 'DIST', 'HCWB001'),
('FCWB500', 'Family Court, Kolkata', 'WB', 'FAMI', 'HCWB001');

-- ============================================================
--  UNION TERRITORIES
-- ============================================================

-- ============================================================
-- ANDAMAN & NICOBAR ISLANDS (AN)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCAN001', 'Calcutta High Court – A&N Circuit Bench', 'AN', 'HIGH', 'HCWB001'),
('DCAN020', 'District & Sessions Court, South Andaman', 'AN', 'DIST', 'HCAN001'),
('DCAN030', 'District & Sessions Court, North & Middle Andaman', 'AN', 'DIST', 'HCAN001'),
('DCAN040', 'District & Sessions Court, Nicobar', 'AN', 'DIST', 'HCAN001');

-- ============================================================
-- CHANDIGARH (CH)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCCH001', 'Punjab & Haryana High Court', 'CH', 'HIGH', NULL),
('DCCH020', 'District & Sessions Court, Chandigarh', 'CH', 'DIST', 'HCCH001'),
('FCCH500', 'Family Court, Chandigarh', 'CH', 'FAMI', 'HCCH001');

-- ============================================================
-- DADRA & NAGAR HAVELI AND DAMAN & DIU (DN)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCDN001', 'Bombay High Court – D&NH/D&D jurisdiction', 'DN', 'HIGH', 'HCMH001'),
('DCDN020', 'District & Sessions Court, Daman', 'DN', 'DIST', 'HCDN001'),
('DCDN030', 'District & Sessions Court, Dadra & Nagar Haveli', 'DN', 'DIST', 'HCDN001');

-- ============================================================
-- DELHI (NCT) (DL)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCDL001', 'Delhi High Court', 'DL', 'HIGH', NULL),
('DCDL020', 'District Court, Central Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL030', 'District Court, East Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL040', 'District Court, New Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL050', 'District Court, North Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL060', 'District Court, North East Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL070', 'District Court, North West Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL080', 'District Court, Rohini', 'DL', 'DIST', 'HCDL001'),
('DCDL090', 'District Court, Saket', 'DL', 'DIST', 'HCDL001'),
('DCDL100', 'District Court, Shahdara', 'DL', 'DIST', 'HCDL001'),
('DCDL110', 'District Court, South Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL120', 'District Court, South East Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL130', 'District Court, South West Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL140', 'District Court, West Delhi', 'DL', 'DIST', 'HCDL001'),
('DCDL150', 'Principal District & Sessions Court, Dwarka', 'DL', 'DIST', 'HCDL001'),
('FCDL500', 'Family Court, Delhi', 'DL', 'FAMI', 'HCDL001'),
('MAGIDL600', 'Chief Metropolitan Magistrate Court, Delhi', 'DL', 'MAGI', 'HCDL001');

-- ============================================================
-- JAMMU & KASHMIR (JK)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCJK001', 'J&K and Ladakh High Court', 'JK', 'HIGH', NULL),
('DCJK020', 'Principal District & Sessions Court, Anantnag', 'JK',  'DIST', 'HCJK001'),
('DCJK030', 'Principal District & Sessions Court, Bandipora', 'JK',  'DIST', 'HCJK001'),
('DCJK040', 'Principal District & Sessions Court, Baramulla', 'JK',  'DIST', 'HCJK001'),
('DCJK050', 'Principal District & Sessions Court, Budgam', 'JK',  'DIST', 'HCJK001'),
('DCJK060', 'Principal District & Sessions Court, Doda', 'JK',  'DIST', 'HCJK001'),
('DCJK070', 'Principal District & Sessions Court, Ganderbal', 'JK',  'DIST', 'HCJK001'),
('DCJK080', 'Principal District & Sessions Court, Jammu', 'JK',  'DIST', 'HCJK001'),
('DCJK090', 'Principal District & Sessions Court, Kathua', 'JK',  'DIST', 'HCJK001'),
('DCJK100', 'Principal District & Sessions Court, Kishtwar', 'JK',  'DIST', 'HCJK001'),
('DCJK110', 'Principal District & Sessions Court, Kulgam', 'JK',  'DIST', 'HCJK001'),
('DCJK120', 'Principal District & Sessions Court, Kupwara', 'JK',  'DIST', 'HCJK001'),
('DCJK130', 'Principal District & Sessions Court, Poonch', 'JK',  'DIST', 'HCJK001'),
('DCJK140', 'Principal District & Sessions Court, Pulwama', 'JK',  'DIST', 'HCJK001'),
('DCJK150', 'Principal District & Sessions Court, Rajouri', 'JK',  'DIST', 'HCJK001'),
('DCJK160', 'Principal District & Sessions Court, Ramban', 'JK',  'DIST', 'HCJK001'),
('DCJK170', 'Principal District & Sessions Court, Reasi', 'JK',  'DIST', 'HCJK001'),
('DCJK180', 'Principal District & Sessions Court, Samba', 'JK',  'DIST', 'HCJK001'),
('DCJK190', 'Principal District & Sessions Court, Shopian', 'JK',  'DIST', 'HCJK001'),
('DCJK200', 'Principal District & Sessions Court, Srinagar', 'JK',  'DIST', 'HCJK001'),
('DCJK210', 'Principal District & Sessions Court, Udhampur', 'JK',  'DIST', 'HCJK001'),
('FCJK500', 'Family Court, Srinagar', 'JK',  'FAMI', 'HCJK001'),
('FCJK510', 'Family Court, Jammu', 'JK',  'FAMI', 'HCJK001');

-- ============================================================
-- LADAKH (LA)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCLA001', 'J&K and Ladakh High Court', 'LA', 'HIGH', 'HCJK001'),
('DCLA020', 'District & Sessions Court, Kargil', 'LA', 'DIST', 'HCLA001'),
('DCLA030', 'District & Sessions Court, Leh', 'LA', 'DIST', 'HCLA001');

-- ============================================================
-- LAKSHADWEEP (LD)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCLD001', 'Kerala High Court – Lakshadweep jurisdiction', 'LD', 'HIGH', 'HCKL001'),
('DCLD020', 'District & Sessions Court, Kavaratti', 'LD', 'DIST', 'HCLD001');

-- ============================================================
-- PUDUCHERRY (PY)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('HCPY001', 'Madras High Court – Puducherry Bench', 'PY', 'HIGH', 'HCTN001'),
('DCPY020', 'District & Sessions Court, Puducherry', 'PY', 'DIST', 'HCPY001'),
('DCPY030', 'District & Sessions Court, Karaikal', 'PY', 'DIST', 'HCPY001'),
('DCPY040', 'District & Sessions Court, Mahe', 'PY', 'DIST', 'HCPY001'),
('DCPY050', 'District & Sessions Court, Yanam', 'PY', 'DIST', 'HCPY001'),
('FCPY500', 'Family Court, Puducherry', 'PY', 'FAMI', 'HCPY001');

-- ============================================================
-- NATIONAL TRIBUNALS (IN)
-- ============================================================
INSERT INTO courts (court_code, court_name, state_code, court_type_code, parent_court_code) VALUES
('TRIBIN010', 'National Green Tribunal (Principal Bench)', NULL, 'TRIB', NULL),
('TRIBIN020', 'National Consumer Disputes Redressal Commission', NULL, 'TRIB', NULL),
('TRIBIN030', 'Central Administrative Tribunal (Principal Bench)', NULL, 'TRIB', NULL),
('TRIBIN040', 'Armed Forces Tribunal (Principal Bench)', NULL, 'TRIB', NULL),
('TRIBIN050', 'Income Tax Appellate Tribunal (Principal Bench)', NULL, 'TRIB', NULL),
('TRIBIN060', 'Debt Recovery Appellate Tribunal, Delhi', NULL, 'TRIB', NULL),
('TRIBIN070', 'Competition Appellate Tribunal', NULL, 'TRIB', NULL),
('TRIBIN080', 'National Company Law Appellate Tribunal', NULL, 'TRIB', NULL),
('TRIBIN090', 'Intellectual Property Appellate Board', NULL, 'TRIB', NULL),
('TRIBIN100', 'Telecom Disputes Settlement & Appellate Tribunal', NULL, 'TRIB', NULL);

-- End of file
-- Total approximate rows: ~950
-- Coverage: 1 Supreme Court + 25 High Courts (incl. benches)
--           + 688 District Courts + Family Courts + Special Courts
--           + 10 National Tribunals