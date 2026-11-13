# ============================================================
# ILEARN UGANDA - COMPLETE FINAL FILE - v44
# Login + 2FA + Forgot OTP + Add User + Audit + Timeout
# + Home Dashboard + Colours + Search + Favourites + Recent
# ============================================================
import streamlit as st
import pandas as pd
import hashlib, random, time, re
from datetime import date, datetime

st.set_page_config(page_title="ILEARN Uganda", page_icon="🌟", layout="wide", initial_sidebar_state="expanded")

# ============ 🎨 COLOURS - CSS ============
st.markdown("""
<style>
.stButton > button { height: 90px !important; font-size: 16px !important; font-weight: bold !important; border-radius: 16px !important; border: 2px solid #E0E0E0 !important; white-space: pre-line !important; line-height: 1.3 !important; }
div[data-testid="stHorizontalBlock"] .stButton > button { height: 50px !important; font-size: 14px !important; }
.color-blue { background: #1976D2; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-green { background: #2E7D32; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-orange { background: #EF6C00; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-red { background: #D32F2F; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-purple { background: #7B1FA2; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-gold { background: #FFB300; color: #333; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-teal { background: #00897B; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
</style>
""", unsafe_allow_html=True)

# ============ 🔐 HELPERS ============
def hash_pw(pw): return hashlib.sha256(pw.encode()).hexdigest()
def get_timeout_for_role(role):
    if role in ["Headteacher","Bursar"]: return 15
    if role=="Teacher": return 30
    if role=="Parent": return 60
    return 30

# Base Users: Email: [hash, Name, Role, PIN]
USERS = {
    "head@ilearn.ug": [hash_pw("head123"), "Headteacher", "Headteacher", "1234"],
    "bursar@ilearn.ug": [hash_pw("bursar123"), "Bursar Grace", "Bursar", "5678"],
    "teacher1@ilearn.ug": [hash_pw("teach123"), "Teacher Amina", "Teacher", ""],
    "teacher2@ilearn.ug": [hash_pw("teach123"), "Teacher John", "Teacher", ""],
    "parent@ilearn.ug": [hash_pw("parent123"), "Parent", "Parent", ""],
}
if "USERS_DYNAMIC" not in st.session_state: st.session_state.USERS_DYNAMIC = {}
if "pending_users" not in st.session_state: st.session_state.pending_users = {}
if "BLOCKED_USERS" not in st.session_state: st.session_state.BLOCKED_USERS = []
def get_all_users():
    all_u = dict(USERS); all_u.update(st.session_state.USERS_DYNAMIC)
    for b in st.session_state.BLOCKED_USERS:
        if b in all_u: del all_u[b]
    return all_u

# ============ 📜 AUDIT LOG ============
if "audit_log" not in st.session_state: st.session_state.audit_log = []
def log_action(action, details=""):
    entry = {"Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Name": st.session_state.get("user_name","Guest"), "Email": st.session_state.get("user_email","guest"), "Role": st.session_state.get("user_role","-"), "Action": action, "Details": details}
    st.session_state.audit_log.insert(0, entry); st.session_state.audit_log = st.session_state.audit_log[:500]

# ============ ⏰ SESSION TIMEOUT ============
SESSION_TIMEOUT_MINS = 30
if "last_activity" not in st.session_state: st.session_state.last_activity = time.time()
def update_activity(): st.session_state.last_activity = time.time()
def check_session_timeout():
    if not st.session_state.get("logged_in", False): return False
    role = st.session_state.get("user_role","Teacher")
    tm = st.session_state.get("SESSION_TIMEOUT_MINS", get_timeout_for_role(role))
    if time.time() - st.session_state.last_activity > tm*60:
        try: log_action("SESSION TIMEOUT", f"Auto-logout after {tm} mins idle")
        except: pass
        st.session_state.logged_in=False; st.session_state.user_email=""; st.session_state.user_name=""; st.session_state.user_role=""; st.session_state.login_step=1; st.session_state.twofa_code=""
        return True
    return False

# ============ SESSION STATE INIT ============
if "logged_in" not in st.session_state:
    st.session_state.logged_in=False; st.session_state.user_email=""; st.session_state.user_name=""; st.session_state.user_role=""; st.session_state.menu="🏠 Home Dashboard"
if "login_step" not in st.session_state:
    st.session_state.login_step=1; st.session_state.pending_email=""; st.session_state.pending_name=""; st.session_state.pending_role=""; st.session_state.twofa_code=""; st.session_state.twofa_expiry=0
if "otp_code" not in st.session_state:
    st.session_state.otp_code=""; st.session_state.otp_email=""; st.session_state.otp_step=1; st.session_state.otp_expiry=0

# Check timeout
timed_out = check_session_timeout()
if timed_out:
    st.warning("🔒 Session Expired - You were idle. Please login again for security.")

# ============ 🔐 LOGIN SCREEN ============
if not st.session_state.logged_in:
    st.title("🌟 ILEARN UGANDA")
    st.markdown('<div class="color-gold">🔐 LOGIN - Staff Only</div>', unsafe_allow_html=True)
    # --- STEP 1: Email + Password ---
    if st.session_state.login_step == 1:
        email = st.text_input("📧 Email", placeholder="e.g. teacher1@ilearn.ug", key="login_email").strip().lower()
        password = st.text_input("🔑 Password", type="password", placeholder="Enter your password", key="login_pw")
        if st.button("🔓 LOGIN - Step 1", type="primary", use_container_width=True):
            ALL = get_all_users()
            if email in ALL and ALL[email][0]==hash_pw(password):
                role = ALL[email][2]
                if role not in ["Headteacher","Bursar"]:
                    st.session_state.logged_in=True; st.session_state.user_email=email; st.session_state.user_name=ALL[email][1]; st.session_state.user_role=role; st.session_state.menu="🏠 Home Dashboard"; update_activity(); log_action("LOGIN","Login Success - No 2FA"); st.rerun()
                else:
                    otp2 = f"{random.randint(100000,999999)}"
                    st.session_state.twofa_code=otp2; st.session_state.twofa_expiry=time.time()+300; st.session_state.pending_email=email; st.session_state.pending_name=ALL[email][1]; st.session_state.pending_role=role; st.session_state.login_step=2
                    st.success("✅ Password OK! Now enter 2FA Code below.")
                    st.info(f"Demo OTP (WhatsApp Mode): *{otp2}* - Valid 5 mins. Or enter your PIN.")
                    pin = ALL[email][3] if len(ALL[email])>3 else ""
                    if pin: st.info(f"Your PIN is also accepted: {pin} (Change it in Admin)")
                    st.rerun()
            else:
                st.error("❌ Wrong Email or Password."); log_action("LOGIN FAILED", f"Failed login for {email}")
        st.caption("Demo: Head: head@ilearn.ug / head123 + PIN 1234 | Teacher: teacher1@ilearn.ug / teach123 | Bursar: bursar@ilearn.ug / bursar123 + PIN 5678 | Parent: parent@ilearn.ug / parent123")
    # --- STEP 2: 2FA ---
    if st.session_state.login_step == 2:
        st.markdown('<div class="color-red">🔐 STEP 2 - Enter 2FA Code / PIN</div>', unsafe_allow_html=True)
        st.write(f"Hello **{st.session_state.pending_name}** ({st.session_state.pending_role}) - {st.session_state.pending_email}")
        code2 = st.text_input("🔢 Enter 2FA Code or 4-Digit PIN", max_chars=6, key="twofa_input", placeholder="e.g. 123456 or 1234")
        c1,c2 = st.columns(2)
        if c1.button("✅ Verify & Login", type="primary", use_container_width=True):
            ALL=get_all_users(); em=st.session_state.pending_email; pin=ALL[em][3] if len(ALL[em])>3 else ""
            otp_ok = (code2==st.session_state.twofa_code and time.time()<=st.session_state.twofa_expiry)
            pin_ok = (pin!="" and code2==pin)
            if otp_ok or pin_ok:
                st.session_state.logged_in=True; st.session_state.user_email=em; st.session_state.user_name=st.session_state.pending_name; st.session_state.user_role=st.session_state.pending_role; st.session_state.menu="🏠 Home Dashboard"; st.session_state.login_step=1; st.session_state.twofa_code=""; update_activity(); log_action("LOGIN","Login Success - 2FA Verified"); st.rerun()
            else:
                st.error("❌ Wrong 2FA / PIN or Expired."); log_action("2FA FAILED", f"Wrong 2FA for {em}")
        if c2.button("🔄 Resend Code", use_container_width=True):
            otp2=f"{random.randint(100000,999999)}"; st.session_state.twofa_code=otp2; st.session_state.twofa_expiry=time.time()+300; st.success(f"New Code (WhatsApp Mode): {otp2}"); st.rerun()
        if st.button("← Back to Login"):
            st.session_state.login_step=1; st.session_state.twofa_code=""; st.rerun()
    # --- FORGOT PASSWORD + OTP ---
    st.divider(); st.subheader("❓ Forgot Password?")
    if st.session_state.otp_step==1:
        fe = st.text_input("Enter your Email to reset:", placeholder="teacher1@ilearn.ug", key="forgot_email").strip().lower()
        if st.button("📩 Send OTP Code", use_container_width=True):
            if fe in get_all_users():
                otp=f"{random.randint(100000,999999)}"; st.session_state.otp_code=otp; st.session_state.otp_email=fe; st.session_state.otp_step=2; st.session_state.otp_expiry=time.time()+600; log_action("FORGOT PW - OTP SENT", f"OTP sent to {fe}"); st.success(f"✅ OTP Sent! (Demo Mode - OTP is: {otp})"); st.info(f"Headteacher: Send via WhatsApp: *Your ILEARN OTP is {otp}. Valid 10 mins.*"); st.rerun()
            else: st.error("❌ Email not found. Ask Headteacher to add you.")
    if st.session_state.otp_step==2:
        st.success(f"OTP sent to {st.session_state.otp_email}")
        eotp = st.text_input("🔢 Enter 6-Digit OTP", max_chars=6, key="entered_otp")
        npw = st.text_input("🔑 New Password", type="password", key="new_pw1")
        npw2 = st.text_input("🔑 Confirm New Password", type="password", key="new_pw2")
        cc1,cc2 = st.columns(2)
        if cc1.button("✅ Reset Password", type="primary", use_container_width=True):
            if time.time()>st.session_state.otp_expiry: st.error("⏰ OTP Expired!"); st.session_state.otp_step=1; st.rerun()
            elif eotp!=st.session_state.otp_code: st.error("❌ Wrong OTP.")
            elif len(npw)<6: st.error("❌ Password must be 6+ chars.")
            elif npw!=npw2: st.error("❌ Passwords do not match.")
            else:
                em=st.session_state.otp_email; ALL=get_all_users(); name,role=ALL[em][1],ALL[em][2]; pin=ALL[em][3] if len(ALL[em])>3 else ""
                st.session_state.USERS_DYNAMIC[em]=[hash_pw(npw),name,role,pin]; log_action("RESET PASSWORD", f"Reset password for {em}"); st.success("✅ Password Changed! Now Login with new password."); st.code(f"New hash: {hash_pw(npw)} - Headteacher: save this"); st.session_state.otp_step=1; st.session_state.otp_code=""
        if cc2.button("🔄 Resend OTP", use_container_width=True): st.session_state.otp_step=1; st.rerun()
        if st.button("← Back to Login"): st.session_state.otp_step=1; st.rerun()
    # --- SELF REGISTER ---
    st.divider(); st.subheader("📝 New Here? Register")
    st.write("Parents / New Staff: Register. Headteacher will approve.")
    rn = st.text_input("Your Full Name", key="reg_name"); re_ = st.text_input("Your Email", key="reg_email").strip().lower(); rp = st.text_input("Choose Password", type="password", key="reg_pw"); rr = st.selectbox("I am a:", ["Parent","Teacher","Bursar"], key="reg_role")
    if st.button("📩 Request Account", use_container_width=True):
        if not rn or "@" not in re_ or len(rp)<6: st.error("Fill Name, valid Email, Password 6+ chars")
        elif re_ in get_all_users() or re_ in st.session_state.pending_users: st.error("Email already registered / pending.")
        else: st.session_state.pending_users[re_]=[hash_pw(rp),rn,rr,""]; st.success("✅ Request Sent! Ask Headteacher to approve in Admin page.")
    st.stop()

# ============ LOGGED IN - TOP BAR ============
update_activity()
st.sidebar.success(f"👤 {st.session_state.user_name}\nRole: {st.session_state.user_role}")
st.sidebar.caption(f"📧 {st.session_state.user_email}")
st.sidebar.caption(f"⏰ Auto-logout in {st.session_state.get('SESSION_TIMEOUT_MINS', get_timeout_for_role(st.session_state.user_role))} mins if idle")
if st.sidebar.button("🟢 I'm Still Here", key="keep_alive"): update_activity(); st.success("✅ Session extended!"); st.rerun()
if st.sidebar.button("🚪 LOGOUT", use_container_width=True):
    log_action("LOGOUT","User logged out"); st.session_state.logged_in=False; st.session_state.user_email=""; st.session_state.user_name=""; st.session_state.user_role=""; st.session_state.login_step=1; st.rerun()
st.write(f"Welcome, **{st.session_state.user_name}** ({st.session_state.user_role}) | Today: {date.today()}")

# ============ TOP BAR - YEAR / TERM / CLASS ============
st.title("🌟 ILEARN UGANDA - One App. One School. All Records.")
c1,c2,c3,c4,c5,c6 = st.columns(6)
with c1: selected_year = st.selectbox("Year", [2024,2025,2026,2027], index=2, key="top_year")
with c2: selected_term = st.selectbox("Term", ["Term 1","Term 2","Term 3"], index=2, key="top_term")
with c3: selected_class = st.selectbox("Class", ["Baby","Middle","Top","P1","P2","P3","P4","P5","P6","P7"], index=7, key="top_class")
with c4: selected_stream = st.selectbox("Stream", ["A","B","C"], index=0, key="top_stream")
with c5: selected_subject = st.selectbox("Subject", ["English","Maths","Science","SST","Kiswahili","All"], index=5, key="top_subject")
with c6: selected_date = st.date_input("Date", date.today(), key="top_date")

# ============ ALL MENUS + ROLE FILTER ============
ALL_MENUS = ["🏠 Home Dashboard","👑 Admin - Add User","🌟 Master Summary","📋 Attendance","📝 Take Quiz","📊 Performance","💬 Behaviour / Clinic","👥 Learners","🏫 Streams","🎓 Alumni","📚 Quiz Bank","🗳️ Voting","📄 Report Cards","💰 Fees","💬 Parent Message","🔢 Student Code & Pay","📚 NCDC Outcomes","📝 Lesson Plans","📔 Record of Work","📅 Schemes of Work","📊 Headteacher Dashboard","🗓️ Timetable & Duty","👩🏾‍🏫 Staff & Payroll","🎓 Exams / PLE Mock","📝 Assessment Records","📚 Library","🚌 Transport / Bus","🏥 Health","⭐ Discipline / Rewards","🛒 School Shop","👨‍👩‍👧 PTA Meeting","🏫 Assets","🚪 Visitors / Gate Pass","📅 Calendar / Events","💝 Donations","🎓 Bursary","🍲 Feeding / Lunch","👩🏾‍🏫 Staff Attendance","📚 Homework","🏦 Cash Book","📢 Notice Board","🎓 PLE / UNEB","🔍 Inspection","🎉 Alumni Reunion"]
ROLE_MENUS = {
    "Headteacher": None,
    "Teacher": ["🏠 Home Dashboard","🌟 Master Summary","📋 Attendance","📝 Take Quiz","📊 Performance","💬 Behaviour / Clinic","👥 Learners","📚 Quiz Bank","📄 Report Cards","💬 Parent Message","📚 NCDC Outcomes","📝 Lesson Plans","📔 Record of Work","📅 Schemes of Work","🗓️ Timetable & Duty","📝 Assessment Records","📚 Library","🏥 Health","⭐ Discipline / Rewards","📚 Homework","📢 Notice Board"],
    "Bursar": ["🏠 Home Dashboard","🌟 Master Summary","👥 Learners","💰 Fees","🔢 Student Code & Pay","👩🏾‍🏫 Staff & Payroll","🛒 School Shop","🏦 Cash Book","💝 Donations","🎓 Bursary","📊 Headteacher Dashboard"],
    "Parent": ["🏠 Home Dashboard","👥 Learners","📊 Performance","📄 Report Cards","💰 Fees","📚 Homework","🏥 Health","📢 Notice Board"],
}
if st.session_state.user_role in ROLE_MENUS and ROLE_MENUS[st.session_state.user_role] is not None:
    ALL_MENUS = [m for m in ALL_MENUS if m in ROLE_MENUS[st.session_state.user_role]]
    if st.session_state.menu not in ALL_MENUS: st.session_state.menu="🏠 Home Dashboard"
if st.session_state.user_role != "Headteacher" and "👑 Admin - Add User" in ALL_MENUS:
    ALL_MENUS.remove("👑 Admin - Add User")
    if st.session_state.menu=="👑 Admin - Add User": st.session_state.menu="🏠 Home Dashboard"
if "menu" not in st.session_state: st.session_state.menu="🏠 Home Dashboard"

# ============ SIDEBAR ============
st.sidebar.title("🌟 ILEARN Uganda"); st.sidebar.caption("43 Features | One School")
st.sidebar.subheader("🔍 Search Feature")
search = st.sidebar.text_input("Type to search... e.g. Fees, PLE, Shop", placeholder="Type Fees, Homework, PLE...", key="search_menu").strip().lower()
if search:
    filtered = [m for m in ALL_MENUS if search in m.lower()]
    if not filtered:
        st.sidebar.warning(f"No feature for '{search}'")
        filtered = ALL_MENUS
    else:
        st.sidebar.success(f"Found {len(filtered)} - Click one:")
    if st.session_state.menu not in filtered:
        st.session_state.menu = filtered[0]
    menu = st.sidebar.radio("Results:", filtered, index=filtered.index(st.session_state.menu))
else:
    if st.session_state.menu not in ALL_MENUS:
        st.session_state.menu = "Home Dashboard"
    safe_index = ALL_MENUS.index(st.session_state.menu) if st.session_state.menu in ALL_MENUS else 0
    menu = st.sidebar.radio("📋 CHOOSE FEATURE:", ALL_MENUS, index=safe_index)
if menu != st.session_state.menu:
    log_action("VIEW PAGE", f"Opened {menu}")
st.session_state.menu=menu
st.sidebar.divider(); st.sidebar.success(f"📍 {selected_class} {selected_stream} | {selected_term} | {selected_year}"); st.sidebar.info("Tip: Start day with 🏠 Home or 🌟 Master")
if st.sidebar.button("🔄 REFRESH"): st.rerun()

# ============ FAVOURITES + RECENT ============
if "recent" not in st.session_state: st.session_state.recent=["🏠 Home Dashboard"]
if "favs" not in st.session_state: st.session_state.favs=["📋 Attendance","💰 Fees","🌟 Master Summary"]
if st.session_state.menu in st.session_state.recent: st.session_state.recent.remove(st.session_state.menu)
st.session_state.recent.insert(0, st.session_state.menu); st.session_state.recent=st.session_state.recent[:5]
st.sidebar.divider(); st.sidebar.subheader("⭐ My Favourites")
for fav in list(st.session_state.favs):
    if fav not in ALL_MENUS: continue
    cc1,cc2 = st.sidebar.columns([4,1])
    if cc1.button(fav, key=f"fav_{fav}", use_container_width=True): st.session_state.menu=fav; st.rerun()
    if cc2.button("❌", key=f"fav_del_{fav}"): st.session_state.favs.remove(fav); st.rerun()
if st.session_state.menu not in st.session_state.favs:
    if st.sidebar.button(f"⭐ Add '{st.session_state.menu}' to Favourites"): st.session_state.favs.append(st.session_state.menu); st.rerun()
else: st.sidebar.caption(f"✅ '{st.session_state.menu}' is in Favourites")
st.sidebar.subheader("🕒 Recent - Last 5")
for r in st.session_state.recent:
    if st.sidebar.button(r, key=f"recent_{r}"): st.session_state.menu=r; st.rerun()
if st.sidebar.button("🧹 Clear Recent"): st.session_state.recent=[st.session_state.menu]; st.rerun()

# ============ TOP QUICK BUTTONS ============
st.markdown('<div class="color-teal">⚡ QUICK ACCESS - Most Used Today</div>', unsafe_allow_html=True)
q1,q2,q3,q4,q5 = st.columns(5)
if q1.button("📋 Attendance", use_container_width=True):
    for m in ALL_MENUS:
        if "Attendance" in m:
            st.session_state.menu = m
    st.rerun()
if q2.button("💰 Fees", use_container_width=True):
    for m in ALL_MENUS:
        if "Fees" in m:
            st.session_state.menu = m
    st.rerun()
if q3.button("📚 Homework", use_container_width=True):
    for m in ALL_MENUS:
        if "Homework" in m:
            st.session_state.menu = m
    st.rerun()
if q4.button("🩺 Health", use_container_width=True):
    for m in ALL_MENUS:
        if "Health" in m or "Behaviour" in m or "Clinic" in m:
            st.session_state.menu = m
    st.rerun()
if q5.button("⭐ Master", type="primary", use_container_width=True):
    for m in ALL_MENUS:
        if "Master" in m:
            st.session_state.menu = m
    st.rerun()

# --- TAKE QUIZ PAGE - ADDED AT BOTTOM ---
if st.session_state.menu == "📝 Take Quiz":
    st.subheader("📝 Take Quiz - Your 20 Questions")
    st.write("Answer all 20, then tap SUBMIT to see your score and explanations.")

    MY_QUESTIONS = [
        ("1. Maths: Zoey scored 30, 40, 50, 40, 60. Find the modal frequency.", ["30","40","50","60"], "40", "Explanation: Mode is the number that appears most. 40 appears twice, others appear once."),
        ("2. Maths: Maximum number of girls who can share 24 oranges or 30 oranges without remainder.", ["4","6","8","12"], "6", "Explanation: Find HCF of 24 and 30. Highest common factor is 6."),
        ("3. Maths: Lydia is thrice as old as Brian. Sum is 32. How old is Lydia?", ["8","16","24","32"], "24", "Explanation: Brian = x, Lydia = 3x. x + 3x = 32, 4x = 32, x = 8. Lydia = 3 x 8 = 24."),
        ("4. Maths: Price of 3 T-shirts is Sh. 24000. Find price of 5 similar T-shirts.", ["Sh. 16000","Sh. 32000","Sh. 40000","Sh. 48000"], "Sh. 40000", "Explanation: 1 T-shirt = 24000 / 3 = 8000. 5 T-shirts = 5 x 8000 = Sh. 40000."),
        ("5. Maths: Volume of cuboid is 120cm3. Base area is 24cm2. Find height.", ["3cm","5cm","6cm","10cm"], "5cm", "Explanation: Height = Volume / Base Area = 120 / 24 = 5cm."),
        ("6. Kiswahili: Which means - this place is good?", ["Mahali hapa ni pazuri","Mahali hapa ni pabaya","Mahali hapa ni pakubwa","Mahali hapa ni padogo"], "Mahali hapa ni pazuri", "Explanation: Pazuri means good. Pabaya means bad. Pakubwa means big. Padogo means small."),
        ("7. RE: One food God provided to Israelites while moving to promised land.", ["Manna","Rice","Bread","Fish"], "Manna", "Explanation: God gave them Manna from heaven every morning while in the desert."),
        ("8. SST: What climate is experienced by central part of Uganda?", ["Desert climate","Tropical climate","Mediterranean climate","Polar climate"], "Tropical climate", "Explanation: Central Uganda is near the equator, warm with rain all year - tropical climate."),
        ("9. SST: How is Lake Victoria related to Lake Albert?", ["Connected by River Nile","Connected by River Congo","They are the same lake","Not connected"], "Connected by River Nile", "Explanation: Water flows from Lake Victoria via Victoria Nile to Lake Albert."),
        ("10. SST: Which region is Mount Rwenzori?", ["Northern","Eastern","Western","Central"], "Western", "Explanation: Rwenzori Mountains are in Western Uganda, near Kasese."),
        ("11. English: Mr Mwenda is a ___ working with Observer newspaper. (column)", ["columnist","colonist","journal","writer"], "columnist", "Explanation: A person who writes a regular column is called a columnist."),
        ("12. English: Our fathers car needs proper ___. (maintain)", ["maintain","maintenance","maintaining","maintained"], "maintenance", "Explanation: After proper we need a noun. Maintenance is the noun from maintain."),
        ("13. English: Very many ___ houses will be closed soon. (medium)", ["medium","media","mediums","medias"], "media", "Explanation: Medium is singular, Media is plural. Very many needs plural."),
        ("14. English: Moris liked reading newspapers more than watching television. Use prefer.", ["Moris prefers reading newspapers to watching television","Moris prefer reading newspapers than watching television","Moris prefers to read newspapers more than television","Moris is preferring newspapers"], "Moris prefers reading newspapers to watching television", "Explanation: We say prefer ... to ..., not prefer ... than ..."),
        ("15. English: Kapere has a good television. Kapere does not watch news. Begin: Although...", ["Although Kapere has a good television, he does not watch any news","Although Kapere does not watch news, he has television","Although Kapere has television, he watches news","Although Kapere is good, he watches news"], "Although Kapere has a good television, he does not watch any news", "Explanation: Although joins two opposite ideas. Although + first idea, comma, + second idea."),
        ("16. English: I bought a motorcycle. I wanted to reach workplace early. Join using ...so that...", ["I bought a new motorcycle so that I could reach my workplace early enough","I bought a motorcycle so that I reach early","I bought a motorcycle so that to reach early","I bought a motorcycle so that I can reach"], "I bought a new motorcycle so that I could reach my workplace early enough", "Explanation: So that shows purpose. Past tense bought, so we use could reach."),
        ("17. Science: Give one example of root tuber crops.", ["Cassava","Beans","Maize","Rice"], "Cassava", "Explanation: Root tubers store food in roots. Cassava, sweet potatoes are root tubers."),
        ("18. Science: Kyle was on moon and pencil could not fall down. What caused that?", ["No gravity on the moon","Too much air","Too much water","Too much heat"], "No gravity on the moon", "Explanation: The moon has very little gravity, so things float instead of falling."),
        ("19. Science: Plant bent towards window. What makes it behave that way?", ["Phototropism - response to light","Photosynthesis","Gravity","Wind"], "Phototropism - response to light", "Explanation: Plants grow towards light to get sunlight. This is called phototropism."),
        ("20. Science: State force experienced by body dropped into water.", ["Upthrust","Friction","Magnetism","Gravity"], "Upthrust", "Explanation: Water pushes a body upwards. That upward push is called upthrust."),
    ]

    my_answers = {}
    for i, (q, opts, correct, expl) in enumerate(MY_QUESTIONS):
        my_answers[i] = st.radio(f"Q{i+1}. {q}", opts, key=f"myquiz_bottom_{i}", index=None)

    if st.button("✅ SUBMIT MY 20 QUESTIONS", use_container_width=True):
        score = sum(1 for i, (q, opts, correct, expl) in enumerate(MY_QUESTIONS) if my_answers[i] == correct)
        st.success(f"✅ You scored {score} / 20")
        if score >= 18:
            st.balloons()
            st.write("Excellent! 🌟")
        elif score >= 14:
            st.write("Very Good! 👍")
        elif score >= 10:
            st.write("Good! Try again for 15+ 💪")
        else:
            st.write("Keep practising, you can do it 💪")
        st.divider()
        st.subheader("📖 Explanations")
        for i, (q, opts, correct, expl) in enumerate(MY_QUESTIONS):
            if my_answers[i] == correct:
                st.success(f"Q{i+1} ✅ Correct: {correct}")
            else:
                st.error(f"Q{i+1} ❌ You chose: {my_answers[i]} | Correct answer is: {correct}")
            st.info(expl)
