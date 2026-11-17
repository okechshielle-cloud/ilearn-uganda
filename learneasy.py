import streamlit as st
import pandas as pd
import os
import requests
import json

st.set_page_config(page_title="iLearn-Uganda", layout="centered")

TEACHER_PASSWORD = st.secrets.get("TEACHER_PASSWORD", "iLearnUganda123")
CSV_FILE = "results.csv"
SHEET_URL = st.secrets.get("SHEET_URL", "")

# Official NCDC Framework Structure (Thematic P1-P3, Subject-Based P4-P7)
NCDC_CURRICULUM = {
    "Lower Primary (Cycle 1: Thematic Approach P1-P3)": {
        "P1": {
            "Term 1: Our School / Our Home": "Focuses on literacy in local language, early numeracy (1-10), personal hygiene, school rules, and family member roles.",
            "Term 2: Our Community / Human Body": "Focuses on community helpers, body parts, five senses, health & sanitation habits, and addition/subtraction up to 20.",
            "Term 3: Plants, Animals & Environment": "Focuses on local plants, domestic/wild animals, weather changes, and road/environmental safety awareness."
        },
        "P2": {
            "Term 1: Food and Nutrition": "Focuses on food classification (local food groups), food hygiene, kitchen safety, safe drinking water, and numbers up to 50.",
            "Term 2: Transport & Communication": "Focuses on road/water/air transport, road safety rules, traditional/modern communication, and basic multiplication.",
            "Term 3: Peace, Security & Changes": "Focuses on peaceful coexistence, conflict resolution, child rights and responsibilities, and non-standard measurement."
        },
        "P3": {
            "Term 1: Our Sub-county / Division": "Focuses on sub-county physical features, hills, valleys, swamps, landmarks, economic activities, and multiplication tables.",
            "Term 2: Energy, Water and Sanitation": "Focuses on sources of light/heat/sound, safe water chain, refuse disposal, vector control, and standard metric units.",
            "Term 3: Transition Foundations": "Focuses on consolidating literacy/numeracy for transition into English-medium instruction and lower primary exit competencies."
        }
    },
    "Upper Primary (Cycle 2 & 3: Subject-Based P4-P7)": {
        "P4": {
            "Mathematics": "The 12 core NCDC strands: Set Concepts, Whole Numbers, Operations, Patterns, Fractions, Geometry, Data, Time, Integers, Money, Measurements, and Algebra.",
            "English": "Grammar, comprehension, composition, punctuation, nouns, pronouns, and guided letter writing.",
            "Integrated Science": "Plant anatomy, crop growing practices, human digestive system, teeth structures, and weather measurement.",
            "Social Studies (SST)": "Map reading (compass, scale, key), district physical geography, vegetation, climate, and local governance.",
            "Religious Education (CRE/IRE)": "Sacred scriptures (Bible/Quran), foundational covenants, prophetic traditions, and moral decision-making.",
            "Creative Arts & Physical Education (CAPE)": "CAPE 1 (Music, Dance & Drama), CAPE 2 (Physical Education & sports rules), CAPE 3 (Art, color mixing & craft)."
        },
        "P5": {
            "Mathematics": "Advanced progress across the 12 NCDC strands including integers, percentages, lines and angles, area/volume, and algebra.",
            "English": "Complex tenses, conjunctions, relative clauses, poem analysis, summary writing, and formal speeches.",
            "Integrated Science": "States of matter, heat transfer (conduction, convection, radiation), human circulatory/respiratory systems, and PHC.",
            "Social Studies (SST)": "Uganda's physical geography, relief zones, ethnic migrations (Bantu, Nilotics), early African kingdoms, and the Constitution.",
            "Religious Education (CRE/IRE)": "Life and teachings of Jesus Christ / Prophet Muhammad, justice, compassion, worship practices, and peer pressure.",
            "Creative Arts & Physical Education (CAPE)": "CAPE 1 (Folk songs & traditional dance), CAPE 2 (Athletics & physical endurance), CAPE 3 (Functional craft & pottery)."
        },
        "P6": {
            "Mathematics": "Mastery of the 12 NCDC strands: proportions, speed/distance/time, simple interest, geometric figures, and statistics.",
            "English": "Active and passive voice, direct/indirect speech, conditional clauses, formal report writing, and minutes.",
            "Integrated Science": "Electricity, magnetism, simple machines (levers, pulleys), friction, mammalian reproduction, adolescence, and immunity.",
            "Social Studies (SST)": "East African physical resources, European scramble and partition, resistance movements, and independence struggles.",
            "Religious Education (CRE/IRE)": "Faith in action, leadership, family values, work ethics, resource stewardship, and conflict resolution.",
            "Creative Arts & Physical Education (CAPE)": "CAPE 1 (Choral performance & drama), CAPE 2 (First-aid safety & sports officiating), CAPE 3 (Advanced sculpture & textile design)."
        },
        "P7": {
            "Mathematics": "Consolidation of all 12 NCDC strands with emphasis on simultaneous equations, geometric construction, set theory, and past paper drills.",
            "English": "Comprehensive grammar consolidation, phrasal verbs, idioms, summary compression, and timed PLE exam preparation.",
            "Integrated Science": "Human excretory and nervous systems, agricultural science, livestock/poultry management, and environmental conservation.",
            "Social Studies (SST)": "Continental geography of Africa, decolonization, African Union (AU), United Nations (UN), and global economic integration.",
            "Religious Education (CRE/IRE)": "Moral theology, human dignity, social responsibility, ethical responses to modern challenges, and holistic PLE revision.",
            "Creative Arts & Physical Education (CAPE)": "CAPE 1 (Advanced MDD productions), CAPE 2 (Recreational sport management & fitness), CAPE 3 (Entrepreneurial craft exhibitions)."
        }
    }
}

# Complete Class-by-Class Topical Breakdown for ALL Subjects in Order
TOPICAL_BREAKDOWN = {
    "P1": {
        "1. Numeracy (Mathematics)": {
            "1. Set Concepts": {
                "Subtopics": "Sorting and matching objects by color, shape, and size; empty sets.",
                "Learning Outcome": "Learner sorts, matches, and classifies objects into sets.",
                "Learning Aids": "Bottle tops, buttons, leaves, set strings.",
                "Life Skills": "Critical thinking, classification.",
                "Values": "Orderliness, accuracy."
            },
            "2. Whole Numbers": {
                "Subtopics": "Counting concrete objects from 1 to 10; reading and writing number symbols and words.",
                "Learning Outcome": "Learner counts and writes whole numbers from 1 to 10.",
                "Learning Aids": "Number cards, counters, abacus.",
                "Life Skills": "Basic numeracy, observation.",
                "Values": "Patience, neatness."
            },
            "3. Operations on Whole Numbers": {
                "Subtopics": "Putting together (addition) and taking away (subtraction) objects up to 20.",
                "Learning Outcome": "Learner adds and subtracts numbers with sums up to 20.",
                "Learning Aids": "Number lines, sticks, counters.",
                "Life Skills": "Problem solving.",
                "Values": "Accuracy."
            }
        },
        "2. Literacy I (Local Language / English)": {
            "Topic 1: Our School": {
                "Subtopics": "People in our school, classroom objects, school rules, school environment.",
                "Learning Outcome": "Learner identifies school members, names classroom objects, and follows basic instructions.",
                "Learning Aids": "Classroom realia, name flashcards, picture charts.",
                "Life Skills": "Effective communication, self-awareness.",
                "Values": "Obedience, respect."
            }
        },
        "3. Literacy II (Health, Science & Environment)": {
            "Topic 1: The Human Body and Personal Hygiene": {
                "Subtopics": "External body parts, five senses, washing hands, brushing teeth.",
                "Learning Outcome": "Learner names body parts and demonstrates daily personal hygiene habits.",
                "Learning Aids": "Human body chart, soap, clean water, toothbrush.",
                "Life Skills": "Self-care, health awareness.",
                "Values": "Cleanliness, self-respect."
            }
        }
    },
    "P2": {
        "1. Numeracy (Mathematics)": {
            "1. Set Concepts": {
                "Subtopics": "Intersection and union of two sets using real objects.",
                "Learning Outcome": "Learner identifies elements belonging to the union and intersection of sets.",
                "Learning Aids": "Intersecting loops, flashcards.",
                "Life Skills": "Logical grouping.",
                "Values": "Cooperation."
            },
            "2. Whole Numbers & Operations": {
                "Subtopics": "Place value (tens and ones) up to 50; addition and subtraction with regrouping.",
                "Learning Outcome": "Learner solves addition and subtraction problems up to 50.",
                "Learning Aids": "Place value tins, bundles of 10 sticks.",
                "Life Skills": "Analytical thinking.",
                "Values": "Precision."
            }
        },
        "2. Literacy I (Local Language / English)": {
            "Topic 1: Food and Nutrition": {
                "Subtopics": "Common foods, sources of food, food hygiene, balanced diet basics.",
                "Learning Outcome": "Learner classifies local foods and explains safe food handling.",
                "Learning Aids": "Real food samples, food group charts.",
                "Life Skills": "Decision making, health consciousness.",
                "Values": "Gratitude, sharing."
            }
        },
        "3. Literacy II (Environment & Social)": {
            "Topic 1: Transport and Communication": {
                "Subtopics": "Means of road/water transport, road safety rules, local communication tools.",
                "Learning Outcome": "Learner identifies transport modes and demonstrates safe road crossing.",
                "Learning Aids": "Toy vehicles, road sign flashcards.",
                "Life Skills": "Safety awareness.",
                "Values": "Caution, discipline."
            }
        }
    },
    "P3": {
        "1. Mathematics": {
            "1. Set Concepts & Whole Numbers": {
                "Subtopics": "Reading and writing numbers up to 1,000; place values (hundreds, tens, ones).",
                "Learning Outcome": "Learner reads and writes numbers up to 1,000 in figures and words.",
                "Learning Aids": "Base-ten blocks, number charts.",
                "Life Skills": "Estimation, numerical fluency.",
                "Values": "Honesty, order."
            },
            "5. Fractions & 10. Money": {
                "Subtopics": "Simple fractions (halves, quarters); Ugandan currency notes and coins up to 50,000/=.",
                "Learning Outcome": "Learner identifies simple fractions and computes basic money transactions.",
                "Learning Aids": "Fraction cut-outs, play currency notes.",
                "Life Skills": "Financial literacy, sharing.",
                "Values": "Fairness, prudence."
            }
        },
        "2. English": {
            "Topic 1: Our Sub-county / Division": {
                "Subtopics": "Naming features, spelling key vocabulary, writing simple sentences about home and school.",
                "Learning Outcome": "Learner writes correct sentences about their local surroundings.",
                "Learning Aids": "Word cards, picture flashcards.",
                "Life Skills": "Effective communication.",
                "Values": "Clarity, neatness."
            }
        },
        "3. Integrated Science": {
            "Topic 1: Environment and Living Things": {
                "Subtopics": "Plants in the environment, uses of plants, domestic animals and their care.",
                "Learning Outcome": "Learner distinguishes living things and cares for domestic animals.",
                "Learning Aids": "Potted plants, animal pictures.",
                "Life Skills": "Environmental observation.",
                "Values": "Stewardship, kindness."
            }
        },
        "4. Social Studies & Religious Education": {
            "Topic 1: Our Sub-county / Division": {
                "Subtopics": "Location, physical features, administrative leadership, places of worship.",
                "Learning Outcome": "Learner locates major landmarks and identifies administrative leaders in the sub-county.",
                "Learning Aids": "Sub-county sketch map, local leader photographs.",
                "Life Skills": "Civic awareness.",
                "Values": "Patriotism, respect."
            }
        }
    },
    "P4": {
        "1. Mathematics (12 Strands)": {
            "1. Set Concepts": {
                "Subtopics": "Equivalent/non-equivalent sets, equal sets, empty sets, union and intersection, 2-set Venn diagrams.",
                "Learning Outcome": "Learner groups items into sets, finds union/intersection, and illustrates them on Venn diagrams.",
                "Learning Aids": "Set string loops, object cards, Venn diagram charts.",
                "Life Skills": "Classification, logical reasoning.",
                "Values": "Orderliness, accuracy."
            },
            "2. Whole Numbers": {
                "Subtopics": "Place values and values up to 99,999, reading/writing in words and figures, expanded form, Roman numerals up to C.",
                "Learning Outcome": "Learner reads, writes, and expands whole numbers up to tens of thousands.",
                "Learning Aids": "Abacus, place value cards, Roman numeral charts.",
                "Life Skills": "Numerical literacy, analytical thinking.",
                "Values": "Precision, neatness."
            },
            "3. Operations on Whole Numbers": {
                "Subtopics": "Addition, subtraction, multiplication, division of large numbers, mixed operations (BODMAS), word problems.",
                "Learning Outcome": "Learner performs the four basic mathematical operations accurately in multi-step problems.",
                "Learning Aids": "Operation flashcards, word problem scenario strips.",
                "Life Skills": "Problem solving, critical thinking.",
                "Values": "Patience, persistence."
            },
            "4. Patterns and Sequences": {
                "Subtopics": "Number sequences, skipping, square numbers, triangular numbers, finding missing terms.",
                "Learning Outcome": "Learner identifies rules in number patterns and completes sequences.",
                "Learning Aids": "Number grid charts, dot pattern cards.",
                "Life Skills": "Pattern recognition, deductive reasoning.",
                "Values": "Curiosity, logical discipline."
            },
            "5. Fractions": {
                "Subtopics": "Proper, improper, mixed fractions, equivalent fractions, addition and subtraction of like/unlike fractions.",
                "Learning Outcome": "Learner manipulates fractions and performs basic fraction operations.",
                "Learning Aids": "Fraction cut-outs, fractional pie charts.",
                "Life Skills": "Proportional reasoning, practical sharing.",
                "Values": "Fairness, accuracy."
            },
            "6. Lines, Angles and Geometric Figures": {
                "Subtopics": "Types of lines, measuring angles using a protractor, properties of triangles and rectangles.",
                "Learning Outcome": "Learner measures angles and identifies geometric properties of basic shapes.",
                "Learning Aids": "Protractors, rulers, set squares, geometric models.",
                "Life Skills": "Spatial awareness, visual precision.",
                "Values": "Accuracy, neatness."
            },
            "7. Data Handling": {
                "Subtopics": "Collecting data, tally marks, interpreting pictographs and simple bar graphs.",
                "Learning Outcome": "Learner collects, records, and interprets data from charts and graphs.",
                "Learning Aids": "Tally charts, grid paper, picture graphs.",
                "Life Skills": "Data organization, analytical interpretation.",
                "Values": "Honesty in data recording, order."
            },
            "8. Time": {
                "Subtopics": "Reading clocks (12-hour), days, weeks, months, years, simple time intervals.",
                "Learning Outcome": "Learner tells time accurately and calculates basic elapsed time.",
                "Learning Aids": "Model clock face, calendar charts.",
                "Life Skills": "Time management, punctuality.",
                "Values": "Discipline, respect for time."
            },
            "9. Integers": {
                "Subtopics": "Introduction to positive and negative numbers, representing integers on a number line.",
                "Learning Outcome": "Learner distinguishes positive and negative numbers on a number line.",
                "Learning Aids": "Integer number line charts.",
                "Life Skills": "Directional awareness, critical reasoning.",
                "Values": "Accuracy, balance."
            },
            "10. Money": {
                "Subtopics": "Ugandan currency, shopping bills, calculating change, profit and loss basics.",
                "Learning Outcome": "Learner computes monetary transactions and calculates shopping change.",
                "Learning Aids": "Play currency notes and coins, supermarket price tags.",
                "Life Skills": "Financial literacy, consumer awareness.",
                "Values": "Honesty in trade, prudence."
            },
            "11. Length, Mass and Capacity": {
                "Subtopics": "Standard units (m, cm, kg, g, litres, millilitres), perimeter and area of squares and rectangles.",
                "Learning Outcome": "Learner measures length/mass/capacity and calculates perimeter and area.",
                "Learning Aids": "Meter rulers, weighing scales, measuring cylinders, grid paper.",
                "Life Skills": "Practical measurement estimation.",
                "Values": "Precision, resourcefulness."
            },
            "12. Algebra": {
                "Subtopics": "Collecting like terms, substitution, solving simple linear equations with one unknown.",
                "Learning Outcome": "Learner simplifies algebraic expressions and solves basic linear equations.",
                "Learning Aids": "Algebra balance cards, letter symbol strips.",
                "Life Skills": "Abstract reasoning, problem solving.",
                "Values": "Logical rigor, perseverance."
            }
        },
        "2. English": {
            "Topic 1: Describing People and Objects": "Adjectives, pronouns, present simple tense, descriptive sentences.",
            "Topic 2: Giving Directions and Letter Writing": "Prepositions of place, imperative verbs, parts of an informal letter."
        },
        "3. Integrated Science": {
            "Topic 1: Plant Life and Crop Growing": "Parts of a flowering plant, functions of roots/stems/leaves, garden tools, crop care.",
            "Topic 2: The Human Digestive System & Teeth": "Types of teeth, tooth structure, digestive organs, deficiency diseases (kwashiorkor, marasmus)."
        },
        "4. Social Studies (SST)": {
            "Topic 1: Location and Physical Features of Our District": "Map elements (title, key, compass, scale), hills, lakes, rivers, vegetation."
        },
        "5. Religious Education (CRE/IRE)": {
            "Topic 1: God's Covenant and Moral Integrity": "Creation, covenants (Abraham/Noah/Prophetic traditions), honesty and service."
        },
        "6. Creative Arts & Physical Education (CAPE)": {
            "Topic 1: Fundamentals of Music, Art and PE": "Color mixing, basic traditional dance steps, ball games, and safety rules."
        }
    },
    "P5": {
        "1. Mathematics (12 Strands Advanced)": {
            "1. Set Concepts": "Describing shaded regions, subsets, listing subsets, probability as a fraction using sets.",
            "2. Whole Numbers": "Place values up to 999,999, rounding off up to ten thousands, Roman numerals up to M (1,000).",
            "3. Operations on Whole Numbers": "Advanced multiplication and division word problems, combined operations.",
            "4. Patterns and Sequences": "Prime numbers, composite numbers, consecutive integers, sequence rules.",
            "5. Fractions, Decimals and Percentages": "Operations on fractions, decimals up to thousandths, converting fractions/decimals/percentages, ratios.",
            "6. Lines, Angles and Geometric Figures": "Angles on a straight line, angles at a point, complementary/supplementary angles, polygons.",
            "7. Data Handling": "Interpreting bar graphs, line graphs, calculating mean, median, and mode.",
            "8. Time": "24-hour clock conversion, time tables, speed, distance, and time calculations.",
            "9. Integers": "Addition and subtraction of integers using number lines and rules.",
            "10. Money": "Buying and selling, profit and loss calculations, simple discount.",
            "11. Length, Mass and Capacity": "Unit conversions, area of triangles and parallelograms, volume of cuboids.",
            "12. Algebra": "Forming and solving algebraic equations, inequalities with one variable."
        },
        "2. English": {
            "Topic 1: Vehicle Repair, Travel & Letter Writing": "Technical vocabulary, past continuous tense, relative clauses, formal vs. informal letters."
        },
        "3. Integrated Science": {
            "Topic 1: Matter, Heat Transfer & Human Systems": "States of matter, conduction/convection/radiation, heart and lung functions, immunization."
        },
        "4. Social Studies (SST)": {
            "Topic 1: Geography and Pre-Colonial History of Uganda": "Relief zones, drainage, ethnic migrations (Bantu, Nilotics), early kingdoms, Constitution."
        },
        "5. Religious Education (CRE/IRE)": {
            "Topic 1: Teachings of Jesus / Prophet Muhammad & Peer Pressure": "Compassion, justice, pillars of worship, resisting negative peer pressure."
        },
        "6. Creative Arts & Physical Education (CAPE)": {
            "Topic 1: Intermediate Sports Tactics & Functional Crafts": "Athletic endurance, pottery, sign-making, folk songs."
        }
    },
    "P6": {
        "1. Mathematics (12 Strands Upper Primary)": {
            "1. Set Concepts": "Difference of sets (complement), universal sets, solving 2-set Venn diagram word problems.",
            "2. Whole Numbers": "Place values up to millions (9,999,999), rounding off, bases (Base Five and Base Two conversions).",
            "3. Operations on Whole Numbers": "Combined arithmetic operations with large numbers and application word problems.",
            "4. Patterns and Sequences": "Fibonacci-type sequences, complex number patterns, finding general terms.",
            "5. Fractions": "Reciprocals, division of fractions, percentages of quantities, commercial arithmetic (simple interest).",
            "6. Lines, Angles and Geometric Figures": "Angles on parallel lines, properties of circles (radius, diameter, circumference).",
            "7. Data Handling": "Constructing and interpreting pie charts, bar-line graphs, calculating median and mode.",
            "8. Time": "Travel graphs, speed-distance-time word problems, time zone calculations.",
            "9. Integers": "Multiplication and division of integers, coordinate plotting on Cartesian plane.",
            "10. Money": "Foreign exchange rates, utility bills (water/electricity), profit/loss percentages.",
            "11. Length, Mass and Capacity": "Area of trapeziums and rings, volume and surface area of cylinders.",
            "12. Algebra": "Expanding brackets, factorisation, solving simultaneous linear equations."
        },
        "2. English": {
            "Topic 1: Reported Speech, Passive Voice & Debating": "Direct to indirect speech, active to passive voice, conditional sentences, debate motions."
        },
        "3. Integrated Science": {
            "Topic 1: Electricity, Simple Machines & Reproduction": "Simple electric circuits, levers/pulleys, mammalian reproduction, adolescence, immunity."
        },
        "4. Social Studies (SST)": {
            "Topic 1: East African Geography & Independence Struggles": "EAC countries, resources, European scramble/partition, resistance movements, independence."
        },
        "5. Religious Education (CRE/IRE)": {
            "Topic 1: Faith in Action, Work Ethics & Reconciliation": "Stewardship of resources, dignity of work, marriage/family values, conflict resolution."
        },
        "6. Creative Arts & Physical Education (CAPE)": {
            "Topic 1: Athletics, Sculpture and Drama": "Track events, first aid procedures, papier-mâché, and issue-based drama."
        }
    },
    "P7": {
        "1. Mathematics (12 Strands PLE Mastery)": {
            "1. Set Concepts": "Application of set concepts in solving 2-set and 3-set Venn diagram word problems.",
            "2. Whole Numbers": "Standard form (scientific notation), non-decimal number bases (Base Two, Five, Eight operations).",
            "3. Operations on Whole Numbers": "Comprehensive word problems and number theory applications for PLE.",
            "4. Patterns and Sequences": "Advanced progressions, sequence formulas, and algebraic pattern proofs.",
            "5. Fractions": "Complex fraction equations, recurring decimals to fractions, advanced commercial arithmetic.",
            "6. Geometric Construction": "Constructing perpendiculars, angle bisectors, 60°, 30°, 90°, 45° angles, triangles and quadrilaterals.",
            "7. Data Handling": "Probability, combined data interpretation, advanced mean/median/mode problem solving.",
            "8. Time": "Advanced speed-distance-time word problems, average speed calculations for multiple journeys.",
            "9. Integers": "Simultaneous inequalities, advanced coordinate geometry applications.",
            "10. Money": "Compound interest basics, complex profit/loss, and taxation problems.",
            "11. Length, Mass and Capacity": "Composite area problems, capacity of complex reservoirs, surface area and volume of composite solids.",
            "12. Algebra": "Simultaneous equations, algebraic word problems, forming and solving quadratic expressions."
        },
        "2. English": {
            "Topic 1: PLE Grammar Consolidation, Idioms & Summary": "Phrasal verbs, idioms, synonyms/antonyms, passage summary writing, timed comprehension."
        },
        "3. Integrated Science": {
            "Topic 1: Excretory & Nervous Systems, Livestock & Environment": "Kidneys, skin, brain/spinal cord reflex actions, poultry/cattle management, pollution control."
        },
        "4. Social Studies (SST)": {
            "Topic 1: Geography of Africa, Pan-Africanism & Global Bodies": "Climate/vegetation of Africa, decolonization, African Union (AU), United Nations (UN), global trade."
        },
        "5. Religious Education (CRE/IRE)": {
            "Topic 1: Moral Theology, Human Dignity & Social Responsibility": "Ethical responses to modern challenges, human rights/dignity, comprehensive PLE revision."
        },
        "6. Creative Arts & Physical Education (CAPE)": {
            "Topic 1: Leadership, Fitness Management & Entrepreneurial Crafts": "Sports officiating, marketing crafts, and practical art exhibitions."
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
    st.caption("Integrated Learning Environment — All Subjects & Official NCDC Curriculum Topics")
    st.write("Select a class, subject, and topic to view detailed learning outcomes, instructional materials, life skills, and values.")
    
    col1, col2 = st.columns(2)
    with col1:
        selected_class = st.selectbox("1. Select Class", [f"P{i}" for i in range(1, 8)], key="tb_class")
    
    class_subjects = TOPICAL_BREAKDOWN.get(selected_class, {})
    with col2:
        selected_subject = st.selectbox("2. Select Subject / Learning Area", list(class_subjects.keys()), key="tb_subject")
    
    subject_topics = class_subjects.get(selected_subject, {})
    
    # Check if subject_topics is a dictionary or string
    if isinstance(subject_topics, dict):
        selected_topic = st.selectbox("3. Select Topic", list(subject_topics.keys()), key="tb_topic")
        st.markdown("---")
        topic_details = subject_topics.get(selected_topic, {})
        if isinstance(topic_details, dict):
            st.subheader(f"{selected_class} • {selected_subject}")
            st.markdown(f"### 📌 {selected_topic}")
            st.info(f"**Learning Outcome:** {topic_details.get('Learning Outcome', '')}")
            st.markdown(f"**Subtopics:** {topic_details.get('Subtopics', '')}")
            st.markdown(f"**Learning Aids / Instructional Materials:** {topic_details.get('Learning Aids', '')}")
            st.markdown(f"**Life Skills Acquired:** {topic_details.get('Life Skills', '')}")
            st.markdown(f"**Core Values Inculcated:** {topic_details.get('Values', '')}")
        else:
            st.subheader(f"{selected_class} • {selected_subject}")
            st.info(topic_details)
    else:
        st.markdown("---")
        st.subheader(f"{selected_class} • {selected_subject}")
        st.info(subject_topics)

elif page == "NCDC Curriculum Overview":
    st.title("📚 NCDC Curriculum Overview")
    st.caption("Integrated Learning Environment — Thematic (P1–P3) & Subject-Based (P4–P7) Frameworks")
    
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
