# ILEARN UGANDA v45.1 COMPLETE - SECRETS FIXED + FORGIVING LOGIN
import streamlit as st
import sqlite3
import pandas as pd
from datetime import date
st.set_page_config(page_title="ILEARN Uganda", layout="wide")
def get_secret(name, default=""):
    try:
        return st.secrets.get(name, default)
    except:
        return default
SCHOOL = {"name": "Your School Name","short_name": "YS","motto": "Strive For Excellence","district": "Kampala","phone": "+256 700 000000","email": "info@yourschool.ac.ug","year": 2026, "term": "Term 3"}
FEES_STRUCTURE = {"Baby":120000,"Middle":120000,"Top":130000,"P1":150000,"P2":150000,"P3":170000,"P4":170000,"P5":200000,"P6":200000,"P7":250000}
CLASSES = ["Baby","Middle","Top","P1","P2","P3","P4","P5","P6","P7"]
STREAMS = ["A","B"]
SUBJECTS = ["English","Maths","Science","SST","RE"]
def ilearn_grade(s):
    try: s = int(s)
    except: return "F"
    if s >= 90: return "D1"
    if s >= 80: return "D2"
    if s >= 70: return "C3"
    if s >= 60: return "C4"
    if s >= 50: return "C5"
    if s >= 40: return "C6"
    if s >= 30: return "P7"
    return "F"
def get_db():
    c = sqlite3.connect("ilearn.db", check_same_thread=False)
    c.execute("CREATE TABLE IF NOT EXISTS learners (name TEXT, class TEXT, stream TEXT, UNIQUE(name, class, stream))")
    c.execute("CREATE TABLE IF NOT EXISTS attendance (date TEXT, class TEXT, stream TEXT, learner TEXT, status TEXT, UNIQUE(date, class, stream, learner))")
    c.execute("CREATE TABLE IF NOT EXISTS fee_payments (learner TEXT, amount INTEGER, date TEXT, receipt TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS fee_totals (learner TEXT PRIMARY KEY, total INTEGER)")
    c.execute("CREATE TABLE IF NOT EXISTS homework (date TEXT, class TEXT, stream TEXT, subject TEXT, task TEXT, UNIQUE(date, class, stream, subject))")
    c.execute("CREATE TABLE IF NOT EXISTS marks (learner TEXT, class TEXT, stream TEXT, term TEXT, subject TEXT, score INTEGER, teacher TEXT, UNIQUE(learner, class, stream, term, subject))")
    c.execute("CREATE TABLE IF NOT EXISTS marks_audit (learner TEXT, subject TEXT, old_score INTEGER, new_score INTEGER, who TEXT, when_ TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS audit (who TEXT, action TEXT, when_ TEXT)")
    if c.execute("SELECT COUNT(*) FROM learners").fetchone()[0] == 0:
        for n, cl in [("Amina","P4"),("John","P4"),("Sarah","P4"),("David","P4"),("Grace","P5"),("Peter","P5"),("Mary","P5"),("James","P6")]:
            c.execute("INSERT OR IGNORE INTO learners VALUES (?,?,?)", (n, cl, "A"))
    c.commit()
    return c
def audit(who, action):
    c = get_db()
    c.execute("INSERT INTO audit VALUES (?,?,datetime('now'))", (who, action))
    c.commit(); c.close()
# ---------- LOGIN - MAIN BLOCK - FIXED v45.1 ----------
if "user" not in st.session_state:
    st.markdown(f"# 🌟 ILEARN UGANDA\n### {SCHOOL['name']} - {SCHOOL['motto']}")
    has_secrets = bool(get_secret("ADMIN_EMAIL"))
    st.info(f"Secrets loaded in cloud: {'YES ✅' if has_secrets else 'NO ❌ - Go to Manage app > Settings > Secrets'}")
    email = st.text_input("Email").strip().lower()
    password = st.text_input("Password", type="password").strip()
    pin = st.text_input("PIN (Headteacher / Bursar only)", type="password").strip()
    if st.button("Login", use_container_width=True):
        users = {
            get_secret("ADMIN_EMAIL","").strip().lower(): (get_secret("ADMIN_PASSWORD","").strip(), get_secret("ADMIN_PIN","").strip(), "Headteacher"),
            get_secret("BURSAR_EMAIL","").strip().lower(): (get_secret("BURSAR_PASSWORD","").strip(), get_secret("BURSAR_PIN","").strip(), "Bursar"),
            get_secret("TEACHER_EMAIL","").strip().lower(): (get_secret("TEACHER_PASSWORD","").strip(), "", "Teacher"),
        }
        if email in users and users[email][0] and password == users[email][0]:
            role = users[email][2]
            saved_pin = users[email][1]
            if saved_pin and role in ["Headteacher","Bursar"] and pin != saved_pin:
                st.error("Password OK, but PIN wrong. Check ADMIN_PIN in Secrets.")
            else:
                st.session_state.user = email
                st.session_state.user_name = email.split("@")[0]
                st.session_state.role = role
                st.session_state.menu = "🌟 Master Summary"
                audit(email, "Login")
                st.rerun()
        else:
            st.error("Wrong email or password. Check secrets.toml")
    st.stop()
st.markdown(f"### 🌟 {SCHOOL['name']} | {SCHOOL['motto']} | {SCHOOL['district']} | {st.session_state.role} - {st.session_state.user_name}")
if st.button("Logout"):
    audit(st.session_state.user, "Logout")
    del st.session_state.user
    st.rerun()
selected_year = st.selectbox("Year", [2025,2026,2027], index=1)
selected_term = st.selectbox("Term", ["Term 1","Term 2","Term 3"], index=2)
selected_class = st.selectbox("Class", CLASSES, index=6)
selected_stream = st.selectbox("Stream", STREAMS)
selected_date = st.date_input("Date", date.today())
selected_subject = st.selectbox("Subject", SUBJECTS)
menu = st.sidebar.radio("Menu", ["🌟 Master Summary","📋 Attendance","💰 Fees","📚 Homework","📊 Performance","📄 Report Cards","📜 Audit Log"])
st.session_state.menu = menu
if menu == "📋 Attendance":
    st.subheader("📋 Attendance")
    c = get_db()
    learners = c.execute("SELECT name FROM learners WHERE class=? AND stream=? ORDER BY name", (selected_class, selected_stream)).fetchall()
    c.close()
    if not learners:
        new = st.text_input("Add learner name")
        if st.button("Add Learner"):
            cc = get_db(); cc.execute("INSERT INTO learners VALUES (?,?,?)", (new, selected_class, selected_stream)); cc.commit(); cc.close(); st.rerun()
    else:
        statuses = {}
        for (nm,) in learners:
            statuses[nm] = st.selectbox(f"{nm}", ["Present","Absent","Late"], key=f"att_{nm}")
        if st.button("✅ SAVE Attendance", use_container_width=True):
            cc = get_db()
            for nm, stt in statuses.items():
                cc.execute("INSERT INTO attendance VALUES (?,?,?,?,?) ON CONFLICT(date,class,stream,learner) DO UPDATE SET status=excluded.status", (str(selected_date), selected_class, selected_stream, nm, stt))
            cc.commit(); cc.close()
            audit(st.session_state.user, f"Saved Attendance {selected_class} {selected_stream} {selected_date}")
            st.success(f"✅ Saved! {list(statuses.values()).count('Present')} Present, {list(statuses.values()).count('Absent')} Absent")
        cc = get_db()
        rows = cc.execute("SELECT learner,status FROM attendance WHERE date=? AND class=? AND stream=?", (str(selected_date), selected_class, selected_stream)).fetchall()
        cc.close()
        if rows: st.dataframe(pd.DataFrame(rows, columns=["Learner","Status"]), use_container_width=True)
elif menu == "💰 Fees":
    st.subheader("💰 Fees")
    search = st.text_input("Search learner").strip().lower()
    c = get_db(); all_l = c.execute("SELECT name,class FROM learners ORDER BY name").fetchall(); c.close()
    filt = [r for r in all_l if search in r[0].lower()] if search else all_l
    if filt:
        pick = st.selectbox("Pick Learner", [f"{n} - {cl}" for n,cl in filt])
        name = pick.split(" - ")[0]; cl = pick.split(" - ")[1]
        c = get_db()
        tot_r = c.execute("SELECT total FROM fee_totals WHERE learner=?", (name,)).fetchone()
        total = tot_r[0] if tot_r else FEES_STRUCTURE.get(cl,150000)
        paid = c.execute("SELECT COALESCE(SUM(amount),0) FROM fee_payments WHERE learner=?", (name,)).fetchone()[0] or 0
        c.close()
        bal = max(0, total-paid)
        c1,c2,c3 = st.columns(3); c1.metric("Total", f"{total:,}"); c2.metric("Paid", f"{paid:,}"); c3.metric("Balance", f"{bal:,}")
        new_total = st.number_input("Change Total (bursary)", value=total, step=1000)
        amt = st.number_input("Payment Amount", min_value=0, step=1000)
        if st.button("✅ SAVE Payment", use_container_width=True):
            if amt > bal and bal>0:
                st.error("Overpay blocked. Pay only balance.")
            elif amt <= 0:
                st.error("Enter amount > 0")
            else:
                cc = get_db()
                cc.execute("INSERT OR REPLACE INTO fee_totals VALUES (?,?)", (name, new_total))
                rec = f"ILEARN-{cc.execute('SELECT COUNT(*)+1 FROM fee_payments').fetchone()[0]:03d}"
                cc.execute("INSERT INTO fee_payments VALUES (?,?,?,?)", (name, amt, str(selected_date), rec))
                cc.commit(); cc.close()
                audit(st.session_state.user, f"Fees {name} paid {amt} receipt {rec}")
                st.success(f"✅ Saved! Receipt {rec} Balance now {max(0,new_total-(paid+amt)):,}")
                st.rerun()
        st.divider(); st.write("Who Owes:")
        cc = get_db(); all2 = cc.execute("SELECT name,class FROM learners").fetchall(); rows=[]
        for nm, cl2 in all2:
            t = cc.execute("SELECT total FROM fee_totals WHERE learner=?", (nm,)).fetchone()
            tt = t[0] if t else FEES_STRUCTURE.get(cl2,150000)
            pp = cc.execute("SELECT COALESCE(SUM(amount),0) FROM fee_payments WHERE learner=?", (nm,)).fetchone()[0] or 0
            if tt-pp>0: rows.append((nm,cl2,tt,pp,tt-pp))
        cc.close()
        if rows: st.dataframe(pd.DataFrame(rows, columns=["Learner","Class","Total","Paid","Balance"]), use_container_width=True)
elif menu == "📚 Homework":
    st.subheader("📚 Homework")
    task = st.text_area("Homework task", placeholder="e.g. Page 42 Q1-5")
    if st.button("✅ SAVE Homework", use_container_width=True):
        if not task: st.error("Type homework first")
        else:
            cc = get_db(); cc.execute("INSERT INTO homework VALUES (?,?,?,?,?) ON CONFLICT(date,class,stream,subject) DO UPDATE SET task=excluded.task", (str(selected_date), selected_class, selected_stream, selected_subject, task)); cc.commit(); cc.close()
            audit(st.session_state.user, f"Homework {selected_class} {selected_stream} {selected_subject}")
            st.success("✅ Saved!")
    cc = get_db(); rows = cc.execute("SELECT class,stream,subject,task FROM homework WHERE date=?", (str(selected_date),)).fetchall(); cc.close()
    if rows: st.dataframe(pd.DataFrame(rows, columns=["Class","Stream","Subject","Task"]), use_container_width=True)
    else: st.info("No homework today yet.")
elif menu == "📊 Performance":
    st.subheader("📊 Performance / Marks")
    c = get_db(); learners = c.execute("SELECT name FROM learners WHERE class=? AND stream=? ORDER BY name", (selected_class, selected_stream)).fetchall(); c.close()
    for (nm,) in learners:
        col1,col2 = st.columns([3,1])
        with col1: st.write(nm)
        with col2:
            sc = st.number_input(f"Score {nm}", min_value=0, max_value=100, value=0, key=f"mark_{nm}")
            if st.button(f"Save {nm}", key=f"btn_{nm}"):
                cc = get_db()
                old = cc.execute("SELECT score FROM marks WHERE learner=? AND class=? AND stream=? AND term=? AND subject=?", (nm, selected_class, selected_stream, selected_term, selected_subject)).fetchone()
                cc.execute("INSERT INTO marks VALUES (?,?,?,?,?,?,?) ON CONFLICT(learner,class,stream,term,subject) DO UPDATE SET score=excluded.score, teacher=excluded.teacher", (nm, selected_class, selected_stream, selected_term, selected_subject, sc, st.session_state.user))
                if old and old[0]!=sc:
                    cc.execute("INSERT INTO marks_audit VALUES (?,?,?,?,?,datetime('now'))", (nm, selected_subject, old[0], sc, st.session_state.user))
                cc.commit(); cc.close()
                audit(st.session_state.user, f"Mark {nm} {selected_subject} {sc}")
                st.success(f"{nm} {sc} ({ilearn_grade(sc)}) Saved")
                st.rerun()
    cc = get_db(); rows = cc.execute("SELECT learner,subject,score FROM marks WHERE class=? AND stream=? AND term=? ORDER BY learner", (selected_class, selected_stream, selected_term)).fetchall(); cc.close()
    if rows:
        df = pd.DataFrame(rows, columns=["Learner","Subject","Score"]); df["Grade"] = df["Score"].apply(ilearn_grade)
        st.dataframe(df, use_container_width=True)
        st.write(f"Average: {df['Score'].mean():.1f}")
elif menu == "📄 Report Cards":
    st.subheader("📄 Report Cards - Real Data")
    c = get_db(); all_l = c.execute("SELECT name,class,stream FROM learners ORDER BY class,name").fetchall(); c.close()
    if not all_l: st.warning("No learners yet.")
    else:
        pick = st.selectbox("Pick Learner", [f"{n} - {cl} {st_}" for n,cl,st_ in all_l])
        name = pick.split(" - ")[0]; cl = pick.split(" - ")[1].split()[0]; st_ = pick.split(" - ")[1].split()[1]
        c = get_db()
        marks = c.execute("SELECT subject,score,teacher FROM marks WHERE learner=? AND class=? AND stream=? AND term=? ORDER BY subject", (name,cl,st_,selected_term)).fetchall()
        att_t = c.execute("SELECT COUNT(*) FROM attendance WHERE learner=?", (name,)).fetchone()[0]
        att_p = c.execute("SELECT COUNT(*) FROM attendance WHERE learner=? AND status='Present'", (name,)).fetchone()[0]
        tot_r = c.execute("SELECT total FROM fee_totals WHERE learner=?", (name,)).fetchone()
        paid = c.execute("SELECT COALESCE(SUM(amount),0) FROM fee_payments WHERE learner=?", (name,)).fetchone()[0] or 0
        c.close()
        total = tot_r[0] if tot_r else FEES_STRUCTURE.get(cl,150000); bal = max(0,total-paid)
        avg = sum([r[1] for r in marks])/len(marks) if marks else 0
        att_pct = (att_p/att_t*100) if att_t>0 else 0
        st.write(f"**{SCHOOL['name']}** | {SCHOOL['motto']} | {SCHOOL['phone']}")
        st.write(f"**Learner:** {name} | **Class:** {cl} {st_} | **Term:** {selected_term} {selected_year} | **Date:** {selected_date}")
        c1,c2,c3,c4 = st.columns(4); c1.metric("Average", f"{avg:.1f} ({ilearn_grade(avg) if marks else '-'})"); c2.metric("Attendance", f"{att_pct:.0f}%"); c3.metric("Fees Balance", f"{bal:,} UGX"); c4.metric("Subjects", len(marks))
        if marks:
            df = pd.DataFrame([(r[0],r[1],ilearn_grade(r[1]),r[2]) for r in marks], columns=["Subject","Score","Grade","Teacher"])
            st.dataframe(df, use_container_width=True)
        else: st.warning("No marks yet for this term.")
        st.write(f"Attendance: Total {att_t} | Present {att_p} | {att_pct:.0f}%")
        st.write(f"Fees: Total {total:,} | Paid {paid:,} | Balance {bal:,}")
        if bal==0: st.success("✅ Fees PAID IN FULL")
        else: st.error(f"Balance Owed: {bal:,} UGX")
        tc = st.text_area("Teacher Comment", key="tc"); hc = st.text_area("Headteacher Comment", key="hc")
        st.write(f"**Teacher:** {tc or '-'}"); st.write(f"**Headteacher:** {hc or '-'}")
        st.write("Class Teacher Signature: __________   Headteacher Signature: __________   Date: __________")
        if marks:
            df2 = pd.DataFrame([(name,cl,st_,selected_term,r[0],r[1],ilearn_grade(r[1])) for r in marks], columns=["Learner","Class","Stream","Term","Subject","Score","Grade"])
            st.download_button("📥 Download Report Card CSV", df2.to_csv(index=False).encode(), f"report_{name}_{selected_term}.csv", "text/csv", use_container_width=True)
elif menu == "🌟 Master Summary":
    st.subheader("🌟 Master Summary - Real Data")
    c = get_db()
    total_l = c.execute("SELECT COUNT(*) FROM learners").fetchone()[0]
    att_t = c.execute("SELECT COUNT(*) FROM attendance WHERE date=?", (str(selected_date),)).fetchone()[0]
    att_p = c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Present'", (str(selected_date),)).fetchone()[0]
    att_a = c.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND status='Absent'", (str(selected_date),)).fetchone()[0]
    hw_t = c.execute("SELECT COUNT(*) FROM homework WHERE date=?", (str(selected_date),)).fetchone()[0]
    fees_paid = c.execute("SELECT COALESCE(SUM(amount),0) FROM fee_payments").fetchone()[0] or 0
    avg_m = c.execute("SELECT AVG(score) FROM marks WHERE term=?", (selected_term,)).fetchone()[0] or 0
    c.close()
    m1,m2,m3,m4 = st.columns(4); m1.metric("Learners", total_l); m2.metric("Attendance Today", f"{att_t} marked"); m3.metric("Present / Absent", f"{att_p} / {att_a}"); m4.metric("Homework Today", f"{hw_t} given")
    m5,m6 = st.columns(2); m5.metric("Fees Paid (All Time)", f"{fees_paid:,} UGX"); m6.metric("Avg Mark This Term", f"{avg_m:.1f}")
    st.divider(); st.write("Per Class:")
    rows=[]
    for cl in CLASSES:
        for st_ in STREAMS:
            cc = get_db()
            li = cc.execute("SELECT COUNT(*) FROM learners WHERE class=? AND stream=?", (cl,st_)).fetchone()[0]
            ai = cc.execute("SELECT COUNT(*) FROM attendance WHERE date=? AND class=? AND stream=?", (str(selected_date),cl,st_)).fetchone()[0]
            hi = cc.execute("SELECT COUNT(*) FROM homework WHERE date=? AND class=? AND stream=?", (str(selected_date),cl,st_)).fetchone()[0]
            av = cc.execute("SELECT AVG(score) FROM marks WHERE class=? AND stream=? AND term=?", (cl,st_,selected_term)).fetchone()[0] or 0
            cc.close()
            rows.append((cl,st_,li,f"{ai}/{li}" if li>0 else "No learners","✅ YES" if hi>0 else "🔴 NO", f"{av:.1f}" if av>0 else "-"))
    st.dataframe(pd.DataFrame(rows, columns=["Class","Stream","Learners","Attendance Today","Homework?","Avg Mark"]), use_container_width=True)
elif menu == "📜 Audit Log":
    st.subheader("📜 Audit Log - Who Did What")
    c = get_db(); rows = c.execute("SELECT who,action,when_ FROM audit ORDER BY rowid DESC LIMIT 100").fetchall(); c.close()
    if rows: st.dataframe(pd.DataFrame(rows, columns=["Who","Action","When"]), use_container_width=True)
