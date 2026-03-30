-- =============================================================================
-- DYNAMIC DATE CONFIGURATION
-- =============================================================================
-- Set the reference date to the current system date
USE courtdiary;
SET @today = CURDATE();

-- =============================================================================
-- CHAMBER & USER SETUP (Existing Logic)
-- =============================================================================
SET @chamber_vk     = (SELECT chamber_id FROM chamber WHERE chamber_name = 'VijayKrishnan & Associates');
SET @chamber_sundar = (SELECT chamber_id FROM chamber WHERE chamber_name = 'Sundar Associates');

SET @user_vijay   = (SELECT user_id FROM users WHERE email = 'admin@vkchamber.in');
SET @user_priya   = (SELECT user_id FROM users WHERE email = 'priya@vkchamber.in');
SET @user_karthik = (SELECT user_id FROM users WHERE email = 'karthik@vkchamber.in');
SET @user_lokesh  = (SELECT user_id FROM users WHERE email = 'lokesh@sundarlaw.in');

-- =============================================================================
-- CASE ID LOOKUPS
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
-- HEARINGS (ALL 9 CASES) - DYNAMIC DATES
-- =============================================================================

INSERT INTO hearings 
(chamber_id, case_id, hearing_date, status_code, purpose_code, notes, next_hearing_date, created_by) VALUES

-- =========================
-- OVERDUE CASES (Past Dates)
-- =========================
-- Logic: Hearing dates are before @today, Next Hearing was scheduled for @today
(@chamber_vk, @case1, DATE_SUB(@today, INTERVAL 4 DAY), 'HSUP', 'HPAR', 'Final arguments pending', @today, @user_priya),
(@chamber_vk, @case2, DATE_SUB(@today, INTERVAL 2 DAY), 'HSUP', 'HPEV', 'Witness examination ongoing', @today, @user_priya),
(@chamber_vk, @case3, DATE_SUB(@today, INTERVAL 6 DAY), 'HSUP', 'HPAD', 'Anticipatory bail hearing', @today, @user_priya),

-- =========================
-- TODAY'S HEARINGS (Current Date)
-- =========================
-- Logic: Hearing date is @today, Next Hearing is NULL (To be decided in court)
(@chamber_vk, @case1, @today, 'HSUP', 'HPAR', 'Final arguments hearing', NULL, @user_priya),
(@chamber_vk, @case2, @today, 'HSUP', 'HPEV', 'Evidence stage hearing', NULL, @user_priya),
(@chamber_vk, @case3, @today, 'HSUP', 'HPAR', 'Arguments stage', NULL, @user_priya),

-- =========================
-- UPCOMING THIS WEEK (Near Future)
-- =========================
-- Logic: Hearing dates are +2 to +4 days from @today
(@chamber_vk, @case4, DATE_ADD(@today, INTERVAL 2 DAY), 'HSUP', 'HPAD', 'First hearing (admission)', NULL, @user_priya),
(@chamber_vk, @case5, DATE_ADD(@today, INTERVAL 3 DAY), 'HSUP', 'HPME', 'Mediation scheduled', NULL, @user_priya),
(@chamber_vk, @case6, DATE_ADD(@today, INTERVAL 4 DAY), 'HSUP', 'HPEV', 'Document evidence submission', NULL, @user_priya),

-- =========================
-- FUTURE HEARINGS (Next Month)
-- =========================
-- Logic: Hearing dates are ~3-4 weeks from @today
(@chamber_vk, @case7, DATE_ADD(@today, INTERVAL 22 DAY), 'HSUP', 'HPAR', 'Arguments to be presented', NULL, @user_priya),
(@chamber_vk, @case8, DATE_ADD(@today, INTERVAL 27 DAY), 'HSUP', 'HPPL', 'Pleadings stage', NULL, @user_priya),

-- =========================
-- ADJOURNED CASE (Past Hearing, Future Next Date)
-- =========================
-- Logic: Hearing was 3 days ago, Next hearing is 12 days from now
(@chamber_vk, @case9, DATE_SUB(@today, INTERVAL 3 DAY), 'HSAD', 'HPAD', 'Adjourned due to counsel absence', DATE_ADD(@today, INTERVAL 12 DAY), @user_priya),

-- =========================
-- COMPLETED HISTORY (Older Past Dates)
-- =========================
-- Logic: Hearings are 1-2 weeks ago, Next Hearing was scheduled for @today
(@chamber_vk, @case1, DATE_SUB(@today, INTERVAL 9 DAY), 'HSCP', 'HPAD', 'Preliminary hearing completed', @today, @user_priya),
(@chamber_vk, @case2, DATE_SUB(@today, INTERVAL 6 DAY), 'HSCP', 'HPPL', 'Pleadings completed', @today, @user_priya),
(@chamber_vk, @case3, DATE_SUB(@today, INTERVAL 14 DAY), 'HSCP', 'HPAD', 'Initial hearing completed', @today, @user_priya);