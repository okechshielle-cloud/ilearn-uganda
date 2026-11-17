import streamlit as st
import pandas as pd
import os
import requests
import json

st.set_page_config(page_title="iLearn-Uganda", layout="centered")

TEACHER_PASSWORD = st.secrets.get("TEACHER_PASSWORD", "iLearnUganda123")
CSV_FILE = "results.csv"
SHEET_URL = st.secrets.get("SHEET_URL", "")

# Comprehensive NCDC Curriculum Dataset with Topics, Subtopics, Learning Aids, Life Skills, and Values
NCDC_CURRICULUM = {
    "Lower Primary (Cycle 1: Thematic Approach P1-P3)": {
        "P1": {
            "Term 1: Our School / Our Home": {
                "Topics": "1. Our School, 2. Our Home and Community",
                "Subtopics": "School environment, classroom objects, school rules, family members, roles of people at home, personal hygiene practices.",
                "Learning Aids": "Chart of classroom objects, realia (pencils, books), charts showing family members, cleaning tools (brooms, water basins).",
                "Life Skills": "Effective communication, self-awareness, empathy, cooperation.",
                "Values": "Respect, obedience, love, cleanliness, responsibility."
            },
            "Term 2: Our Community / Human Body": {
                "Topics": "1. Human Body and Health, 2. Community Helpers",
                "Subtopics": "Body parts and senses, keeping our bodies clean, common diseases, neighbors, local authority roles, market places.",
                "Learning Aids": "Human body charts, mirrors, soap, clean water, flashcards of community helpers (teachers, nurses, police).",
                "Life Skills": "Critical thinking, problem solving, interpersonal relationships, coping with emotions.",
                "Values": "Appreciation, hygiene, helpfulness, care for others."
            },
            "Term 3: Plants, Animals & Environment": {
                "Topics": "1. Plants in Our Environment, 2. Animals and Weather",
                "Subtopics": "Parts of plants, uses of plants, domestic and wild animals, weather changes, safe water sources, road safety.",
                "Learning Aids": "Real plant leaves/roots, pictures of domestic and wild animals, weather charts, flashcards on road signs.",
                "Life Skills": "Decision making, environmental observation, creative thinking.",
                "Values": "Environmental conservation, kindness to animals, safety consciousness."
            }
        },
        "P2": {
            "Term 1: Food and Nutrition": {
                "Topics": "1. Sources of Food, 2. Food Hygiene and Safety",
                "Subtopics": "Types of food (local food groups), food storage, kitchen hygiene, clean and safe drinking water, signs of malnutrition.",
                "Learning Aids": "Real food items (maize, cassava, beans), food group charts, clean containers for safe drinking water.",
                "Life Skills": "Critical thinking about nutrition, decision making, health management.",
                "Values": "Appreciation of food, hygiene, honesty, sharing."
            },
            "Term 2: Transport & Communication": {
                "Topics": "1. Means of Transport, 2. Communication Systems & Weather",
                "Subtopics": "Road, water, and air transport; safety on the road; traditional and modern communication methods; weather conditions.",
                "Learning Aids": "Toy cars, model boats, pictures of aeroplanes, old radios, mobile phone mockups, rain gauges.",
                "Life Skills": "Effective communication, creative thinking, safety awareness.",
                "Values": "Caution, patience, appreciation of technology."
            },
            "Term 3: Peace, Security & Changes": {
                "Topics": "1. Peace and Security in the Community, 2. Changes in the Environment",
                "Subtopics": "Promoting peace, resolving conflicts, child rights and responsibilities, environmental changes (deforestation, soil erosion).",
                "Learning Aids": "Storybooks on peace, pictures showing tree planting, charts on children's rights.",
                "Life Skills": "Conflict resolution, negotiation, empathy, civic responsibility.",
                "Values": "Peacefulness, tolerance, justice, love for one another."
            }
        },
        "P3": {
            "Term 1: Our Sub-county / Division": {
                "Topics": "1. Physical Features, 2. Location and Landmarks",
                "Subtopics": "Locating the sub-county, hills, valleys, swamps, rivers, economic activities, administrative units.",
                "Learning Aids": "Local sketch maps, physical feature charts, clay models of hills and valleys.",
                "Life Skills": "Spatial orientation, environmental awareness, research skills.",
                "Values": "Patriotism, cooperation, community pride."
            },
            "Term 2: Energy, Water and Sanitation": {
                "Topics": "1. Sources of Energy, 2. Water and Environmental Sanitation",
                "Subtopics": "Sources of light/heat/sound, saving energy, safe water chain, proper disposal of refuse, vector control.",
                "Learning Aids": "Solar panels, firewood samples, charcoal stoves, clean jerrycans, tippy-taps.",
                "Life Skills": "Resource conservation, problem-solving, critical thinking.",
                "Values": "Responsibility, resourcefulness, cleanliness."
            },
            "Term 3: Transition Foundations": {
                "Topics": "1. Transition Foundations, 2. Creative Arts & Crafts",
                "Subtopics": "Consolidation of lower primary literacy/numeracy, transition to English medium, local art, physical education coordination.",
                "Learning Aids": "Bilingual storybooks, transition assessment cards, local musical instruments, skipping ropes.",
                "Life Skills": "Adaptability, self-confidence, teamwork, physical coordination.",
                "Values": "Perseverance, creativity, sportsmanship."
            }
        }
    },
    "Upper Primary (Cycle 2 & 3: Subject-Based P4-P7)": {
        "P4": {
            "English": {
                "Topics": "1. School and Community, 2. Weather and Transport, 3. Health and Environment",
                "Subtopics": "Nouns, pronouns, present simple tense, guided compositions, informal letters, punctuation marks.",
                "Learning Aids": "Grammar flashcards, sample friendly letters, vocabulary charts.",
                "Life Skills": "Written communication, creative writing, active listening.",
                "Values": "Accuracy, neatness, respect in communication."
            },
            "Mathematics": {
                "Topics": "1. Whole Numbers & Place Values, 2. Fractions and Decimals, 3. Measurement and Geometry",
                "Subtopics": "Operations up to ten thousands, equivalent fractions, metric conversions, perimeter and area, basic angles.",
                "Learning Aids": "Abacus, base-ten blocks, fraction cut-out charts, rulers, protractors.",
                "Life Skills": "Logical reasoning, problem-solving, numerical estimation.",
                "Values": "Precision, honesty in calculation, patience."
            },
            "Integrated Science": {
                "Topics": "1. Plant Anatomy & Crops, 2. The Human Digestive System, 3. Weather Instruments",
                "Subtopics": "Roots, stems, leaves, flowers, crop growing practices, human teeth structure, deficiency diseases, rain gauges.",
                "Learning Aids": "Actual flowering plants, model of human teeth, rain gauge model, thermometer.",
                "Life Skills": "Scientific inquiry, observation, data recording, health hygiene management.",
                "Values": "Curiosity, environmental stewardship, self-care."
            },
            "Social Studies": {
                "Topics": "1. Map Reading, 2. Physical Geography of District, 3. District Governance",
                "Subtopics": "Compass directions, scale and keys, relief features, vegetation, climate, district leadership structures.",
                "Learning Aids": "Topographical maps, magnetic compasses, district administrative charts.",
                "Life Skills": "Map reading, critical thinking about governance, civic awareness.",
                "Values": "Civic responsibility, respect for leaders, national unity."
            },
            "Religious Education": {
                "Topics": "1. Sacred Scriptures (Bible/Quran), 2. Moral Decision Making",
                "Subtopics": "Foundational covenants, prophetic traditions, personal integrity, honesty, community service.",
                "Learning Aids": "Bibles, Qurans, moral dilemma scenario cards.",
                "Life Skills": "Moral reasoning, decision-making, empathy.",
                "Values": "Integrity, truthfulness, reverence, kindness."
            },
            "Kiswahili": {
                "Topics": "1. Matamshi na Herufi, 2. Ngeli za Nomino (M-WA, KI-VI)",
                "Subtopics": "Phonetic spelling, greetings, vocabulary for home/school, basic present tense (na-), short reading passages.",
                "Learning Aids": "Kiswahili vocabulary charts, conversational audio prompts.",
                "Life Skills": "Linguistic adaptability, cross-cultural communication.",
                "Values": "Regional integration appreciation, respect for languages."
            },
            "Creative Arts & PE": {
                "Topics": "1. Visual Arts & Craft, 2. Music, Dance & Drama, 3. Physical Education",
                "Subtopics": "Color mixing, line and texture, folk songs, traditional dance steps, major sports rules (football/netball).",
                "Learning Aids": "Watercolors, drawing books, footballs, netballs, local drums.",
                "Life Skills": "Creative expression, motor skill coordination, teamwork.",
                "Values": "Appreciation of culture, sportsmanship, discipline."
            }
        },
        "P5": {
            "English": {
                "Topics": "1. Advanced Tenses & Conjunctions, 2. Poetry and Literature Analysis, 3. Speeches & Debates",
                "Subtopics": "Relative clauses, comparative adjectives, poem interpretation, summary writing, formal speeches.",
                "Learning Aids": "Anthologies of poems, debate motion cards, structural grammar charts.",
                "Life Skills": "Public speaking, critical literary analysis, persuasive communication.",
                "Values": "Confidence, open-mindedness, respect for opposing views."
            },
            "Mathematics": {
                "Topics": "1. Integers & Percentages, 2. Area, Volume and Capacity, 3. Algebra & Statistics",
                "Subtopics": "Operations with negative numbers, percentage calculations, volume of cuboids, basic algebraic expressions, bar graphs.",
                "Learning Aids": "Integer number lines, 3D rectangular blocks, graph paper, mathematical sets.",
                "Life Skills": "Analytical thinking, financial calculation, data interpretation.",
                "Values": "Logical discipline, perseverance."
            },
            "Integrated Science": {
                "Topics": "1. States of Matter & Heat Transfer, 2. Human Circulatory & Respiratory Systems, 3. Primary Health Care",
                "Subtopics": "Conduction, convection, radiation, blood circulation, lung functions, immunization, water-borne diseases.",
                "Learning Aids": "Beakers, burners, charts of the heart and lungs, vaccination schedules.",
                "Life Skills": "Experimental design, health safety evaluation, critical thinking.",
                "Values": "Health consciousness, scientific rigor, responsibility."
            },
            "Social Studies": {
                "Topics": "1. Physical Geography of Uganda, 2. Pre-colonial Uganda & Kingdoms, 3. Governance and Constitution",
                "Subtopics": "Relief zones, lakes, ethnic migrations, early African kingdoms, foreign influence, the Ugandan constitution.",
                "Learning Aids": "Relief map of Uganda, historical timeline charts, copy of the National Constitution.",
                "Life Skills": "Historical analysis, civic participation, critical evaluation.",
                "Values": "National heritage appreciation, patriotism, tolerance."
            },
            "Religious Education": {
                "Topics": "1. Life and Teachings of Jesus Christ / Prophet Muhammad, 2. Worship and Spiritual Discipline",
                "Subtopics": "Justice, compassion, pillars of faith, sacraments, dealing with peer pressure.",
                "Learning Aids": "Scriptural passages, reflective journals, peer pressure case studies.",
                "Life Skills": "Spiritual resilience, assertiveness against peer pressure, ethical decision-making.",
                "Values": "Compassion, justice, piety, steadfastness."
            },
            "Kiswahili": {
                "Topics": "1. Nyakati (Nyakati zilizopita, za sasa, na zijazo), 2. Msamiati wa Masoko na Usafiri",
                "Subtopics": "Past (li-), present (na-), and future (ta-) tenses; market transactions; travel vocabulary; role-plays.",
                "Learning Aids": "Market dialogue scripts, tense conjugation tables.",
                "Life Skills": "Practical language application, negotiation skills.",
                "Values": "Cultural integration, confidence."
            },
            "Creative Arts & PE": {
                "Topics": "1. Intermediate Sports Tactics, 2. Functional Craft & Posters, 3. Traditional Instruments",
                "Subtopics": "Sports endurance, sportsmanship, sign-making, pottery, local musical instruments (drums, xylophones).",
                "Learning Aids": "Local clay, poster paints, traditional instruments (endingidi, adungu).",
                "Life Skills": "Artistic design, physical endurance, teamwork.",
                "Values": "Cultural preservation, perseverance, collaboration."
            }
        },
        "P6": {
            "English": {
                "Topics": "1. Active and Passive Voice, 2. Direct and Indirect Speech, 3. Persuasive Essays & Reports",
                "Subtopics": "Conditional clauses, formal letters, minutes of meetings, report writing, advanced inference.",
                "Learning Aids": "Sample meeting minutes, formal letter templates, advanced grammar workbooks.",
                "Life Skills": "Technical writing, formal communication, critical inference.",
                "Values": "Professionalism, integrity in reporting, thoroughness."
            },
            "Mathematics": {
                "Topics": "1. Proportions, Speed, Distance & Time, 2. Simple Interest, 3. Advanced Data Handling",
                "Subtopics": "Speed formulas, financial literacy, pie charts, mean, median, mode, probability foundations.",
                "Learning Aids": "Stopwatches, financial interest tables, statistical survey data charts.",
                "Life Skills": "Problem-solving under time constraints, financial literacy, statistical analysis.",
                "Values": "Prudence, accuracy, analytical honesty."
            },
            "Integrated Science": {
                "Topics": "1. Electricity & Magnetism, 2. Simple Machines & Friction, 3. Mammalian Reproduction & Immunity",
                "Subtopics": "Circuits, conductors, levers, pulleys, reproductive health, STIs/HIV prevention, human immunity systems.",
                "Learning Aids": "Wires, dry cells, bulbs, levers, pulleys, HIV prevention awareness charts.",
                "Life Skills": "Technical problem-solving, self-protection, health counseling awareness.",
                "Values": "Safety mindfulness, responsibility, empathy for the sick."
            },
            "Social Studies": {
                "Topics": "1. East African Physical Resources, 2. Colonial Rule & Independence Struggles",
                "Subtopics": "Mining, agriculture, European scramble, partition of East Africa, independence movements, nationalism.",
                "Learning Aids": "Map of East Africa, historical portraits of independence heroes, resource distribution charts.",
                "Life Skills": "Historical synthesis, geopolitical awareness, critical thinking.",
                "Values": "Pan-African solidarity, patriotism, appreciation of freedom."
            },
            "Religious Education": {
                "Topics": "1. Faith in Action & Leadership, 2. Family Values & Work Ethics, 3. Conflict Resolution",
                "Subtopics": "Stewardship of resources, marriage values, interfaith harmony, reconciliation processes.",
                "Learning Aids": "Case studies on community leadership, family code guidelines.",
                "Life Skills": "Leadership ethics, conflict mediation, responsible stewardship.",
                "Values": "Stewardship, accountability, peace-building."
            },
            "Kiswahili": {
                "Topics": "1. Ngeli za Ziada na Vivumishi, 2. Ufupisho wa Hadithi",
                "Subtopics": "Adjectives, prepositions, negation forms, reading and summarizing dialogues and short stories.",
                "Learning Aids": "Kiswahili story booklets, grammar exercise cards.",
                "Life Skills": "Text summarization, advanced linguistic comprehension.",
                "Values": "Diligence, linguistic pride."
            },
            "Creative Arts & PE": {
                "Topics": "1. Athletics and Safety Rules, 2. Advanced Sculpture, 3. Drama for Civic Education",
                "Subtopics": "Track events, first aid procedures, papier-mâché, textile design, directing issue-based drama pieces.",
                "Learning Aids": "First aid kits, papier-mâché materials, script excerpts for civic drama.",
                "Life Skills": "Emergency response awareness, dramatic direction, advanced motor coordination.",
                "Values": "Safety consciousness, civic responsibility, aesthetic appreciation."
            }
        },
        "P7": {
            "English": {
                "Topics": "1. Comprehensive Exam Revision, 2. Advanced Vocabulary & Idioms, 3. Timed Composition Editing",
                "Subtopics": "Synonyms, antonyms, phrasal verbs, summary compression, rapid comprehension for PLE standards.",
                "Learning Aids": "PLE past paper booklets, idiom dictionaries, timed practice sheets.",
                "Life Skills": "Time management, stress management, high-stakes exam strategy, critical editing.",
                "Values": "Resilience, self-discipline, academic honesty."
            },
            "Mathematics": {
                "Topics": "1. Advanced Geometry & Sets, 2. Simultaneous Equations, 3. Comprehensive PLE Past Paper Drill",
                "Subtopics": "Circle theorems, Venn diagrams, algebraic word problems, profit and loss calculations, matrix foundations.",
                "Learning Aids": "Geometrical instruments, sets visualizer, past paper compilations.",
                "Life Skills": "Complex problem-solving, strategic thinking, perseverance.",
                "Values": "Excellence, precision, tenacity."
            },
            "Integrated Science": {
                "Topics": "1. Human Excretory & Nervous Systems, 2. Agricultural Science & Livestock, 3. Environmental Management",
                "Subtopics": "Kidneys, skin, brain reflex actions, poultry management, soil conservation, pollution control for PLE.",
                "Learning Aids": "Nervous system anatomy charts, livestock feed samples, environmental conservation models.",
                "Life Skills": "Scientific synthesis, agricultural entrepreneurship planning, ecological conservation.",
                "Values": "Environmental accountability, respect for biological life, diligence."
            },
            "Social Studies": {
                "Topics": "1. Continental Geography of Africa, 2. Pan-Africanism & International Organizations, 3. Global Trade & Challenges",
                "Subtopics": "African regions, AU, UN, Common Wealth, economic integration, population challenges, PLE mapping.",
                "Learning Aids": "Wall map of Africa, UN charter summaries, trade flow diagrams.",
                "Life Skills": "Global citizenship awareness, geopolitical analysis, international cooperation understanding.",
                "Values": "Global empathy, international peace advocacy, civic pride."
            },
            "Religious Education": {
                "Topics": "1. Moral Theology & Ethics, 2. Human Dignity & Social Responsibility, 3. PLE Revision Framework",
                "Subtopics": "Comprehensive scripture application, ethical responses to modern dilemmas, spiritual preparedness.",
                "Learning Aids": "Thematic revision guides, ethical case study briefs.",
                "Life Skills": "Ethical discernment, holistic self-evaluation, principled decision-making.",
                "Values": "Ultimate moral integrity, spiritual maturity, human dignity advocacy."
            },
            "Kiswahili": {
                "Topics": "1. Upigaji Chapa na Barua Rasmi, 2. Ufasaha wa Lugha na Mawasiliano",
                "Subtopics": "Formal letter writing in Kiswahili, conversational fluency, advanced sentence structuring for secondary transition.",
                "Learning Aids": "Formal letter templates in Kiswahili, conversational evaluation rubrics.",
                "Life Skills": "Formal administrative writing fluency, bilingual professional readiness.",
                "Values": "Excellence in regional communication, respect for linguistic standards."
            },
            "Creative Arts & PE": {
                "Topics": "1. Leadership & Fitness Management, 2. Entrepreneurial Craft Production, 3. Cultural Competency",
                "Subtopics": "Recreational sport management, marketing local crafts, comprehensive practical art exhibitions for PLE.",
                "Learning Aids": "Sports officiating equipment, craft exhibition display boards.",
                "Life Skills": "Sports leadership, entrepreneurial marketing, event organization.",
                "Values": "Enterprise, cultural leadership, collaborative achievement."
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
    st.caption("Integrated Learning Environment — Complete NCDC Framework with Topics, Subtopics, Learning Aids, Life Skills & Values")
    st.write("Explore complete syllabus structures mirroring NCDC frameworks: Lower Primary Thematic Approach (P1–P3) and Upper Primary Subject-Based Structure (P4–P7).")
    
    cycle_choice = st.selectbox("Select Cycle", list(NCDC_CURRICULUM.keys()))
    
    if "Thematic" in cycle_choice:
        selected_class = st.selectbox("Select Class", ["P1", "P2", "P3"])
        st.markdown("---")
        st.subheader(f"Thematic Curriculum Breakdown for {selected_class}")
        terms_data = NCDC_CURRICULUM[cycle_choice].get(selected_class, {})
        for term, details in terms_data.items():
            st.markdown(f"### 🗓️ {term}")
            if isinstance(details, dict):
                st.markdown(f"**Topics Covered:** {details.get('Topics', '')}")
                st.markdown(f"**Subtopics:** {details.get('Subtopics', '')}")
                st.markdown(f"**Learning Aids / Instructional Materials:** {details.get('Learning Aids', '')}")
                st.markdown(f"**Life Skills Acquired:** {details.get('Life Skills', '')}")
                st.markdown(f"**Core Values Inculcated:** {details.get('Values', '')}")
            else:
                st.info(details)
            st.markdown("---")
    else:
        selected_class = st.selectbox("Select Class", ["P4", "P5", "P6", "P7"])
        st.markdown("---")
        st.subheader(f"Subject-Based Breakdown for {selected_class}")
        subjects_data = NCDC_CURRICULUM[cycle_choice].get(selected_class, {})
        for subj, details in subjects_data.items():
            st.markdown(f"### 📘 {subj}")
            if isinstance(details, dict):
                st.markdown(f"**Topics Covered:** {details.get('Topics', '')}")
                st.markdown(f"**Subtopics:** {details.get('Subtopics', '')}")
                st.markdown(f"**Learning Aids / Instructional Materials:** {details.get('Learning Aids', '')}")
                st.markdown(f"**Life Skills Acquired:** {details.get('Life Skills', '')}")
                st.markdown(f"**Core Values Inculcated:** {details.get('Values', '')}")
            else:
                st.info(details)
            st.markdown("---")

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
