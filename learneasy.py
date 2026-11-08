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
    ("Q1. [Maths] What is the place value of 5 in 5,432?", ["5", "50", "500", "Thousands / 5000"], "Thousands / 5000"),
    ("Q2. [Maths] What is 1/2 + 1/4?", ["2/6", "3/4", "1/6", "2/4"], "3/4"),
    ("Q3. [English] Choose the correct sentence.", ["She go to school.", "She goes to school.", "She going to school.", "She gone to school."], "She goes to school."),
    ("Q4. [Science] Which gas do plants use to make food?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], "Carbon dioxide"),
    ("Q5. [Maths] What is 12 x 8?", ["86", "96", "108", "88"], "96"),
    ("Q6. [SST] What is the capital city of Uganda?", ["Jinja", "Entebbe", "Kampala", "Mbarara"], "Kampala"),
    ("Q7. [English] What is the opposite of 'happy'?", ["Glad", "Sad", "Joyful", "Smiling"], "Sad"),
    ("Q8. [Science] Which animal is a mammal?", ["Chicken", "Lizard", "Cow", "Fish"], "Cow"),
    ("Q9. [Maths] What is 100 - 37?", ["63", "73", "67", "53"], "63"),
    ("Q10. [English] Fill in: ___ apple is red.", ["A", "An", "The", "Some"], "The"),
    ("Q11. [Maths] Simplify 2m - 8m + 13m", ["7m", "5m", "23m", "3m"], "7m"),
    ("Q12. [SST] Which country does Uganda border in the East?", ["Kenya", "Tanzania", "South Sudan", "DR Congo"], "Kenya"),
    ("Q13. [Science] Why is heat unable to travel in a vacuum?", ["There are no particles to carry it", "Vacuum is too hot", "Vacuum is too cold", "Heat hates vacuum"], "There are no particles to carry it"),
    ("Q14. [Maths] Which of these is the net of a cylinder?", ["Two circles and a rectangle", "One circle and a triangle", "Three squares", "Two triangles and a rectangle"], "Two circles and a rectangle"),
    ("Q15. [SST] Name the major physical feature that is known for the formation of relief rainfall in Eastern Uganda.", ["Mt. Elgon", "Lake Victoria", "Mt. Rwenzori", "River Nile"], "Mt. Elgon"),
    ("Q16. [English] Sarah ........ meat to chicken. (Prefers, likes)", ["Prefers", "Likes", "Prefer", "Like"], "Prefers"),
    ("Q17. [Maths] Molly is twice as old as Jolly. If the sum of their ages is 30, how old is Molly?", ["10 years", "15 years", "20 years", "30 years"], "20 years"),
    ("Q18. [SST] What is a landlocked country?", ["A country with no sea coast", "A country with many lakes", "A country with a big airport", "A country near the sea"], "A country with no sea coast"),
    ("Q19. [CRE] 'I AM WHO I AM.' To whom was the statement made?", ["Moses", "Abraham", "Jacob", "David"], "Moses"),
    ("Q20. [English] One of the following words means elephant in Kiswahili.", ["Tembo", "Tendo", "Rembo", "Pembo"], "Tembo"),
]
    if st.button("🔄 New Pupil - Start Fresh Quiz"):
    st.session_state.clear()
    st.rerun()
    answers = []
    for i, (q, options, correct) in enumerate(questions):
        ans = st.radio(f"{q}", options, key=f"q{i}")
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
                    top3 = df.sort_values(by="Percentage", ascending=False).head(3)
                    st.subheader("🏆 Top 3 Performers")
                    medals = ["🥇", "🥈", "🥉"]
                    for i, (idx, row) in enumerate(top3.iterrows()):
                        st.success(f"{medals[i]} {row['Name']} — {row['Score']} / 10 ({row['Percentage']:.0f}%)")
                    st.balloons()
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
