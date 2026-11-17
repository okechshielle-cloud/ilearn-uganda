import streamlit as st
import pandas as pd
import os
import requests
import json

st.set_page_config(page_title="LearnEasy", layout="centered")

TEACHER_PASSWORD = st.secrets.get("TEACHER_PASSWORD", "LearnEasy123")
CSV_FILE = "results.csv"
SHEET_URL = st.secrets.get("SHEET_URL", "")

# Complete Integrated NCDC Curriculum Dataset (P1-P7 across all components)
NCDC_CURRICULUM = {
    "English": {
        "P1": {
            "term_1": "Develop basic listening and speaking skills using simple greetings, commands, and classroom vocabulary.",
            "term_2": "Identify common objects, family members, and body parts in spoken English; begin recognizing letter sounds.",
            "term_3": "Construct simple oral sentences and read basic two- and three-letter words."
        },
        "P2": {
            "term_1": "Read short, simple sentences and build vocabulary around food, home, and school routines.",
            "term_2": "Use basic prepositions, plurals, and simple present tense in oral and written descriptions of weather and transport.",
            "term_3": "Write short guided sentences and comprehend brief, illustrated stories."
        },
        "P3": {
            "term_1": "Read and comprehend short paragraphs; apply basic punctuation (capital letters, full stops, question marks).",
            "term_2": "Expand vocabulary on community, health, and environment; write simple descriptive sentences.",
            "term_3": "Demonstrate foundational reading fluency and written grammar readiness for upper-primary English-medium instruction."
        },
        "P4": {
            "term_1": "Transition fully to English as the medium of instruction; master nouns, pronouns, and simple tenses.",
            "term_2": "Construct coherent paragraphs, guided compositions, and informal/formal letters.",
            "term_3": "Comprehend longer passages, extract main ideas, and use adjectives and adverbs accurately."
        },
        "P5": {
            "term_1": "Apply complex tenses, conjunctions, and relative clauses in structured composition writing.",
            "term_2": "Analyze short stories and poems for vocabulary, tone, and comprehension.",
            "term_3": "Engage in structured debates, formal speeches, and summary writing."
        },
        "P6": {
            "term_1": "Master active and passive voice, direct and indirect speech, and conditional sentences.",
            "term_2": "Write persuasive essays, formal reports, and functional documents (notices, minutes).",
            "term_3": "Demonstrate advanced reading comprehension and critical inference across varied texts."
        },
        "P7": {
            "term_1": "Consolidate all primary grammar, vocabulary, and comprehension skills for national assessment standards.",
            "term_2": "Refine analytical writing, editing, and rapid comprehension under timed conditions.",
            "term_3": "Demonstrate full linguistic competence for Primary Leaving Examination (PLE) and secondary school entry."
        }
    },
    "Mathematics": {
        "P1": {
            "term_1": "Sort, match, count, and write whole numbers from 1 to 10 using concrete objects.",
            "term_2": "Perform basic addition and subtraction of numbers up to 20; identify basic 2D shapes.",
            "term_3": "Count up to 99, compare lengths and weights using non-standard units, and recognize local currency notes/coins."
        },
        "P2": {
            "term_1": "Understand place value (tens and ones) and perform addition and subtraction up to 50 with regrouping.",
            "term_2": "Introduce basic multiplication as repeated addition and division as equal sharing.",
            "term_3": "Solve practical word problems involving length, mass, capacity, and telling time by the hour/half-hour."
        },
        "P3": {
            "term_1": "Work with numbers up to 1,000; master multiplication tables and basic division facts.",
            "term_2": "Introduce simple fractions (halves, quarters, thirds) and standard metric units (meters, kilograms, liters).",
            "term_3": "Apply arithmetic operations to money transactions, calendars, and basic pictographs."
        },
        "P4": {
            "term_1": "Master place values up to ten thousands; perform operations with equivalent fractions and decimals.",
            "term_2": "Calculate perimeter and area of simple rectangles and squares; convert standard metric units.",
            "term_3": "Solve multi-step word problems involving money, time intervals, and basic geometric angles."
        },
        "P5": {
            "term_1": "Perform operations with integers, decimals, percentages, and basic algebraic expressions.",
            "term_2": "Calculate area, perimeter, and volume of standard shapes; interpret bar graphs and line graphs.",
            "term_3": "Apply ratios, averages, and geometric construction skills using a compass and protractor."
        },
        "P6": {
            "term_1": "Solve problems involving proportions, speed, distance, time, and simple interest.",
            "term_2": "Master algebraic equations, inequalities, and advanced data interpretation (pie charts, mean, median, mode).",
            "term_3": "Apply geometry theorems (angles on parallel lines, triangles, circles) and scale drawing."
        },
        "P7": {
            "term_1": "Consolidate arithmetic, algebra, geometry, and set theory across upper-primary competencies.",
            "term_2": "Solve complex, multi-concept application problems and interpret statistical datasets.",
            "term_3": "Demonstrate comprehensive mathematical problem-solving readiness for PLE."
        }
    },
    "Integrated Science": {
        "P1": {
            "term_1": "Identify parts of the human body and practice basic personal hygiene (handwashing, dental care).",
            "term_2": "Recognize common foods, clean water sources, and basic sanitation habits at home and school.",
            "term_3": "Observe and name common local plants, domestic animals, and basic weather conditions."
        },
        "P2": {
            "term_1": "Classify foods into basic groups and understand safe food handling and storage.",
            "term_2": "Explore basic properties of air, water, and soil through simple observation.",
            "term_3": "Identify common accidents at home/school and practice basic safety and first-aid awareness."
        },
        "P3": {
            "term_1": "Investigate soil types, plant growth requirements, and local ecosystems.",
            "term_2": "Identify common vectors, communicable diseases, and methods of disease prevention.",
            "term_3": "Explore sources of light, heat, and sound energy in the immediate environment."
        },
        "P4": {
            "term_1": "Examine plant anatomy (roots, stems, leaves, flowers) and crop growing practices.",
            "term_2": "Study the human digestive system, teeth structure, and nutritional deficiency diseases.",
            "term_3": "Investigate weather elements, measurement instruments, and basic environmental conservation."
        },
        "P5": {
            "term_1": "Explore states of matter, heat transfer, and basic poultry/livestock management.",
            "term_2": "Study human body systems (circulatory and respiratory) and primary health care practices.",
            "term_3": "Investigate soil conservation, immunization, and prevention of common tropical diseases."
        },
        "P6": {
            "term_1": "Examine electricity, magnetism, simple machines, and friction.",
            "term_2": "Study mammalian reproduction, adolescence, reproductive health, and immunity.",
            "term_3": "Analyze sound and light energy, water purification, and environmental degradation."
        },
        "P7": {
            "term_1": "Consolidate human anatomy (excretory, nervous, muscular-skeletal systems) and energy resources.",
            "term_2": "Apply scientific inquiry to agriculture, population health, and sustainable resource management.",
            "term_3": "Demonstrate mastery of practical science concepts and health education for PLE."
        }
    },
    "Social Studies": {
        "P1": {
            "term_1": "Identify family members, home roles, and school rules and leadership.",
            "term_2": "Recognize immediate neighborhood landmarks, community helpers, and basic needs.",
            "term_3": "Practice peaceful coexistence, sharing, and respect for elders and peers."
        },
        "P2": {
            "term_1": "Describe local community services (health centers, markets, places of worship).",
            "term_2": "Identify local means of transport and communication and their importance.",
            "term_3": "Understand basic child rights, responsibilities, and community safety rules."
        },
        "P3": {
            "term_1": "Locate physical features, administrative units, and economic activities in the local sub-county/division.",
            "term_2": "Examine cultural traditions, customs, and basic resource management in the community.",
            "term_3": "Understand local leadership structures and civic responsibilities."
        },
        "P4": {
            "term_1": "Use map-reading skills (compass direction, key, scale) to study the local district.",
            "term_2": "Examine the physical geography, climate, vegetation, and early history of the district.",
            "term_3": "Analyze social services, district governance, and economic activities."
        },
        "P5": {
            "term_1": "Study the physical geography, climate, and vegetation zones of Uganda.",
            "term_2": "Examine pre-colonial Uganda, ethnic migrations, early kingdoms, and foreign influence.",
            "term_3": "Analyze Uganda's governance, constitution, citizenship, and post-independence development."
        },
        "P6": {
            "term_1": "Examine the physical geography, resources, and economic development of East Africa.",
            "term_2": "Analyze colonial administration, resistance movements, and struggles for independence in East Africa.",
            "term_3": "Evaluate regional cooperation (East African Community), trade, and environmental management."
        },
        "P7": {
            "term_1": "Study the physical geography, climate, and major economic regions of Africa.",
            "term_2": "Analyze Pan-Africanism, decolonization, governance challenges, and international organizations (AU, UN).",
            "term_3": "Synthesize geographical, historical, and civic competencies for PLE."
        }
    },
    "Religious Education": {
        "P1": {
            "term_1": "Recognize God/Allah as the Creator and appreciate the gift of life, family, and nature.",
            "term_2": "Practice basic values of love, obedience, honesty, and respect at home and school.",
            "term_3": "Participate in simple prayers, songs, and stories about kindness and sharing."
        },
        "P2": {
            "term_1": "Understand the importance of worship, prayer, and sacred spaces (Church/Mosque).",
            "term_2": "Learn foundational stories of faith, forgiveness, and helping those in need.",
            "term_3": "Demonstrate fairness, truthfulness, and peaceful play with peers."
        },
        "P3": {
            "term_1": "Explore major religious festivals, traditions, and community celebrations.",
            "term_2": "Understand moral responsibility, stewardship of the environment, and care for the vulnerable.",
            "term_3": "Identify key religious leaders and early foundational teachings (CRE/IRE)."
        },
        "P4": {
            "term_1": "Study sacred scriptures (Bible/Quran) and foundational covenants/prophetic traditions.",
            "term_2": "Examine moral decision-making, personal integrity, and service to the community.",
            "term_3": "Appreciate religious diversity and practice tolerance and peaceful coexistence."
        },
        "P5": {
            "term_1": "Analyze the life and teachings of Jesus Christ (CRE) or Prophet Muhammad (IRE) regarding justice and compassion.",
            "term_2": "Explore worship practices, sacraments/pillars of faith, and spiritual discipline.",
            "term_3": "Apply ethical principles to contemporary issues such as peer pressure and honesty."
        },
        "P6": {
            "term_1": "Examine faith in action, leadership, and social responsibility in the modern community.",
            "term_2": "Study marriage, family values, work ethics, and stewardship of resources from a religious perspective.",
            "term_3": "Analyze conflict resolution, reconciliation, and interfaith harmony."
        },
        "P7": {
            "term_1": "Consolidate scriptural knowledge, moral theology/ethics, and civic responsibility.",
            "term_2": "Reflect on personal values, human dignity, and ethical responses to societal challenges.",
            "term_3": "Demonstrate comprehensive mastery of CRE/IRE competencies for PLE."
        }
    },
    "Kiswahili": {
        "P1": {
            "term_1": "Introduced orally through songs, rhymes, and basic greetings (e.g., Shikamoo, Habari).",
            "term_2": "Recognize and respond to simple classroom instructions and polite expressions.",
            "term_3": "Name common family members, numbers 1-10, and everyday classroom objects orally."
        },
        "P2": {
            "term_1": "Expand oral vocabulary for body parts, domestic animals, and basic foods.",
            "term_2": "Form simple two- and three-word oral phrases using basic nouns and verbs.",
            "term_3": "Participate in short conversational dialogues and action songs."
        },
        "P3": {
            "term_1": "Transition from oral listening/speaking to recognizing Kiswahili vowels, syllables, and simple words.",
            "term_2": "Read and write basic words and short simple sentences about home and school.",
            "term_3": "Count up to 50 and describe days of the week and simple daily activities."
        },
        "P4": {
            "term_1": "Master Kiswahili phonetic spelling, noun classes (M-WA, KI-VI), and basic present tense (na-).",
            "term_2": "Read short graded passages and answer basic comprehension questions.",
            "term_3": "Write simple guided sentences describing people, places, and weather."
        },
        "P5": {
            "term_1": "Apply past (li-), present (na-), and future (ta-) tenses in spoken and written sentences.",
            "term_2": "Expand vocabulary on travel, markets, health, and East African cultural ties.",
            "term_3": "Write short paragraphs and engage in structured conversational role-plays."
        },
        "P6": {
            "term_1": "Master additional noun classes, adjectives, prepositions, and negation forms.",
            "term_2": "Read and summarize short stories, dialogues, and informational texts.",
            "term_3": "Write informal letters and descriptive compositions using accurate grammar."
        },
        "P7": {
            "term_1": "Consolidate upper-primary grammar, vocabulary, and comprehension across thematic topics.",
            "term_2": "Demonstrate fluent oral communication and structured essay writing for regional integration.",
            "term_3": "Exhibit functional proficiency in listening, speaking, reading, and writing Kiswahili."
        }
    },
    "Creative Arts & PE": {
        "P1": {
            "term_1": "Develop gross motor skills through running, jumping, balancing, and rhythmic movement.",
            "term_2": "Explore basic drawing, coloring, modeling with clay, and singing simple local songs.",
            "term_3": "Participate in cooperative group games and simple traditional dances."
        },
        "P2": {
            "term_1": "Improve hand-eye coordination through ball games, skipping, and basic gymnastics.",
            "term_2": "Create simple crafts using locally available materials (fibers, paper, clay).",
            "term_3": "Perform rhythmic songs, storytelling, and dramatization."
        },
        "P3": {
            "term_1": "Practice foundational athletics, team game rules, and personal physical fitness.",
            "term_2": "Develop basic weaving, printing, and musical rhythm patterns.",
            "term_3": "Participate in school cultural performances and cooperative sports."
        },
        "P4": {
            "term_1": "Learn structured rules and techniques for major sports (football, netball, athletics).",
            "term_2": "Explore elements of visual art (line, shape, texture, color mixing) and basic music notation.",
            "term_3": "Perform traditional Ugandan dances and dramatic skits on social themes."
        },
        "P5": {
            "term_1": "Develop intermediate sports tactics, physical endurance, and sportsmanship.",
            "term_2": "Design functional crafts, posters, and decorative patterns using local resources.",
            "term_3": "Compose simple songs, play basic traditional instruments, and perform choral pieces."
        },
        "P6": {
            "term_1": "Refine athletic and team sport skills alongside first-aid and sports safety practices.",
            "term_2": "Produce advanced visual art projects, sculpture, and textile designs.",
            "term_3": "Direct and perform drama and music pieces addressing community health and civic values."
        },
        "P7": {
            "term_1": "Demonstrate leadership, teamwork, and fitness management in competitive and recreational sports.",
            "term_2": "Integrate entrepreneurial skills into craft production and performing arts.",
            "term_3": "Exhibit well-rounded physical, creative, and cultural competencies upon primary completion."
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

page = st.sidebar.selectbox("Go to", ["Take Quiz", "NCDC Curriculum Explorer", "Teacher Dashboard"])

if page == "Take Quiz":
    st.title("LearnEasy Quiz")
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
    st.title("📚 NCDC Primary Curriculum Explorer")
    st.write("Explore official learning outcomes from Primary One (P1) to Primary Seven (P7) across all core subjects, Kiswahili, Religious Education, and Creative Arts & PE.")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_subject = st.selectbox("Select Subject", list(NCDC_CURRICULUM.keys()))
    with col2:
        selected_class = st.selectbox("Select Class", [f"P{i}" for i in range(1, 8)])
        
    st.markdown("---")
    st.subheader(f"Learning Outcomes for {selected_subject} ({selected_class})")
    
    class_data = NCDC_CURRICULUM.get(selected_subject, {}).get(selected_class, {})
    if class_data:
        for term, outcome in class_data.items():
            term_name = term.replace("_", " ").title()
            st.markdown(f"**{term_name}:**")
            st.info(outcome)
    else:
        st.write("No outcomes found for this combination.")

elif page == "Teacher Dashboard":
    st.title("Teacher Dashboard - Locked")
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
        
    st.title("Teacher Dashboard")
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
            
    results = st.session_state
