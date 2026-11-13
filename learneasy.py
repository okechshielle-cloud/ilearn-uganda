import streamlit as st
import pandas as pd
from datetime import date, datetime
import calendar

st.set_page_config(page_title="ILEARN Uganda", layout="wide")
st.title("🇺🇬 ILEARN Uganda - School Management System")
conn = st.connection("gsheets", type="GSheetsConnection")

def read_sheet(name):
    try:
        df = conn.read(worksheet=name, ttl=0)
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception:
        return pd.DataFrame()

def save_to_sheet(name, new_row_dict):
    df = read_sheet(name)
    new_df = pd.DataFrame([new_row_dict])
    if df.empty:
        df = new_df
    else:
        for col in new_df.columns:
            if col not in df.columns:
                df[col] = ""
        for col in df.columns:
            if col not in new_df.columns:
                new_df[col] = ""
        df = pd.concat([df, new_df], ignore_index=True)
    conn.update(worksheet=name, data=df)
    return df

def update_row_in_sheet(name, orig_index, new_dict):
    df = read_sheet(name)
    if df.empty or orig_index not in df.index:
        return False
    for k, v in new_dict.items():
        if k not in df.columns:
            df[k] = ""
        df.at[orig_index, k] = v
    conn.update(worksheet=name, data=df)
    return True

def delete_row_in_sheet(name, orig_index):
    df = read_sheet(name)
    if df.empty or orig_index not in df.index:
        return False
    df = df.drop(index=orig_index).reset_index(drop=True)
    conn.update(worksheet=name, data=df)
    return True

def get_grade(percent):
    if percent >= 80: return "D1"
    elif percent >= 70: return "D2"
    elif percent >= 60: return "C3"
    elif percent >= 50: return "C4"
    elif percent >= 40: return "C5"
    elif percent >= 30: return "C6"
    elif percent >= 20: return "P7"
    elif percent >= 10: return "P8"
    else: return "F9"

def get_active_learners(year, class_name, stream):
    df = read_sheet("Learners")
    if df.empty or "Learner_Name" not in df.columns:
        return []
    filt = df[(df["Year"].astype(str)==str(year)) & (df["Class"]==class_name) & (df["Stream"]==stream)]
    if "Status" in filt.columns:
        active = filt[filt["Status"].astype(str).str.lower()=="active"]
        if not active.empty:
            return active["Learner_Name"].drop_duplicates().tolist()
        return filt["Learner_Name"].drop_duplicates().tolist()
    return filt["Learner_Name"].drop_duplicates().tolist()

# ============ SIDEBAR ============
st.sidebar.header("📅 School Filter - Applies Everywhere")
YEARS = ["2025","2026","2027","2028","2029","2030"]
selected_year = st.sidebar.selectbox("School Year - Annual Records", YEARS, index=1)
selected_class = st.sidebar.selectbox("Class", ["P1","P2","P3","P4","P5","P6","P7"])
selected_stream = st.sidebar.selectbox("Stream", ["A","B","C","Blue","Red"], index=0)
selected_subject = st.sidebar.selectbox("Subject", ["English","Maths","Science","SST","Reading","R.E","Kiswahili"])
selected_term = st.sidebar.selectbox("Term", ["Term 1", "Term 2", "Term 3"], index=0)
st.sidebar.info(f"Viewing: **{selected_year} | {selected_class} {selected_stream} | {selected_subject} | {selected_term}**")
st.sidebar.subheader("📅 Calendar - Click a Day")
cal_month = st.sidebar.selectbox("Month", list(calendar.month_name)[1:], index=datetime.now().month-1)
month_num = list(calendar.month_name).index(cal_month)
cal = calendar.monthcalendar(int(selected_year), month_num)
st.sidebar.write(f"**{cal_month} {selected_year}**")
if "selected_date" not in st.session_state:
    st.session_state.selected_date = date.today()
for week in cal:
    cols = st.sidebar.columns(7)
    for i, day in enumerate(week):
        if day != 0:
            if cols[i].button(f"{day}", key=f"cal_{selected_year}_{month_num}_{day}"):
                st.session_state.selected_date = date(int(selected_year), month_num, day)
selected_date = st.sidebar.date_input("Selected Date", value=st.session_state.selected_date)

# ============ MAIN TABS - 17 TABS ============
tab_att, tab_quiz, tab_perf, tab_behav, tab_learn, tab_stream, tab_alumni, tab_quizbank, tab_vote, tab_report, tab_fees, tab_parent, tab_code, tab_curr, tab_lesson, tab_row, tab_scheme = st.tabs([
    "📋 Attendance", "📝 Take Quiz", "📊 Performance", "💬 Behaviour / Clinic",
    "👥 Learners", "🏫 Streams", "🎓 Alumni", "📚 Quiz Bank", "🗳️ Voting",
    "📄 Report Cards", "💰 Fees", "💬 Parent Message", "🔢 Student Code & Pay",
    "📚 NCDC Outcomes", "📝 Lesson Plans", "📔 Record of Work", "📅 Schemes of Work"
])

# ============ 1. ATTENDANCE ============
with tab_att:
    st.subheader(f"📋 Attendance - {selected_date} - {selected_class} {selected_stream} - {selected_year}")
    learners = get_active_learners(selected_year, selected_class, selected_stream)
    if not learners:
        st.warning("No Active learners. Go to Learners tab.")
    else:
        results = {}
        for learner in learners:
            results[learner] = st.selectbox(learner, ["✅ Present", "❌ Absent", "⏰ Late"], key=f"att_{learner}_{selected_date}_{selected_class}_{selected_stream}")
        if st.button("💾 SAVE ATTENDANCE", type="primary"):
            present = sum(1 for v in results.values() if "Present" in v)
            absent = sum(1 for v in results.values() if "Absent" in v)
            late = sum(1 for v in results.values() if "Late" in v)
            save_to_sheet("Attendance", {"Year": selected_year, "Date": str(selected_date), "Class": selected_class, "Stream": selected_stream, "Present": present, "Absent": absent, "Late": late, "Total": len(learners)})
            st.success(f"✅ Saved! {present} Present | {absent} Absent | {late} Late")
    att_df = read_sheet("Attendance")
    if not att_df.empty and "Year" in att_df.columns:
        st.dataframe(att_df[att_df["Year"].astype(str)==selected_year], use_container_width=True)

# ============ 2. TAKE QUIZ ============
with tab_quiz:
    st.subheader(f"📝 Take Quiz - {selected_subject} - {selected_class} {selected_stream}")
    quiz_sets_df = read_sheet("Quiz_Sets")
    available = []
    if not quiz_sets_df.empty and "Quiz_ID" in quiz_sets_df.columns:
        available = quiz_sets_df[(quiz_sets_df["Year"].astype(str)==selected_year) & (quiz_sets_df["Status"].astype(str).str.lower()=="active")]["Quiz_ID"].tolist() if "Status" in quiz_sets_df.columns else quiz_sets_df["Quiz_ID"].tolist()
    if not available:
        st.warning("No Active Quiz in Quiz Bank. Go to Quiz Bank and create Q1 first.")
        learner_name = st.text_input("Learner Name", key="quiz_learner_fallback")
        if selected_subject == "Kiswahili":
            q1 = st.radio("1. Neno 'Mwalimu' lina maana gani?", ["Mwanafunzi", "Mfundishaji", "Daktari", "Mkulima"], key="q1_fallback")
            q2 = st.radio("2. Chagua neno sahihi: Mtoto ___ shule.", ["anaenda", "wanaenda", "naenda", "tunaenda"], key="q2_fallback")
            if st.button("Submit Quick Quiz", type="primary"):
                if learner_name:
                    score = (1 if q1=="Mfundishaji" else 0) + (1 if q2=="anaenda" else 0)
                    grade = get_grade((score/2)*100)
                    save_to_sheet("Quiz_Results", {"Year": selected_year, "Date": str(selected_date), "Quiz_ID": "QUICK", "Learner_Name": learner_name, "Class": selected_class, "Stream": selected_stream, "Subject": selected_subject, "Score": score, "Grade": grade, "Total_Questions": 2})
                    st.success(f"✅ Saved! {learner_name} got {score}/2 = {grade}")
        else:
            q1 = st.radio("1. What is 5 + 3?", ["6","7","8","9"], key="q1_fallback")
            q2 = st.radio("2. What is 10 - 4?", ["5","6","7","8"], key="q2_fallback")
            if st.button("Submit Quick Quiz", type="primary"):
                if learner_name:
                    score = (1 if q1=="8" else 0) + (1 if q2=="6" else 0)
                    grade = get_grade((score/2)*100)
                    save_to_sheet("Quiz_Results", {"Year": selected_year, "Date": str(selected_date), "Quiz_ID": "QUICK", "Learner_Name": learner_name, "Class": selected_class, "Stream": selected_stream, "Subject": selected_subject, "Score": score, "Grade": grade, "Total_Questions": 2})
                    st.success(f"✅ Saved! {learner_name} got {score}/2 = {grade}")
    else:
        chosen_quiz_id = st.selectbox("Choose Quiz Set", available, key="take_quiz_id")
        learner_name = st.text_input("Learner Name", key="quiz_learner")
        q_df = read_sheet("Quiz_Questions")
        questions = pd.DataFrame()
        if not q_df.empty and "Quiz_ID" in q_df.columns:
            questions = q_df[q_df["Quiz_ID"].astype(str)==str(chosen_quiz_id)].sort_values("Question_No") if "Question_No" in q_df.columns else q_df[q_df["Quiz_ID"].astype(str)==str(chosen_quiz_id)]
        if questions.empty:
            st.info(f"No questions yet for {chosen_quiz_id}. Go to Quiz Bank.")
        else:
            answers = {}
            for idx, row in questions.iterrows():
                opts = [str(row.get("Option_A","")), str(row.get("Option_B","")), str(row.get("Option_C","")), str(row.get("Option_D",""))]
                opts = [o for o in opts if o and o!="nan"]
                answers[str(idx)] = st.radio(f"{row.get('Question_No','')}. {row.get('Question','')}", opts, key=f"ans_{chosen_quiz_id}_{idx}")
            if st.button("Submit Quiz - Save to Google Sheets", type="primary"):
                if not learner_name:
                    st.warning("Type learner name first.")
                else:
                    score = 0
                    total = len(questions)
                    for idx, row in questions.iterrows():
                        letter = str(row.get("Correct_Answer","")).strip().upper()
                        correct_text = ""
                        if letter=="A": correct_text = str(row.get("Option_A",""))
                        elif letter=="B": correct_text = str(row.get("Option_B",""))
                        elif letter=="C": correct_text = str(row.get("Option_C",""))
                        elif letter=="D": correct_text = str(row.get("Option_D",""))
                        if answers.get(str(idx)) == correct_text:
                            score += 1
                    grade = get_grade((score/total)*100 if total>0 else 0)
                    save_to_sheet("Quiz_Results", {"Year": selected_year, "Date": str(selected_date), "Quiz_ID": chosen_quiz_id, "Learner_Name": learner_name, "Class": selected_class, "Stream": selected_stream, "Subject": selected_subject, "Score": score, "Grade": grade, "Total_Questions": total})
                    save_to_sheet("Performance", {"Year": selected_year, "Class": selected_class, "Stream": selected_stream, "Subject": selected_subject, "D1": 1 if grade=="D1" else 0, "D2": 1 if grade=="D2" else 0, "C3": 1 if grade=="C3" else 0, "C4": 1 if grade=="C4" else 0, "C5": 1 if grade=="C5" else 0, "C6": 1 if grade=="C6" else 0, "P7": 1 if grade=="P7" else 0, "P8": 1 if grade=="P8" else 0, "F9": 1 if grade=="F9" else 0, "Total": 1})
                    st.success(f"✅ Saved! {learner_name} got {score}/{total} = {grade}")
                    st.balloons()
    quiz_df = read_sheet("Quiz_Results")
    if not quiz_df.empty and "Year" in quiz_df.columns:
        st.dataframe(quiz_df[quiz_df["Year"].astype(str)==selected_year].tail(20), use_container_width=True)

# ============ 3. PERFORMANCE ============
with tab_perf:
    st.subheader(f"📊 SUBJECT GENERAL PERFORMANCE - {selected_year} - {selected_class} {selected_stream}")
    quiz_df = read_sheet("Quiz_Results")
    if not quiz_df.empty and "Grade" in quiz_df.columns:
        filtered = quiz_df[(quiz_df["Year"].astype(str)==selected_year) & (quiz_df["Class"]==selected_class) & (quiz_df["Stream"]==selected_stream)]
        if not filtered.empty:
            perf = filtered.groupby(["Subject","Grade"]).size().unstack(fill_value=0)
            for col in ["D1","D2","C3","C4","C5","C6","P7","P8","F9"]:
                if col not in perf.columns: perf[col] = 0
            perf = perf[["D1","D2","C3","C4","C5","C6","P7","P8","F9"]]
            perf["TOT"] = perf.sum(axis=1)
            perf.insert(0, "CLASS", selected_class)
            st.dataframe(perf, use_container_width=True)
            total_row = perf[["D1","D2","C3","C4","C5","C6","P7","P8","F9","TOT"]].sum()
            st.write("**TOTAL Row:**")
            st.dataframe(pd.DataFrame([total_row], index=["TOTAL"]), use_container_width=True)
        else:
            st.info("No quiz results yet.")
    else:
        st.info("No quiz results yet.")

# ============ 4. BEHAVIOUR / CLINIC ============
with tab_behav:
    st.subheader(f"💬 Behaviour / Clinic - {selected_date} - {selected_class} {selected_stream}")
    learners = get_active_learners(selected_year, selected_class, selected_stream)
    if not learners:
        st.warning("No Active learners.")
    else:
        col1, col2 = st.columns(2)
        behav_learner = col1.selectbox("Choose Learner", learners, key="behav_learner")
        behav_type = col2.selectbox("Type", ["Behaviour", "Clinic / Sickbay"], key="behav_type")
        if behav_type == "Behaviour":
            category = st.selectbox("Behaviour Category", ["Good Behaviour - Praise", "Late Coming", "Noise Making", "Fighting / Bullying", "Missing Homework", "Neatness - Dirty Uniform", "Helping Others", "Respectful", "Other"], key="behav_cat")
            action_options = ["Talked to Learner", "Warned", "Called Parent", "Punishment - Clean Class", "Praised in Assembly", "No Action - Note Only"]
        else:
            category = st.selectbox("Clinic Category", ["Headache", "Fever", "Stomach Pain", "Injury / Wound", "Malaria Symptoms", "Cough / Flu", "First Aid Given", "Rest in Sickbay", "Sent Home", "Taken to Hospital"], key="clinic_cat")
            action_options = ["Given First Aid", "Given Paracetamol / Rest", "Called Parent", "Sent Home", "Rest in Sickbay", "Taken to Hospital", "No Action - Note Only"]
        note = st.text_area("Note / Details", key="behav_note")
        action = st.selectbox("Action Taken", action_options, key="behav_action")
        teacher = st.text_input("Teacher Name", value="Tr. Okech", key="behav_teacher")
        follow_up = st.date_input("Follow-Up Date", value=selected_date, key="behav_follow")
        need_follow = st.checkbox("Needs Follow-Up?", key="behav_follow_check")
        if st.button("💾 SAVE BEHAVIOUR / CLINIC", type="primary"):
            if not note:
                st.warning("Write a small note first.")
            else:
                save_to_sheet("Behaviour_Clinic", {"Year": selected_year, "Date": str(selected_date), "Learner_Name": behav_learner, "Class": selected_class, "Stream": selected_stream, "Type": behav_type, "Category": category, "Note": note, "Action_Taken": action, "Teacher": teacher, "Follow_Up_Date": str(follow_up) if need_follow else ""})
                st.success(f"✅ Saved! {behav_learner} - {behav_type} - {category}")
                st.rerun()
    bc_df = read_sheet("Behaviour_Clinic")
    if not bc_df.empty and "Year" in bc_df.columns:
        filtered_bc = bc_df[(bc_df["Year"].astype(str)==selected_year) & (bc_df["Class"]==selected_class) & (bc_df["Stream"]==selected_stream)]
        st.dataframe(filtered_bc, use_container_width=True)

# ============ 5. LEARNERS ============
with tab_learn:
    st.subheader(f"👥 Learners - {selected_year} - {selected_class} {selected_stream}")
    bulk = st.text_area("Paste names - one per line", placeholder="Okello John\nAchieng Mary", key="bulk_learners")
    if st.button("Save Learners to Google Sheets"):
        names = [n.strip() for n in bulk.split("\n") if n.strip()]
        for name in names:
            save_to_sheet("Learners", {"Year": selected_year, "Class": selected_class, "Stream": selected_stream, "Learner_Name": name, "Status": "Active", "Graduation_Year": "", "Reason": ""})
        st.success(f"✅ Saved {len(names)} learners!")
        st.rerun()
    learners_df = read_sheet("Learners")
    if not learners_df.empty and "Learner_Name" in learners_df.columns:
        show_filter = st.radio("Show:", ["Active Only (Daily Use)", "Graduated / Alumni", "All Learners"], horizontal=True, key="learn_filter")
        filtered = learners_df[learners_df["Year"].astype(str)==selected_year]
        if "Status" in filtered.columns:
            if show_filter == "Active Only (Daily Use)": filtered = filtered[filtered["Status"].astype(str).str.lower()=="active"]
            elif show_filter == "Graduated / Alumni": filtered = filtered[filtered["Status"].astype(str).str.lower()=="graduated"]
        st.dataframe(filtered, use_container_width=True)
        st.divider()
        st.subheader("🎓 Graduate Learner - Keep Records")
        active_names = learners_df[(learners_df["Year"].astype(str)==selected_year) & (learners_df["Status"].astype(str).str.lower()=="active")]["Learner_Name"].drop_duplicates().tolist() if "Status" in learners_df.columns else []
        if active_names:
            learner_to_graduate = st.selectbox("Choose learner", active_names, key="grad_select")
            graduation_reason = st.selectbox("Reason", ["Completed P7 - Graduated", "Transferred to Another School", "Left School"], key="grad_reason")
            if st.button("🎓 Mark as Graduated - Keep Records", type="primary"):
                save_to_sheet("Learners", {"Year": selected_year, "Class": selected_class, "Stream": selected_stream, "Learner_Name": learner_to_graduate, "Status": "Graduated", "Graduation_Year": selected_year, "Reason": graduation_reason})
                save_to_sheet("Alumni", {"Year": selected_year, "Learner_Name": learner_to_graduate, "Class": selected_class, "Stream": selected_stream, "Status": "Graduated", "Graduation_Year": selected_year, "Reason": graduation_reason})
                st.success(f"✅ {learner_to_graduate} marked as Graduated. Records SAFE.")
                st.rerun()

# ============ 6. STREAMS ============
with tab_stream:
    st.subheader(f"🏫 Streams - {selected_year} - {selected_class}")
    new_stream = st.text_input("New Stream Name", key="new_stream")
    if st.button("Add Stream to Google Sheets"):
        if new_stream:
            save_to_sheet("Streams", {"Year": selected_year, "Class": selected_class, "Stream": new_stream})
            st.success(f"✅ Stream {new_stream} saved!")
            st.rerun()
    streams_df = read_sheet("Streams")
    if not streams_df.empty and "Year" in streams_df.columns:
        st.dataframe(streams_df[streams_df["Year"].astype(str)==selected_year], use_container_width=True)
    st.divider()
    st.subheader("⬆️ Promote Learners to Next Year")
    next_year = st.selectbox("Copy to Year", YEARS, index=2, key="next_year")
    to_class = st.selectbox("To Class", ["P1","P2","P3","P4","P5","P6","P7"], key="to_class")
    if st.button("Copy Active Learners to Next Year"):
        to_copy = get_active_learners(selected_year, selected_class, selected_stream)
        for name in to_copy:
            save_to_sheet("Learners", {"Year": next_year, "Class": to_class, "Stream": selected_stream, "Learner_Name": name, "Status": "Active", "Graduation_Year": "", "Reason": ""})
        st.success(f"✅ Copied {len(to_copy)} learners to {to_class} {selected_stream} {next_year}.")

# ============ 7. ALUMNI ============
with tab_alumni:
    st.subheader("🎓 Alumni - Search Any Learner - P1 to P7 History")
    search_name = st.text_input("Type learner name to search", key="alumni_search")
    if search_name:
        for sheet_name, name_col, title in [("Quiz_Results","Learner_Name","📝 Quiz History"), ("Behaviour_Clinic","Learner_Name","💬 Behaviour / Clinic History"), ("Votes","Voter_Name","🗳️ Voting History"), ("Fees","Learner_Name","💰 Fees History"), ("Parent_Messages","Learner_Name","💬 Parent Messages History"), ("Mastery","Learner_Name","📚 Mastery History")]:
            df = read_sheet(sheet_name)
            if not df.empty and name_col in df.columns:
                filtered = df[df[name_col].astype(str).str.contains(search_name, case=False, na=False)]
                if not filtered.empty:
                    st.write(title)
                    st.dataframe(filtered, use_container_width=True)
