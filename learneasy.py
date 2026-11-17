import streamlit as st
import pandas as pd
import os
import requests
import json

st.set_page_config(page_title="iLearn-Uganda", layout="centered")

TEACHER_PASSWORD = st.secrets.get("TEACHER_PASSWORD", "iLearnUganda123")
CSV_FILE = "results.csv"
SHEET_URL = st.secrets.get("SHEET_URL", "")

# Official NCDC Curriculum Framework Mapped Directly from Booklets
NCDC_OFFICIAL_CURRICULUM = {
    "Lower Primary Cycle (P1–P3: Thematic Approach)": {
        "P1 (12 National Themes)": [
            "1. Our School", "2. Our Home and Community", "3. The Human Body and Health", 
            "4. Food and Nutrition", "5. Our Environment", "6. Plants", 
            "7. Animals", "8. Weather", "9. Transport", 
            "10. Communication", "11. Peace and Security", "12. Occupations"
        ],
        "P2 (12 National Themes)": [
            "1. Our Community", "2. Food and Nutrition", "3. Changes in the Environment", 
            "4. Sanitation and Hygiene", "5. Transport and Communication", "6. Peace and Security", 
            "7. Accidents and Safety", "8. Child Rights", "9. Energy", 
            "10. Leisure Time", "11. Keeping Animals and Plants", "12. Our Leaders"
        ],
        "P3 (12 National Themes & Transition Foundations)": [
            "1. Our Sub-county / Division", "2. Living Together", "3. Environment and Weather", 
            "4. Food and Nutrition", "5. Sanitation and Water", "6. Transport", 
            "7. Communication", "8. Energy", "9. Occupations and Trade", 
            "10. Security and Peace", "11. Culture", "12. Transition Foundations"
        ]
    },
    "Upper Primary Cycle (P4–P7: Subject-Based Sets)": {
        "P4 (Transition Year)": {
            "Set One Subjects": [
                "English (Grammar, Comprehension, Composition)", 
                "Mathematics (12 Core NCDC Strands)", 
                "Integrated Science", 
                "Social Studies (SST)", 
                "Religious Education (CRE / IRE)", 
                "Local Language Framework"
            ],
            "Set Two (CAPE Framework)": [
                "CAPE 1: Music, Dance and Drama (MDD)", 
                "CAPE 2: Physical Education (PE & Sports)", 
                "CAPE 3: Art, Craft and Technology"
            ]
        },
        "P5": {
            "Set One Subjects": [
                "English", "Mathematics", "Integrated Science", 
                "Social Studies (Uganda's Geography, Kingdoms, Constitution)", 
                "Religious Education (CRE / IRE)", "Local Language"
            ],
            "Set Two (CAPE Framework)": [
                "CAPE 1: Music, Dance and Drama", 
                "CAPE 2: Physical Education", 
                "CAPE 3: Art and Technology"
            ]
        },
        "P6": {
            "Set One Subjects": [
                "English", "Mathematics", "Integrated Science", 
                "Social Studies (East Africa, Scramble & Partition, Independence)", 
                "Religious Education (CRE / IRE)", "Local Language"
            ],
            "Set Two (CAPE Framework)": [
                "CAPE 1: Music, Dance and Drama", 
                "CAPE 2: Physical Education", 
                "CAPE 3: Art and Technology"
            ]
        },
        "P7 (PLE Class)": {
            "Set One Subjects (Examinable for PLE)": [
                "English", "Mathematics (Advanced Strands & Past Papers)", 
                "Integrated Science (Excretory/Nervous Systems, Agriculture)", 
                "Social Studies (Africa, International Bodies, Governance)", 
                "Religious Education (CRE / IRE)", "Local Language Framework"
            ],
            "Set Two (CAPE Framework)": [
                "CAPE 1: Music, Dance and Drama", 
                "CAPE 2: Physical Education", 
                "CAPE 3: Art and Technology"
            ]
        }
    }
}

# Official NCDC Mathematics 12 Strands Database for Upper Primary
NCDC_MATH_STRANDS = [
    "1. Set Concepts (Venn Diagrams, Subsets, Probability)",
    "2. Whole Numbers (Place Values, Roman Numerals, Bases)",
    "3. Operations on Whole Numbers (BODMAS, Word Problems)",
    "4. Patterns and Sequences (Progressions, Primes, Squares)",
    "5. Fractions, Decimals and Percentages (Ratios, Commercial Arithmetic)",
    "6. Lines, Angles and Geometric Figures (Constructions, Properties)",
    "7. Data Handling (Statistics, Mean, Median, Mode, Graphs)",
    "8. Time (Speed, Distance, Timetables, Travel Graphs)",
    "9. Integers (Number Line Operations, Coordinates)",
    "10. Money (Profit, Loss, Simple/Compound Interest, Utility Bills)",
    "11. Length, Mass and Capacity (Perimeter, Area, Volume, Density)",
    "12. Algebra (Linear Equations, Inequalities, Simultaneous Equations)"
]

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
        ("Q4. [English] Choose the correct form: Neither John nor his friends ........ coming.", ["is", "are", "was", "has"], "are", "Verb agrees with the closer subject ('friends' -> are)."),
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
st.sidebar.caption("Official NCDC Curriculum Portal")
page = st.sidebar.selectbox(
    "Go to",
    ["Take Quiz", "NCDC Official Syllabus Structure", "Teacher Dashboard"]
)

if page == "Take Quiz":
    st.title("iLearn-Uganda Assessment Portal")
    st.caption("Primary Level Competency Assessment based on NCDC Standards")
    st.write("Select your class, answer the questions, and submit your score.")
    
    if st.button("Next Child - Clear for New Learner"):
        saved = st.session_state.get("results", [])
        st.session_state.clear()
        st.session_state.results = saved
        st.session_state.submitted = False
        st.session_state.last_submit_key = ""
        st.session_state.dashboard_unlocked = False
        st.rerun()
        
    name = st.text_input("Learner Name", key="name")
    school = st.text_input("School Name", key="school")
    learner_class = st.selectbox("Select Class", [f"P{i}" for i in range(1, 8)], key="learner_class")
    
    questions = CLASS_QUESTIONS.get(learner_class, [])
    
    st.markdown(f"### Assessment for {learner_class}")
    answers = []
    for i, (q, options, correct, explain) in enumerate(questions):
        ans = st.radio(q, options, key=f"q{i}_{learner_class}", index=None)
        answers.append(ans)
        
    if st.session_state.submitted:
        st.info("This child has already submitted. Click 'Next Child' above for the next learner.")
        
    if st.button("Submit Quiz - See Results"):
        if st.session_state.submitted:
            st.warning("Already submitted. Click 'Next Child' for a new learner.")
        elif not name or not school:
            st.warning("Please fill in Learner Name and School Name.")
        elif any(a is None for a in answers):
            st.warning("Please answer all questions before submitting.")
        else:
            submit_key = f"{name}|{school}|{learner_class}|{answers}"
            if submit_key == st.session_state.last_submit_key:
                st.warning("Already submitted.")
            else:
                score = 0
                for i, (q, options, correct, explain) in enumerate(questions):
                    if str(answers[i]) == str(correct):
                        score = score + 1
                total = len(questions)
                pct = round(score * 100 / total, 1) if total > 0 else 0
                
                if pct >= 80:
                    grade, comment = "A", "Excellent mastery!"
                elif pct >= 60:
                    grade, comment = "B", "Very good performance."
                elif pct >= 40:
                    grade, comment = "C", "Good, keep revising."
                else:
                    grade, comment = "D", "Needs more practice."
                    
                new_row = {
                    "Name": name, "Class": learner_class, "School": school, 
                    "Score": f"{score}/{total}", "Percentage": pct, "Grade": grade, "Comment": comment
                }
                st.session_state.results.append(new_row)
                ok = save_one_result(new_row)
                if ok:
                    st.success("Saved to Google Sheets database successfully ✅")
                else:
                    st.warning("Saved locally (Check Google Sheets secret configuration).")
                    
                st.session_state.last_submit_key = submit_key
                st.session_state.submitted = True
                st.success(f"Well done {name}! Score: {score}/{total} ({pct}%) — Grade: {grade}")
                st.write(comment)
                
                st.subheader("Detailed Review")
                for i, (q, options, correct, explain) in enumerate(questions):
                    st.write(f"**Q{i+1}:** {q}")
                    st.write(f"Your Answer: {answers[i]} | Correct Answer: {correct}")
                    st.write(f"Explanation: {explain}")
                    st.markdown("---")

elif page == "NCDC Official Syllabus Structure":
    st.title("📖 NCDC Official Primary Curriculum Booklets")
    st.caption("National Curriculum Development Centre (Uganda) Official Framework Index")
    
    cycle_sel = st.selectbox("Select Curriculum Cycle", list(NCDC_OFFICIAL_CURRICULUM.keys()))
    class_sel = st.selectbox("Select Class Level", list(NCDC_OFFICIAL_CURRICULUM[cycle_sel].keys()))
    
    st.markdown("---")
    st.subheader(f"Curriculum Details for {class_sel}")
    
    class_info = NCDC_OFFICIAL_CURRICULUM[cycle_sel][class_sel]
    if isinstance(class_info, dict):
        for key, val in class_info.items():
            st.markdown(f"### **{key}**")
            if isinstance(val, list):
                for item in val:
                    st.write(f"- {item}")
            else:
                st.info(val)
    elif isinstance(class_info, list):
        for item in class_info:
            st.write(f"- {item}")
            
    if "P4" in class_sel or "P5" in class_sel or "P6" in class_sel or "P7" in class_sel:
        st.markdown("---")
        st.subheader("📐 Official NCDC Mathematics 12 Core Strands Structure")
        st.write("Mathematics across upper primary is standardized around these 12 core NCDC strands:")
        for strand in NCDC_MATH_STRANDS:
            st.write(f"✅ {strand}")

elif page == "Teacher Dashboard":
    st.title("iLearn-Uganda Teacher Dashboard - Locked")
    if not st.session_state.dashboard_unlocked:
        pwd = st.text_input("Enter Teacher Password", type="password", key="teacher_pwd")
        if st.button("Unlock Dashboard"):
            if pwd == TEACHER_PASSWORD:
                st.session_state.dashboard_unlocked = True
                st.rerun()
            else:
                st.error("Incorrect password.")
        st.stop()
        
    st.title("iLearn-Uganda Teacher Dashboard")
    st.caption("Official Class Performance & Leaderboard")
    
    if SHEET_URL:
        st.success("Google Sheets Connection Active ✅")
    else:
        st.warning("Google Sheets URL not provided in secrets (Local CSV mode active).")
        
    if st.button("Lock Dashboard"):
        st.session_state.dashboard_unlocked = False
        st.rerun()
        
    results = st.session_state.get("results", [])
    st.write(f"Total Submissions Logged: {len(results)}")
    
    if len(results) > 0:
        df = pd.DataFrame(results)
        class_filter = st.selectbox("Filter by Class", ["All"] + sorted(df["Class"].unique().tolist()))
        if class_filter != "All":
            df = df[df["Class"] == class_filter]
            
        df = df.sort_values(by="Percentage", ascending=False).reset_index(drop=True)
        df.insert(0, "Rank", range(1, len(df) + 1))
        
        st.subheader("🏆 Learner Leaderboard")
        st.dataframe(df)
        
        csv = df.to_csv(index=False).encode("utf-8")
        st.download_button("Download Leaderboard CSV", csv, "ilearn_uganda_official_results.csv", "text/csv")
    else:
        st.info("No learner results logged yet.")
