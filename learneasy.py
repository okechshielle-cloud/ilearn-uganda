# ============================================================
# ILEARN UGANDA - COMPLETE FINAL FILE - v43
# Home Dashboard + Colours + Side Task Bar + Search
# + Favourites + Recent + Top Quick Buttons
# ============================================================
import streamlit as st
import pandas as pd
from datetime import date, datetime

st.set_page_config(page_title="ILEARN Uganda", page_icon="🌟", layout="wide", initial_sidebar_state="expanded")

# ============ 🎨 COLOURS - CSS ============
st.markdown("""
<style>
.stButton > button {
    height: 90px !important;
    font-size: 16px !important;
    font-weight: bold !important;
    border-radius: 16px !important;
    border: 2px solid #E0E0E0 !important;
    white-space: pre-line !important;
    line-height: 1.3 !important;
}
div[data-testid="stHorizontalBlock"] .stButton > button {
    height: 50px !important;
    font-size: 14px !important;
}
.color-blue { background: #1976D2; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-green { background: #2E7D32; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-orange { background: #EF6C00; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-red { background: #D32F2F; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-purple { background: #7B1FA2; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-gold { background: #FFB300; color: #333; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
.color-teal { background: #00897B; color: white; padding: 12px 16px; border-radius: 12px; font-size: 20px; font-weight: bold; margin: 16px 0 8px 0; }
</style>
""", unsafe_allow_html=True)

# ============ TOP BAR - YEAR / TERM / CLASS ============
st.title("🌟 ILEARN UGANDA - One App. One School. All Records.")
c1, c2, c3, c4, c5, c6 = st.columns(6)
with c1:
    selected_year = st.selectbox("Year", [2024, 2025, 2026, 2027], index=2, key="top_year")
with c2:
    selected_term = st.selectbox("Term", ["Term 1", "Term 2", "Term 3"], index=2, key="top_term")
with c3:
    selected_class = st.selectbox("Class", ["Baby", "Middle", "Top", "P1", "P2", "P3", "P4", "P5", "P6", "P7"], index=7, key="top_class")
with c4:
    selected_stream = st.selectbox("Stream", ["A", "B", "C"], index=0, key="top_stream")
with c5:
    selected_subject = st.selectbox("Subject", ["English", "Maths", "Science", "SST", "Kiswahili", "All"], index=5, key="top_subject")
with c6:
    selected_date = st.date_input("Date", date.today(), key="top_date")

# ============ ALL MENUS ============
ALL_MENUS = [
    "🏠 Home Dashboard",
    "🌟 Master Summary","📋 Attendance","📝 Take Quiz","📊 Performance",
    "💬 Behaviour / Clinic","👥 Learners","🏫 Streams","🎓 Alumni",
    "📚 Quiz Bank","🗳️ Voting","📄 Report Cards","💰 Fees",
    "💬 Parent Message","🔢 Student Code & Pay","📚 NCDC Outcomes",
    "📝 Lesson Plans","📔 Record of Work","📅 Schemes of Work",
    "📊 Headteacher Dashboard","🗓️ Timetable & Duty","👩🏾‍🏫 Staff & Payroll",
    "🎓 Exams / PLE Mock","📝 Assessment Records","📚 Library",
    "🚌 Transport / Bus","🏥 Health","⭐ Discipline / Rewards",
    "🛒 School Shop","👨‍👩‍👧 PTA Meeting","🏫 Assets",
    "🚪 Visitors / Gate Pass","📅 Calendar / Events","💝 Donations",
    "🎓 Bursary","🍲 Feeding / Lunch","👩🏾‍🏫 Staff Attendance",
    "📚 Homework","🏦 Cash Book","📢 Notice Board",
    "🎓 PLE / UNEB","🔍 Inspection","🎉 Alumni Reunion",
]
if "menu" not in st.session_state:
    st.session_state.menu = "🏠 Home Dashboard"

# ============ SIDEBAR - TASK BAR + SEARCH ============
st.sidebar.title("🌟 ILEARN Uganda")
st.sidebar.caption("43 Features | One School")
st.sidebar.subheader("🔍 Search Feature")
search = st.sidebar.text_input("Type to search... e.g. Fees, PLE, Shop", placeholder="Type Fees, Homework, PLE...", key="search_menu").strip().lower()
if search:
    filtered = [m for m in ALL_MENUS if search in m.lower()]
    if not filtered:
        st.sidebar.warning(f"No feature found for '{search}'")
        filtered = ALL_MENUS
    else:
        st.sidebar.success(f"Found {len(filtered)} - Click one:")
    menu = st.sidebar.radio("Results - Click to Open:", filtered, index=filtered.index(st.session_state.menu) if st.session_state.menu in filtered else 0, key="side_menu_search")
else:
    menu = st.sidebar.radio("📂 CHOOSE FEATURE:", ALL_MENUS, index=ALL_MENUS.index(st.session_state.menu), key="side_menu_main")
st.session_state.menu = menu
st.sidebar.divider()
st.sidebar.success(f"📍 {selected_class} {selected_stream} | {selected_term} | {selected_year}")
st.sidebar.info("Tip: Start day with 🏠 Home or 🌟 Master")
if st.sidebar.button("🔄 REFRESH"):
    st.rerun()

# ============ ⭐ FAVOURITES + 🕒 RECENT ============
if "recent" not in st.session_state:
    st.session_state.recent = ["🏠 Home Dashboard"]
if "favs" not in st.session_state:
    st.session_state.favs = ["📋 Attendance", "💰 Fees", "🌟 Master Summary"]
if st.session_state.menu in st.session_state.recent:
    st.session_state.recent.remove(st.session_state.menu)
st.session_state.recent.insert(0, st.session_state.menu)
st.session_state.recent = st.session_state.recent[:5]

st.sidebar.divider()
st.sidebar.subheader("⭐ My Favourites")
for fav in st.session_state.favs:
    c1, c2 = st.sidebar.columns([4, 1])
    if c1.button(fav, key=f"fav_{fav}", use_container_width=True):
        st.session_state.menu = fav; st.rerun()
    if c2.button("❌", key=f"fav_del_{fav}"):
        st.session_state.favs.remove(fav); st.rerun()
if st.session_state.menu not in st.session_state.favs:
    if st.sidebar.button(f"⭐ Add '{st.session_state.menu}' to Favourites"):
        st.session_state.favs.append(st.session_state.menu); st.rerun()
else:
    st.sidebar.caption(f"✅ '{st.session_state.menu}' is in Favourites")
st.sidebar.subheader("🕒 Recent - Last 5")
for r in st.session_state.recent:
    if st.sidebar.button(r, key=f"recent_{r}"):
        st.session_state.menu = r; st.rerun()
if st.sidebar.button("🧹 Clear Recent"):
    st.session_state.recent = [st.session_state.menu]; st.rerun()

# ============ TOP QUICK BUTTONS + TOP SEARCH ============
st.markdown('<div class="color-teal">⚡ QUICK ACCESS - Most Used Today</div>', unsafe_allow_html=True)
q1, q2, q3, q4, q5 = st.columns(5)
if q1.button("📋\nAttendance", use_container_width=True):
    st.session_state.menu = "📋 Attendance"; st.rerun()
if q2.button("💰\nFees", use_container_width=True):
    st.session_state.menu = "💰 Fees"; st.rerun()
if q3.button("📚\nHomework", use_container_width=True):
    st.session_state.menu = "📚 Homework"; st.rerun()
if q4.button("🏥\nHealth", use_container_width=True):
    st.session_state.menu = "🏥 Health"; st.rerun()
if q5.button("🌟\nMaster", type="primary", use_container_width=True):
    st.session_state.menu = "🌟 Master Summary"; st.rerun()

top_search = st.text_input("🔍 Quick Search - Type feature name and press Enter:", placeholder="e.g. type 'PLE' or 'Cash' or 'Shop' then press Enter", key="top_search_box").strip().lower()
if top_search:
    matches = [m for m in ALL_MENUS if top_search in m.lower()]
    if matches:
        st.write("Found:")
        cols = st.columns(min(len(matches), 4))
        for i, m in enumerate(matches[:8]):
            if cols[i % len(cols)].button(m, key=f"top_search_{m}"):
                st.session_state.menu = m; st.rerun()
    else:
        st.warning("No match. Try: Fees, Homework, PLE, Cash, Shop, Library")

if len(st.session_state.recent) > 1:
    st.write("🕒 **Recent:**")
    rcols = st.columns(len(st.session_state.recent))
    for i, r in enumerate(st.session_state.recent):
        if rcols[i].button(r, key=f"top_recent_{r}", use_container_width=True):
            st.session_state.menu = r; st.rerun()

st.divider()

# ============ 🏠 HOME DASHBOARD ============
if st.session_state.menu == "🏠 Home Dashboard":
    st.header("🏠 ILEARN UGANDA - Home")
    st.write(f"Welcome! Today is **{selected_date}** | Class: **{selected_class} {selected_stream}** | Term: **{selected_term}**")
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("👥 Learners", "450")
    s2.metric("📋 Today", "Tap Attendance")
    s3.metric("💰 Fees", "Check Balance")
    s4.metric("🌟 Status", "All Good ✅")
    st.markdown('<div class="color-gold">⚡ Quick - Do Today</div>', unsafe_allow_html=True)
    a1, a2, a3, a4 = st.columns(4)
    if a1.button("📋\n\nATTENDANCE\nMark Today", use_container_width=True):
        st.session_state.menu = "📋 Attendance"; st.rerun()
    if a2.button("💰\n\nFEES\nCheck Balance", use_container_width=True):
        st.session_state.menu = "💰 Fees"; st.rerun()
    if a3.button("📚\n\nHOMEWORK\nGive / Mark", use_container_width=True):
        st.session_state.menu = "📚 Homework"; st.rerun()
    if a4.button("🌟\n\nMASTER\nWhole School", type="primary", use_container_width=True):
        st.session_state.menu = "🌟 Master Summary"; st.rerun()
    st.markdown('<div class="color-blue">📚 LEARNING - Blue</div>', unsafe_allow_html=True)
    l1, l2, l3, l4 = st.columns(4)
    if l1.button("📝\n\nTake Quiz", use_container_width=True):
        st.session_state.menu = "📝 Take Quiz"; st.rerun()
    if l2.button("📊\n\nPerformance", use_container_width=True):
        st.session_state.menu = "📊 Performance"; st.rerun()
    if l3.button("📄\n\nReport Cards", use_container_width=True):
        st.session_state.menu = "📄 Report Cards"; st.rerun()
    if l4.button("📚\n\nLibrary", use_container_width=True):
        st.session_state.menu = "📚 Library"; st.rerun()
    l5, l6, l7, l8 = st.columns(4)
    if l5.button("👥\n\nLearners", use_container_width=True):
        st.session_state.menu = "👥 Learners"; st.rerun()
    if l6.button("🗳️\n\nVoting", use_container_width=True):
        st.session_state.menu = "🗳️ Voting"; st.rerun()
    if l7.button("🎓\n\nExams / PLE Mock", use_container_width=True):
        st.session_state.menu = "🎓 Exams / PLE Mock"; st.rerun()
    if l8.button("🎓\n\nPLE / UNEB", use_container_width=True):
        st.session_state.menu = "🎓 PLE / UNEB"; st.rerun()
    st.markdown('<div class="color-green">💰 MONEY - Green</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    if m1.button("💰\n\nFees", use_container_width=True):
        st.session_state.menu = "💰 Fees"; st.rerun()
    if m2.button("🏦\n\nCash Book", use_container_width=True):
        st.session_state.menu = "🏦 Cash Book"; st.rerun()
    if m3.button("🛒\n\nSchool Shop", use_container_width=True):
        st.session_state.menu = "🛒 School Shop"; st.rerun()
    if m4.button("💝\n\nDonations", use_container_width=True):
        st.session_state.menu = "💝 Donations"; st.rerun()
    m5, m6, m7, m8 = st.columns(4)
    if m5.button("🎓\n\nBursary", use_container_width=True):
        st.session_state.menu = "🎓 Bursary"; st.rerun()
    if m6.button("👩🏾‍🏫\n\nStaff & Payroll", use_container_width=True):
        st.session_state.menu = "👩🏾‍🏫 Staff & Payroll"; st.rerun()
    if m7.button("🔢\n\nStudent Code & Pay", use_container_width=True):
        st.session_state.menu = "🔢 Student Code & Pay"; st.rerun()
    if m8.button("💬\n\nParent Message", use_container_width=True):
        st.session_state.menu = "💬 Parent Message"; st.rerun()
    st.markdown('<div class="color-orange">👩🏾‍🏫 TEACHING - Orange</div>', unsafe_allow_html=True)
    t1, t2, t3, t4 = st.columns(4)
    if t1.button("📝\n\nLesson Plans", use_container_width=True):
        st.session_state.menu = "📝 Lesson Plans"; st.rerun()
    if t2.button("📔\n\nRecord of Work", use_container_width=True):
        st.session_state.menu = "📔 Record of Work"; st.rerun()
    if t3.button("📅\n\nSchemes of Work", use_container_width=True):
        st.session_state.menu = "📅 Schemes of Work"; st.rerun()
    if t4.button("🗓️\n\nTimetable & Duty", use_container_width=True):
        st.session_state.menu = "🗓️ Timetable & Duty"; st.rerun()
    t5, t6, t7, t8 = st.columns(4)
    if t5.button("📚\n\nNCDC Outcomes", use_container_width=True):
        st.session_state.menu = "📚 NCDC Outcomes"; st.rerun()
    if t6.button("📝\n\nAssessment", use_container_width=True):
        st.session_state.menu = "📝 Assessment Records"; st.rerun()
    if t7.button("👩🏾‍🏫\n\nStaff Attendance", use_container_width=True):
        st.session_state.menu = "👩🏾‍🏫 Staff Attendance"; st.rerun()
    if t8.button("📚\n\nQuiz Bank", use_container_width=True):
        st.session_state.menu = "📚 Quiz Bank"; st.rerun()
    st.markdown('<div class="color-purple">🏫 SCHOOL LIFE - Purple</div>', unsafe_allow_html=True)
    s1, s2, s3, s4 = st.columns(4)
    if s1.button("🏥\n\nHealth", use_container_width=True):
        st.session_state.menu = "🏥 Health"; st.rerun()
    if s2.button("⭐\n\nDiscipline", use_container_width=True):
        st.session_state.menu = "⭐ Discipline / Rewards"; st.rerun()
    if s3.button("🍲\n\nFeeding / Lunch", use_container_width=True):
        st.session_state.menu = "🍲 Feeding / Lunch"; st.rerun()
    if s4.button("🚌\n\nTransport / Bus", use_container_width=True):
        st.session_state.menu = "🚌 Transport / Bus"; st.rerun()
    s5, s6, s7, s8 = st.columns(4)
    if s5.button("🏫\n\nAssets", use_container_width=True):
        st.session_state.menu = "🏫 Assets"; st.rerun()
    if s6.button("🚪\n\nVisitors", use_container_width=True):
        st.session_state.menu = "🚪 Visitors / Gate Pass"; st.rerun()
    if s7.button("📅\n\nCalendar / Events", use_container_width=True):
        st.session_state.menu = "📅 Calendar / Events"; st.rerun()
    if s8.button("📢\n\nNotice Board", use_container_width=True):
        st.session_state.menu = "📢 Notice Board"; st.rerun()
    s9, s10, s11, s12 = st.columns(4)
    if s9.button("👨‍👩‍👧\n\nPTA Meeting", use_container_width=True):
        st.session_state.menu = "👨‍👩‍👧 PTA Meeting"; st.rerun()
    if s10.button("🔍\n\nInspection", use_container_width=True):
        st.session_state.menu = "🔍 Inspection"; st.rerun()
    if s11.button("🎓\n\nAlumni", use_container_width=True):
        st.session_state.menu = "🎓 Alumni"; st.rerun()
    if s12.button("🎉\n\nAlumni Reunion", use_container_width=True):
        st.session_state.menu = "🎉 Alumni Reunion"; st.rerun()
    s13, s14, s15, s16 = st.columns(4)
    if s13.button("💬\n\nBehaviour / Clinic", use_container_width=True):
        st.session_state.menu = "💬 Behaviour / Clinic"; st.rerun()
    if s14.button("🏫\n\nStreams", use_container_width=True):
        st.session_state.menu = "🏫 Streams"; st.rerun()
    if s15.button("📊\n\nHeadteacher Dashboard", use_container_width=True):
        st.session_state.menu = "📊 Headteacher Dashboard"; st.rerun()
    if s16.button("🌟\n\nMaster Summary", type="primary", use_container_width=True):
        st.session_state.menu = "🌟 Master Summary"; st.rerun()
    st.divider()
    st.success("🏠 Home Dashboard - Tap any tile to open. Use Search or Side Menu for fast jump.")
    st.stop()

# ============ ALL OTHER PAGES - PASTE YOUR OLD CODE INSIDE EACH ============
# Header for current page
st.header(st.session_state.menu)

if st.session_state.menu == "🌟 Master Summary":
    st.markdown('<div class="color-gold">🌟 MASTER SUMMARY - Whole School</div>', unsafe_allow_html=True)
    st.write("This is your whole school in 1 page.")
    # PASTE YOUR OLD Master Summary CODE HERE
    st.info("Paste your old Master code here - keep your Google Sheets logic")

if st.session_state.menu == "📋 Attendance":
    st.markdown('<div class="color-blue">📋 ATTENDANCE - Blue = Learning</div>', unsafe_allow_html=True)
    # PASTE YOUR OLD Attendance CODE HERE
    st.write(f"Attendance for {selected_class} {selected_stream} - {selected_date}")
    st.info("Paste your old Attendance code here")

if st.session_state.menu == "📝 Take Quiz":
    st.markdown('<div class="color-blue">📝 TAKE QUIZ</div>', unsafe_allow_html=True)
    # PASTE YOUR OLD Quiz CODE HERE
    st.info("Paste your old Quiz code here")

if st.session_state.menu == "📊 Performance":
    st.markdown('<div class="color-blue">📊 PERFORMANCE</div>', unsafe_allow_html=True)
    # PASTE YOUR OLD Performance CODE HERE
    st.info("Paste your old Performance code here")

if st.session_state.menu == "💬 Behaviour / Clinic":
    st.markdown('<div class="color-red">💬 BEHAVIOUR / CLINIC</div>', unsafe_allow_html=True)
    st.info("Paste your old Behaviour code here")

if st.session_state.menu == "👥 Learners":
    st.markdown('<div class="color-blue">👥 LEARNERS</div>', unsafe_allow_html=True)
    st.info("Paste your old Learners code here")

if st.session_state.menu == "🏫 Streams":
    st.markdown('<div class="color-purple">🏫 STREAMS</div>', unsafe_allow_html=True)
    st.info("Paste your old Streams code here")

if st.session_state.menu == "🎓 Alumni":
    st.markdown('<div class="color-purple">🎓 ALUMNI</div>', unsafe_allow_html=True)
    st.info("Paste your old Alumni code here")

if st.session_state.menu == "📚 Quiz Bank":
    st.markdown('<div class="color-blue">📚 QUIZ BANK</div>', unsafe_allow_html=True)
    st.info("Paste your old Quiz Bank code here")

if st.session_state.menu == "🗳️ Voting":
    st.markdown('<div class="color-purple">🗳️ VOTING</div>', unsafe_allow_html=True)
    st.info("Paste your old Voting code here")

if st.session_state.menu == "📄 Report Cards":
    st.markdown('<div class="color-blue">📄 REPORT CARDS</div>', unsafe_allow_html=True)
    st.info("Paste your old Report Cards code here")

if st.session_state.menu == "💰 Fees":
    st.markdown('<div class="color-green">💰 FEES - Green = Money</div>', unsafe_allow_html=True)
    # PASTE YOUR OLD Fees CODE HERE
    st.info("Paste your old Fees code here")

if st.session_state.menu == "💬 Parent Message":
    st.markdown('<div class="color-green">💬 PARENT MESSAGE</div>', unsafe_allow_html=True)
    st.info("Paste your old Parent Message code here")

if st.session_state.menu == "🔢 Student Code & Pay":
    st.markdown('<div class="color-green">🔢 STUDENT CODE & PAY</div>', unsafe_allow_html=True)
    st.info("Paste your old Student Code code here")

if st.session_state.menu == "📚 NCDC Outcomes":
    st.markdown('<div class="color-orange">📚 NCDC OUTCOMES - Orange = Teaching</div>', unsafe_allow_html=True)
    st.info("Paste your old NCDC code here")

if st.session_state.menu == "📝 Lesson Plans":
    st.markdown('<div class="color-orange">📝 LESSON PLANS</div>', unsafe_allow_html=True)
    st.info("Paste your old Lesson Plans code here")

if st.session_state.menu == "📔 Record of Work":
    st.markdown('<div class="color-orange">📔 RECORD OF WORK</div>', unsafe_allow_html=True)
    st.info("Paste your old Record of Work code here")

if st.session_state.menu == "📅 Schemes of Work":
    st.markdown('<div class="color-orange">📅 SCHEMES OF WORK</div>', unsafe_allow_html=True)
    st.info("Paste your old Schemes code here")

if st.session_state.menu == "📊 Headteacher Dashboard":
    st.markdown('<div class="color-gold">📊 HEADTEACHER DASHBOARD</div>', unsafe_allow_html=True)
    st.info("Paste your old Dashboard code here")

if st.session_state.menu == "🗓️ Timetable & Duty":
    st.markdown('<div class="color-orange">🗓️ TIMETABLE & DUTY</div>', unsafe_allow_html=True)
    st.info("Paste your old Timetable code here")

if st.session_state.menu == "👩🏾‍🏫 Staff & Payroll":
    st.markdown('<div class="color-green">👩🏾‍🏫 STAFF & PAYROLL - Green = Money</div>', unsafe_allow_html=True)
    st.info("Paste your old Staff & Payroll code here")

if st.session_state.menu == "🎓 Exams / PLE Mock":
    st.markdown('<div class="color-blue">🎓 EXAMS / PLE MOCK</div>', unsafe_allow_html=True)
    st.info("Paste your next piece here")
