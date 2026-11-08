import streamlit as st
import gspread
import pandas as pd
import io
from google.oauth2.service_account import Credentials

SHEET_ID = "1G2PdfSMPXXlZCnumPYpAPkyIU84JrJ9wq97SHI0FoFg"

def get_creds():
    if "gcp_service_account" in st.secrets:
        creds_dict = dict(st.secrets["gcp_service_account"])
    else:
        creds_dict = dict(st.secrets)
    # --- FIX BROKEN PRIVATE KEY ---
    pk = creds_dict["private_key"]
    pk = pk.replace("\\n", "\n").replace("\r", "")
    body = pk.replace("-----BEGIN PRIVATE KEY-----", "").replace("-----END PRIVATE KEY-----", "").replace("\n", "").replace(" ", "")
    body = "".join([c for c in body if c in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="])
    body += "=" * (-len(body) % 4)
    body = "\n".join([body[i:i+64] for i in range(0, len(body), 64)])
    creds_dict["private_key"] = "-----BEGIN PRIVATE KEY-----\n" + body + "\n-----END PRIVATE KEY-----\n"
    return Credentials.from_service_account_info(creds_dict, scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"])

def get_worksheet():
    client = gspread.authorize(get_creds())
    return client.open("learneasy-scores2").sheet1

def save_to_sheet(name, school, score, percentage, grade):
    try:
        ws = get_worksheet()
        ws.append_row([name, school, score, percentage, grade])
        return True
    except Exception as e:
        st.error(f"Could not save: {e}")
        return False

# --- MENU ---
st.sidebar.title("Menu")
page = st.sidebar.radio("Go to:", ["Take Quiz", "Teacher Dashboard"])

# ================= TAKE QUIZ =================
if page == "Take Quiz":
    st.title("LearnEasy Quiz")
    st.write("Welcome! Answer all questions.")

    name = st.text_input("Your Name")
    school = st.text_input("Your School")

    questions = [
        ("Who is the head of a family?", ["Father / Mother", "Teacher", "LC1 Chairman", "President"], "Father / Mother"),
        ("Who teaches learners at school?", ["Teacher", "Doctor", "Farmer", "Driver"], "Teacher"),
        ("Who is the chairman of a village?", ["LC1 Chairman", "President", "Teacher", "Doctor"], "LC1 Chairman"),
        ("Who is the head of Uganda?", ["President", "Teacher", "LC1 Chairman", "Father"], "President"),
        ("What is 2 + 3?", ["5", "4", "6", "3"], "5"),
        ("What is 10 - 4?", ["6", "5", "7", "4"], "6"),
        ("Which is the capital of Uganda?", ["Kampala", "Jinja", "Mbarara", "Gulu"], "Kampala"),
        ("How many days are in a week?", ["7", "5", "6", "10"], "7"),
        ("Which colour is the Ugandan flag NOT?", ["Blue", "Black", "Yellow", "Red"], "Blue"),
        ("What do plants need to grow?", ["Sunlight and water", "Soap", "Plastic", "Stone"], "Sunlight and water"),
    ]

    answers = []
    for i, (q, options, correct) in enumerate(questions):
        ans = st.radio(f"Q{i+1}. {q}", options, key=f"q{i}")
        answers.append(ans)

    if st.button("Submit Quiz - See My Results"):
        if not name or not school:
            st.warning("Please enter your Name and School first.")
        else:
            score = sum(1 for (q, opts, corr), ans in zip(questions, answers) if ans == corr)
            percentage = (score / len(questions)) * 100
            if percentage >= 90:
                grade, comment = "D1", "Excellent! Keep it up!"
            elif percentage >= 75:
                grade, comment = "D2", "Very good!"
            elif percentage >= 60:
                grade, comment = "C3", "Good, keep working!"
            elif percentage >= 50:
                grade, comment = "C4", "Fair, you can improve!"
            else:
                grade, comment = "F9", "Don't give up, try again!"

            st.success(f"🎉 Well done, {name}!")
            st.write(f"Score: {score} out of {len(questions)}")
            st.write(f"Percentage: {percentage:.0f}%")
            st.write(f"Grade: {grade}")
            st.write(f"Comment: {comment}")

            if save_to_sheet(name, school, score, percentage, grade):
                st.info("✅ Your result has been saved!")

# ================= TEACHER DASHBOARD =================
if page == "Teacher Dashboard":
    st.title("📊 Teacher Dashboard - LearnEasy")
    password = st.text_input("Enter Teacher Password", type="password")
    if password == "teacher123":
        st.success("Welcome Teacher!")
        try:
                ws = get_worksheet()
                data = ws.get_all_records()
                df = pd.DataFrame(data)
                df.columns = [str(c).strip().capitalize() for c in df.columns]
                df["Score"] = pd.to_numeric(df["Score"], errors="coerce")
                df["Percentage"] = pd.to_numeric(df["Percentage"].astype(str).str.replace("%", "").str.strip(), errors="coerce")
                if len(df) == 0:
                    st.info("No results yet.")
                else:
                    col1, col2 = st.columns(2)
                    col1.metric("Total Learners", len(df))
                    col2.metric("Average Score", f"{df['Percentage'].mean():.1f}%")
                    st.write("Search by name:")
                    search = st.text_input("Type name...")
                    if search:
                        df = df[df['Name'].astype(str).str.contains(search, case=False)]
                    st.dataframe(df)
                    st.download_button("📥 Download Results", df.to_csv(index=False).encode("utf-8"), "results.csv", "text/csv")
        except Exception as e:
                st.error(f"Could not load results: {e}")        
        elif password != "":
                st.error("Wrong password")
