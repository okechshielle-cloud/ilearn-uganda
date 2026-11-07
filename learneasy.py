import streamlit as st
import gspread
from google.oauth2.service_account import Credentials

SHEET_ID = "14xwMoPTvxoOQfK_R5bqqnADSjaIby080WuGNkpO59qU"

def save_to_sheet(name, school, score, percentage, grade):
    try:
        if "gcp_service_account" in st.secrets:
            creds_dict = dict(st.secrets["gcp_service_account"])
        else:
            creds_dict = dict(st.secrets)
        creds = Credentials.from_service_account_info(
            creds_dict,
            scopes=["https://www.googleapis.com/auth/spreadsheets"]
        )
        client = gspread.authorize(creds)
        sheet = client.open_by_key(SHEET_ID).worksheet("Sheet1")
        sheet.append_row([name, school, score, f"{percentage:.0f}%", grade])
    except Exception as e:
        st.warning(f"Could not save to Sheet: {e}")

# --- 1. UNEB GRADING (for P.5 we use same D1 - F9) ---
def get_uneb_grade(mark):
    if mark >= 80:
        return "D1"
    elif mark >= 70:
        return "D2"
    elif mark >= 65:
        return "C3"
    elif mark >= 60:
        return "C4"
    elif mark >= 55:
        return "C5"
    elif mark >= 50:
        return "C6"
    elif mark >= 45:
        return "P7"
    elif mark >= 40:
        return "P8"
    else:
        return "F9"


# --- 2. P.5 QUESTIONS ---
QUESTIONS = [
    # MATHS - P.5
    {
        "subject": "Maths",
        "question": "What is the place value of 5 in 5,432?",
        "options": ["5", "50", "500", "Thousands / 5000"],
        "answer": "Thousands / 5000",
        "explanation": "In 5,432, the 5 is in the thousands place. So its value is 5 x 1000 = 5000."
    },
    {
        "subject": "Maths",
        "question": "What is 1/2 + 1/4?",
        "options": ["2/6", "3/4", "1/6", "2/4"],
        "answer": "3/4",
        "explanation": "Change 1/2 to 2/4. Then 2/4 + 1/4 = 3/4. You add the top numbers, the bottom stays the same."
    },
    {
        "subject": "Maths",
        "question": "A book costs Shs. 2,500. How much do 4 books cost?",
        "options": ["Shs. 5,000", "Shs. 7,500", "Shs. 10,000", "Shs. 8,000"],
        "answer": "Shs. 10,000",
        "explanation": "2,500 x 4 = 10,000. 25 x 4 = 100, so 2,500 x 4 = 10,000."
    },
    # ENGLISH - P.5
    {
        "subject": "English",
        "question": "Choose the correct sentence:",
        "options": ["The boys is playing", "The boys are playing", "The boys am playing", "The boys plays"],
        "answer": "The boys are playing",
        "explanation": "'Boys' is many (plural). We use 'are' for many people. We use 'is' for one person."
    },
    {
        "subject": "English",
        "question": "What is the opposite of 'early'?",
        "options": ["Fast", "Late", "Quick", "Soon"],
        "answer": "Late",
        "explanation": "Opposite means the reverse. If you come early, you are before time. If you come late, you are after time."
    },
    {
        "subject": "English",
        "question": "Which word is a verb? (a doing word)",
        "options": ["Happy", "Run", "Big", "Table"],
        "answer": "Run",
        "explanation": "A verb is a doing word. You can RUN. Happy, Big and Table are not actions."
    },
    # SCIENCE - P.5
    {
        "subject": "Science",
        "question": "Which part of the plant makes food?",
        "options": ["Root", "Stem", "Leaf", "Flower"],
        "answer": "Leaf",
        "explanation": "The leaf makes food for the plant using sunlight, water and air. This is called photosynthesis."
    },
    {
        "subject": "Science",
        "question": "Which of these is a living thing?",
        "options": ["Stone", "Chair", "Dog", "Water"],
        "answer": "Dog",
        "explanation": "A dog can breathe, eat, grow and move on its own. Stone, chair and water cannot do all these."
    },
    # SST - P.5
    {
        "subject": "SST",
        "question": "Which district is the capital city of Uganda found in?",
        "options": ["Wakiso", "Mukono", "Kampala", "Jinja"],
        "answer": "Kampala",
        "explanation": "Kampala is both a city and a district. The capital city Kampala is found in Kampala District."
    },
    {
        "subject": "SST",
        "question": "Who is the head of a family at home?",
        "options": ["Teacher", "Father / Mother", "LC1 Chairman", "President"],
        "answer": "Father / Mother",
        "explanation": "At home, the parents (father and mother) are the heads of the family. The President is head of the country."
    },
]

# --- 3. THE APP ---
st.set_page_config(page_title="P.5 Learning Platform", page_icon="📚")
st.title("📚 P.5 Learning Platform")
st.write("Answer all 10 questions. Then click Submit to see your marks, grade and explanations.")

name = st.text_input("Enter your name:")
school = st.text_input("Enter your school (optional):")

answers = {}
for i, q in enumerate(QUESTIONS):
    st.subheader(f"Q{i + 1}. [{q['subject']}] {q['question']}")
    answers[i] = st.radio("Choose your answer:", q["options"], key=f"p5_q{i}", index=None)

st.divider()

if st.button("Submit Quiz - See My Results", type="primary"):
    if not name:
        st.warning("Please enter your name first!")
    elif None in answers.values():
        st.warning("Please answer ALL 10 questions before submitting.")
    else:
        score = 0
        for i, q in enumerate(QUESTIONS):
            if answers[i] == q["answer"]:
                score += 1

        percentage = score / len(QUESTIONS) * 100
        grade = get_uneb_grade(percentage)
        save_to_sheet(name, school, score, percentage, grade)

        st.success(f"### 🎉 Well done, {name}!")
        st.write(f"**Score:** {score} out of 10")
        st.write(f"**Percentage:** {percentage:.0f}%")
        st.write(f"**Grade:** {grade}")

        if grade in ["D1", "D2"]:
            st.balloons()
            st.write("Comment: Excellent! Keep it up!")
        elif grade in ["C3", "C4", "C5", "C6"]:
            st.write("Comment: Good! Read the explanations below to get D1 next time.")
        else:
            st.write("Comment: Don't give up! Read all explanations below carefully.")

        st.divider()
        st.header("📖 Review - Learn from your answers")

        for i, q in enumerate(QUESTIONS):
            user_ans = answers[i]
            is_correct = user_ans == q["answer"]

            if is_correct:
                st.success(f"Q{i + 1}. {q['question']} ✅ Correct")
            else:
                st.error(f"Q{i + 1}. {q['question']} ❌ Wrong")

            st.write(f"**Your answer:** {user_ans}")
            st.write(f"**Correct answer:** {q['answer']}")
            st.info(f"**Explanation:** {q['explanation']}")
            st.write("---")
