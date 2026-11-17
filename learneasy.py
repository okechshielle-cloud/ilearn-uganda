import streamlit as st
import pandas as pd
import os
import requests
import json

st.set_page_config(page_title="iLearn-Uganda", layout="centered")

TEACHER_PASSWORD = st.secrets.get("TEACHER_PASSWORD", "iLearnUganda123")
CSV_FILE = "results.csv"
SHEET_URL = st.secrets.get("SHEET_URL", "")

# Comprehensive NCDC Curriculum Framework Overview
NCDC_CURRICULUM = {
    "Lower Primary (Cycle 1: Thematic Approach P1-P3)": {
        "P1": {
            "Term 1: Our School / Our Home": "Literacy in local language, early numeracy (1-10), personal hygiene, and family roles.",
            "Term 2: Our Community / Human Body": "Community helpers, health & sanitation habits, and addition/subtraction up to 20.",
            "Term 3: Plants, Animals & Environment": "Local plants/animals, simple reading sentences, and road/environmental safety."
        },
        "P2": {
            "Term 1: Food and Nutrition": "Food classification, hygiene, safe water, and addition/subtraction up to 50.",
            "Term 2: Transport & Communication": "Local transport/communication systems, weather changes, and multiplication/division basics.",
            "Term 3: Peace, Security & Changes": "Conflict resolution, child rights, and non-standard measurements."
        },
        "P3": {
            "Term 1: Our Sub-county / Division": "Sub-county physical features, landmarks, graded reading, and multiplication tables.",
            "Term 2: Energy, Water and Sanitation": "Sources of energy, safe water chain, vectors/diseases, and standard metric units.",
            "Term 3: Transition Foundations": "Transition from mother tongue to English-medium instruction and creative arts."
        }
    },
    "Upper Primary (Cycle 2 & 3: Subject-Based P4-P7)": {
        "P4": {
            "English": "Transition to English medium; nouns, pronouns, simple tenses, and guided compositions.",
            "Mathematics": "Place values up to 10,000, equivalent fractions, decimals, and metric units.",
            "Integrated Science": "Plant anatomy, crop growing, human digestive system, teeth, and weather instruments.",
            "Social Studies": "Map reading (compass, scale, key), district physical geography, and governance.",
            "Religious Education": "Sacred scriptures (Bible/Quran), covenants, and moral decision-making.",
            "Kiswahili": "Phonetic spelling, noun classes (M-WA, KI-VI), and basic present tense (na-).",
            "Creative Arts & PE": "Sports rules (football/netball), color mixing, folk songs, and traditional dance."
        },
        "P5": {
            "English": "Complex tenses, conjunctions, relative clauses, poetry analysis, and formal debates.",
            "Mathematics": "Integers, percentages, area, volume of cuboids, basic algebra, and bar graphs.",
            "Integrated Science": "States of matter, heat transfer, circulatory/respiratory systems, and primary health care.",
            "Social Studies": "Physical geography of Uganda, pre-colonial kingdoms, ethnic migrations, and constitution.",
            "Religious Education": "Life and teachings of Jesus Christ / Prophet Muhammad, worship, and peer pressure.",
            "Kiswahili": "Past (li-), present (na-), and future (ta-) tenses; market and travel vocabulary.",
            "Creative Arts & PE": "Sports tactics, sportsmanship, functional crafts, and traditional instruments."
        },
        "P6": {
            "English": "Active/passive voice, direct/indirect speech, conditional clauses, and formal report writing.",
            "Mathematics": "Proportions, speed/distance/time, simple interest, pie charts, and statistics.",
            "Integrated Science": "Electricity, magnetism, simple machines, friction, mammalian reproduction, and immunity.",
            "Social Studies": "East African resources, colonial administration, and independence struggles.",
            "Religious Education": "Faith in action, leadership, family values, work ethics, and reconciliation.",
            "Kiswahili": "Additional noun classes, adjectives, prepositions, negation, and story summaries.",
            "Creative Arts & PE": "Athletics, first-aid safety, sculpture, and civic-themed drama."
        },
        "P7": {
            "English": "Comprehensive grammar consolidation, idioms, summary compression, and PLE exam readiness.",
            "Mathematics": "Advanced geometry, circle theorems, sets (Venn diagrams), and simultaneous equations.",
            "Integrated Science": "Human excretory & nervous systems, livestock/poultry, and environmental management.",
            "Social Studies": "Geography of Africa, Pan-Africanism, AU, UN, and global economic integration.",
            "Religious Education": "Moral theology, human dignity, social responsibility, and spiritual maturity.",
            "Kiswahili": "Formal letter writing, conversational fluency, and secondary transition readiness.",
            "Creative Arts & PE": "Sports leadership, entrepreneurial crafts, and cultural exhibitions."
        }
    }
}

# Complete Class-by-Class Topical Breakdown (P1 to P7 across all subjects)
TOPICAL_BREAKDOWN = {
    "P1": {
        "Literacy & Language (Thematic)": {
            "Topic 1: Our School": {
                "Subtopics": "People in our school, things in our classroom, school rules, school buildings.",
                "Learning Outcome": "Learner identifies school members, names classroom objects, and follows basic instructions.",
                "Learning Aids": "Classroom realia, name flashcards, picture charts of school buildings.",
                "Life Skills": "Effective communication, self-awareness, interpersonal relationships.",
                "Values": "Obedience, respect, neatness."
            },
            "Topic 2: Our Home and Community": {
                "Subtopics": "Family members, roles of family members, basic needs, neighbors.",
                "Learning Outcome": "Learner describes family relationships and appreciates roles played at home.",
                "Learning Aids": "Family tree charts, storybooks, puppets.",
                "Life Skills": "Empathy, cooperation, sharing.",
                "Values": "Love, responsibility, unity."
            }
        },
        "Numeracy (Mathematics)": {
            "Topic 1: Sorting, Counting and Number Concepts (1-10)": {
                "Subtopics": "Sorting by color/size, counting concrete objects 1-10, writing number symbols.",
                "Learning Outcome": "Learner counts, matches, and writes whole numbers from 1 to 10 accurately.",
                "Learning Aids": "Bottle tops, sticks, stones, number cards, abacus.",
                "Life Skills": "Logical thinking, accuracy, decision making.",
                "Values": "Patience, orderliness, honesty."
            },
            "Topic 2: Addition and Subtraction up to 20": {
                "Subtopics": "Putting together (addition), taking away (subtraction), simple word problems.",
                "Learning Outcome": "Learner adds and subtracts single- and two-digit numbers up to 20.",
                "Learning Aids": "Counters, number lines, bundle of sticks.",
                "Life Skills": "Problem solving, critical thinking.",
                "Values": "Perseverance, accuracy."
            }
        },
        "Health, Science & Environment": {
            "Topic 1: The Human Body and Personal Hygiene": {
                "Subtopics": "External body parts, five senses, washing hands, brushing teeth.",
                "Learning Outcome": "Learner names body parts and demonstrates daily personal hygiene habits.",
                "Learning Aids": "Human body chart, soap, clean water, toothbrush, basin.",
                "Life Skills": "Self-care, health awareness.",
                "Values": "Cleanliness, self-respect."
            },
            "Topic 2: Plants and Animals in Our Environment": {
                "Subtopics": "Common local plants, uses of plants, domestic vs. wild animals.",
                "Learning Outcome": "Learner distinguishes domestic from wild animals and names common plants.",
                "Learning Aids": "Real leaves/flowers, animal flashcards, nature walk.",
                "Life Skills": "Observation, environmental care.",
                "Values": "Kindness to animals, stewardship."
            }
        }
    },
    "P2": {
        "Literacy & Language (Thematic)": {
            "Topic 1: Food and Nutrition": {
                "Subtopics": "Common foods, sources of food, food hygiene, balanced diet basics.",
                "Learning Outcome": "Learner classifies local foods and explains safe food handling.",
                "Learning Aids": "Real food samples (beans, maize, greens), food group charts.",
                "Life Skills": "Decision making, health consciousness.",
                "Values": "Gratitude, cleanliness, sharing."
            },
            "Topic 2: Transport and Communication": {
                "Subtopics": "Means of road/water/air transport, road safety, local communication tools.",
                "Learning Outcome": "Learner identifies transport modes and demonstrates safe road crossing.",
                "Learning Aids": "Toy vehicles, road sign flashcards, mobile phone/radio models.",
                "Life Skills": "Safety awareness, effective communication.",
                "Values": "Caution, patience, discipline."
            }
        },
        "Numeracy (Mathematics)": {
            "Topic 1: Place Value and Operations up to 50": {
                "Subtopics": "Tens and ones, addition with regrouping, subtraction up to 50.",
                "Learning Outcome": "Learner identifies place values and solves addition/subtraction up to 50.",
                "Learning Aids": "Place value tins, abacus, bundles of tens.",
                "Life Skills": "Analytical thinking, problem solving.",
                "Values": "Precision, diligence."
            },
            "Topic 2: Introduction to Multiplication and Division": {
                "Subtopics": "Repeated addition (2s, 3s, 5s), equal sharing of concrete objects.",
                "Learning Outcome": "Learner multiplies by 2, 3, and 5 and divides items equally.",
                "Learning Aids": "Counters, multiplication tables chart, small containers.",
                "Life Skills": "Fairness in sharing, logical reasoning.",
                "Values": "Fairness, cooperation, accuracy."
            }
        }
    },
    "P3": {
        "Thematic Environment & Social Studies": {
            "Topic 1: Our Sub-county / Division": {
                "Subtopics": "Location, physical features (hills, swamps, rivers), administrative leadership.",
                "Learning Outcome": "Learner locates major landmarks and describes economic activities in the sub-county.",
                "Learning Aids": "Sub-county sketch map, clay physical models, compass.",
                "Life Skills": "Spatial orientation, civic awareness.",
                "Values": "Patriotism, community pride."
            },
            "Topic 2: Energy, Water and Sanitation": {
                "Subtopics": "Sources of energy, safe water chain, refuse disposal, vector control.",
                "Learning Outcome": "Learner practices water purification and safe energy conservation.",
                "Learning Aids": "Tippy-tap, charcoal stove, solar panel picture, water filter.",
                "Life Skills": "Resource conservation, problem solving.",
                "Values": "Responsibility, cleanliness, resourcefulness."
            }
        },
        "Mathematics": {
            "Topic 1: Numbers up to 1,000 and Fractions": {
                "Subtopics": "Hundreds, tens, ones; halves, quarters, thirds; metric units (m, kg, l).",
                "Learning Outcome": "Learner works with 3-digit numbers and compares simple fractions.",
                "Learning Aids": "Fraction strips, meter ruler, weighing scale, measuring jugs.",
                "Life Skills": "Measurement accuracy, financial literacy.",
                "Values": "Honesty in trade, precision."
            }
        }
    },
    "P4": {
        "English": {
            "Topic 1: Describing People and Objects": {
                "Subtopics": "Adjectives, pronouns, present simple tense, descriptive sentences.",
                "Learning Outcome": "Learner writes coherent descriptive paragraphs using accurate adjectives.",
                "Learning Aids": "Picture cards, grammar charts, sentence strips.",
                "Life Skills": "Creative expression, effective communication.",
                "Values": "Respect, neatness."
            },
            "Topic 2: Giving Directions and Letter Writing": {
                "Subtopics": "Prepositions of place, imperative verbs, parts of an informal letter.",
                "Learning Outcome": "Learner gives clear directions and writes a well-structured friendly letter.",
                "Learning Aids": "Local area map, sample informal letter chart.",
                "Life Skills": "Clear communication, spatial guidance.",
                "Values": "Helpfulness, courtesy."
            }
        },
        "Mathematics": {
            "Topic 1: Whole Numbers up to 10,000 & Fractions": {
                "Subtopics": "Place values up to ten thousands, equivalent fractions, addition/subtraction of decimals.",
                "Learning Outcome": "Learner performs operations with large numbers, fractions, and decimals.",
                "Learning Aids": "Abacus, fraction charts, decimal grids.",
                "Life Skills": "Logical reasoning, numerical problem solving.",
                "Values": "Accuracy, perseverance."
            },
            "Topic 2: Perimeter, Area and Metric Units": {
                "Subtopics": "Perimeter and area of squares/rectangles, converting km/m/cm and kg/g.",
                "Learning Outcome": "Learner calculates area/perimeter and converts standard metric units.",
                "Learning Aids": "Rulers, tape measures, square grid paper.",
                "Life Skills": "Spatial estimation, practical measurement.",
                "Values": "Precision, diligence."
            }
        },
        "Integrated Science": {
            "Topic 1: Plant Life and Crop Growing": {
                "Subtopics": "Parts of a flowering plant, functions of roots/stems/leaves, garden tools, crop care.",
                "Learning Outcome": "Learner identifies plant parts and demonstrates basic crop husbandry.",
                "Learning Aids": "Real uprooted flowering plant, hoe, watering can, seed samples.",
                "Life Skills": "Scientific observation, agricultural skills.",
                "Values": "Environmental stewardship, hard work."
            },
            "Topic 2: The Human Digestive System & Teeth": {
                "Subtopics": "Types of teeth, tooth structure, digestive organs, deficiency diseases (kwashiorkor, marasmus).",
                "Learning Outcome": "Learner explains digestion and practices proper dental and nutritional care.",
                "Learning Aids": "Model of human teeth, digestive system chart, food samples.",
                "Life Skills": "Health management, critical thinking.",
                "Values": "Self-care, hygiene."
            }
        },
        "Social Studies": {
            "Topic 1: Location and Physical Features of Our District": {
                "Subtopics": "Map elements (title, key, compass, scale), hills, lakes, rivers, vegetation.",
                "Learning Outcome": "Learner uses a compass and map key to locate features in their district.",
                "Learning Aids": "District wall map, magnetic compass, relief models.",
                "Life Skills": "Map reading, environmental observation.",
                "Values": "Patriotism, environmental care."
            }
        },
        "Kiswahili": {
            "Topic 1: Salamu na Ngeli za Nomino (M-WA, KI-VI)": {
                "Subtopics": "Polite greetings, phonetic spelling, singular/plural in M-WA and KI-VI classes.",
                "Learning Outcome": "Learner greets appropriately and constructs simple sentences in M-WA and KI-VI.",
                "Learning Aids": "Kiswahili greeting charts, noun class flashcards.",
                "Life Skills": "Cross-cultural communication, linguistic adaptability.",
                "Values": "Respect, regional unity."
            }
        },
        "Religious Education": {
            "Topic 1: God's Covenant and Moral Integrity": {
                "Subtopics": "Creation, covenants (Abraham/Noah/Prophetic traditions), honesty and service.",
                "Learning Outcome": "Learner demonstrates moral integrity and respect for sacred scriptures.",
                "Learning Aids": "Bible, Quran, moral scenario flashcards.",
                "Life Skills": "Moral reasoning, empathy.",
                "Values": "Integrity, truthfulness, reverence."
            }
        }
    },
    "P5": {
        "English": {
            "Topic 1: Vehicle Repair, Travel & Letter Writing": {
                "Subtopics": "Technical vocabulary, past continuous tense, relative clauses, formal vs. informal letters.",
                "Learning Outcome": "Learner uses relative clauses accurately and writes structured letters.",
                "Learning Aids": "Vehicle parts chart, sample formal letter templates.",
                "Life Skills": "Formal communication, problem solving.",
                "Values": "Courtesy, clarity."
            }
        },
        "Mathematics": {
            "Topic 1: Integers, Percentages and Algebra": {
                "Subtopics": "Adding/subtracting negative numbers, converting fractions to percentages, simple algebraic equations.",
                "Learning Outcome": "Learner solves integer operations, percentage word problems, and basic equations.",
                "Learning Aids": "Integer number line, percentage grids, algebra balance cards.",
                "Life Skills": "Analytical thinking, financial literacy.",
                "Values": "Logical discipline, honesty."
            }
        },
        "Integrated Science": {
            "Topic 1: Matter, Heat Transfer & Human Systems": {
                "Subtopics": "States of matter, conduction/convection/radiation, heart and lung functions, immunization.",
                "Learning Outcome": "Learner demonstrates heat transfer methods and explains circulatory/respiratory health.",
                "Learning Aids": "Heat source, metal rod, chart of human heart/lungs, immunization card.",
                "Life Skills": "Experimental inquiry, health safety.",
                "Values": "Scientific curiosity, responsibility."
            }
        },
        "Social Studies": {
            "Topic 1: Geography and Pre-Colonial History of Uganda": {
                "Subtopics": "Relief zones, drainage, ethnic migrations (Bantu, Nilotics), early kingdoms, Constitution.",
                "Learning Outcome": "Learner traces ethnic migration routes and explains Uganda's governance structure.",
                "Learning Aids": "Physical map of Uganda, migration arrow map, Constitution extract.",
                "Life Skills": "Historical analysis, civic participation.",
                "Values": "National unity, tolerance, patriotism."
            }
        },
        "Kiswahili": {
            "Topic 1: Nyakati (li-, na-, ta-) na Msamiati wa Masoko": {
                "Subtopics": "Past, present, and future verb tenses; market buying/selling dialogues.",
                "Learning Outcome": "Learner converses in past, present, and future tenses in market role-plays.",
                "Learning Aids": "Tense conjugation chart, market item flashcards.",
                "Life Skills": "Negotiation, practical communication.",
                "Values": "Honesty in trade, cultural integration."
            }
        },
        "Religious Education": {
            "Topic 1: Teachings of Jesus / Prophet Muhammad & Peer Pressure": {
                "Subtopics": "Compassion, justice, pillars of worship, resisting negative peer pressure.",
                "Learning Outcome": "Learner applies religious teachings to make ethical choices against peer pressure.",
                "Learning Aids": "Scripture texts, peer-pressure role-play cards.",
                "Life Skills": "Assertiveness, ethical decision-making.",
                "Values": "Compassion, steadfastness, justice."
            }
        }
    },
    "P6": {
        "English": {
            "Topic 1: Reported Speech, Passive Voice & Debating": {
                "Subtopics": "Direct to indirect speech, active to passive voice, conditional sentences (If 1, 2, 3), debate motions.",
                "Learning Outcome": "Learner transforms sentences accurately and presents structured debate arguments.",
                "Learning Aids": "Speech transformation charts, debate rubric cards.",
                "Life Skills": "Public speaking, critical thinking, persuasion.",
                "Values": "Confidence, respect for differing views."
            }
        },
        "Mathematics": {
            "Topic 1: Proportions, Speed, Simple Interest & Data": {
                "Subtopics": "Direct/inverse proportion, Speed = Distance/Time, Simple Interest (PRT/100), pie charts, mean/median/mode.",
                "Learning Outcome": "Learner calculates speed, interest, and interprets statistical pie charts.",
                "Learning Aids": "Stopwatches, interest rate tables, protractors for pie charts.",
                "Life Skills": "Financial planning, time management, data analysis.",
                "Values": "Prudence, accuracy."
            }
        },
        "Integrated Science": {
            "Topic 1: Electricity, Simple Machines & Reproduction": {
                "Subtopics": "Simple electric circuits, levers/pulleys/friction, mammalian reproduction, adolescence, HIV/AIDS immunity.",
                "Learning Outcome": "Learner constructs a simple circuit, classifies levers, and explains reproductive health.",
                "Learning Aids": "Dry cells, copper wires, bulbs, pulley/lever models, health charts.",
                "Life Skills": "Technical problem solving, self-protection, empathy.",
                "Values": "Safety consciousness, responsibility."
            }
        },
        "Social Studies": {
            "Topic 1: East African Geography & Independence Struggles": {
                "Subtopics": "EAC countries, resources, European scramble/partition, resistance movements, path to independence.",
                "Learning Outcome": "Learner analyzes East African resource distribution and independence milestones.",
                "Learning Aids": "East Africa political/resource map, historical timelines.",
                "Life Skills": "Geopolitical awareness, historical synthesis.",
                "Values": "Pan-African solidarity, patriotism."
            }
        },
        "Kiswahili": {
            "Topic 1: Vivumishi, Vihusishi na Ufupisho wa Hadithi": {
                "Subtopics": "Adjectives, prepositions, negative verb forms, summarizing short passages.",
                "Learning Outcome": "Learner summarizes short Kiswahili texts using accurate adjectives and prepositions.",
                "Learning Aids": "Kiswahili readers, grammar summary tables.",
                "Life Skills": "Summarization, reading comprehension.",
                "Values": "Diligence, linguistic pride."
            }
        },
        "Religious Education": {
            "Topic 1: Faith in Action, Work Ethics & Reconciliation": {
                "Subtopics": "Stewardship of resources, dignity of work, marriage/family values, conflict resolution.",
                "Learning Outcome": "Learner demonstrates responsible stewardship and peaceful conflict mediation.",
                "Learning Aids": "Community leadership case studies, scripture guides.",
                "Life Skills": "Conflict mediation, leadership ethics.",
                "Values": "Accountability, peace-building, stewardship."
            }
        }
    },
    "P7": {
        "English": {
            "Topic 1: PLE Grammar Consolidation, Idioms & Summary": {
                "Subtopics": "Phrasal verbs, idioms, synonyms/antonyms, passage summary writing, timed comprehension.",
                "Learning Outcome": "Learner completes comprehension and composition tasks within PLE time standards.",
                "Learning Aids": "PLE past papers, idiom reference sheets, stopwatch.",
                "Life Skills": "Time management, stress control, critical editing.",
                "Values": "Resilience, academic integrity."
            }
        },
        "Mathematics": {
            "Topic 1: Set Theory, Geometry & Simultaneous Equations": {
                "Subtopics": "Venn diagrams (2 and 3 sets), angle properties on parallel lines/circles, algebraic equations.",
                "Learning Outcome": "Learner solves multi-step set problems, geometric angles, and equations.",
                "Learning Aids": "Mathematical sets, Venn diagram templates, past paper drills.",
                "Life Skills": "Complex analytical reasoning, strategic problem solving.",
                "Values": "Precision, perseverance, excellence."
            }
        },
        "Integrated Science": {
            "Topic 1: Excretory & Nervous Systems, Livestock & Environment": {
                "Subtopics": "Kidneys, skin, brain/spinal cord reflex actions, poultry/cattle management, pollution control.",
                "Learning Outcome": "Learner explains excretion/nervous coordination and sustainable farming practices.",
                "Learning Aids": "Kidney/brain anatomical charts, livestock feed samples.",
                "Life Skills": "Scientific synthesis, agricultural entrepreneurship.",
                "Values": "Environmental accountability, diligence."
            }
        },
        "Social Studies": {
            "Topic 1: Geography of Africa, Pan-Africanism & Global Bodies": {
                "Subtopics": "Climate/vegetation of Africa, decolonization, African Union (AU), United Nations (UN), global trade.",
                "Learning Outcome": "Learner evaluates Africa's physical regions and international cooperation roles.",
                "Learning Aids": "Wall map of Africa, AU/UN organization charts.",
                "Life Skills": "Global citizenship, geopolitical evaluation.",
                "Values": "Global empathy, peace advocacy, civic pride."
            }
        },
        "Kiswahili": {
            "Topic 1: Barua Rasmi na Mawasiliano Fasaha": {
                "Subtopics": "Formal letter format in Kiswahili, advanced sentence structures, oral fluency.",
                "Learning Outcome": "Learner writes formal Kiswahili letters and communicates fluently for secondary entry.",
                "Learning Aids": "Formal letter samples, conversational assessment prompts.",
                "Life Skills": "Formal administrative communication, bilingual readiness.",
                "Values": "Excellence, respect for regional languages."
            }
        },
        "Religious Education": {
            "Topic 1: Moral Theology, Human Dignity & Social Responsibility": {
                "Subtopics": "Ethical responses to modern challenges, human rights/dignity, comprehensive PLE revision.",
                "Learning Outcome": "Learner synthesizes scriptural principles to uphold human dignity and civic duty.",
                "Learning Aids": "Thematic PLE revision briefs, ethical dilemma discussions.",
                "Life Skills": "Ethical discernment, holistic self-evaluation.",
                "Values": "Moral integrity, spiritual maturity, justice."
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
page = st.sidebar.selectbox(
    "Go to",
    ["Take Quiz", "Topical Breakdown", "NCDC Curriculum Overview", "Teacher Dashboard"]
)

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

elif page == "Topical Breakdown":
    st.title("🗂️ NCDC Class-by-Class Topical Breakdown (P1–P7)")
    st.caption("Integrated Learning Environment — Select Class, Subject & Topic")
    st.write("Browse individual syllabus topics across all primary classes, along with subtopics, learning outcomes, learning aids, life skills, and values.")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_class = st.selectbox("1. Select Class", [f"P{i}" for i in range(1, 8)], key="tb_class")
    
    class_subjects = TOPICAL_BREAKDOWN.get(selected_class, {})
    with col2:
        selected_subject = st.selectbox("2. Select Subject / Learning Area", list(class_subjects.keys()), key="tb_subject")
    
    subject_topics = class_subjects.get(selected_subject, {})
    selected_topic = st.selectbox("3. Select Topic", list(subject_topics.keys()), key="tb_topic")
    
    st.markdown("---")
    topic_details = subject_topics.get(selected_topic, {})
    if topic_details:
        st.subheader(f"{selected_class} • {selected_subject}")
        st.markdown(f"### 📌 {selected_topic}")
        st.info(f"**Learning Outcome:** {topic_details.get('Learning Outcome', '')}")
        st.markdown(f"**Subtopics:** {topic_details.get('Subtopics', '')}")
        st.markdown(f"**Learning Aids / Instructional Materials:** {topic_details.get('Learning Aids', '')}")
        st.markdown(f"**Life Skills Acquired:** {topic_details.get('Life Skills', '')}")
        st.markdown(f"**Core Values Inculcated:** {topic_details.get('Values', '')}")

elif page == "NCDC Curriculum Overview":
    st.title("📚 NCDC Curriculum Overview")
    st.caption("Integrated Learning Environment — Thematic (P1–P3) & Subject-Based (P4–P7) Cycles")
    
    cycle_choice = st.selectbox("Select Cycle", list(NCDC_CURRICULUM.keys()))
    
    if "Thematic" in cycle_choice:
        selected_class = st.selectbox("Select Class", ["P1", "P2", "P3"])
        st.markdown("---")
        st.subheader(f"Thematic Curriculum Summary for {selected_class}")
        terms_data = NCDC_CURRICULUM[cycle_choice].get(selected_class, {})
        for term, desc in terms_data.items():
            st.markdown(f"**{term}:**")
            st.info(desc)
    else:
        selected_class = st.selectbox("Select Class", ["P4", "P5", "P6", "P7"])
        st.markdown("---")
        st.subheader(f"Subject-Based Summary for {selected_class}")
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
