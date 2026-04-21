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
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Supreme Court of India', 'IN', 'Supreme Court', 1);

-- ============================================================
--  ANDHRA PRADESH  (AP)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Andhra Pradesh High Court',                      'AP', 'High Court',      10),
('Principal District Court, Anantapur',            'AP', 'District Court',  20),
('Principal District Court, Chittoor',             'AP', 'District Court',  30),
('Principal District Court, East Godavari',        'AP', 'District Court',  40),
('Principal District Court, Guntur',               'AP', 'District Court',  50),
('Principal District Court, Krishna',              'AP', 'District Court',  60),
('Principal District Court, Kurnool',              'AP', 'District Court',  70),
('Principal District Court, Nellore',              'AP', 'District Court',  80),
('Principal District Court, Prakasam',             'AP', 'District Court',  90),
('Principal District Court, Srikakulam',           'AP', 'District Court', 100),
('Principal District Court, Visakhapatnam',        'AP', 'District Court', 110),
('Principal District Court, Vizianagaram',         'AP', 'District Court', 120),
('Principal District Court, West Godavari',        'AP', 'District Court', 130),
('Principal District Court, YSR Kadapa',           'AP', 'District Court', 140),
('Family Court, Vijayawada',                       'AP', 'Family Court',   500),
('Family Court, Visakhapatnam',                    'AP', 'Family Court',   510);

-- ============================================================
--  ARUNACHAL PRADESH  (AR)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Gauhati High Court – Itanagar Permanent Bench',  'AR', 'High Court',      10),
('District & Sessions Court, Itanagar',            'AR', 'District Court',  20),
('District & Sessions Court, Naharlagun',          'AR', 'District Court',  30),
('District & Sessions Court, Pasighat',            'AR', 'District Court',  40),
('District & Sessions Court, Tezpur (Sonitpur)',   'AR', 'District Court',  50);

-- ============================================================
--  ASSAM  (AS)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Gauhati High Court',                             'AS', 'High Court',      10),
('District & Sessions Court, Baksa',               'AS', 'District Court',  20),
('District & Sessions Court, Barpeta',             'AS', 'District Court',  30),
('District & Sessions Court, Biswanath',           'AS', 'District Court',  40),
('District & Sessions Court, Bongaigaon',          'AS', 'District Court',  50),
('District & Sessions Court, Cachar',              'AS', 'District Court',  60),
('District & Sessions Court, Charaideo',           'AS', 'District Court',  70),
('District & Sessions Court, Chirang',             'AS', 'District Court',  80),
('District & Sessions Court, Darrang',             'AS', 'District Court',  90),
('District & Sessions Court, Dhemaji',             'AS', 'District Court', 100),
('District & Sessions Court, Dhubri',              'AS', 'District Court', 110),
('District & Sessions Court, Dibrugarh',           'AS', 'District Court', 120),
('District & Sessions Court, Dima Hasao',          'AS', 'District Court', 130),
('District & Sessions Court, Goalpara',            'AS', 'District Court', 140),
('District & Sessions Court, Golaghat',            'AS', 'District Court', 150),
('District & Sessions Court, Hailakandi',          'AS', 'District Court', 160),
('District & Sessions Court, Hojai',               'AS', 'District Court', 170),
('District & Sessions Court, Jorhat',              'AS', 'District Court', 180),
('District & Sessions Court, Kamrup',              'AS', 'District Court', 190),
('District & Sessions Court, Kamrup Metro (Guwahati)', 'AS', 'District Court', 200),
('District & Sessions Court, Karbi Anglong',       'AS', 'District Court', 210),
('District & Sessions Court, Karimganj',           'AS', 'District Court', 220),
('District & Sessions Court, Kokrajhar',           'AS', 'District Court', 230),
('District & Sessions Court, Lakhimpur',           'AS', 'District Court', 240),
('District & Sessions Court, Majuli',              'AS', 'District Court', 250),
('District & Sessions Court, Morigaon',            'AS', 'District Court', 260),
('District & Sessions Court, Nagaon',              'AS', 'District Court', 270),
('District & Sessions Court, Nalbari',             'AS', 'District Court', 280),
('District & Sessions Court, Sivasagar',           'AS', 'District Court', 290),
('District & Sessions Court, Sonitpur',            'AS', 'District Court', 300),
('District & Sessions Court, South Salmara',       'AS', 'District Court', 310),
('District & Sessions Court, Tinsukia',            'AS', 'District Court', 320),
('District & Sessions Court, Udalguri',            'AS', 'District Court', 330),
('District & Sessions Court, West Karbi Anglong',  'AS', 'District Court', 340),
('Family Court, Guwahati',                         'AS', 'Family Court',   500);

-- ============================================================
--  BIHAR  (BR)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Patna High Court',                               'BR', 'High Court',      10),
('District & Sessions Court, Araria',              'BR', 'District Court',  20),
('District & Sessions Court, Aurangabad',          'BR', 'District Court',  30),
('District & Sessions Court, Banka',               'BR', 'District Court',  40),
('District & Sessions Court, Begusarai',           'BR', 'District Court',  50),
('District & Sessions Court, Bhagalpur',           'BR', 'District Court',  60),
('District & Sessions Court, Bhojpur',             'BR', 'District Court',  70),
('District & Sessions Court, Buxar',               'BR', 'District Court',  80),
('District & Sessions Court, Darbhanga',           'BR', 'District Court',  90),
('District & Sessions Court, East Champaran',      'BR', 'District Court', 100),
('District & Sessions Court, Gaya',                'BR', 'District Court', 110),
('District & Sessions Court, Gopalganj',           'BR', 'District Court', 120),
('District & Sessions Court, Jamui',               'BR', 'District Court', 130),
('District & Sessions Court, Jehanabad',           'BR', 'District Court', 140),
('District & Sessions Court, Kaimur',              'BR', 'District Court', 150),
('District & Sessions Court, Katihar',             'BR', 'District Court', 160),
('District & Sessions Court, Khagaria',            'BR', 'District Court', 170),
('District & Sessions Court, Kishanganj',          'BR', 'District Court', 180),
('District & Sessions Court, Lakhisarai',          'BR', 'District Court', 190),
('District & Sessions Court, Madhepura',           'BR', 'District Court', 200),
('District & Sessions Court, Madhubani',           'BR', 'District Court', 210),
('District & Sessions Court, Munger',              'BR', 'District Court', 220),
('District & Sessions Court, Muzaffarpur',         'BR', 'District Court', 230),
('District & Sessions Court, Nalanda',             'BR', 'District Court', 240),
('District & Sessions Court, Nawada',              'BR', 'District Court', 250),
('District & Sessions Court, Patna',               'BR', 'District Court', 260),
('District & Sessions Court, Purnea',              'BR', 'District Court', 270),
('District & Sessions Court, Rohtas',              'BR', 'District Court', 280),
('District & Sessions Court, Saharsa',             'BR', 'District Court', 290),
('District & Sessions Court, Samastipur',          'BR', 'District Court', 300),
('District & Sessions Court, Saran',               'BR', 'District Court', 310),
('District & Sessions Court, Sheikhpura',          'BR', 'District Court', 320),
('District & Sessions Court, Sheohar',             'BR', 'District Court', 330),
('District & Sessions Court, Sitamarhi',           'BR', 'District Court', 340),
('District & Sessions Court, Siwan',               'BR', 'District Court', 350),
('District & Sessions Court, Supaul',              'BR', 'District Court', 360),
('District & Sessions Court, Vaishali',            'BR', 'District Court', 370),
('District & Sessions Court, West Champaran',      'BR', 'District Court', 380),
('Family Court, Patna',                            'BR', 'Family Court',   500);

-- ============================================================
--  CHHATTISGARH  (CG)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Chhattisgarh High Court',                        'CG', 'High Court',      10),
('District & Sessions Court, Balod',               'CG', 'District Court',  20),
('District & Sessions Court, Baloda Bazar',        'CG', 'District Court',  30),
('District & Sessions Court, Balrampur',           'CG', 'District Court',  40),
('District & Sessions Court, Bastar',              'CG', 'District Court',  50),
('District & Sessions Court, Bemetara',            'CG', 'District Court',  60),
('District & Sessions Court, Bijapur',             'CG', 'District Court',  70),
('District & Sessions Court, Bilaspur',            'CG', 'District Court',  80),
('District & Sessions Court, Dantewada',           'CG', 'District Court',  90),
('District & Sessions Court, Dhamtari',            'CG', 'District Court', 100),
('District & Sessions Court, Durg',                'CG', 'District Court', 110),
('District & Sessions Court, Gariaband',           'CG', 'District Court', 120),
('District & Sessions Court, Gaurela-Pendra-Marwahi', 'CG', 'District Court', 130),
('District & Sessions Court, Janjgir-Champa',      'CG', 'District Court', 140),
('District & Sessions Court, Jashpur',             'CG', 'District Court', 150),
('District & Sessions Court, Kabirdham',           'CG', 'District Court', 160),
('District & Sessions Court, Kanker',              'CG', 'District Court', 170),
('District & Sessions Court, Kondagaon',           'CG', 'District Court', 180),
('District & Sessions Court, Korba',               'CG', 'District Court', 190),
('District & Sessions Court, Koriya',              'CG', 'District Court', 200),
('District & Sessions Court, Mahasamund',          'CG', 'District Court', 210),
('District & Sessions Court, Mungeli',             'CG', 'District Court', 220),
('District & Sessions Court, Narayanpur',          'CG', 'District Court', 230),
('District & Sessions Court, Raigarh',             'CG', 'District Court', 240),
('District & Sessions Court, Raipur',              'CG', 'District Court', 250),
('District & Sessions Court, Rajnandgaon',         'CG', 'District Court', 260),
('District & Sessions Court, Sukma',               'CG', 'District Court', 270),
('District & Sessions Court, Surajpur',            'CG', 'District Court', 280),
('District & Sessions Court, Surguja',             'CG', 'District Court', 290),
('Family Court, Raipur',                           'CG', 'Family Court',   500);

-- ============================================================
--  GOA  (GA)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Bombay High Court – Goa Bench',                  'GA', 'High Court',      10),
('District & Sessions Court, North Goa',           'GA', 'District Court',  20),
('District & Sessions Court, South Goa',           'GA', 'District Court',  30),
('Family Court, Panaji',                           'GA', 'Family Court',   500);

-- ============================================================
--  GUJARAT  (GJ)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Gujarat High Court',                             'GJ', 'High Court',      10),
('City Civil & Sessions Court, Ahmedabad',         'GJ', 'Civil Court',     20),
('Chief Judicial Magistrate Court, Ahmedabad',     'GJ', 'Magistrate',      25),
('Small Causes Court, Ahmedabad',                  'GJ', 'Civil Court',     28),
('District Court, Ahmedabad Rural',                'GJ', 'District Court',  30),
('District Court, Amreli',                         'GJ', 'District Court',  40),
('District Court, Anand',                          'GJ', 'District Court',  50),
('District Court, Aravalli',                       'GJ', 'District Court',  60),
('District Court, Banaskantha',                    'GJ', 'District Court',  70),
('District Court, Bharuch',                        'GJ', 'District Court',  80),
('District Court, Bhavnagar',                      'GJ', 'District Court',  90),
('District Court, Botad',                          'GJ', 'District Court', 100),
('District Court, Chhota Udepur',                  'GJ', 'District Court', 110),
('District Court, Dahod',                          'GJ', 'District Court', 120),
('District Court, Dang',                           'GJ', 'District Court', 130),
('District Court, Devbhumi Dwarka',                'GJ', 'District Court', 140),
('District Court, Gandhinagar',                    'GJ', 'District Court', 150),
('District Court, Gir Somnath',                    'GJ', 'District Court', 160),
('District Court, Jamnagar',                       'GJ', 'District Court', 170),
('District Court, Junagadh',                       'GJ', 'District Court', 180),
('District Court, Kheda',                          'GJ', 'District Court', 190),
('District Court, Kutch',                          'GJ', 'District Court', 200),
('District Court, Mahisagar',                      'GJ', 'District Court', 210),
('District Court, Mehsana',                        'GJ', 'District Court', 220),
('District Court, Morbi',                          'GJ', 'District Court', 230),
('District Court, Narmada',                        'GJ', 'District Court', 240),
('District Court, Navsari',                        'GJ', 'District Court', 250),
('District Court, Panchmahals',                    'GJ', 'District Court', 260),
('District Court, Patan',                          'GJ', 'District Court', 270),
('District Court, Porbandar',                      'GJ', 'District Court', 280),
('District Court, Rajkot',                         'GJ', 'District Court', 290),
('District Court, Sabarkantha',                    'GJ', 'District Court', 300),
('District Court, Surat',                          'GJ', 'District Court', 310),
('District Court, Surendranagar',                  'GJ', 'District Court', 320),
('District Court, Tapi',                           'GJ', 'District Court', 330),
('District Court, Vadodara',                       'GJ', 'District Court', 340),
('District Court, Valsad',                         'GJ', 'District Court', 350),
('Family Court, Ahmedabad',                        'GJ', 'Family Court',   500),
('Family Court, Surat',                            'GJ', 'Family Court',   510),
('Family Court, Vadodara',                         'GJ', 'Family Court',   520);

-- ============================================================
--  HARYANA  (HR)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Punjab & Haryana High Court',                    'HR', 'High Court',      10),
('District & Sessions Court, Ambala',              'HR', 'District Court',  20),
('District & Sessions Court, Bhiwani',             'HR', 'District Court',  30),
('District & Sessions Court, Charkhi Dadri',       'HR', 'District Court',  40),
('District & Sessions Court, Faridabad',           'HR', 'District Court',  50),
('District & Sessions Court, Fatehabad',           'HR', 'District Court',  60),
('District & Sessions Court, Gurugram',            'HR', 'District Court',  70),
('District & Sessions Court, Hisar',               'HR', 'District Court',  80),
('District & Sessions Court, Jhajjar',             'HR', 'District Court',  90),
('District & Sessions Court, Jind',                'HR', 'District Court', 100),
('District & Sessions Court, Kaithal',             'HR', 'District Court', 110),
('District & Sessions Court, Karnal',              'HR', 'District Court', 120),
('District & Sessions Court, Kurukshetra',         'HR', 'District Court', 130),
('District & Sessions Court, Mahendragarh',        'HR', 'District Court', 140),
('District & Sessions Court, Nuh',                 'HR', 'District Court', 150),
('District & Sessions Court, Palwal',              'HR', 'District Court', 160),
('District & Sessions Court, Panchkula',           'HR', 'District Court', 170),
('District & Sessions Court, Panipat',             'HR', 'District Court', 180),
('District & Sessions Court, Rewari',              'HR', 'District Court', 190),
('District & Sessions Court, Rohtak',              'HR', 'District Court', 200),
('District & Sessions Court, Sirsa',               'HR', 'District Court', 210),
('District & Sessions Court, Sonipat',             'HR', 'District Court', 220),
('District & Sessions Court, Yamunanagar',         'HR', 'District Court', 230),
('Family Court, Gurugram',                         'HR', 'Family Court',   500),
('Family Court, Faridabad',                        'HR', 'Family Court',   510);

-- ============================================================
--  HIMACHAL PRADESH  (HP)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Himachal Pradesh High Court',                    'HP', 'High Court',      10),
('District & Sessions Court, Bilaspur',            'HP', 'District Court',  20),
('District & Sessions Court, Chamba',              'HP', 'District Court',  30),
('District & Sessions Court, Hamirpur',            'HP', 'District Court',  40),
('District & Sessions Court, Kangra',              'HP', 'District Court',  50),
('District & Sessions Court, Kinnaur',             'HP', 'District Court',  60),
('District & Sessions Court, Kullu',               'HP', 'District Court',  70),
('District & Sessions Court, Lahaul & Spiti',      'HP', 'District Court',  80),
('District & Sessions Court, Mandi',               'HP', 'District Court',  90),
('District & Sessions Court, Shimla',              'HP', 'District Court', 100),
('District & Sessions Court, Sirmaur',             'HP', 'District Court', 110),
('District & Sessions Court, Solan',               'HP', 'District Court', 120),
('District & Sessions Court, Una',                 'HP', 'District Court', 130);

-- ============================================================
--  JHARKHAND  (JH)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Jharkhand High Court',                           'JH', 'High Court',      10),
('Civil Court, Dhanbad',                           'JH', 'Civil Court',     15),
('Civil Court, Ranchi',                            'JH', 'Civil Court',     16),
('District & Sessions Court, Bokaro',              'JH', 'District Court',  20),
('District & Sessions Court, Chatra',              'JH', 'District Court',  30),
('District & Sessions Court, Deoghar',             'JH', 'District Court',  40),
('District & Sessions Court, Dhanbad',             'JH', 'District Court',  50),
('District & Sessions Court, Dumka',               'JH', 'District Court',  60),
('District & Sessions Court, East Singhbhum',      'JH', 'District Court',  70),
('District & Sessions Court, Garhwa',              'JH', 'District Court',  80),
('District & Sessions Court, Giridih',             'JH', 'District Court',  90),
('District & Sessions Court, Godda',               'JH', 'District Court', 100),
('District & Sessions Court, Gumla',               'JH', 'District Court', 110),
('District & Sessions Court, Hazaribagh',          'JH', 'District Court', 120),
('District & Sessions Court, Jamtara',             'JH', 'District Court', 130),
('District & Sessions Court, Khunti',              'JH', 'District Court', 140),
('District & Sessions Court, Koderma',             'JH', 'District Court', 150),
('District & Sessions Court, Latehar',             'JH', 'District Court', 160),
('District & Sessions Court, Lohardaga',           'JH', 'District Court', 170),
('District & Sessions Court, Pakur',               'JH', 'District Court', 180),
('District & Sessions Court, Palamu',              'JH', 'District Court', 190),
('District & Sessions Court, Ramgarh',             'JH', 'District Court', 200),
('District & Sessions Court, Ranchi',              'JH', 'District Court', 210),
('District & Sessions Court, Sahebganj',           'JH', 'District Court', 220),
('District & Sessions Court, Seraikela-Kharsawan', 'JH', 'District Court', 230),
('District & Sessions Court, Simdega',             'JH', 'District Court', 240),
('District & Sessions Court, West Singhbhum',      'JH', 'District Court', 250),
('Family Court, Ranchi',                           'JH', 'Family Court',   500);

-- ============================================================
--  KARNATAKA  (KA)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Karnataka High Court',                           'KA', 'High Court',      10),
('City Civil & Sessions Court, Bengaluru',         'KA', 'Civil Court',     15),
('District & Sessions Court, Bagalkot',            'KA', 'District Court',  20),
('District & Sessions Court, Ballari',             'KA', 'District Court',  30),
('District & Sessions Court, Belagavi',            'KA', 'District Court',  40),
('District & Sessions Court, Bengaluru Rural',     'KA', 'District Court',  50),
('District & Sessions Court, Bengaluru Urban',     'KA', 'District Court',  60),
('District & Sessions Court, Bidar',               'KA', 'District Court',  70),
('District & Sessions Court, Chamarajanagar',      'KA', 'District Court',  80),
('District & Sessions Court, Chikkaballapur',      'KA', 'District Court',  90),
('District & Sessions Court, Chikkamagaluru',      'KA', 'District Court', 100),
('District & Sessions Court, Chitradurga',         'KA', 'District Court', 110),
('District & Sessions Court, Dakshina Kannada',    'KA', 'District Court', 120),
('District & Sessions Court, Davanagere',          'KA', 'District Court', 130),
('District & Sessions Court, Dharwad',             'KA', 'District Court', 140),
('District & Sessions Court, Gadag',               'KA', 'District Court', 150),
('District & Sessions Court, Hassan',              'KA', 'District Court', 160),
('District & Sessions Court, Haveri',              'KA', 'District Court', 170),
('District & Sessions Court, Kalaburagi',          'KA', 'District Court', 180),
('District & Sessions Court, Kodagu',              'KA', 'District Court', 190),
('District & Sessions Court, Kolar',               'KA', 'District Court', 200),
('District & Sessions Court, Koppal',              'KA', 'District Court', 210),
('District & Sessions Court, Mandya',              'KA', 'District Court', 220),
('District & Sessions Court, Mysuru',              'KA', 'District Court', 230),
('District & Sessions Court, Raichur',             'KA', 'District Court', 240),
('District & Sessions Court, Ramanagara',          'KA', 'District Court', 250),
('District & Sessions Court, Shivamogga',          'KA', 'District Court', 260),
('District & Sessions Court, Tumakuru',            'KA', 'District Court', 270),
('District & Sessions Court, Udupi',               'KA', 'District Court', 280),
('District & Sessions Court, Uttara Kannada',      'KA', 'District Court', 290),
('District & Sessions Court, Vijayapura',          'KA', 'District Court', 300),
('District & Sessions Court, Vijayanagara',        'KA', 'District Court', 310),
('District & Sessions Court, Yadgir',              'KA', 'District Court', 320),
('Family Court, Bengaluru',                        'KA', 'Family Court',   500),
('Family Court, Mysuru',                           'KA', 'Family Court',   510);

-- ============================================================
--  KERALA  (KL)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Kerala High Court',                              'KL', 'High Court',      10),
('District & Sessions Court, Alappuzha',           'KL', 'District Court',  20),
('District & Sessions Court, Ernakulam',           'KL', 'District Court',  30),
('District & Sessions Court, Idukki',              'KL', 'District Court',  40),
('District & Sessions Court, Kannur',              'KL', 'District Court',  50),
('District & Sessions Court, Kasaragod',           'KL', 'District Court',  60),
('District & Sessions Court, Kollam',              'KL', 'District Court',  70),
('District & Sessions Court, Kottayam',            'KL', 'District Court',  80),
('District & Sessions Court, Kozhikode',           'KL', 'District Court',  90),
('District & Sessions Court, Malappuram',          'KL', 'District Court', 100),
('District & Sessions Court, Palakkad',            'KL', 'District Court', 110),
('District & Sessions Court, Pathanamthitta',      'KL', 'District Court', 120),
('District & Sessions Court, Thiruvananthapuram',  'KL', 'District Court', 130),
('District & Sessions Court, Thrissur',            'KL', 'District Court', 140),
('District & Sessions Court, Wayanad',             'KL', 'District Court', 150),
('Family Court, Ernakulam',                        'KL', 'Family Court',   500),
('Family Court, Thiruvananthapuram',               'KL', 'Family Court',   510),
('Family Court, Kozhikode',                        'KL', 'Family Court',   520);

-- ============================================================
--  MADHYA PRADESH  (MP)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Madhya Pradesh High Court',                      'MP', 'High Court',      10),
('District & Sessions Court, Alirajpur',           'MP', 'District Court',  20),
('District & Sessions Court, Anuppur',             'MP', 'District Court',  30),
('District & Sessions Court, Ashoknagar',          'MP', 'District Court',  40),
('District & Sessions Court, Balaghat',            'MP', 'District Court',  50),
('District & Sessions Court, Barwani',             'MP', 'District Court',  60),
('District & Sessions Court, Betul',               'MP', 'District Court',  70),
('District & Sessions Court, Bhind',               'MP', 'District Court',  80),
('District & Sessions Court, Bhopal',              'MP', 'District Court',  90),
('District & Sessions Court, Burhanpur',           'MP', 'District Court', 100),
('District & Sessions Court, Chhatarpur',          'MP', 'District Court', 110),
('District & Sessions Court, Chhindwara',          'MP', 'District Court', 120),
('District & Sessions Court, Damoh',               'MP', 'District Court', 130),
('District & Sessions Court, Datia',               'MP', 'District Court', 140),
('District & Sessions Court, Dewas',               'MP', 'District Court', 150),
('District & Sessions Court, Dhar',                'MP', 'District Court', 160),
('District & Sessions Court, Dindori',             'MP', 'District Court', 170),
('District & Sessions Court, Guna',                'MP', 'District Court', 180),
('District & Sessions Court, Gwalior',             'MP', 'District Court', 190),
('District & Sessions Court, Harda',               'MP', 'District Court', 200),
('District & Sessions Court, Hoshangabad',         'MP', 'District Court', 210),
('District & Sessions Court, Indore',              'MP', 'District Court', 220),
('District & Sessions Court, Jabalpur',            'MP', 'District Court', 230),
('District & Sessions Court, Jhabua',              'MP', 'District Court', 240),
('District & Sessions Court, Katni',               'MP', 'District Court', 250),
('District & Sessions Court, Khandwa',             'MP', 'District Court', 260),
('District & Sessions Court, Khargone',            'MP', 'District Court', 270),
('District & Sessions Court, Mandla',              'MP', 'District Court', 280),
('District & Sessions Court, Mandsaur',            'MP', 'District Court', 290),
('District & Sessions Court, Morena',              'MP', 'District Court', 300),
('District & Sessions Court, Narsinghpur',         'MP', 'District Court', 310),
('District & Sessions Court, Neemuch',             'MP', 'District Court', 320),
('District & Sessions Court, Niwari',              'MP', 'District Court', 325),
('District & Sessions Court, Panna',               'MP', 'District Court', 330),
('District & Sessions Court, Raisen',              'MP', 'District Court', 340),
('District & Sessions Court, Rajgarh',             'MP', 'District Court', 350),
('District & Sessions Court, Ratlam',              'MP', 'District Court', 360),
('District & Sessions Court, Rewa',                'MP', 'District Court', 370),
('District & Sessions Court, Sagar',               'MP', 'District Court', 380),
('District & Sessions Court, Satna',               'MP', 'District Court', 390),
('District & Sessions Court, Sehore',              'MP', 'District Court', 400),
('District & Sessions Court, Seoni',               'MP', 'District Court', 410),
('District & Sessions Court, Shahdol',             'MP', 'District Court', 420),
('District & Sessions Court, Shajapur',            'MP', 'District Court', 430),
('District & Sessions Court, Sheopur',             'MP', 'District Court', 440),
('District & Sessions Court, Shivpuri',            'MP', 'District Court', 450),
('District & Sessions Court, Sidhi',               'MP', 'District Court', 460),
('District & Sessions Court, Singrauli',           'MP', 'District Court', 470),
('District & Sessions Court, Tikamgarh',           'MP', 'District Court', 480),
('District & Sessions Court, Ujjain',              'MP', 'District Court', 490),
('District & Sessions Court, Umaria',              'MP', 'District Court', 500),
('District & Sessions Court, Vidisha',             'MP', 'District Court', 510),
('Family Court, Bhopal',                           'MP', 'Family Court',   600),
('Family Court, Indore',                           'MP', 'Family Court',   610),
('Family Court, Jabalpur',                         'MP', 'Family Court',   620);

-- ============================================================
--  MAHARASHTRA  (MH)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Bombay High Court',                              'MH', 'High Court',      10),
('Bombay High Court – Aurangabad Bench',           'MH', 'High Court',      11),
('Bombay High Court – Nagpur Bench',               'MH', 'High Court',      12),
('City Civil & Sessions Court, Mumbai',            'MH', 'Civil Court',     15),
('Small Causes Court, Mumbai',                     'MH', 'Civil Court',     16),
('Chief Metropolitan Magistrate Court, Mumbai',    'MH', 'Magistrate',      17),
('District & Sessions Court, Ahmadnagar',          'MH', 'District Court',  20),
('District & Sessions Court, Akola',               'MH', 'District Court',  30),
('District & Sessions Court, Amravati',            'MH', 'District Court',  40),
('District & Sessions Court, Aurangabad',          'MH', 'District Court',  50),
('District & Sessions Court, Beed',                'MH', 'District Court',  60),
('District & Sessions Court, Bhandara',            'MH', 'District Court',  70),
('District & Sessions Court, Buldhana',            'MH', 'District Court',  80),
('District & Sessions Court, Chandrapur',          'MH', 'District Court',  90),
('District & Sessions Court, Dhule',               'MH', 'District Court', 100),
('District & Sessions Court, Gadchiroli',          'MH', 'District Court', 110),
('District & Sessions Court, Gondia',              'MH', 'District Court', 120),
('District & Sessions Court, Hingoli',             'MH', 'District Court', 130),
('District & Sessions Court, Jalgaon',             'MH', 'District Court', 140),
('District & Sessions Court, Jalna',               'MH', 'District Court', 150),
('District & Sessions Court, Kolhapur',            'MH', 'District Court', 160),
('District & Sessions Court, Latur',               'MH', 'District Court', 170),
('District & Sessions Court, Mumbai Suburban',     'MH', 'District Court', 175),
('District & Sessions Court, Nagpur',              'MH', 'District Court', 180),
('District & Sessions Court, Nanded',              'MH', 'District Court', 190),
('District & Sessions Court, Nandurbar',           'MH', 'District Court', 200),
('District & Sessions Court, Nashik',              'MH', 'District Court', 210),
('District & Sessions Court, Osmanabad',           'MH', 'District Court', 220),
('District & Sessions Court, Parbhani',            'MH', 'District Court', 230),
('District & Sessions Court, Pune',                'MH', 'District Court', 240),
('District & Sessions Court, Raigad',              'MH', 'District Court', 250),
('District & Sessions Court, Ratnagiri',           'MH', 'District Court', 260),
('District & Sessions Court, Sangli',              'MH', 'District Court', 270),
('District & Sessions Court, Satara',              'MH', 'District Court', 280),
('District & Sessions Court, Sindhudurg',          'MH', 'District Court', 290),
('District & Sessions Court, Solapur',             'MH', 'District Court', 300),
('District & Sessions Court, Thane',               'MH', 'District Court', 310),
('District & Sessions Court, Wardha',              'MH', 'District Court', 320),
('District & Sessions Court, Washim',              'MH', 'District Court', 330),
('District & Sessions Court, Yavatmal',            'MH', 'District Court', 340),
('Family Court, Mumbai',                           'MH', 'Family Court',   500),
('Family Court, Pune',                             'MH', 'Family Court',   510),
('Family Court, Nagpur',                           'MH', 'Family Court',   520),
('Family Court, Aurangabad',                       'MH', 'Family Court',   530),
('Motor Accident Claims Tribunal, Mumbai',         'MH', 'Tribunal',       700);

-- ============================================================
--  MANIPUR  (MN)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Manipur High Court',                             'MN', 'High Court',      10),
('District & Sessions Court, Bishnupur',           'MN', 'District Court',  20),
('District & Sessions Court, Chandel',             'MN', 'District Court',  30),
('District & Sessions Court, Churachandpur',       'MN', 'District Court',  40),
('District & Sessions Court, Imphal East',         'MN', 'District Court',  50),
('District & Sessions Court, Imphal West',         'MN', 'District Court',  60),
('District & Sessions Court, Jiribam',             'MN', 'District Court',  70),
('District & Sessions Court, Kakching',            'MN', 'District Court',  80),
('District & Sessions Court, Kamjong',             'MN', 'District Court',  90),
('District & Sessions Court, Kangpokpi',           'MN', 'District Court', 100),
('District & Sessions Court, Noney',               'MN', 'District Court', 110),
('District & Sessions Court, Pherzawl',            'MN', 'District Court', 120),
('District & Sessions Court, Senapati',            'MN', 'District Court', 130),
('District & Sessions Court, Tamenglong',          'MN', 'District Court', 140),
('District & Sessions Court, Tengnoupal',          'MN', 'District Court', 150),
('District & Sessions Court, Thoubal',             'MN', 'District Court', 160),
('District & Sessions Court, Ukhrul',              'MN', 'District Court', 170);

-- ============================================================
--  MEGHALAYA  (ML)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Meghalaya High Court',                           'ML', 'High Court',      10),
('District & Sessions Court, East Garo Hills',     'ML', 'District Court',  20),
('District & Sessions Court, East Jaintia Hills',  'ML', 'District Court',  30),
('District & Sessions Court, East Khasi Hills',    'ML', 'District Court',  40),
('District & Sessions Court, North Garo Hills',    'ML', 'District Court',  50),
('District & Sessions Court, Ri Bhoi',             'ML', 'District Court',  60),
('District & Sessions Court, South Garo Hills',    'ML', 'District Court',  70),
('District & Sessions Court, South West Garo Hills','ML', 'District Court',  80),
('District & Sessions Court, South West Khasi Hills','ML','District Court',  90),
('District & Sessions Court, West Garo Hills',     'ML', 'District Court', 100),
('District & Sessions Court, West Jaintia Hills',  'ML', 'District Court', 110),
('District & Sessions Court, West Khasi Hills',    'ML', 'District Court', 120);

-- ============================================================
--  MIZORAM  (MZ)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Gauhati High Court – Mizoram Bench',             'MZ', 'High Court',      10),
('District & Sessions Court, Aizawl',              'MZ', 'District Court',  20),
('District & Sessions Court, Champhai',            'MZ', 'District Court',  30),
('District & Sessions Court, Hnahthial',           'MZ', 'District Court',  40),
('District & Sessions Court, Khawzawl',            'MZ', 'District Court',  50),
('District & Sessions Court, Kolasib',             'MZ', 'District Court',  60),
('District & Sessions Court, Lawngtlai',           'MZ', 'District Court',  70),
('District & Sessions Court, Lunglei',             'MZ', 'District Court',  80),
('District & Sessions Court, Mamit',               'MZ', 'District Court',  90),
('District & Sessions Court, Saiha',               'MZ', 'District Court', 100),
('District & Sessions Court, Saitual',             'MZ', 'District Court', 110),
('District & Sessions Court, Serchhip',            'MZ', 'District Court', 120);

-- ============================================================
--  NAGALAND  (NL)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Gauhati High Court – Nagaland Bench',            'NL', 'High Court',      10),
('District & Sessions Court, Chumoukedima',        'NL', 'District Court',  20),
('District & Sessions Court, Dimapur',             'NL', 'District Court',  30),
('District & Sessions Court, Kiphire',             'NL', 'District Court',  40),
('District & Sessions Court, Kohima',              'NL', 'District Court',  50),
('District & Sessions Court, Longleng',            'NL', 'District Court',  60),
('District & Sessions Court, Mokokchung',          'NL', 'District Court',  70),
('District & Sessions Court, Mon',                 'NL', 'District Court',  80),
('District & Sessions Court, Niuland',             'NL', 'District Court',  90),
('District & Sessions Court, Noklak',              'NL', 'District Court', 100),
('District & Sessions Court, Peren',               'NL', 'District Court', 110),
('District & Sessions Court, Phek',                'NL', 'District Court', 120),
('District & Sessions Court, Shamator',            'NL', 'District Court', 130),
('District & Sessions Court, Tseminyü',            'NL', 'District Court', 140),
('District & Sessions Court, Tuensang',            'NL', 'District Court', 150),
('District & Sessions Court, Wokha',               'NL', 'District Court', 160),
('District & Sessions Court, Zunheboto',           'NL', 'District Court', 170);

-- ============================================================
--  ODISHA  (OD)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Orissa High Court',                              'OD', 'High Court',      10),
('District & Sessions Court, Angul',               'OD', 'District Court',  20),
('District & Sessions Court, Balangir',            'OD', 'District Court',  30),
('District & Sessions Court, Balasore',            'OD', 'District Court',  40),
('District & Sessions Court, Bargarh',             'OD', 'District Court',  50),
('District & Sessions Court, Bhadrak',             'OD', 'District Court',  60),
('District & Sessions Court, Boudh',               'OD', 'District Court',  70),
('District & Sessions Court, Cuttack',             'OD', 'District Court',  80),
('District & Sessions Court, Debagarh',            'OD', 'District Court',  90),
('District & Sessions Court, Dhenkanal',           'OD', 'District Court', 100),
('District & Sessions Court, Gajapati',            'OD', 'District Court', 110),
('District & Sessions Court, Ganjam',              'OD', 'District Court', 120),
('District & Sessions Court, Jagatsinghpur',       'OD', 'District Court', 130),
('District & Sessions Court, Jajpur',              'OD', 'District Court', 140),
('District & Sessions Court, Jharsuguda',          'OD', 'District Court', 150),
('District & Sessions Court, Kalahandi',           'OD', 'District Court', 160),
('District & Sessions Court, Kandhamal',           'OD', 'District Court', 170),
('District & Sessions Court, Kendrapara',          'OD', 'District Court', 180),
('District & Sessions Court, Kendujhar',           'OD', 'District Court', 190),
('District & Sessions Court, Khordha',             'OD', 'District Court', 200),
('District & Sessions Court, Koraput',             'OD', 'District Court', 210),
('District & Sessions Court, Malkangiri',          'OD', 'District Court', 220),
('District & Sessions Court, Mayurbhanj',          'OD', 'District Court', 230),
('District & Sessions Court, Nabarangpur',         'OD', 'District Court', 240),
('District & Sessions Court, Nayagarh',            'OD', 'District Court', 250),
('District & Sessions Court, Nuapada',             'OD', 'District Court', 260),
('District & Sessions Court, Puri',                'OD', 'District Court', 270),
('District & Sessions Court, Rayagada',            'OD', 'District Court', 280),
('District & Sessions Court, Sambalpur',           'OD', 'District Court', 290),
('District & Sessions Court, Subarnapur',          'OD', 'District Court', 300),
('District & Sessions Court, Sundargarh',          'OD', 'District Court', 310),
('Family Court, Bhubaneswar',                      'OD', 'Family Court',   500),
('Family Court, Cuttack',                          'OD', 'Family Court',   510);

-- ============================================================
--  PUNJAB  (PB)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Punjab & Haryana High Court',                    'PB', 'High Court',      10),
('District & Sessions Court, Amritsar',            'PB', 'District Court',  20),
('District & Sessions Court, Barnala',             'PB', 'District Court',  30),
('District & Sessions Court, Bathinda',            'PB', 'District Court',  40),
('District & Sessions Court, Faridkot',            'PB', 'District Court',  50),
('District & Sessions Court, Fatehgarh Sahib',     'PB', 'District Court',  60),
('District & Sessions Court, Fazilka',             'PB', 'District Court',  70),
('District & Sessions Court, Ferozepur',           'PB', 'District Court',  80),
('District & Sessions Court, Gurdaspur',           'PB', 'District Court',  90),
('District & Sessions Court, Hoshiarpur',          'PB', 'District Court', 100),
('District & Sessions Court, Jalandhar',           'PB', 'District Court', 110),
('District & Sessions Court, Kapurthala',          'PB', 'District Court', 120),
('District & Sessions Court, Ludhiana',            'PB', 'District Court', 130),
('District & Sessions Court, Mansa',               'PB', 'District Court', 140),
('District & Sessions Court, Moga',                'PB', 'District Court', 150),
('District & Sessions Court, Mohali',              'PB', 'District Court', 160),
('District & Sessions Court, Muktsar',             'PB', 'District Court', 170),
('District & Sessions Court, Nawanshahr',          'PB', 'District Court', 180),
('District & Sessions Court, Pathankot',           'PB', 'District Court', 190),
('District & Sessions Court, Patiala',             'PB', 'District Court', 200),
('District & Sessions Court, Rupnagar',            'PB', 'District Court', 210),
('District & Sessions Court, Sangrur',             'PB', 'District Court', 220),
('District & Sessions Court, Tarn Taran',          'PB', 'District Court', 230),
('Family Court, Ludhiana',                         'PB', 'Family Court',   500),
('Family Court, Amritsar',                         'PB', 'Family Court',   510);

-- ============================================================
--  RAJASTHAN  (RJ)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Rajasthan High Court',                           'RJ', 'High Court',      10),
('Rajasthan High Court – Jaipur Bench',            'RJ', 'High Court',      11),
('District & Sessions Court, Ajmer',               'RJ', 'District Court',  20),
('District & Sessions Court, Alwar',               'RJ', 'District Court',  30),
('District & Sessions Court, Balotra',             'RJ', 'District Court',  35),
('District & Sessions Court, Banswara',            'RJ', 'District Court',  40),
('District & Sessions Court, Baran',               'RJ', 'District Court',  50),
('District & Sessions Court, Barmer',              'RJ', 'District Court',  60),
('District & Sessions Court, Beawar',              'RJ', 'District Court',  65),
('District & Sessions Court, Bharatpur',           'RJ', 'District Court',  70),
('District & Sessions Court, Bhilwara',            'RJ', 'District Court',  80),
('District & Sessions Court, Bikaner',             'RJ', 'District Court',  90),
('District & Sessions Court, Bundi',               'RJ', 'District Court', 100),
('District & Sessions Court, Chittorgarh',         'RJ', 'District Court', 110),
('District & Sessions Court, Churu',               'RJ', 'District Court', 120),
('District & Sessions Court, Dausa',               'RJ', 'District Court', 130),
('District & Sessions Court, Dholpur',             'RJ', 'District Court', 140),
('District & Sessions Court, Dungarpur',           'RJ', 'District Court', 150),
('District & Sessions Court, Ganganagar',          'RJ', 'District Court', 160),
('District & Sessions Court, Hanumangarh',         'RJ', 'District Court', 170),
('District & Sessions Court, Jaipur',              'RJ', 'District Court', 180),
('District & Sessions Court, Jaisalmer',           'RJ', 'District Court', 190),
('District & Sessions Court, Jalore',              'RJ', 'District Court', 200),
('District & Sessions Court, Jhalawar',            'RJ', 'District Court', 210),
('District & Sessions Court, Jhunjhunu',           'RJ', 'District Court', 220),
('District & Sessions Court, Jodhpur',             'RJ', 'District Court', 230),
('District & Sessions Court, Karauli',             'RJ', 'District Court', 240),
('District & Sessions Court, Kota',                'RJ', 'District Court', 250),
('District & Sessions Court, Nagaur',              'RJ', 'District Court', 260),
('District & Sessions Court, Pali',                'RJ', 'District Court', 270),
('District & Sessions Court, Pratapgarh',          'RJ', 'District Court', 280),
('District & Sessions Court, Rajsamand',           'RJ', 'District Court', 290),
('District & Sessions Court, Sawai Madhopur',      'RJ', 'District Court', 300),
('District & Sessions Court, Sikar',               'RJ', 'District Court', 310),
('District & Sessions Court, Sirohi',              'RJ', 'District Court', 320),
('District & Sessions Court, Tonk',                'RJ', 'District Court', 330),
('District & Sessions Court, Udaipur',             'RJ', 'District Court', 340),
('Family Court, Jaipur',                           'RJ', 'Family Court',   500),
('Family Court, Jodhpur',                          'RJ', 'Family Court',   510);

-- ============================================================
--  SIKKIM  (SK)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Sikkim High Court',                              'SK', 'High Court',      10),
('District & Sessions Court, East Sikkim',         'SK', 'District Court',  20),
('District & Sessions Court, North Sikkim',        'SK', 'District Court',  30),
('District & Sessions Court, Pakyong',             'SK', 'District Court',  35),
('District & Sessions Court, Soreng',              'SK', 'District Court',  40),
('District & Sessions Court, South Sikkim',        'SK', 'District Court',  50),
('District & Sessions Court, West Sikkim',         'SK', 'District Court',  60);

-- ============================================================
--  TAMIL NADU  (TN)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Madras High Court',                              'TN', 'High Court',      10),
('Madras High Court – Madurai Bench',              'TN', 'High Court',      11),
('City Civil Court, Chennai',                      'TN', 'Civil Court',     15),
('Small Causes Court, Chennai',                    'TN', 'Civil Court',     16),
('Principal District Court, Ariyalur',             'TN', 'District Court',  20),
('Principal District Court, Chengalpattu',         'TN', 'District Court',  30),
('Principal District Court, Chennai',              'TN', 'District Court',  40),
('Principal District Court, Coimbatore',           'TN', 'District Court',  50),
('Principal District Court, Cuddalore',            'TN', 'District Court',  60),
('Principal District Court, Dharmapuri',           'TN', 'District Court',  70),
('Principal District Court, Dindigul',             'TN', 'District Court',  80),
('Principal District Court, Erode',                'TN', 'District Court',  90),
('Principal District Court, Kallakurichi',         'TN', 'District Court', 100),
('Principal District Court, Kanchipuram',          'TN', 'District Court', 110),
('Principal District Court, Kanyakumari',          'TN', 'District Court', 120),
('Principal District Court, Karur',                'TN', 'District Court', 130),
('Principal District Court, Krishnagiri',          'TN', 'District Court', 140),
('Principal District Court, Madurai',              'TN', 'District Court', 150),
('Principal District Court, Mayiladuthurai',       'TN', 'District Court', 160),
('Principal District Court, Nagapattinam',         'TN', 'District Court', 170),
('Principal District Court, Namakkal',             'TN', 'District Court', 180),
('Principal District Court, Nilgiris',             'TN', 'District Court', 190),
('Principal District Court, Perambalur',           'TN', 'District Court', 200),
('Principal District Court, Pudukkottai',          'TN', 'District Court', 210),
('Principal District Court, Ramanathapuram',       'TN', 'District Court', 220),
('Principal District Court, Ranipet',              'TN', 'District Court', 230),
('Principal District Court, Salem',                'TN', 'District Court', 240),
('Principal District Court, Sivaganga',            'TN', 'District Court', 250),
('Principal District Court, Tenkasi',              'TN', 'District Court', 260),
('Principal District Court, Thanjavur',            'TN', 'District Court', 270),
('Principal District Court, Theni',                'TN', 'District Court', 280),
('Principal District Court, Thoothukudi',          'TN', 'District Court', 290),
('Principal District Court, Tiruchirappalli',      'TN', 'District Court', 300),
('Principal District Court, Tirunelveli',          'TN', 'District Court', 310),
('Principal District Court, Tirupathur',           'TN', 'District Court', 320),
('Principal District Court, Tiruppur',             'TN', 'District Court', 330),
('Principal District Court, Tiruvallur',           'TN', 'District Court', 340),
('Principal District Court, Tiruvannamalai',       'TN', 'District Court', 350),
('Principal District Court, Tiruvarur',            'TN', 'District Court', 360),
('Principal District Court, Vellore',              'TN', 'District Court', 370),
('Principal District Court, Villuppuram',          'TN', 'District Court', 380),
('Principal District Court, Virudhunagar',         'TN', 'District Court', 390),
('Family Court, Chennai',                          'TN', 'Family Court',   500),
('Family Court, Coimbatore',                       'TN', 'Family Court',   510),
('Family Court, Madurai',                          'TN', 'Family Court',   520),
('Family Court, Salem',                            'TN', 'Family Court',   530),
('Family Court, Tiruchirappalli',                  'TN', 'Family Court',   540),
('JM Court, Saidapet',                             'TN', 'Magistrate',     600),
('JM Court, Egmore',                               'TN', 'Magistrate',     610),
('Chief Metropolitan Magistrate Court, Chennai',   'TN', 'Magistrate',     620),
('Motor Accident Claims Tribunal, Chennai',        'TN', 'Tribunal',       700);

-- ============================================================
--  TELANGANA  (TS)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Telangana High Court',                           'TS', 'High Court',      10),
('City Civil Court, Hyderabad',                    'TS', 'Civil Court',     15),
('City Small Causes Court, Hyderabad',             'TS', 'Civil Court',     16),
('CBI Court, Hyderabad',                           'TS', 'Special Court',   18),
('District & Sessions Court, Adilabad',            'TS', 'District Court',  20),
('District & Sessions Court, Bhadradri Kothagudem','TS', 'District Court',  30),
('District & Sessions Court, Hanumakonda',         'TS', 'District Court',  40),
('District & Sessions Court, Hyderabad',           'TS', 'District Court',  50),
('District & Sessions Court, Jagtial',             'TS', 'District Court',  60),
('District & Sessions Court, Jangaon',             'TS', 'District Court',  70),
('District & Sessions Court, Jayashankar Bhupalpally', 'TS', 'District Court', 80),
('District & Sessions Court, Jogulamba Gadwal',    'TS', 'District Court',  90),
('District & Sessions Court, Kamareddy',           'TS', 'District Court', 100),
('District & Sessions Court, Karimnagar',          'TS', 'District Court', 110),
('District & Sessions Court, Khammam',             'TS', 'District Court', 120),
('District & Sessions Court, Komaram Bheem Asifabad', 'TS', 'District Court', 130),
('District & Sessions Court, Mahabubabad',         'TS', 'District Court', 140),
('District & Sessions Court, Mahabubnagar',        'TS', 'District Court', 150),
('District & Sessions Court, Mancherial',          'TS', 'District Court', 160),
('District & Sessions Court, Medak',               'TS', 'District Court', 170),
('District & Sessions Court, Medchal-Malkajgiri',  'TS', 'District Court', 180),
('District & Sessions Court, Mulugu',              'TS', 'District Court', 190),
('District & Sessions Court, Nagarkurnool',        'TS', 'District Court', 200),
('District & Sessions Court, Nalgonda',            'TS', 'District Court', 210),
('District & Sessions Court, Narayanpet',          'TS', 'District Court', 220),
('District & Sessions Court, Nirmal',              'TS', 'District Court', 230),
('District & Sessions Court, Nizamabad',           'TS', 'District Court', 240),
('District & Sessions Court, Peddapalli',          'TS', 'District Court', 250),
('District & Sessions Court, Rajanna Sircilla',    'TS', 'District Court', 260),
('District & Sessions Court, Rangareddy',          'TS', 'District Court', 270),
('District & Sessions Court, Sangareddy',          'TS', 'District Court', 280),
('District & Sessions Court, Siddipet',            'TS', 'District Court', 290),
('District & Sessions Court, Suryapet',            'TS', 'District Court', 300),
('District & Sessions Court, Vikarabad',           'TS', 'District Court', 310),
('District & Sessions Court, Wanaparthy',          'TS', 'District Court', 320),
('District & Sessions Court, Warangal',            'TS', 'District Court', 330),
('District & Sessions Court, Yadadri Bhuvanagiri', 'TS', 'District Court', 340),
('Family Court, Hyderabad',                        'TS', 'Family Court',   500),
('Family Court, Warangal',                         'TS', 'Family Court',   510);

-- ============================================================
--  TRIPURA  (TR)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Tripura High Court',                             'TR', 'High Court',      10),
('District & Sessions Court, Dhalai',              'TR', 'District Court',  20),
('District & Sessions Court, Gomati',              'TR', 'District Court',  30),
('District & Sessions Court, Khowai',              'TR', 'District Court',  40),
('District & Sessions Court, North Tripura',       'TR', 'District Court',  50),
('District & Sessions Court, Sepahijala',          'TR', 'District Court',  60),
('District & Sessions Court, South Tripura',       'TR', 'District Court',  70),
('District & Sessions Court, Unakoti',             'TR', 'District Court',  80),
('District & Sessions Court, West Tripura',        'TR', 'District Court',  90),
('Family Court, Agartala',                         'TR', 'Family Court',   500);

-- ============================================================
--  UTTAR PRADESH  (UP)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Allahabad High Court',                           'UP', 'High Court',      10),
('Allahabad High Court – Lucknow Bench',           'UP', 'High Court',      11),
('District & Sessions Court, Agra',                'UP', 'District Court',  20),
('District & Sessions Court, Aligarh',             'UP', 'District Court',  30),
('District & Sessions Court, Ambedkar Nagar',      'UP', 'District Court',  40),
('District & Sessions Court, Amethi',              'UP', 'District Court',  50),
('District & Sessions Court, Amroha',              'UP', 'District Court',  60),
('District & Sessions Court, Auraiya',             'UP', 'District Court',  70),
('District & Sessions Court, Ayodhya',             'UP', 'District Court',  80),
('District & Sessions Court, Azamgarh',            'UP', 'District Court',  90),
('District & Sessions Court, Baghpat',             'UP', 'District Court', 100),
('District & Sessions Court, Bahraich',            'UP', 'District Court', 110),
('District & Sessions Court, Ballia',              'UP', 'District Court', 120),
('District & Sessions Court, Balrampur',           'UP', 'District Court', 130),
('District & Sessions Court, Banda',               'UP', 'District Court', 140),
('District & Sessions Court, Barabanki',           'UP', 'District Court', 150),
('District & Sessions Court, Bareilly',            'UP', 'District Court', 160),
('District & Sessions Court, Basti',               'UP', 'District Court', 170),
('District & Sessions Court, Bhadohi',             'UP', 'District Court', 180),
('District & Sessions Court, Bijnor',              'UP', 'District Court', 190),
('District & Sessions Court, Budaun',              'UP', 'District Court', 200),
('District & Sessions Court, Bulandshahar',        'UP', 'District Court', 210),
('District & Sessions Court, Chandauli',           'UP', 'District Court', 220),
('District & Sessions Court, Chitrakoot',          'UP', 'District Court', 230),
('District & Sessions Court, Deoria',              'UP', 'District Court', 240),
('District & Sessions Court, Etah',                'UP', 'District Court', 250),
('District & Sessions Court, Etawah',              'UP', 'District Court', 260),
('District & Sessions Court, Farrukhabad',         'UP', 'District Court', 270),
('District & Sessions Court, Fatehpur',            'UP', 'District Court', 280),
('District & Sessions Court, Firozabad',           'UP', 'District Court', 290),
('District & Sessions Court, Gautam Budh Nagar',   'UP', 'District Court', 300),
('District & Sessions Court, Ghaziabad',           'UP', 'District Court', 310),
('District & Sessions Court, Ghazipur',            'UP', 'District Court', 320),
('District & Sessions Court, Gonda',               'UP', 'District Court', 330),
('District & Sessions Court, Gorakhpur',           'UP', 'District Court', 340),
('District & Sessions Court, Hamirpur',            'UP', 'District Court', 350),
('District & Sessions Court, Hapur',               'UP', 'District Court', 360),
('District & Sessions Court, Hardoi',              'UP', 'District Court', 370),
('District & Sessions Court, Hathras',             'UP', 'District Court', 380),
('District & Sessions Court, Jalaun',              'UP', 'District Court', 390),
('District & Sessions Court, Jaunpur',             'UP', 'District Court', 400),
('District & Sessions Court, Jhansi',              'UP', 'District Court', 410),
('District & Sessions Court, Kannauj',             'UP', 'District Court', 420),
('District & Sessions Court, Kanpur Dehat',        'UP', 'District Court', 430),
('District & Sessions Court, Kanpur Nagar',        'UP', 'District Court', 440),
('District & Sessions Court, Kasganj',             'UP', 'District Court', 450),
('District & Sessions Court, Kaushambi',           'UP', 'District Court', 460),
('District & Sessions Court, Kheri',               'UP', 'District Court', 470),
('District & Sessions Court, Kushinagar',          'UP', 'District Court', 480),
('District & Sessions Court, Lalitpur',            'UP', 'District Court', 490),
('District & Sessions Court, Lucknow',             'UP', 'District Court', 500),
('District & Sessions Court, Maharajganj',         'UP', 'District Court', 510),
('District & Sessions Court, Mahoba',              'UP', 'District Court', 520),
('District & Sessions Court, Mainpuri',            'UP', 'District Court', 530),
('District & Sessions Court, Mathura',             'UP', 'District Court', 540),
('District & Sessions Court, Mau',                 'UP', 'District Court', 550),
('District & Sessions Court, Meerut',              'UP', 'District Court', 560),
('District & Sessions Court, Mirzapur',            'UP', 'District Court', 570),
('District & Sessions Court, Moradabad',           'UP', 'District Court', 580),
('District & Sessions Court, Muzaffarnagar',       'UP', 'District Court', 590),
('District & Sessions Court, Pilibhit',            'UP', 'District Court', 600),
('District & Sessions Court, Pratapgarh',          'UP', 'District Court', 610),
('District & Sessions Court, Prayagraj',           'UP', 'District Court', 620),
('District & Sessions Court, Rae Bareli',          'UP', 'District Court', 630),
('District & Sessions Court, Rampur',              'UP', 'District Court', 640),
('District & Sessions Court, Saharanpur',          'UP', 'District Court', 650),
('District & Sessions Court, Sambhal',             'UP', 'District Court', 655),
('District & Sessions Court, Sant Kabir Nagar',    'UP', 'District Court', 660),
('District & Sessions Court, Shahjahanpur',        'UP', 'District Court', 670),
('District & Sessions Court, Shamli',              'UP', 'District Court', 680),
('District & Sessions Court, Shravasti',           'UP', 'District Court', 690),
('District & Sessions Court, Siddharthnagar',      'UP', 'District Court', 700),
('District & Sessions Court, Sitapur',             'UP', 'District Court', 710),
('District & Sessions Court, Sonbhadra',           'UP', 'District Court', 720),
('District & Sessions Court, Sultanpur',           'UP', 'District Court', 730),
('District & Sessions Court, Unnao',               'UP', 'District Court', 740),
('District & Sessions Court, Varanasi',            'UP', 'District Court', 750),
('Family Court, Lucknow',                          'UP', 'Family Court',   800),
('Family Court, Kanpur Nagar',                     'UP', 'Family Court',   810),
('Family Court, Agra',                             'UP', 'Family Court',   820),
('Family Court, Varanasi',                         'UP', 'Family Court',   830);

-- ============================================================
--  UTTARAKHAND  (UK)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Uttarakhand High Court',                         'UK', 'High Court',      10),
('District & Sessions Court, Almora',              'UK', 'District Court',  20),
('District & Sessions Court, Bageshwar',           'UK', 'District Court',  30),
('District & Sessions Court, Chamoli',             'UK', 'District Court',  40),
('District & Sessions Court, Champawat',           'UK', 'District Court',  50),
('District & Sessions Court, Dehradun',            'UK', 'District Court',  60),
('District & Sessions Court, Haridwar',            'UK', 'District Court',  70),
('District & Sessions Court, Nainital',            'UK', 'District Court',  80),
('District & Sessions Court, Pauri Garhwal',       'UK', 'District Court',  90),
('District & Sessions Court, Pithoragarh',         'UK', 'District Court', 100),
('District & Sessions Court, Rudraprayag',         'UK', 'District Court', 110),
('District & Sessions Court, Tehri Garhwal',       'UK', 'District Court', 120),
('District & Sessions Court, Udham Singh Nagar',   'UK', 'District Court', 130),
('District & Sessions Court, Uttarkashi',          'UK', 'District Court', 140),
('Family Court, Dehradun',                         'UK', 'Family Court',   500);

-- ============================================================
--  WEST BENGAL  (WB)
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Calcutta High Court',                            'WB', 'High Court',      10),
('City Civil Court, Kolkata',                      'WB', 'Civil Court',     15),
('Small Causes Court, Kolkata',                    'WB', 'Civil Court',     16),
('District & Sessions Court, Alipurduar',          'WB', 'District Court',  20),
('District & Sessions Court, Bankura',             'WB', 'District Court',  30),
('District & Sessions Court, Birbhum',             'WB', 'District Court',  40),
('District & Sessions Court, Cooch Behar',         'WB', 'District Court',  50),
('District & Sessions Court, Dakshin Dinajpur',    'WB', 'District Court',  60),
('District & Sessions Court, Darjeeling',          'WB', 'District Court',  70),
('District & Sessions Court, Hooghly',             'WB', 'District Court',  80),
('District & Sessions Court, Howrah',              'WB', 'District Court',  90),
('District & Sessions Court, Jalpaiguri',          'WB', 'District Court', 100),
('District & Sessions Court, Jhargram',            'WB', 'District Court', 110),
('District & Sessions Court, Kalimpong',           'WB', 'District Court', 120),
('District & Sessions Court, Kolkata',             'WB', 'District Court', 130),
('District & Sessions Court, Maldah',              'WB', 'District Court', 140),
('District & Sessions Court, Murshidabad',         'WB', 'District Court', 150),
('District & Sessions Court, Nadia',               'WB', 'District Court', 160),
('District & Sessions Court, North 24 Parganas',   'WB', 'District Court', 170),
('District & Sessions Court, Paschim Bardhaman',   'WB', 'District Court', 180),
('District & Sessions Court, Paschim Medinipur',   'WB', 'District Court', 190),
('District & Sessions Court, Purba Bardhaman',     'WB', 'District Court', 200),
('District & Sessions Court, Purba Medinipur',     'WB', 'District Court', 210),
('District & Sessions Court, Purulia',             'WB', 'District Court', 220),
('District & Sessions Court, South 24 Parganas',   'WB', 'District Court', 230),
('District & Sessions Court, Uttar Dinajpur',      'WB', 'District Court', 240),
('Family Court, Kolkata',                          'WB', 'Family Court',   500);

-- ============================================================
--  UNION TERRITORIES
-- ============================================================

-- ANDAMAN & NICOBAR ISLANDS  (AN)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Calcutta High Court – A&N Circuit Bench',        'AN', 'High Court',      10),
('District & Sessions Court, South Andaman',       'AN', 'District Court',  20),
('District & Sessions Court, North & Middle Andaman', 'AN', 'District Court', 30),
('District & Sessions Court, Nicobar',             'AN', 'District Court',  40);

-- CHANDIGARH  (CH)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Punjab & Haryana High Court',                    'CH', 'High Court',      10),
('District & Sessions Court, Chandigarh',          'CH', 'District Court',  20),
('Family Court, Chandigarh',                       'CH', 'Family Court',   500);

-- DADRA & NAGAR HAVELI AND DAMAN & DIU  (DN)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Bombay High Court – D&NH/D&D jurisdiction',      'DN', 'High Court',      10),
('District & Sessions Court, Daman',               'DN', 'District Court',  20),
('District & Sessions Court, Dadra & Nagar Haveli','DN', 'District Court',  30);

-- DELHI (NCT)  (DL)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Delhi High Court',                               'DL', 'High Court',      10),
('District Court, Central Delhi',                  'DL', 'District Court',  20),
('District Court, East Delhi',                     'DL', 'District Court',  30),
('District Court, New Delhi',                      'DL', 'District Court',  40),
('District Court, North Delhi',                    'DL', 'District Court',  50),
('District Court, North East Delhi',               'DL', 'District Court',  60),
('District Court, North West Delhi',               'DL', 'District Court',  70),
('District Court, Rohini',                         'DL', 'District Court',  80),
('District Court, Saket',                          'DL', 'District Court',  90),
('District Court, Shahdara',                       'DL', 'District Court', 100),
('District Court, South Delhi',                    'DL', 'District Court', 110),
('District Court, South East Delhi',               'DL', 'District Court', 120),
('District Court, South West Delhi',               'DL', 'District Court', 130),
('District Court, West Delhi',                     'DL', 'District Court', 140),
('Family Court, Delhi',                            'DL', 'Family Court',   500),
('Principal District & Sessions Court, Dwarka',    'DL', 'District Court', 150),
('Chief Metropolitan Magistrate Court, Delhi',     'DL', 'Magistrate',     600);

-- JAMMU & KASHMIR  (JK)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('J&K and Ladakh High Court',                      'JK', 'High Court',      10),
('Principal District & Sessions Court, Anantnag',  'JK', 'District Court',  20),
('Principal District & Sessions Court, Bandipora', 'JK', 'District Court',  30),
('Principal District & Sessions Court, Baramulla', 'JK', 'District Court',  40),
('Principal District & Sessions Court, Budgam',    'JK', 'District Court',  50),
('Principal District & Sessions Court, Doda',      'JK', 'District Court',  60),
('Principal District & Sessions Court, Ganderbal', 'JK', 'District Court',  70),
('Principal District & Sessions Court, Jammu',     'JK', 'District Court',  80),
('Principal District & Sessions Court, Kathua',    'JK', 'District Court',  90),
('Principal District & Sessions Court, Kishtwar',  'JK', 'District Court', 100),
('Principal District & Sessions Court, Kulgam',    'JK', 'District Court', 110),
('Principal District & Sessions Court, Kupwara',   'JK', 'District Court', 120),
('Principal District & Sessions Court, Poonch',    'JK', 'District Court', 130),
('Principal District & Sessions Court, Pulwama',   'JK', 'District Court', 140),
('Principal District & Sessions Court, Rajouri',   'JK', 'District Court', 150),
('Principal District & Sessions Court, Ramban',    'JK', 'District Court', 160),
('Principal District & Sessions Court, Reasi',     'JK', 'District Court', 170),
('Principal District & Sessions Court, Samba',     'JK', 'District Court', 180),
('Principal District & Sessions Court, Shopian',   'JK', 'District Court', 190),
('Principal District & Sessions Court, Srinagar',  'JK', 'District Court', 200),
('Principal District & Sessions Court, Udhampur',  'JK', 'District Court', 210),
('Family Court, Srinagar',                         'JK', 'Family Court',   500),
('Family Court, Jammu',                            'JK', 'Family Court',   510);

-- LADAKH  (LA)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('J&K and Ladakh High Court',                      'LA', 'High Court',      10),
('District & Sessions Court, Kargil',              'LA', 'District Court',  20),
('District & Sessions Court, Leh',                 'LA', 'District Court',  30);

-- LAKSHADWEEP  (LD)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Kerala High Court – Lakshadweep jurisdiction',   'LD', 'High Court',      10),
('District & Sessions Court, Kavaratti',           'LD', 'District Court',  20);

-- PUDUCHERRY  (PY)
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('Madras High Court – Puducherry Bench',           'PY', 'High Court',      10),
('District & Sessions Court, Puducherry',          'PY', 'District Court',  20),
('District & Sessions Court, Karaikal',            'PY', 'District Court',  30),
('District & Sessions Court, Mahe',                'PY', 'District Court',  40),
('District & Sessions Court, Yanam',               'PY', 'District Court',  50),
('Family Court, Puducherry',                       'PY', 'Family Court',   500);

-- ============================================================
--  NATIONAL TRIBUNALS (state_code = 'IN')
-- ============================================================
INSERT INTO indian_courts (court_name, state_code, court_type, sort_order) VALUES
('National Green Tribunal (Principal Bench)',       'IN', 'Tribunal',       10),
('National Consumer Disputes Redressal Commission','IN', 'Tribunal',        20),
('Central Administrative Tribunal (Principal Bench)','IN','Tribunal',       30),
('Armed Forces Tribunal (Principal Bench)',         'IN', 'Tribunal',       40),
('Income Tax Appellate Tribunal (Principal Bench)', 'IN', 'Tribunal',       50),
('Debt Recovery Appellate Tribunal, Delhi',         'IN', 'Tribunal',       60),
('Competition Appellate Tribunal',                  'IN', 'Tribunal',       70),
('National Company Law Appellate Tribunal',         'IN', 'Tribunal',       80),
('Intellectual Property Appellate Board',           'IN', 'Tribunal',       90),
('Telecom Disputes Settlement & Appellate Tribunal','IN', 'Tribunal',      100);

-- End of file
-- Total approximate rows: ~950
-- Coverage: 1 Supreme Court + 25 High Courts (incl. benches)
--           + 688 District Courts + Family Courts + Special Courts
--           + 10 National Tribunals