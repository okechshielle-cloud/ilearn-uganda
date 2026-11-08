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
    ("Q1. [Maths] What is the place value of 5 in 5,432?", ["5000", "500", "50", "5"], "5000", "5 is in the thousands place. 5 thousands = 5000. The digits are: 5 thousands, 4 hundreds, 3 tens, 2 ones."),
    ("Q2. [Maths] What is 1/2 + 1/4?", ["3/4", "2/6", "1/4", "2/4"], "3/4", "Change to same denominator: 1/2 = 2/4. Then 2/4 + 1/4 = 3/4."),
    ("Q3. [English] Choose the correct sentence.", ["She goes to school every day.", "She go to school every day.", "she goes to school every day", "She goes to school every day"], "She goes to school every day.", "The correct sentence starts with a capital letter, ends with a full stop, and the verb agrees with the subject. 'She goes' is correct, not 'She go'."),
    ("Q4. [Science] Which gas do plants use to make food?", ["Carbon dioxide", "Oxygen", "Nitrogen", "Hydrogen"], "Carbon dioxide", "Plants use carbon dioxide from the air + water + sunlight to make food in photosynthesis. They give out oxygen."),
    ("Q5. [Maths] What is 12 x 8?", ["96", "86", "108", "84"], "96", "12 x 8 = 96. Think: 10 x 8 = 80, 2 x 8 = 16, 80 + 16 = 96."),
    ("Q6. [SST] What is the capital city of Uganda?", ["Kampala", "Entebbe", "Jinja", "Mbarara"], "Kampala", "Kampala is the capital city of Uganda. It is where the government and Parliament sit. Entebbe has the airport, Jinja is the source of the Nile."),
    ("Q7. [English] What is the opposite of 'happy'?", ["Sad", "Glad", "Joyful", "Cheerful"], "Sad", "The opposite of happy is sad. Glad, joyful and cheerful all mean almost the same as happy."),
    ("Q8. [Science] Which animal is a mammal?", ["Cow", "Chicken", "Fish", "Frog"], "Cow", "A mammal gives birth to live young, breastfeeds its babies with milk, has hair/fur, and breathes with lungs. Birds, fish, frogs and insects are not mammals."),
    ("Q9. [Maths] What is 100 - 37?", ["63", "67", "73", "37"], "63", "100 - 37 = 63. Subtract 30 to get 70, then subtract 7 more to get 63."),
    ("Q10. [English] Fill in: ___ apple is red.", ["An", "The", "A", "Some"], "The", "We use 'The' because we are talking about a specific apple that we both know. 'An' is for any one apple, not a specific one."),
    ("Q11. [Maths] Simplify 2m - 8m + 13m", ["7m", "23m", "3m", "19m"], "7m", "2m - 8m = -6m. Then -6m + 13m = 7m. We add and subtract like terms."),
    ("Q12. [SST] Which country does Uganda border in the East?", ["DR Congo", "Kenya", "Tanzania", "South Sudan"], "Kenya", "Kenya is to the east of Uganda where the sun rises. DR Congo is to the west where the sun sets."),
    ("Q13. [Science] Why is heat unable to travel in a vacuum?", ["There are no particles to carry it", "Vacuum is too cold", "Heat needs light", "Vacuum blocks heat"], "There are no particles to carry it", "Heat by conduction and convection needs particles to pass it along. A vacuum has no particles, so heat cannot travel that way."),
    ("Q14. [Maths] Which of these is the net of a cylinder?", ["2 circles and a rectangle", "1 circle and a triangle", "3 squares", "2 triangles and a rectangle"], "2 circles and a rectangle", "A cylinder has 2 circular ends (top and bottom) and 1 curved side that opens into a rectangle."),
    ("Q15. [SST] Name the major physical feature that is known for the formation of relief rainfall in Eastern Uganda.", ["Mt Elgon", "Mt Rwenzori", "Lake Victoria", "Mt Mufumbiro"], "Mt Elgon", "Mt Elgon in Eastern Uganda forces moist air to rise, cool and form relief rainfall on its slopes."),
    ("Q16. [English] Sarah ........ meat to chicken. (Prefers, likes)", ["Prefers", "Likes", "Prefer", "Like"], "Prefers", "We use 'Prefers' because Sarah likes meat MORE than chicken. 'Prefers... to...' shows a choice between two things. Sarah is one person, so we add 's' - She prefers."),
    ("Q17. [Maths] Molly is twice as old as Jolly. If the sum of their ages is 30, how old is Molly?", ["20", "10", "15", "30"], "20", "Let Jolly = 1 part, Molly = 2 parts. Total = 3 parts = 30. 1 part = 30 / 3 = 10. So Molly = 2 x 10 = 20 years."),
    ("Q18. [SST] What is a landlocked country?", ["A country with no sea coast", "A country with many lakes", "A country with a big sea port", "A country surrounded by water"], "A country with no sea coast", "A landlocked country has no coastline on the sea or ocean. It is surrounded by other countries on all sides. Uganda is landlocked."),
    ("Q19. [CRE] 'I AM WHO I AM.' To whom was the statement made?", ["Moses", "Abraham", "Jacob", "Aaron"], "Moses", "God said 'I AM WHO I AM' to Moses at the burning bush in Exodus 3, when Moses asked for God's name before going to Pharaoh in Egypt."),
    ("Q20. [English] One of the following words means elephant in Kiswahili.", ["Tembo", "Simba", "Nyani", "Paka"], "Tembo", "In Kiswahili, elephant = Tembo. Simba = lion, Nyani = monkey, Paka = cat."),
]
    if st.button("🔄 New Pupil - Start Fresh Quiz"): [st.session_state.pop(k) for k in list(st.session_state.keys()) if k.startswith("q")]; st.rerun()
    answers = []
    for i, t in enumerate(questions):
        q, options, correct, exp = (t + ("",) * 4)[:4]
        ans = st.radio(f"{q}", options, key=f"q{i}", index=None)
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
            st.subheader("Review - See correct answers and explanations")
            for i, t in enumerate(questions):
                q, options, correct, exp = (t + ("",) * 4)[:4]
                ans = answers[i]
                if ans == correct:
                    st.success(f"Q{i+1}: {q} - Correct!")
                else:
                   st.error(f"Q{i+1}: {q} - Wrong. Your answer: {ans}. Correct answer: {correct}")
                if exp:
                    st.info(f"Explanation: {exp}")

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
                    for i, (idx, row) in enumerate(top3.iterrows()): st.success(f"{medals[i]} {row['Name']} - Score: {row['Score']} ({row['Percentage']}%)")
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
