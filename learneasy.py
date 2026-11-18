import streamlit as st
import pandas as pd
import os
import requests
import json

st.set_page_config(page_title="iLearn-Uganda", layout="centered")

TEACHER_PASSWORD = st.secrets.get("TEACHER_PASSWORD", "iLearnUganda123")
CSV_FILE = "results.csv"
SHEET_URL = st.secrets.get("SHEET_URL", "")

# Complete Official NCDC Primary Curriculum Framework (P1–P7)
NCDC_OFFICIAL_FRAMEWORK = {
    "Lower Primary (Cycle 1: Thematic Approach P1–P3)": {
        "P1": {
            "Literacy I (Local Language)": {
                "Topics / Themes": ["Our School", "Our Home and Community", "Our Environment", "Plants and Animals"],
                "Life Skills": ["Effective communication", "Self-awareness", "Interpersonal relationships"],
                "Values": ["Obedience", "Respect", "Neatness"],
                "Learning Aids": ["Name flashcards", "Picture charts", "Real school objects"]
            },
            "Literacy II (Health, Science & Environment)": {
                "Topics / Themes": ["The Human Body and Health", "Food and Nutrition", "Weather Changes", "Sanitation"],
                "Life Skills": ["Self-care", "Health awareness", "Critical thinking"],
                "Values": ["Cleanliness", "Self-respect", "Hygiene"],
                "Learning Aids": ["Soap, clean water, basin", "Human body charts", "Weather symbols"]
            },
            "Numeracy (Mathematics)": {
                "Topics / Themes": ["Set Concepts (Sorting & Matching)", "Whole Numbers (1-10)", "Operations (Addition & Subtraction up to 20)"],
                "Life Skills": ["Logical thinking", "Problem solving", "Accuracy"],
                "Values": ["Patience", "Orderliness", "Honesty"],
                "Learning Aids": ["Bottle tops, sticks, stones (counters)", "Number cards", "Abacus"]
            },
            "English (Oral & Transition)": {
                "Topics / Themes": ["Greetings & Courtesies", "Simple Classroom Instructions", "Naming Common Objects"],
                "Life Skills": ["Listening attention", "Verbal expression"],
                "Values": ["Confidence", "Courtesy"],
                "Learning Aids": ["Audio flashcards", "Puppets", "Action charts"]
            }
        },
        "P2": {
            "Literacy I (Local Language)": {
                "Topics / Themes": ["Our Community", "Child Rights and Responsibilities", "Cultural Practices"],
                "Life Skills": ["Decision making", "Empathy", "Effective communication"],
                "Values": ["Cooperation", "Sharing", "Responsibility"],
                "Learning Aids": ["Storybooks", "Community role-play cards", "Local language charts"]
            },
            "Literacy II (Environment & Science)": {
                "Topics / Themes": ["Food and Nutrition (Local food groups)", "Sanitation and Personal Hygiene", "Sources of Energy", "Keeping Animals and Plants"],
                "Life Skills": ["Health consciousness", "Environmental observation", "Coping with stress"],
                "Values": ["Gratitude", "Stewardship", "Cleanliness"],
                "Learning Aids": ["Real food samples", "Seed samples", "Energy source charts"]
            },
            "Numeracy (Mathematics)": {
                "Topics / Themes": ["Set Concepts (Intersection & Union)", "Whole Numbers up to 50", "Addition & Subtraction with Regrouping", "Basic Multiplication"],
                "Life Skills": ["Analytical thinking", "Numerical estimation"],
                "Values": ["Precision", "Diligence"],
                "Learning Aids": ["Place value tins", "Bundles of 10 sticks", "Multiplication grids"]
            },
            "English": {
                "Topics / Themes": ["Descriptive Vocabulary", "Simple Present Tense", "Reading Short Sentences"],
                "Life Skills": ["Literacy comprehension", "Confidence"],
                "Values": ["Perseverance", "Neatness"],
                "Learning Aids": ["Word flashcards", "Reader books"]
            }
        },
        "P3": {
            "Literacy I / Transition to English": {
                "Topics / Themes": ["Our Sub-county / Division", "Living Together", "Transition Foundations to English-medium instruction"],
                "Life Skills": ["Spatial orientation", "Civic awareness", "Negotiation"],
                "Values": ["Patriotism", "Community pride", "Tolerance"],
                "Learning Aids": ["Sub-county sketch maps", "Transition reading cards"]
            },
            "Literacy II (Science & Environment)": {
                "Topics / Themes": ["Environment and Weather", "Sanitation and Water", "Energy Resources", "Vector Control"],
                "Life Skills": ["Health protection", "Problem solving"],
                "Values": ["Responsibility", "Environmental care"],
                "Learning Aids": ["Safe water chain charts", "Rain gauge models"]
            },
            "Numeracy (Mathematics)": {
                "Topics / Themes": ["Numbers up to 1,000", "Multiplication Tables", "Simple Fractions (Halves, Quarters)", "Money & Local Currency", "Standard Metric Units"],
                "Life Skills": ["Financial literacy", "Measurement estimation"],
                "Values": ["Honesty in trade", "Fairness"],
                "Learning Aids": ["Currency notes/coins", "Meter rulers", "Fraction cut-outs"]
            },
            "English": {
                "Topics / Themes": ["Grammar fundamentals", "Paragraph construction", "Guided composition"],
                "Life Skills": ["Effective writing", "Expression"],
                "Values": ["Clarity", "Discipline"],
                "Learning Aids": ["Sentence strips", "Writing charts"]
            }
        }
    },
    "Upper Primary (Cycle 2 & 3: Subject-Based P4–P7)": {
        "P4": {
            "1. Mathematics (12 Core NCDC Strands)": {
                "Topics / Themes": ["Set Concepts", "Whole Numbers", "Operations on Whole Numbers", "Patterns & Sequences", "Fractions", "Lines, Angles & Geometry", "Data Handling", "Time", "Integers", "Money", "Length, Mass & Capacity", "Algebra"],
                "Life Skills": ["Logical reasoning", "Spatial precision", "Problem solving"],
                "Values": ["Accuracy", "Orderliness", "Persistence"],
                "Learning Aids": ["Venn diagram charts", "Abacus", "Protractors", "Weighing scales"]
            },
            "2. English Language": {
                "Topics / Themes": ["Nouns & Pronouns", "Present & Past Simple Tenses", "Punctuation", "Comprehension & Summary", "Guided Letter Writing"],
                "Life Skills": ["Effective written & oral communication", "Critical analysis"],
                "Values": ["Neatness", "Clarity", "Courtesy"],
                "Learning Aids": ["Grammar charts", "Letter templates", "Comprehension readers"]
            },
            "3. Integrated Science": {
                "Topics / Themes": ["Plant Anatomy & Crop Growing", "Human Digestive System & Teeth", "Weather Instruments", "Sanitation & Vectors"],
                "Life Skills": ["Scientific observation", "Agricultural husbandry", "Health safety"],
                "Values": ["Environmental stewardship", "Hard work", "Cleanliness"],
                "Learning Aids": ["Uprooted flowering plants", "Dental anatomy charts", "Rain gauge"]
            },
            "4. Social Studies (SST)": {
                "Topics / Themes": ["Map Reading (Compass, Scale, Key)", "District Physical Geography", "Vegetation & Climate", "Local Administrative Leadership"],
                "Life Skills": ["Map navigation", "Civic participation", "Environmental awareness"],
                "Values": ["Patriotism", "Respect for leaders", "Unity"],
                "Learning Aids": ["District wall maps", "Magnetic compass", "Relief models"]
            },
            "5. Religious Education (CRE / IRE)": {
                "Topics / Themes": ["Creation & God's Purpose", "Foundational Covenants (Noah, Abraham)", "Moral Integrity & Honesty", "Service to Community"],
                "Life Skills": ["Moral reasoning", "Empathy", "Spiritual reflection"],
                "Values": ["Integrity", "Truthfulness", "Reverence"],
                "Learning Aids": ["Bible / Quran extracts", "Moral scenario flashcards"]
            },
            "6. CAPE (Arts & PE)": {
                "Topics / Themes": ["CAPE 1: Music, Dance & Drama (Folk tunes & rhythm)", "CAPE 2: Physical Education (Athletics & ball game rules)", "CAPE 3: Art & Technology (Color mixing, paper craft)"],
                "Life Skills": ["Motor coordination", "Physical endurance", "Creative design"],
                "Values": ["Sportsmanship", "Discipline", "Cultural appreciation"],
                "Learning Aids": ["Watercolors", "Footballs", "Local drums"]
            }
        },
        "P5": {
            "1. Mathematics (12 Core NCDC Strands)": {
                "Topics / Themes": ["Advanced Sets & Subsets", "Whole Numbers up to 999,999 & Roman Numerals", "BODMAS & Word Problems", "Primes & Sequences", "Fractions, Decimals & Percentages", "Angles on Lines & Polygons", "Statistics (Mean, Median, Mode)", "24-Hour Clock & Speed", "Integers", "Profit & Loss", "Area & Volume", "Basic Algebra & Inequalities"],
                "Life Skills": ["Logical deduction", "Proportional reasoning", "Statistical interpretation"],
                "Values": ["Precision", "Curiosity", "Diligence"],
                "Learning Aids": ["Percentage grid charts", "Geometric shape models", "Statistical survey sheets"]
            },
            "2. English Language": {
                "Topics / Themes": ["Relative Clauses", "Conjunctions (because, although)", "Poetry Analysis", "Formal & Informal Letters", "Summary Writing"],
                "Life Skills": ["Formal speech", "Advanced reading comprehension"],
                "Values": ["Respect", "Clarity"],
                "Learning Aids": ["Poetry anthologies", "Formal letter samples"]
            },
            "3. Integrated Science": {
                "Topics / Themes": ["States of Matter", "Heat Transfer (Conduction, Convection, Radiation)", "Human Circulatory & Respiratory Systems", "Primary Health Care (PHC) & Immunization"],
                "Life Skills": ["Experimental inquiry", "Health safety management"],
                "Values": ["Scientific curiosity", "Responsibility"],
                "Learning Aids": ["Heat sources & metal rods", "Heart and lung anatomical charts", "Immunization schedules"]
            },
            "4. Social Studies (SST)": {
                "Topics / Themes": ["Uganda's Physical Geography & Relief Zones", "Drainage Systems", "Ethnic Migrations (Bantu, Nilotics)", "Early African Kingdoms", "The National Constitution"],
                "Life Skills": ["Historical synthesis", "Geopolitical awareness", "Civic responsibility"],
                "Values": ["National unity", "Tolerance", "Patriotism"],
                "Learning Aids": ["Physical map of Uganda", "Migration arrow maps", "Constitution extracts"]
            },
            "5. Religious Education (CRE / IRE)": {
                "Topics / Themes": ["Life and Teachings of Jesus Christ / Prophet Muhammad", "Compassion and Justice", "Worship Practices", "Resisting Negative Peer Pressure"],
                "Life Skills": ["Assertiveness", "Ethical decision-making", "Moral fortitude"],
                "Values": ["Compassion", "Steadfastness", "Justice"],
                "Learning Aids": ["Scripture text guides", "Peer-pressure role-play cards"]
            },
            "6. CAPE (Arts & PE)": {
                "Topics / Themes": ["CAPE 1: Traditional Folk Songs & Dance Formations", "CAPE 2: Gymnastics & Athletic Endurance", "CAPE 3: Functional Craft, Pottery & Weaving"],
                "Life Skills": ["Physical stamina", "Artistic craftsmanship"],
                "Values": ["Cultural preservation", "Perseverance"],
                "Learning Aids": ["Local clay", "Weaving reeds", "Gym mats"]
            }
        },
        "P6": {
            "1. Mathematics (12 Core NCDC Strands)": {
                "Topics / Themes": ["Venn Diagram Word Problems (2-Set)", "Place Values in Millions & Number Bases (Base 5 & 2)", "Advanced Operations", "Fibonacci Sequences", "Reciprocals & Simple Interest", "Parallel Lines & Circle Properties", "Pie Charts & Bar-Line Graphs", "Travel Graphs & Time Zones", "Cartesian Plane Coordinates", "Foreign Exchange & Utility Bills", "Area of Trapeziums/Rings & Volume of Cylinders", "Brackets, Factorization & Simultaneous Equations"],
                "Life Skills": ["Logical synthesis", "Financial literacy", "Spatial visualization"],
                "Values": ["Tenacity", "Prudence", "Accuracy"],
                "Learning Aids": ["Venn diagram worksheet charts", "Sample utility bills", "Cylinder models", "Cartesian grid boards"]
            },
            "2. English Language": {
                "Topics / Themes": ["Active and Passive Voice", "Direct and Indirect (Reported) Speech", "Conditional Clauses (First, Second, Third)", "Formal Report Writing", "Meeting Minutes"],
                "Life Skills": ["Public speaking", "Critical editing", "Persuasion"],
                "Values": ["Confidence", "Respect for views", "Accuracy"],
                "Learning Aids": ["Speech transformation charts", "Meeting minute templates"]
            },
            "3. Integrated Science": {
                "Topics / Themes": ["Electricity and Magnetism", "Simple Machines (Levers, Pulleys, Inclined Planes)", "Friction", "Mammalian Reproduction & Adolescence", "Personal Hygiene & Immunity"],
                "Life Skills": ["Technical problem solving", "Self-protection", "Health maintenance"],
                "Values": ["Safety consciousness", "Responsibility", "Self-respect"],
                "Learning Aids": ["Dry cells & copper wires", "Pulley/lever models", "Health education charts"]
            },
            "4. Social Studies (SST)": {
                "Topics / Themes": ["East African Physical Resources", "European Scramble and Partition", "African Resistance Movements", "Path to Independence", "Regional Cooperation (EAC)"],
                "Life Skills": ["Geopolitical analysis", "Historical synthesis"],
                "Values": ["Pan-African solidarity", "Patriotism", "Peace advocacy"],
                "Learning Aids": ["East Africa political & resource maps", "Historical timelines"]
            },
            "5. Religious Education (CRE / IRE)": {
                "Topics / Themes": ["Faith in Action", "Christian/Islamic Leadership Models", "Family Values & Dignity of Work", "Resource Stewardship & Conflict Resolution"],
                "Life Skills": ["Conflict mediation", "Leadership ethics"],
                "Values": ["Accountability", "Stewardship", "Peace-building"],
                "Learning Aids": ["Community leadership case studies", "Scripture guides"]
            },
            "6. CAPE (Arts & PE)": {
                "Topics / Themes": ["CAPE 1: Choral Performance & Drama Scripts", "CAPE 2: First-Aid Safety & Sports Officiating", "CAPE 3: Advanced Sculpture, Tie-and-Dye, Textile Design"],
                "Life Skills": ["Emergency response", "Dramatic direction"],
                "Values": ["Safety mindfulness", "Civic responsibility", "Enterprise"],
                "Learning Aids": ["First aid kits", "Papier-mâché", "Textile dyes"]
            }
        },
        "P7": {
            "1. Mathematics (12 Core NCDC Strands Mastery)": {
                "Topics / Themes": ["3-Set Venn Diagram Word Problems", "Standard Form & Non-Decimal Base Arithmetic", "PLE Past Paper Problem Solving", "Advanced Progressions & Proofs", "Recurring Decimals & Advanced Commercial Math", "Compass Construction of Angles & Triangles", "Probability & Combined Data Interpretation", "Average Speed for Multi-Stage Journeys", "Linear Inequalities & Graphing", "Simple Interest & Taxation", "Composite Area & Volume of Solids", "Quadratic Expressions & Word Problems"],
                "Life Skills": ["Strategic time management under pressure", "Advanced analytical deduction", "Risk evaluation"],
                "Values": ["Resilience", "Excellence", "Analytical honesty"],
                "Learning Aids": ["PLE past paper compilations", "Mathematical sets", "Probability spinners"]
            },
            "2. English Language": {
                "Topics / Themes": ["PLE Grammar Consolidation", "Phrasal Verbs & Idioms", "Proverb Meanings & Synonyms", "Passage Summary Compression", "Timed Exam Simulation"],
                "Life Skills": ["Stress control", "Time management under exams", "Rapid comprehension"],
                "Values": ["Academic integrity", "Perseverance"],
                "Learning Aids": ["Timed PLE past papers", "Idiom reference sheets"]
            },
            "3. Integrated Science": {
                "Topics / Themes": ["Excretory System (Kidneys, Skin)", "Nervous System (Brain, Spinal Cord, Reflex Arc)", "Agricultural Science & Crop Production", "Livestock & Poultry Management", "Environmental Conservation"],
                "Life Skills": ["Scientific synthesis", "Agricultural entrepreneurship", "Environmental advocacy"],
                "Values": ["Environmental accountability", "Diligence", "Hard work"],
                "Learning Aids": ["Kidney/brain anatomical charts", "Livestock feed samples", "Conservation posters"]
            },
            "4. Social Studies (SST)": {
                "Topics / Themes": ["Continental Geography of Africa", "Decolonization Struggles in Africa", "African Union (AU) & United Nations (UN)", "International Trade & Global Governance", "Holistic PLE SST Revision"],
                "Life Skills": ["Global citizenship", "International relations evaluation"],
                "Values": ["Global empathy", "Peace advocacy", "Civic pride"],
                "Learning Aids": ["Wall map of Africa", "AU/UN organizational charts", "Revision briefs"]
            },
            "5. Religious Education (CRE / IRE)": {
                "Topics / Themes": ["Moral Theology & Human Dignity", "Ethical Responses to Modern Challenges", "Social Responsibility", "Comprehensive PLE CRE/IRE Revision"],
                "Life Skills": ["Ethical discernment", "Holistic self-evaluation"],
                "Values": ["Spiritual maturity", "Moral integrity", "Justice"],
                "Learning Aids": ["Thematic PLE revision briefs", "Ethical dilemma discussion cards"]
            },
            "6. CAPE (Arts & PE)": {
                "Topics / Themes": ["CAPE 1: Advanced MDD Stage Productions", "CAPE 2: Recreational Sport Management & Fitness", "CAPE 3: Entrepreneurial Craft Exhibitions & Marketing"],
                "Life Skills": ["Sports leadership", "Event organization", "Entrepreneurship"],
                "Values": ["Enterprise", "Cultural leadership", "Teamwork"],
                "Learning Aids": ["Sports officiating gear", "Exhibition boards", "Craft marketing tags"]
            }
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
        ("Q4. [English] Choose the correct form: Neither John nor his friends ........ coming.", ["is", "are", "was", "has"], "are", "Verb agrees with the closer subject ('friends' -> are)."),
    ],
    "P7": [
        ("Q1. [Maths] Solve for x: 2x + 4 = 12", ["x = 4", "x = 6", "x = 8", "x = 2"], "x = 4", "2x = 12 - 4 => 2x = 8 => x = 4."),
        ("Q2. [Science] Why is heat unable to travel in a vacuum?", ["There are no particles to carry it", "Vacuum is too hot", "Vacuum is too cold", "Vacuum has many particles"], "There are no particles to carry it", "Heat requires particles to transfer via conduction or convection; a vacuum has none."),
        ("Q3. [SST] Name the organization that replaced the East African Community in 1977 before it was revived later.", ["COMESA", "None / It collapsed", "ECOWAS", "AU"], "None / It collapsed", "The initial EAC collapsed in 1977."),
        ("Q4. [English] Choose the correct indirect speech: John said, 'I am going home.'", ["John said that he is going home", "John said that he was going home", "John said he is went home", "John said that I was going home"], "John said that he was going home", "Present tense changes to past tense in indirect speech."),
    ]
}

OMWESO_PUZZLES = {
    "P1–P3 (Counting & Number Bonds)": {
        "question": "Pit 1 holds 5 seeds. If you sow anti-clockwise (1 seed per pit across your 16-pit loop), which pit receives the last seed?",
        "options": ["Pit 5", "Pit 6", "Pit 7", "Pit 4"],
        "answer": "Pit 6",
        "explanation": "1 + 5 = 6. Counting on 5 steps anti-clockwise from Pit 1 lands in Pit 6.",
        "ncdc_strand": "Whole Numbers & Addition (P1–P3)"
    },
    "P4–P5 (Division & Remainders)": {
        "question": "One full lap around your 16 pits takes 16 steps anti-clockwise. Pit 2 holds 19 seeds. Where does the 19th seed land?",
        "options": ["Pit 3", "Pit 4", "Pit 5", "Pit 6"],
        "answer": "Pit 5",
        "explanation": "19 ÷ 16 = 1 full lap with remainder 3. Starting at Pit 2 moving anti-clockwise: 2 + 3 = Pit 5.",
        "ncdc_strand": "Operations & Remainders (P4–P5)"
    },
    "P6–P7 (Relay Chain & Okutta Capture)": {
        "question": "When you land in a pit, which opponent pits do you capture from?",
        "options": ["Any random pit", "The immediate front line and back line pits directly opposite where you landed", "All opponent pits", "Only corner pits"],
        "answer": "The immediate front line and back line pits directly opposite where you landed",
        "explanation": "Okutta captures seeds from the immediate front line and back line pits directly across from the landing pit.",
        "ncdc_strand": "Modular Arithmetic & Multi-Step Problem Solving (P6–P7)"
    }
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
    ["Take Quiz", "Omweso Math Arena", "NCDC Official Syllabus Reference", "Teacher Dashboard"]
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

elif page == "Omweso Math Arena":
    st.title("🎲 Omweso Math Arena (Front & Back Line Capture)")
    st.caption("Ugandan Traditional Rules: Immediate Front and Back Opposing Pits Capture & Virtual Finger Sowing")

    tab_play, tab_puzzle = st.tabs(["🕹️ Pass & Play (Locality Rules)", "🧩 NCDC Curriculum Puzzles"])

    with tab_play:
        omweso_front_back_html = """
        <!DOCTYPE html>
        <html>
        <head>
        <style>
          body {
            background: #2b1810;
            color: #f4e8d8;
            font-family: sans-serif;
            text-align: center;
            margin: 0;
            padding: 5px;
          }
          #board-container {
            background: linear-gradient(135deg, #5c2c16, #3a1a0b);
            border: 5px solid #8B4513;
            border-radius: 14px;
            padding: 12px;
            box-shadow: 0 8px 20px rgba(0,0,0,0.6);
            display: inline-block;
            max-width: 620px;
            width: 100%;
            position: relative;
          }
          .row {
            display: flex;
            justify-content: center;
            gap: 6px;
            margin: 8px 0;
          }
          .pit {
            width: 52px;
            height: 65px;
            background: radial-gradient(circle at 50% 30%, #1e0d05, #0f0502);
            border: 3px solid #d4a373;
            border-radius: 50%/30%;
            box-shadow: inset 0 6px 10px rgba(0,0,0,0.9), 0 3px 5px rgba(0,0,0,0.4);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            position: relative;
            transition: transform 0.1s, background-color 0.3s;
          }
          .pit:hover {
            transform: scale(1.05);
            border-color: #faedcd;
          }
          .pit.playable-p1 {
            border-color: #52b788;
            box-shadow: inset 0 6px 10px rgba(0,0,0,0.9), 0 0 10px #52b788;
          }
          .pit.playable-p2 {
            border-color: #ffb703;
            box-shadow: inset 0 6px 10px rgba(0,0,0,0.9), 0 0 10px #ffb703;
          }
          .pit.capturing {
            background: radial-gradient(circle at 50% 30%, #780000, #370617);
            border-color: #ff4d6d;
            box-shadow: inset 0 6px 10px rgba(0,0,0,0.9), 0 0 14px #ff4d6d;
            transform: scale(1.1);
          }
          .pit-label {
            position: absolute;
            top: 2px;
            font-size: 8px;
            color: #d4a373;
            font-weight: bold;
          }
          .seeds-container {
            display: flex;
            flex-wrap: wrap;
            width: 40px;
            height: 40px;
            align-items: center;
            justify-content: center;
            gap: 2px;
            margin-top: 8px;
          }
          .seed-3d {
            width: 10px;
            height: 10px;
            background: radial-gradient(circle at 35% 35%, #ffb703, #b5651d 60%, #53330b);
            border-radius: 50%;
            box-shadow: 1px 2px 3px rgba(0,0,0,0.8), inset -1px -1px 2px rgba(0,0,0,0.5);
            display: inline-block;
          }
          #game-finger {
            position: absolute;
            font-size: 32px;
            pointer-events: none;
            transition: top 0.15s ease, left 0.15s ease;
            z-index: 50;
            display: none;
            filter: drop-shadow(0 3px 5px rgba(0,0,0,0.7));
          }
          #status-bar {
            font-size: 14px;
            margin: 10px 0;
            padding: 8px;
            background: #432818;
            border-radius: 8px;
            border: 1px solid #bb9457;
            font-weight: bold;
          }
          #direction-modal {
            display: none;
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: rgba(0,0,0,0.8);
            z-index: 100;
            align-items: center;
            justify-content: center;
          }
          .modal-content {
            background: #3a1a0b;
            border: 4px solid #d4a373;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            max-width: 350px;
            width: 90%;
          }
          button.dir-btn {
            background: #52b788;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            margin: 8px;
            font-size: 14px;
          }
          button.dir-btn.clock {
            background: #bc6c25;
          }
          button.action-btn {
            background: #bc6c25;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            font-weight: bold;
            cursor: pointer;
            margin-top: 10px;
          }
          button.action-btn:hover {
            background: #dda15e;
          }
        </style>
        </head>
        <body>

          <div id="status-bar">Game Active: Tap any pit (2+ seeds) to start sowing!</div>

          <!-- Left Corner Reverse Choice Modal -->
          <div id="direction-modal">
            <div class="modal-content">
              <h3 style="color: #ffb703; margin-top:0;">🔄 Left Corner Reverse Option</h3>
              <p style="font-size: 13px;">This is one of the four left corner pits. You can choose to reverse (clockwise) or play standard anti-clockwise.</p>
              <button class="dir-btn" onclick="executeMoveWithDir(-1)">← Anti-Clockwise (Standard)</button><br>
              <button class="dir-btn clock" onclick="executeMoveWithDir(1)">Clockwise → (Reverse Option)</button>
            </div>
          </div>

          <div id="board-container">
            <!-- Virtual Finger -->
            <div id="game-finger">👆🏿</div>

            <div id="p2-header" style="font-size:11px; color:#ffb703; margin-bottom:3px;">PLAYER 2 SIDE (Top)</div>
            <div class="row" id="p2-outer"></div>
            <div class="row" id="p2-inner"></div>

            <hr style="border-color: #8B4513; margin: 10px 0;">

            <div class="row" id="p1-inner"></div>
            <div class="row" id="p1-outer"></div>
            <div id="p1-header" style="font-size:11px; color:#52b788; margin-top:3px;">PLAYER 1 SIDE (Bottom)</div>
          </div>

          <div>
            <button class="action-btn" onclick="resetGame()">Reset Board (2 Seeds/Pit)</button>
          </div>

        <script>
          let p1 = [2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2];
          let p2 = [2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2];
          let isAnimating = false;
          let capturingPits = [];
          let pendingStartPit = null;
          let pendingPlayer = null;
          let p1CornerCapturesCount = 0;
          let p2CornerCapturesCount = 0;

          let audioCtx = null;
          function playSeedSound() {
            try {
              if (!audioCtx) audioCtx = new (window.AudioContext || window.webkitAudioContext)();
              let osc = audioCtx.createOscillator();
              let gain = audioCtx.createGain();
              osc.type = 'triangle';
              osc.frequency.setValueAtTime(450 + Math.random() * 120, audioCtx.currentTime);
              osc.frequency.exponentialRampToValueAtTime(100, audioCtx.currentTime + 0.07);
              gain.gain.setValueAtTime(0.35, audioCtx.currentTime);
              gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.07);
              osc.connect(gain);
              gain.connect(audioCtx.destination);
              osc.start();
              osc.stop(audioCtx.currentTime + 0.07);
            } catch(e) {}
          }

          function renderBoard() {
            let htmlP2Outer = "";
            for (let i = 15; i >= 8; i--) { htmlP2Outer += createPitHTML(2, i, p2[i]); }
            document.getElementById('p2-outer').innerHTML = htmlP2Outer;

            let htmlP2Inner = "";
            for (let i = 7; i >= 0; i--) { htmlP2Inner += createPitHTML(2, i, p2[i]); }
            document.getElementById('p2-inner').innerHTML = htmlP2Inner;

            let htmlP1Inner = "";
            for (let i = 0; i <= 7; i++) { htmlP1Inner += createPitHTML(1, i, p1[i]); }
            document.getElementById('p1-inner').innerHTML = htmlP1Inner;

            let htmlP1Outer = "";
            for (let i = 15; i >= 8; i--) { htmlP1Outer += createPitHTML(1, i, p1[i]); }
            document.getElementById('p1-outer').innerHTML = htmlP1Outer;
          }

          function createPitHTML(player, index, count) {
            let seedsHTML = "";
            let displayCount = Math.min(count, 12);
            for (let s = 0; s < displayCount; s++) {
              seedsHTML += `<div class="seed-3d"></div>`;
            }
            if (count > 12) {
              seedsHTML += `<span style="font-size:8px; color:#ffb703; font-weight:bold;">+${count-12}</span>`;
            }
            let playable = !isAnimating && count >= 2;
            let onclickAttr = playable ? `onclick="initiateMove(${player}, ${index})"` : "";
            let playableClass = playable ? (player === 1 ? "playable-p1" : "playable-p2") : "";
            let isCapturing = (capturingPits.length > 0 && capturingPits.includes(index)) ? "capturing" : "";
            return `
              <div id="pit-${player}-${index}" class="pit ${playableClass} ${isCapturing}" ${onclickAttr}>
                <span class="pit-label">P${index}</span>
                <div class="seeds-container">${seedsHTML}</div>
              </div>
            `;
          }

          function pointFingerAtPit(player, index) {
            let finger = document.getElementById('game-finger');
            let pitEl = document.getElementById(`pit-${player}-${index}`);
            if (!pitEl) return;
            let container = document.getElementById('board-container');
            let cRect = container.getBoundingClientRect();
            let pRect = pitEl.getBoundingClientRect();
            
            let left = pRect.left - cRect.left + (pRect.width / 2) - 16;
            let top = pRect.top - cRect.top - 38;
            
            finger.style.left = left + 'px';
            finger.style.top = top + 'px';
            finger.style.display = 'block';
          }

          function hideFinger() {
            document.getElementById('game-finger').style.display = 'none';
          }

          function checkLossConditions(board, player) {
            let allSingle = true;
            for (let i = 0; i < 16; i++) {
              if (board[i] > 1) { allSingle = false; break; }
            }
            if (allSingle) {
              let winner = player === 1 ? "Player 1" : "Player 2";
              let loser = player === 1 ? "Player 2" : "Player 1";
              document.getElementById('status-bar').innerText = `🚨 ${loser} has only single seeds left! ${winner} WINS by Starvation (Rule 6)!`;
              return true;
            }
            if (player === 1 && p1CornerCapturesCount >= 2) {
              document.getElementById('status-bar').innerText = `🏆 Player 1 wins by capturing from both opponent corner pits twice (Rule 7 / Emitwe-ebiri)!`;
              return true;
            }
            if (player === 2 && p2CornerCapturesCount >= 2) {
              document.getElementById('status-bar').innerText = `🏆 Player 2 wins by capturing from both opponent corner pits twice (Rule 7 / Emitwe-ebiri)!`;
              return true;
            }
            return false;
          }

          // Immediate front-line and back-line pits directly opposite the landing pit
          function getFrontAndBackOppositePits(curr) {
            // curr: 0-7 (inner row), 8-15 (outer row)
            // Opposite front-line (inner row) and back-line (outer row) directly across:
            let frontOpp = curr <= 7 ? (7 - curr) : (15 - (curr - 8));
            let backOpp = curr <= 7 ? (8 + curr) : curr;
            return [frontOpp, backOpp];
          }

          function testCapture(board, oppBoard, startPit, dir) {
            let tempBoard = [...board];
            let tempOpp = [...oppBoard];
            let seeds = tempBoard[startPit];
            tempBoard[startPit] = 0;
            let curr = startPit;
            let steps = 0;
            while (seeds > 0 && steps < 200) {
              steps++;
              if (dir === -1) curr = (curr - 1 + 16) % 16;
              else curr = (curr + 1) % 16;
              tempBoard[curr] += 1;
              seeds -= 1;
              if (seeds === 0) {
                let [frontOpp, backOpp] = getFrontAndBackOppositePits(curr);
                if (tempOpp[frontOpp] > 0 || tempOpp[backOpp] > 0) return true;
              }
            }
            return false;
          }

          function initiateMove(player, startPit) {
            pendingPlayer = player;
            pendingStartPit = startPit;
            let board = (player === 1) ? p1 : p2;
            let oppBoard = (player === 1) ? p2 : p1;

            if ((startPit === 0 || startPit === 7 || startPit === 8 || startPit === 15) && board[startPit] >= 2) {
              let canClock = testCapture(board, oppBoard, startPit, 1);
              if (canClock) {
                document.getElementById('direction-modal').style.display = 'flex';
                return;
              }
            }
            executeMoveWithDir(-1);
          }

          async function executeMoveWithDir(dir) {
            document.getElementById('direction-modal').style.display = 'none';
            if (isAnimating) return;
            isAnimating = true;

            let player = pendingPlayer;
            let startPit = pendingStartPit;
            let board = (player === 1) ? p1 : p2;
            let opponentBoard = (player === 1) ? p2 : p1;

            let seedsInHand = board[startPit];
            board[startPit] = 0;
            let curr = startPit;
            renderBoard();

            pointFingerAtPit(player, startPit);
            document.getElementById('status-bar').innerText = `👆🏿 Player ${player} picks up ${seedsInHand} seeds from Pit ${startPit}!`;
            await sleep(600);

            if (dir === 1) {
              document.getElementById('status-bar').innerText = `👉 Reversing (clockwise) from left corner Pit ${startPit}...`;
              let tempSeeds = seedsInHand;
              let tempCurr = startPit;
              let steps = 0;
              while (tempSeeds > 0 && steps < 200) {
                steps++;
                tempCurr = (tempCurr + 1) % 16;
                board[tempCurr] += 1;
                tempSeeds -= 1;
                pointFingerAtPit(player, tempCurr);
                playSeedSound();
                renderBoard();
                await sleep(180);
              }

              let [frontOpp, backOpp] = getFrontAndBackOppositePits(tempCurr);
              if (opponentBoard[frontOpp] > 0 || opponentBoard[backOpp] > 0) {
                let captured = opponentBoard[frontOpp] + opponentBoard[backOpp];
                capturingPits = [frontOpp, backOpp];
                pointFingerAtPit(player === 1 ? 2 : 1, frontOpp);
                renderBoard();
                document.getElementById('status-bar').innerText = `✨ LEFT CORNER REVERSE CAPTURE! Finger takes front & back pits (${frontOpp} & ${backOpp})!`;
                playSeedSound();
                await sleep(1000);

                if (frontOpp === 0 || frontOpp === 7 || backOpp === 8 || backOpp === 15) {
                  if (player === 1) p1CornerCapturesCount++; else p2CornerCapturesCount++;
                }

                opponentBoard[frontOpp] = 0;
                opponentBoard[backOpp] = 0;
                capturingPits = [];
                renderBoard();

                if (checkLossConditions(opponentBoard, player)) { hideFinger(); isAnimating = false; return; }

                document.getElementById('status-bar').innerText = `🔄 Resuming normal movement from original start Pit ${startPit} anti-clockwise!`;
                seedsInHand = captured;
                curr = startPit;
                dir = -1;
              } else {
                hideFinger();
                isAnimating = false;
                renderBoard();
                return;
              }
            }

            // Standard Anti-Clockwise Sowing Loop with Finger Guide
            while (seedsInHand > 0) {
              await sleep(180);
              curr = (curr - 1 + 16) % 16;
              board[curr] += 1;
              seedsInHand -= 1;
              pointFingerAtPit(player, curr);
              playSeedSound();
              renderBoard();

              if (seedsInHand === 0) {
                let [frontOpp, backOpp] = getFrontAndBackOppositePits(curr);
                if (opponentBoard[frontOpp] > 0 || opponentBoard[backOpp] > 0) {
                  let captured = opponentBoard[frontOpp] + opponentBoard[backOpp];
                  
                  capturingPits = [frontOpp, backOpp];
                  pointFingerAtPit(player === 1 ? 2 : 1, frontOpp);
                  renderBoard();
                  document.getElementById('status-bar').innerText = `✨ PLAYER ${player} OKUTTA CAPTURE! Finger takes seeds from front & back opposite pits (${frontOpp} & ${backOpp})!`;
                  playSeedSound();
                  await sleep(1000);

                  if (frontOpp === 0 || frontOpp === 7 || backOpp === 8 || backOpp === 15) {
                    if (player === 1) p1CornerCapturesCount++; else p2CornerCapturesCount++;
                  }

                  opponentBoard[frontOpp] = 0;
                  opponentBoard[backOpp] = 0;
                  capturingPits = [];
                  renderBoard();

                  if (checkLossConditions(opponentBoard, player)) { hideFinger(); isAnimating = false; return; }

                  document.getElementById('status-bar').innerText = `🔄 Resuming movement from original start Pit ${startPit} with captured seeds!`;
                  seedsInHand = captured;
                  curr = startPit;
                  pointFingerAtPit(player, startPit);
                  await sleep(400);
                  continue;
                }

                if (board[curr] >= 2) {
                  seedsInHand = board[curr];
                  board[curr] = 0;
                  pointFingerAtPit(player, curr);
                  document.getElementById('status-bar').innerText = `🔄 RELAY! Finger picks up ${seedsInHand} seeds from Pit ${curr}!`;
                  await sleep(400);
                  continue;
                }
              }
            }

            hideFinger();
            isAnimating = false;
            renderBoard();
          }

          function sleep(ms) { return new Promise(resolve => setTimeout(resolve, ms)); }

          function resetGame() {
            if (isAnimating) return;
            p1 = [2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2];
            p2 = [2,2,2,2,2,2,2,2, 2,2,2,2,2,2,2,2];
            capturingPits = [];
            p1CornerCapturesCount = 0;
            p2CornerCapturesCount = 0;
            hideFinger();
            document.getElementById('status-bar').innerText = "Board reset with 2 seeds per pit. Tap any pit to play!";
            renderBoard();
          }

          renderBoard();
        </script>
        </body>
        </html>
        """
        st.components.v1.html(omweso_front_back_html, height=580, scrolling=False)

    with tab_puzzle:
        tier = st.selectbox("Select NCDC Level", list(OMWESO_PUZZLES.keys()))
        pz = OMWESO_PUZZLES[tier]
        st.caption(f"NCDC Strand: {pz['ncdc_strand']}")
        choice = st.radio(pz["question"], pz["options"], index=None, key=f"pz_{tier}")
        if st.button("Check Puzzle Answer"):
            if choice == pz["answer"]:
                st.success(f"Correct! {pz['explanation']}")
            elif choice is not None:
                st.error(f"Not quite. {pz['explanation']}")
            else:
                st.warning("Select an answer first.")

elif page == "NCDC Official Syllabus Reference":
    st.title("📖 Complete NCDC Primary Curriculum Reference")
    st.caption("National Curriculum Development Centre (Uganda) Official Framework (P1–P7)")
    
    cycle_sel = st.selectbox("1. Select Curriculum Cycle", list(NCDC_OFFICIAL_FRAMEWORK.keys()))
    class_sel = st.selectbox("2. Select Class Level", list(NCDC_OFFICIAL_FRAMEWORK[cycle_sel].keys()))
    
    class_subjects = NCDC_OFFICIAL_FRAMEWORK[cycle_sel][class_sel]
    subject_sel = st.selectbox("3. Select Subject / Learning Area", list(class_subjects.keys()))
    
    st.markdown("---")
    st.subheader(f"Official Syllabus Details: {class_sel} — {subject_sel}")
    
    sub_data = class_subjects[subject_sel]
    for key, val in sub_data.items():
        st.markdown(f"### **{key}**")
        if isinstance(val, list):
            for item in val:
                st.write(f"- {item}")
        else:
            st.write(val)

elif page == "Teacher Dashboard":
    st.title("Teacher Dashboard")
    st.caption("Protected Teacher Portal for Monitoring Student Competencies")
    
    if not st.session_state.dashboard_unlocked:
        pwd = st.text_input("Enter Teacher Password", type="password")
        if st.button("Login"):
            if pwd == TEACHER_PASSWORD:
                st.session_state.dashboard_unlocked = True
                st.success("Unlocked successfully!")
                st.rerun()
            else:
                st.error("Incorrect password.")
    else:
        st.success("Dashboard unlocked.")
        if st.button("Lock Dashboard"):
            st.session_state.dashboard_unlocked = False
            st.rerun()
            
        results = st.session_state.results
        if not results:
            st.info("No results recorded yet.")
        else:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            st.download_button(
                label="Download Results CSV",
                data=df.to_csv(index=False).encode('utf-8'),
                file_name="ilearn_uganda_results.csv",
                mime="text/csv",
            )
