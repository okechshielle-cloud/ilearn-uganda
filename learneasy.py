import streamlit as st
import pandas as pd
import os
import requests
import json

st.set_page_config(page_title="iLearn-Uganda", layout="centered")

TEACHER_PASSWORD = st.secrets.get("TEACHER_PASSWORD", "iLearnUganda123")
CSV_FILE = "results.csv"
SHEET_URL = st.secrets.get("SHEET_URL", "")

# Official NCDC Curriculum Dataset structured by cycles and subjects/themes
NCDC_CURRICULUM = {
    "Lower Primary (Cycle 1: Thematic Approach P1-P3)": {
        "P1": {
            "Term 1 (Themes: Our School / Our Home)": "Develop basic listening, speaking, reading, and writing literacy in a familiar local language; acquire early numeracy (counting 1-10) and personal hygiene values.",
            "Term 2 (Themes: Our Community / Human Body)": "Recognize immediate community roles, practice health and sanitation habits, and extend numeracy (addition/subtraction up to 20).",
            "Term 3 (Themes: Environment & Animals)": "Identify plants, domestic and wild animals in the local environment; build early reading sentence structures and safety awareness."
        },
        "P2": {
            "Term 1 (Themes: Food & Nutrition)": "Consolidate foundational literacy fluency, classify local food sources, and perform addition/subtraction up to 50 with regrouping aids.",
            "Term 2 (Themes: Transport, Communication & Weather)": "Identify major local transport/communication systems and describe weather changes affecting daily human clothing and activities.",
            "Term 3 (Themes: Peace, Security & Changes)": "Demonstrate cooperative living, conflict resolution, and practical measurements using non-standard units."
        },
        "P3": {
            "Term 1 (Themes: Our Sub-county / Division)": "Map out physical features and significant landmarks within the sub-county; read graded paragraphs and perform multiplication/division foundations.",
            "Term 2 (Themes: Energy, Water & Sanitation)": "Identify sources/safe uses of energy and water; apply basic scientific inquiry properties to air, soil, and water.",
            "Term 3 (Themes: Transition Foundations)": "Consolidate all literacy and numeracy required for transition into upper-primary English-medium instruction; express creative arts and physical coordination."
        }
    },
    "Upper Primary (Cycle 2 & 3: Subject-Based P4-P7)": {
        "P4": {
            "English": "Transition fully to English as the medium of instruction; master nouns, pronouns, guided compositions, and letter-writing.",
            "Mathematics": "Master place values up to ten thousands, operations with fractions, decimals, and metric units of measurement.",
            "Integrated Science": "Investigate plant anatomy, crop growing, the human digestive system, teeth structures, and weather measurement instruments.",
            "Social Studies": "Use map-reading skills (compass directions, keys, scale) to study the local district history, physical geography, and governance.",
            "Religious Education": "Study sacred scriptures (Bible/Quran), foundational covenants, and moral decision-making for community service.",
            "Kiswahili": "Master phonetic spelling, noun classes (M-WA, KI-VI), basic present tense (na-), and short graded reading passages.",
            "Creative Arts & PE": "Learn structured rules and techniques for major sports, visual arts (color mixing, shapes), and traditional dances."
        },
        "P5": {
            "English": "Apply complex tenses, conjunctions, relative clauses, poem analysis, and structured debate/speech delivery.",
            "Mathematics": "Perform operations with integers, decimals, percentages, area, volume, and basic algebraic expressions.",
            "Integrated Science": "Explore states of matter, heat transfer, human circulatory/respiratory systems, and primary health care.",
            "Social Studies": "Examine the physical geography, climate, vegetation zones, pre-colonial history, and governance of Uganda.",
            "Religious Education": "Analyze the life and teachings of Jesus Christ (CRE) or Prophet Muhammad (IRE) regarding justice, compassion, and discipline.",
            "Kiswahili": "Apply past (li-), present (na-), and future (ta-) tenses; expand vocabulary on markets, travel, and East African ties.",
            "Creative Arts & PE": "Develop intermediate sports tactics, sportsmanship, functional craft designs, and traditional musical arrangements."
        },
        "P6": {
            "English": "Master active/passive voice, direct/indirect speech, conditional sentences, persuasive essays, and formal report writing.",
            "Mathematics": "Solve problems involving proportions, speed, distance, time, simple interest, and advanced data interpretation (pie charts).",
            "Integrated Science": "Examine electricity, magnetism, simple machines, friction, mammalian reproduction, adolescence, and immunity.",
            "Social Studies": "Examine the physical geography, resources, colonial administration, and struggles for independence in East Africa.",
            "Religious Education": "Study faith in action, leadership, family values, work ethics, and reconciliation from a religious perspective.",
            "Kiswahili": "Master additional noun classes, adjectives, prepositions, negation forms, and summaries of short stories or dialogues.",
            "Creative Arts & PE": "Refine athletic skills, first-aid safety practices, advanced sculpture projects, and civic-themed drama pieces."
        },
        "P7": {
            "English": "Consolidate all primary grammar, vocabulary, editing, and rapid comprehension under timed conditions for PLE readiness.",
            "Mathematics": "Consolidate arithmetic, algebra, geometry, and set theory to solve complex multi-concept application problems.",
            "Integrated Science": "Master human anatomy (excretory, nervous systems), agricultural applications, population health, and sustainable resource management.",
            "Social Studies": "Analyze Pan-Africanism, decolonization, governance challenges, and international organizations (AU, UN) across Africa.",
            "Religious Education": "Synthesize scriptural knowledge, moral theology, ethical responses to societal challenges, and human dignity for PLE.",
            "Kiswahili": "Demonstrate fluent oral communication, structured essay writing, and functional proficiency for regional integration.",
            "Creative Arts & PE": "Demonstrate leadership, fitness management, entrepreneurial craft production, and well-rounded cultural competencies."
        }
    }
}

CLASS_QUESTIONS = {
    "P1": [
        ("Q1. [Maths] What is 2 + 3?", ["4", "5", "6", "3"], "5", "2 plus 3 equals 5."),
        ("Q2. [English] What is the opposite of day?", ["Sun", "Night", "Morning", "Dark"], "Night", "The opposite of day is night."),
        ("Q3. [Science] Which body part do we use for seeing?", ["Nose", "Eyes", "Ears", "Mouth"], "Eyes", "We use eyes for seeing."),
        ("Q4. [SST] Who heads a family at home?", ["Teacher", "Father/Mother", "Doctor", "Driver"], "Father/Mother", "Parents or guardians head the family."),
    ],
    "P2": [
        ("Q1. [Maths] What is 15 - 7?", ["7", "8", "9", "6"], "8", "15 minus 7 equals 8."),
        ("Q2. [English] Choose the correct plural of 'cat':", ["Cats", "Cates", "Cat", "Catie"], "Cats", "The plural of cat is cats."),
        ("Q3. [Science] Which food group gives us energy?", ["Proteins", "Carbohydrates", "Vitamins", "Water"], "Carbohydrates", "Carbohydrates give the body energy."),
        ("Q4. [SST] Name the place where we buy things in our community.", ["School", "Market", "Hospital", "Well"], "Market", "We buy goods from the market."),
    ],
    "P3": [
        ("Q1. [Maths] What is 6 multiplied by 4?", ["20", "24", "18", "28"], "24", "6 x 4 = 24."),
        ("Q2. [Science] Which soil type holds the most water?", ["Sandy soil", "Loam soil", "Clay soil", "Topsoil"], "Clay soil", "Clay soil has fine particles that hold water best."),
        ("Q3. [SST] What is the title of the political head of a sub-county?", ["LC III Chairperson", "LC I Chairperson", "RDC", "Mayor"], "LC III Chairperson", "An LC III Chairperson heads a sub-county."),
        ("Q4. [English] Fill in the gap: She ........ to school every day.", ["walk", "walks", "walking", "walked"], "walks", "Third-person singular uses 'walks'."),
    ],
    "P4": [
        ("Q1. [Maths] Express 1/2 as a percentage.", ["25%", "50%", "75%", "100%"], "50%", "1/2 x 100% = 50%."),
        ("Q2. [Science] Which part of a plant manufactures food?", ["Root", "Stem", "Leaf", "Flower"], "Leaf", "Leaves perform photosynthesis to make food."),
        ("Q3. [SST] What instrument is used to show directions on a map?", ["Windsock", "Compass", "Thermometer", "Barometer"], "Compass", "A compass shows cardinal directions."),
        ("Q4. [English] Give the plural of 'baby':", ["Babys", "Babies", "Babyies", "Babs"], "Babies", "Words ending in 'y' preceded by a consonant change to 'ies'."),
    ],
    "P5": [
        ("Q1. [Maths] Simplify: -5 - (-6)", ["-11", "1", "11", "-1"], "1", "-5 + 6 = 1. Minus a minus becomes plus."),
        ("Q2. [Science] What gas is used by plants during photosynthesis?", ["Oxygen", "Carbon dioxide", "Nitrogen", "Hydrogen"], "Carbon dioxide", "Plants absorb carbon dioxide from the air."),
        ("Q3. [SST] Which is the largest country in East Africa by land area?", ["Uganda", "Kenya", "Tanzania", "Rwanda"], "Tanzania", "Tanzania is the largest East African country."),
        ("Q4. [CRE] Who was sold by his brothers into Egypt?", ["Joseph", "Moses", "David", "Abraham"], "Joseph", "Joseph was sold into slavery by his brothers."),
    ],
    "P6": [
        ("Q1. [Maths] Find the area of a rectangle of length 10cm and width 5cm.", ["15cm²", "50cm²", "30cm²", "25cm²"], "50cm²", "Area = Length x Width = 10 x 5 = 50cm²."),
        ("Q2. [Science] Which blood cells fight against diseases in the human body?", ["Red blood cells", "White blood cells", "Platelets", "Plasma"], "White blood cells", "White blood cells defend the body against infections."),
        ("Q3. [SST] When did Uganda gain her independence?", ["9th October 1962", "26th January 1986", "9th October 1952", "1st January 1960"], "9th October 1962", "Uganda became independent on October 9, 1962."),
        ("Q4. [Kiswahili] What does the word 'Rafiki' mean in English?", ["Teacher", "Friend", "Brother", "Enemy"], "Friend", "'Rafiki' means friend in Kiswahili."),
    ],
    "P7": [
        ("Q1. [Maths] Solve for x: 2x + 4 = 12", ["x = 4", "x = 6", "x = 8", "x = 2"], "x = 4", "2x = 12 - 4 => 2x = 8 => x = 4."),
        ("Q2. [Science] Why is heat unable to travel in a vacuum?", ["There are no particles to carry it", "Vacuum is too hot", "Vacuum is too cold", "Vacuum has many particles"], "There are no particles to carry it", "Heat requires particles to transfer via conduction or convection; a vacuum has none."),
        ("Q3. [SST] Name the organization that replaced the East African Community in 1977 before it was revived later.", ["COMESA", "None / It collapsed", "ECOWAS", "AU"], "None / It collapsed", "The initial EAC collapsed in 1977."),
        ("Q4. [English] Choose the correct indirect speech: John said, 'I am going home.'", ["John said that he is going home", "John said that he was going home", "John said he is went home", "John said that I was going home"], "John said that he was going home", "Present tense changes to past tense in indirect speech."),
    ]
}

def load_results():
    if SHEET_URL:
        try:
            r = requests.get(SHEET_URL, timeout=10)
            data = r.json()
            clean = []
            for row in data:
                if str(row.get("Name", "")).strip() != "":
                    clean.append({
                        "Name": row.get("Name", ""),
                        "Class": row.get("Class", "P1"),
                        "School": row.get("School", ""),
                        "Score": row.get("Score", ""),
                        "Percentage": float(row.get("Percentage", 0)) if str(row.get("Percentage", "")).strip() != "" else 0,
                        "Grade": row.get("Grade", ""),
                        "Comment": row.get("Comment", ""),
                    })
            return clean
        except Exception as e:
            st.warning(f"Could not load from Google Sheets: {e}")
    if os.path.exists(CSV_FILE):
        try:
            return pd.read_csv(CSV_FILE).to_dict("records")
        except:
            return []
    return []

def save_one_result(row):
    saved = False
    if SHEET_URL:
        try:
            r = requests.post(SHEET_URL, data=json.dumps(row), headers={"Content-Type": "application/json"}, timeout=10)
            if r.status_code == 200:
                saved = True
        except Exception as e:
            st.warning(f"Google Sheets save failed: {e}")
    try:
        existing = []
        if os.path.exists(CSV_FILE):
            existing = pd.read_csv(CSV_FILE).to_dict("records")
        existing.append(row)
        pd.DataFrame(existing).to_csv(CSV_FILE, index=False)
    except:
        pass
    return saved

if "results" not in st.session_state:
    st.session_state.results = load_results()
if "submitted" not in st.session_state:
    st.session_state.submitted = False
if "last_submit_key" not in st.session_state:
    st.session_state.last_submit_key = ""
if "dashboard_unlocked" not in st.session_state:
    st.session_state.dashboard_unlocked = False

st.sidebar.title("iLearn-Uganda")
st.sidebar.caption("Integrated Learning Environment")
page = st.sidebar.selectbox("Go to", ["Take Quiz", "NCDC Curriculum Explorer", "Teacher Dashboard"])

if page == "Take Quiz":
    st.title("iLearn-Uganda Quiz")
    st.caption("Integrated Learning Environment — Primary Assessment")
    st.write("Select your class, answer the questions for your level, then click Submit.")
    
    if st.button("Next Child - Clear for New Learner"):
        saved = st.session_state.get("results", [])
        st.session_state.clear()
        st.session_state.results = saved
        st.session_state.submitted = False
        st.session_state.last_submit_key = ""
        st.session_state.dashboard_unlocked = False
        st.rerun()
        
    name = st.text_input("Your Name", key="name")
    school = st.text_input("Your School", key="school")
    learner_class = st.selectbox("Your Class", [f"P{i}" for i in range(1, 8)], key="learner_class")
    
    questions = CLASS_QUESTIONS.get(learner_class, [])
    
    st.markdown(f"### Assessment for {learner_class}")
    answers = []
    for i, (q, options, correct, explain) in enumerate(questions):
        ans = st.radio(q, options, key=f"q{i}_{learner_class}", index=None)
        answers.append(ans)
        
    if st.session_state.submitted:
        st.info("This child has already submitted. Click 'Next Child' above for the next learner.")
        
    if st.button("Submit Quiz - See My Results"):
        if st.session_state.submitted:
            st.warning("Already submitted. Click 'Next Child' for the next learner.")
        elif not name or not school:
            st.warning("Please enter Your Name and Your School first.")
        elif any(a is None for a in answers):
            st.warning("Please answer all questions before submitting.")
        else:
            submit_key = f"{name}|{school}|{learner_class}|{answers}"
            if submit_key == st.session_state.last_submit_key:
                st.warning("Already submitted. Click 'Next Child' for the next learner.")
            else:
                score = 0
                for i, (q, options, correct, explain) in enumerate(questions):
                    if str(answers[i]) == str(correct):
                        score = score + 1
                total = len(questions)
                pct = round(score * 100 / total, 1) if total > 0 else 0
                
                if pct >= 80:
                    grade = "A"
                    comment = "Excellent! Keep it up."
                elif pct >= 60:
                    grade = "B"
                    comment = "Very good!"
                elif pct >= 40:
                    grade = "C"
                    comment = "Good, keep practising."
                else:
                    grade = "D"
                    comment = "Keep trying, you can do better."
                    
                new_row = {
                    "Name": name, 
                    "Class": learner_class, 
                    "School": school, 
                    "Score": f"{score}/{total}", 
                    "Percentage": pct, 
                    "Grade": grade, 
                    "Comment": comment
                }
                st.session_state.results.append(new_row)
                ok = save_one_result(new_row)
                if ok:
                    st.success("Saved to Google Sheets ✅ - Will survive reboot")
                else:
                    st.warning("Saved locally only - Check SHEET_URL in Secrets")
                    
                st.session_state.last_submit_key = submit_key
                st.session_state.submitted = True
                st.success(f"Well done {name}! You scored {score}/{total} = {pct}% Grade {grade}")
                st.write(comment)
                
                st.subheader("Review Your Answers")
                for i, (q, options, correct, explain) in enumerate(questions):
                    st.write(f"Q{i+1}: {q}")
                    st.write(f"Your answer: {answers[i]}")
                    st.write(f"Correct answer: {correct}")
                    if str(answers[i]) == str(correct):
                        st.write("Correct! Well done.")
                    else:
                        st.write("Not correct.")
                    st.write(f"Explanation: {explain}")
                    st.write("---")

elif page == "NCDC Curriculum Explorer":
    st.title("📚 iLearn-Uganda Curriculum Explorer")
    st.caption("Integrated Learning Environment — Official NCDC Framework")
    st.write("Explore learning outcomes mirroring NCDC frameworks: Lower Primary Thematic Approach (P1–P3) and Upper Primary Subject-Based Structure (P4–P7).")
    
    cycle_choice = st.selectbox("Select Cycle", list(NCDC_CURRICULUM.keys()))
    
    if "Thematic" in cycle_choice:
        selected_class = st.selectbox("Select Class", ["P1", "P2", "P3"])
        st.markdown("---")
        st.subheader(f"Thematic Curriculum Outcomes for {selected_class}")
        terms_data = NCDC_CURRICULUM[cycle_choice].get(selected_class, {})
        for term, desc in terms_data.items():
            st.markdown(f"**{term}:**")
            st.info(desc)
    else:
        selected_class = st.selectbox("Select Class", ["P4", "P5", "P6", "P7"])
        st.markdown("---")
        st.subheader(f"Subject-Based Curriculum Outcomes for {selected_class} (Set One & Set Two)")
        subjects_data = NCDC_CURRICULUM[cycle_choice].get(selected_class, {})
        for subj, desc in subjects_data.items():
            st.markdown(f"**{subj}:**")
            st.info(desc)

elif page == "Teacher Dashboard":
    st.title("iLearn-Uganda Teacher Dashboard - Locked")
    if not st.session_state.dashboard_unlocked:
        st.write("This page is for teachers only. Enter your password.")
        pwd = st.text_input("Teacher Password", type="password", key="teacher_pwd")
        if st.button("Unlock Dashboard"):
            if pwd == TEACHER_PASSWORD:
                st.session_state.dashboard_unlocked = True
                st.rerun()
            else:
                st.error("Wrong password. Try again.")
        st.stop()
        
    st.title("iLearn-Uganda Teacher Dashboard")
    st.caption("Integrated Learning Environment — Analytics & Leaderboard")
    if SHEET_URL:
        st.success("Google Sheets Link is set ✅")
    else:
        st.error("No SHEET_URL in Secrets")
        
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        if st.button("Lock Dashboard"):
            st.session_state.dashboard_unlocked = False
            st.rerun()
    with col_btn2:
        if st.button("Refresh from Google Sheets"):
            st.session_state.results = load_results()
            st.rerun()
            
    results = st.session_state.get("results", [])
    st.write(f"Total attempts: {len(results)}")
    
    if len(results) == 0:
        st.info("No results yet. Let a child take the quiz first.")
    else:
        df = pd.DataFrame(results)
        
        if "Class" in df.columns:
            all_classes = ["All"] + sorted(df["Class"].unique().tolist())
            selected_filter_class = st.selectbox("Filter Leaderboard by Class", all_classes)
            if selected_filter_class != "All":
                df = df[df["Class"] == selected_filter_class]

        df = df.sort_values(by="Percentage", ascending=False).reset_index(drop=True)
        medals = []
        for idx in range(len(df)):
            if idx == 0:
                medals.append("🥇 Gold")
            elif idx == 1:
                medals.append("🥈 Silver")
            elif idx == 2:
                medals.append("🥉 Bronze")
            else:
                medals.append("")
        df.insert(0, "Medal", medals)
        df.insert(0, "Rank", range(1, len(df) + 1))
        
        st.subheader("🏆 Top 3 Medal Winners")
        for idx in range(min(3, len(df))):
            row = df.iloc[idx]
            if idx == 0:
                st.success(f"🥇 GOLD - {row['Name']} ({row.get('Class', 'N/A')}) - {row['School']} - {row['Score']} = {row['Percentage']}%")
            elif idx == 1:
                st.info(f"🥈 SILVER - {row['Name']} ({row.get('Class', 'N/A')}) - {row['School']} - {row['Score']} = {row['Percentage']}%")
            elif idx == 2:
                st.warning(f"🥉 BRONZE - {row['Name']} ({row.get('Class', 'N/A')}) - {row['School']} - {row['Score']} = {row['Percentage']}%")
                
        st.subheader("Learner Leaderboard")
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Results CSV", csv, "ilearn_uganda_results.csv", "text/csv")
