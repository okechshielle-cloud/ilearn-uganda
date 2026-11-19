import streamlit as st
import pandas as pd
import random
from typing import List, Dict, Any

# ==============================================================================
# 1. NCDC PRIMARY MATHEMATICS CURRICULUM DATA (P1 - P7)
# ==============================================================================
# P1 - P3 follows the NCDC Thematic Curriculum (Themes -> Sub-themes -> Math Competences)
# P4 - P7 follows the NCDC Subject-Based Syllabus (Themes -> Topics -> Competences)

NCDC_MATH_CURRICULUM: Dict[str, List[Dict[str, Any]]] = {
    "P1": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Our School and Neighbourhood",
            "topic": "Pre-Number Activities & Counting (1–20)",
            "periods": 18,
            "sub_topics": ["Sorting and grouping objects", "Matching sets", "Counting 1 to 20", "Writing number symbols 1–9"],
            "learning_outcomes": "Learner counts, sorts, and relates real objects in the school environment to numbers up to 20.",
            "subject_competences": ["Sorts bottle tops and seeds by colour/size", "Counts concrete objects accurately up to 20"],
            "language_competences": ["Pronounces and spells number names one to twenty in English and local language"],
            "learning_aids": ["Bottle tops", "Beans/seeds", "Number flash cards", "Sticks"],
            "life_skills_values": ["Sharing", "Orderliness", "Cooperation"],
            "assessment": ["Oral counting drills", "Sorting observation checklist"]
        },
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Our Home and Community",
            "topic": "Basic Operations (Addition & Subtraction up to 20)",
            "periods": 20,
            "sub_topics": ["Putting together (sum less than 20)", "Taking away using concrete objects", "Number bonds of 10"],
            "learning_outcomes": "Learner solves simple everyday addition and subtraction stories using counters.",
            "subject_competences": ["Adds two single-digit numbers using counters", "Subtracts single-digit numbers from numbers up to 20"],
            "language_competences": ["Uses words: add, altogether, take away, remain, equals"],
            "learning_aids": ["Counters", "Number line on floor", "Abacus"],
            "life_skills_values": ["Accuracy", "Honesty when sharing items"],
            "assessment": ["Practical counter tasks", "Simple picture-story sums"]
        }
    ],
    "P2": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Our Environment & Things We Make",
            "topic": "Place Value & Numbers up to 999",
            "periods": 22,
            "sub_topics": ["Tens and Ones", "Introducing Hundreds", "Ordering numbers up to 999", "Skip counting in 2s, 5s, and 10s"],
            "learning_outcomes": "Learner identifies place values of Hundreds, Tens, and Ones and orders numbers up to 999.",
            "subject_competences": ["Bundles sticks in tens and hundreds", "Writes expanded form of 3-digit numbers"],
            "language_competences": ["Reads and writes number words up to nine hundred ninety-nine"],
            "learning_aids": ["Bundles of 10 sticks", "Place value tins", "Abacus"],
            "life_skills_values": ["Critical thinking", "Neatness"],
            "assessment": ["Abacus reading test", "Written place-value exercises"]
        },
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Transport and Communication",
            "topic": "Measurement: Ugandan Currency & Time",
            "periods": 16,
            "sub_topics": ["Identifying UGX coins and notes (100 to 5,000)", "Simple shopping bills", "Days of the week and telling time by the hour"],
            "learning_outcomes": "Learner recognizes Ugandan currency denominations and performs basic shopping transactions.",
            "subject_competences": ["Calculates total cost and change within UGX 5,000", "Reads clock faces to the exact hour"],
            "language_competences": ["Uses terms: shillings, cost, change, hour, o'clock"],
            "learning_aids": ["Model UGX notes/coins", "Classroom shop corner", "Clock face"],
            "life_skills_values": ["Financial literacy", "Integrity", "Time management"],
            "assessment": ["Role-play classroom shop", "Clock-reading drill"]
        }
    ],
    "P3": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Managing Resources in Our Sub-County",
            "topic": "Multiplication, Division & Basic Fractions",
            "periods": 24,
            "sub_topics": ["Multiplication tables 2, 3, 4, 5, 10", "Sharing equally (division without remainder)", "Halves, quarters, and thirds of a whole"],
            "learning_outcomes": "Learner applies multiplication and division to real-life sharing and identifies simple fractions.",
            "subject_competences": ["Multiplies 2-digit numbers by 1-digit numbers", "Shades halves, quarters, and thirds accurately"],
            "language_competences": ["Explains terms: multiply, share equally, half, quarter, third"],
            "learning_aids": ["Multiplication grid", "Oranges/paper strips for folding", "Bottle tops"],
            "life_skills_values": ["Fairness", "Resourcefulness"],
            "assessment": ["Speed multiplication test", "Fraction paper-folding task"]
        }
    ],
    "P4": [
        {
            "curriculum_type": "Subject-Based Syllabus (Transition Class)",
            "theme": "Sets",
            "topic": "Set Concepts",
            "periods": 14,
            "sub_topics": ["Naming and listing members of a set", "Equivalent and equal sets", "Empty sets", "Intersection and Union of two sets (Venn diagrams)"],
            "learning_outcomes": "Learner forms, compares, and represents sets using Venn diagrams in English.",
            "subject_competences": ["Identifies common elements in two sets", "Represents union and intersection on a 2-circle Venn diagram"],
            "language_competences": ["Uses English set vocabulary: member, element, subset, empty, union, intersection"],
            "learning_aids": ["Real classroom objects", "Hula hoops/strings for Venn diagrams", "Flash cards"],
            "life_skills_values": ["Classification skills", "Logical reasoning", "Teamwork"],
            "assessment": ["Venn diagram drawing exercise", "Oral vocabulary check"]
        },
        {
            "curriculum_type": "Subject-Based Syllabus (Transition Class)",
            "theme": "Numeracy",
            "topic": "Whole Numbers & Fractions",
            "periods": 26,
            "sub_topics": ["Place value up to Ten Thousands (99,999)", "Roman numerals (I to L)", "Types of fractions (proper, improper, mixed)", "Addition and subtraction of fractions with same denominator"],
            "learning_outcomes": "Learner manipulates whole numbers up to 99,999 and performs basic operations on fractions.",
            "subject_competences": ["Converts between Hindu-Arabic and Roman numerals", "Converts improper fractions to mixed numbers"],
            "language_competences": ["Reads and writes five-digit numbers and fraction terms in English"],
            "learning_aids": ["Place value chart", "Fraction strips", "Roman numeral cards"],
            "life_skills_values": ["Precision", "Problem solving"],
            "assessment": ["Weekly continuous assessment test", "Fraction strip practical"]
        }
    ],
    "P5": [
        {
            "curriculum_type": "Subject-Based Syllabus",
            "theme": "Numeracy",
            "topic": "Whole Numbers, Operations & Number Patterns",
            "periods": 24,
            "sub_topics": ["Place value up to Millions", "Divisibility tests (2, 3, 4, 5, 10)", "Prime factorization, LCM and GCF", "Rounding off whole numbers"],
            "learning_outcomes": "Learner applies place value up to millions and uses prime factorization to find LCM and GCF.",
            "subject_competences": ["Finds LCM and GCF using prime factor trees/ladders", "Applies divisibility rules to solve word problems"],
            "language_competences": ["Articulates mathematical reasoning using: factor, multiple, divisible, prime, composite"],
            "learning_aids": ["Abacus (7 spikes)", "Factor tree charts", "Number grids"],
            "life_skills_values": ["Analytical thinking", "Perseverance"],
            "assessment": ["Power test on LCM/GCF", "Peer-explained board work"]
        },
        {
            "curriculum_type": "Subject-Based Syllabus",
            "theme": "Measurement & Geometry",
            "topic": "Lines, Angles, Perimeter & Area",
            "periods": 22,
            "sub_topics": ["Constructing parallel and perpendicular lines", "Measuring angles using a protractor", "Perimeter and area of rectangles, squares, and triangles", "Ugandan currency bills and profit/loss"],
            "learning_outcomes": "Learner constructs geometric figures accurately and computes perimeter, area, and simple profit/loss.",
            "subject_competences": ["Measures acute, right, and obtuse angles", "Calculates area of triangles and combined shapes"],
            "language_competences": ["Describes geometric properties: parallel, perpendicular, vertex, acute, obtuse"],
            "learning_aids": ["Mathematical set (protractor, ruler, compass)", "Manila cutouts", "Sample market price lists"],
            "life_skills_values": ["Accuracy", "Entrepreneurship awareness"],
            "assessment": ["Geometry construction practical", "Market-bill project"]
        }
    ],
    "P6": [
        {
            "curriculum_type": "Subject-Based Syllabus",
            "theme": "Numeracy & Data Handling",
            "topic": "Ratios, Proportions, Percentages & Data Graphs",
            "periods": 26,
            "sub_topics": ["Direct and inverse proportion", "Percentage increase/decrease and simple interest", "Mean, median, mode, and range", "Drawing and interpreting pie charts and line graphs"],
            "learning_outcomes": "Learner solves proportional and financial problems and interprets statistical graphs.",
            "subject_competences": ["Calculates simple interest (PRT/100)", "Constructs pie charts using angle sectors (360 degrees)"],
            "language_competences": ["Interprets statistical and financial terms: principal, rate, interest, ratio, sector"],
            "learning_aids": ["Protractor and compass", "Graph paper", "Local census/school attendance data"],
            "life_skills_values": ["Financial prudence", "Data-driven decision making"],
            "assessment": ["School survey pie-chart project", "Word-problem evaluation"]
        }
    ],
    "P7": [
        {
            "curriculum_type": "Subject-Based Syllabus (PLE Consolidation)",
            "theme": "Geometry, Measurement & Algebra",
            "topic": "Bearings, Speed-Distance-Time, Volume & Equations",
            "periods": 30,
            "sub_topics": ["Scale drawing and compass bearings", "Speed, distance, and time (travel graphs)", "Surface area and volume of cylinders, prisms, and cubes", "Solving linear equations and inequalities"],
            "learning_outcomes": "Learner synthesizes upper-primary mathematics to solve multi-step PLE-standard problems.",
            "subject_competences": ["Calculates average speed and interprets distance-time graphs", "Solves algebraic equations with brackets and fractions"],
            "language_competences": ["Justifies multi-step solutions clearly in written English"],
            "learning_aids": ["Mathematical set", "3D solid nets (cylinders/prisms)", "Past PLE topical papers"],
            "life_skills_values": ["Critical thinking", "Self-reliance", "Exam readiness"],
            "assessment": ["PLE-standard mock topical papers", "3D net construction model"]
        }
    ]
}

# ==============================================================================
# 2. CLASS-SPECIFIC QUIZ BANK (P1 - P7)
# ==============================================================================

QUIZ_BANK: Dict[str, List[Dict[str, Any]]] = {
    "P1": [
        {"q": "Count the bottle tops: 🟢🟢🟢🟢🟢 + 🟢🟢🟢 = ?", "options": ["7", "8", "9", "6"], "ans": "8", "topic": "Addition up to 20"},
        {"q": "Which number comes right after 14?", "options": ["13", "15", "16", "12"], "ans": "15", "topic": "Counting 1–20"}
    ],
    "P2": [
        {"q": "What is the place value of 4 in the number 428?", "options": ["Ones", "Tens", "Hundreds", "Thousands"], "ans": "Hundreds", "topic": "Place Value"},
        {"q": "A pencil costs UGX 500. How much do 2 pencils cost?", "options": ["UGX 700", "UGX 1,000", "UGX 1,500", "UGX 500"], "ans": "UGX 1,000", "topic": "Ugandan Currency"}
    ],
    "P3": [
        {"q": "Share 24 mangoes equally among 4 pupils. How many does each get?", "options": ["5", "6", "8", "4"], "ans": "6", "topic": "Division"},
        {"q": "What is 1/4 of 12 oranges?", "options": ["4", "3", "6", "2"], "ans": "3", "topic": "Basic Fractions"}
    ],
    "P4": [
        {"q": "If Set A = {1, 2, 3, 4} and Set B = {3, 4, 5, 6}, find A ∩ B.", "options": ["{1, 2}", "{3, 4}", "{5, 6}", "{1, 2, 3, 4, 5, 6}"], "ans": "{3, 4}", "topic": "Set Concepts"},
        {"q": "Write 24 in Roman numerals.", "options": ["XXVI", "XXIV", "XIX", "XIV"], "ans": "XXIV", "topic": "Whole Numbers"}
    ],
    "P5": [
        {"q": "Find the Lowest Common Multiple (LCM) of 6 and 8.", "options": ["12", "24", "48", "2"], "ans": "24", "topic": "Number Patterns"},
        {"q": "A trader bought a bag of posho at UGX 45,000 and sold it at UGX 52,000. Find the profit.", "options": ["UGX 6,000", "UGX 7,000", "UGX 8,000", "UGX 97,000"], "ans": "UGX 7,000", "topic": "Measurement & Money"}
    ],
    "P6": [
        {"q": "Calculate the simple interest on UGX 200,000 for 2 years at 5% per annum.", "options": ["UGX 10,000", "UGX 20,000", "UGX 40,000", "UGX 15,000"], "ans": "UGX 20,000", "topic": "Percentages & Interest"},
        {"q": "Find the mean of 4, 6, 8, and 10.", "options": ["6", "7", "8", "28"], "ans": "7", "topic": "Data Handling"}
    ],
    "P7": [
        {"q": "A bus travels 180 km in 3 hours. Calculate its average speed.", "options": ["50 km/h", "60 km/h", "90 km/h", "540 km/h"], "ans": "60 km/h", "topic": "Speed, Distance & Time"},
        {"q": "Solve for x: 3(x - 2) = 15", "options": ["x = 5", "x = 7", "x = 3", "x = 17"], "ans": "x = 7", "topic": "Algebra"}
    ]
}

# ==============================================================================
# 3. TRADITIONAL UGANDAN OMWESO ENGINE (LOCAL RULES)
# ==============================================================================
# Board indexing (32 pits total: 16 per player, 2 rows of 8)
# Player 0 (Bottom / Learner):
#   Outer row (indices 0..7): left to right [0, 1, 2, 3, 4, 5, 6, 7]
#   Inner row (indices 8..15): right to left [15, 14, 13, 12, 11, 10, 9, 8]
#   Counter-clockwise loop for Player 0: 0 -> 1 -> 2 -> 3 -> 4 -> 5 -> 6 -> 7 -> 8 -> 9 -> 10 -> 11 -> 12 -> 13 -> 14 -> 15 -> 0
#   Left-corner pits (conditional reverse sowing):
#     Outer-left = index 0, Inner-left = index 15 (and adjacent left-corner pair 1, 14)

class OmwesoGame:
    def __init__(self):
        # Standard 32 seeds per side (e.g., 4 seeds in each of the 8 outer pits, or balanced setup)
        self.board = [
            [4]*8 + [0]*8,  # Player 0 (Learner)
            [4]*8 + [0]*8   # Player 1 (AI / Partner)
        ]
        self.turn = 0
        self.log = ["Board set with 32 seeds each. Ready for simultaneous or turn-based start!"]

    def get_opposite_enemy_pits(self, player: int, inner_idx: int):
        """
        Maps Player's inner-row pit (indices 8..15) to Opponent's front (inner) and back (outer) pits.
        Player 0 inner pits [15..8] align left-to-right with Opponent's inner [8..15] and outer [7..0].
        """
        col_from_left = 15 - inner_idx  # 0 (leftmost) to 7 (rightmost)
        opp_inner = 8 + col_from_left
        opp_outer = 7 - col_from_left
        return opp_inner, opp_outer

    def sow(self, player: int, pit_idx: int, reverse: bool = False):
        seeds = self.board[player][pit_idx]
        if seeds < 2:
            self.log.append("Invalid move: You must pick a pit with at least 2 seeds.")
            return False

        # Validate conditional reverse sowing (only permitted from the 4 left-corner pits: 0, 1, 14, 15)
        left_corner_pits = {0, 1, 14, 15}
        if reverse and pit_idx not in left_corner_pits:
            self.log.append("Reverse sowing is only allowed from the 4 left-corner pits!")
            reverse = False

        self.board[player][pit_idx] = 0
        curr = pit_idx
        step = -1 if reverse else 1
        opp = 1 - player

        while True:
            while seeds > 0:
                curr = (curr + step) % 16
                self.board[player][curr] += 1
                seeds -= 1

            # Check if the last seed landed in an occupied pit (relay sowing)
            if self.board[player][curr] > 1:
                # Check Front-Line Capture: must land on inner row (8..15) AND opponent has seeds in BOTH opposite pits
                if 8 <= curr <= 15:
                    opp_inner, opp_outer = self.get_opposite_enemy_pits(player, curr)
                    if self.board[opp][opp_inner] > 0 and self.board[opp][opp_outer] > 0:
                        captured = self.board[opp][opp_inner] + self.board[opp][opp_outer]
                        self.board[opp][opp_inner] = 0
                        self.board[opp][opp_outer] = 0
                        # Captured seeds are sown starting from the origin pit of the current lap
                        seeds = captured
                        self.log.append(f"Player {player+1} captured {captured} seeds from opposite inner & outer pits!")
                        continue

                # Standard relay pickup from current pit
                seeds = self.board[player][curr]
                self.board[player][curr] = 0
            else:
                # Landed in an empty pit -> turn ends
                break

        self.turn = opp
        return True

# ==============================================================================
# 4. STREAMLIT UI: CURRICULUM, QUIZ, DASHBOARD & OMWESO
# ==============================================================================

def main():
    st.set_page_config(page_title="iLearn-Uganda | Primary Maths", layout="wide")
    st.title("🇺🇬 iLearn-Uganda: NCDC Primary Mathematics (P1 – P7)")

    # Initialize session state
    if "quiz_scores" not in st.session_state:
        st.session_state.quiz_scores = {cls: {"attempted": 0, "correct": 0} for cls in NCDC_MATH_CURRICULUM}
    if "omweso" not in st.session_state:
        st.session_state.omweso = OmwesoGame()

    # Sidebar Class & Module Selector
    selected_class = st.sidebar.selectbox("Select Class Level", list(NCDC_MATH_CURRICULUM.keys()), index=4)
    tab_syllabus, tab_quiz, tab_dashboard, tab_omweso = st.tabs([
        "📚 NCDC Syllabus Explorer",
        "📝 Class Quiz",
        "📊 Learner & Teacher Dashboard",
        "🎲 Traditional Omweso Lab"
    ])

    # --- TAB 1: NCDC SYLLABUS EXPLORER ---
    with tab_syllabus:
        st.subheader(f"{selected_class} Mathematics — Official NCDC Structure")
        topics = NCDC_MATH_CURRICULUM[selected_class]
        for idx, item in enumerate(topics, 1):
            with st.expander(f"{idx}. [{item['theme']}] {item['topic']} ({item['periods']} Periods)", expanded=True):
                st.caption(f"**Framework:** {item['curriculum_type']}")
                st.write(f"**Learning Outcome:** {item['learning_outcomes']}")
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Sub-Topics:**")
                    for s in item["sub_topics"]:
                        st.markdown(f"- {s}")
                    st.markdown("**Subject Competences:**")
                    for c in item["subject_competences"]:
                        st.markdown(f"- {c}")
                with col2:
                    st.markdown("**Language Competences:**")
                    for l in item["language_competences"]:
                        st.markdown(f"- {l}")
                    st.markdown(f"**Learning Aids:** {', '.join(item['learning_aids'])}")
                    st.markdown(f"**Life Skills & Values:** {', '.join(item['life_skills_values'])}")
                    st.markdown(f"**Continuous Assessment:** {', '.join(item['assessment'])}")

    # --- TAB 2: CLASS-SPECIFIC QUIZ ---
    with tab_quiz:
        st.subheader(f"{selected_class} Competency Quiz")
        questions = QUIZ_BANK.get(selected_class, [])
        for i, q_data in enumerate(questions):
            st.markdown(f"**Q{i+1} ({q_data['topic']}):** {q_data['q']}")
            choice = st.radio("Choose your answer:", q_data["options"], key=f"q_{selected_class}_{i}")
            if st.button(f"Check Answer {i+1}", key=f"btn_{selected_class}_{i}"):
                st.session_state.quiz_scores[selected_class]["attempted"] += 1
                if choice == q_data["ans"]:
                    st.session_state.quiz_scores[selected_class]["correct"] += 1
                    st.success(f"Correct! Well done.")
                else:
                    st.error(f"Not quite. The correct answer is **{q_data['ans']}**.")
            st.divider()

    # --- TAB 3: PROGRESS DASHBOARD ---
    with tab_dashboard:
        st.subheader("📊 Curriculum Coverage & Quiz Analytics")
        summary_rows = []
        for cls, topics_list in NCDC_MATH_CURRICULUM.items():
            total_periods = sum(t["periods"] for t in topics_list)
            attempted = st.session_state.quiz_scores[cls]["attempted"]
            correct = st.session_state.quiz_scores[cls]["correct"]
            accuracy = round((correct / attempted) * 100, 1) if attempted > 0 else 0.0
            summary_rows.append({
                "Class": cls,
                "Curriculum Model": topics_list[0]["curriculum_type"],
                "Mapped Topics": len(topics_list),
                "Suggested Periods": total_periods,
                "Quizzes Attempted": attempted,
                "Accuracy (%)": accuracy
            })
        df_dash = pd.DataFrame(summary_rows)
        st.dataframe(df_dash, use_container_width=True)
        st.bar_chart(df_dash.set_index("Class")["Suggested Periods"])

    # --- TAB 4: TRADITIONAL UGANDAN OMWESO ---
    with tab_omweso:
        st.subheader("🎲 Traditional Ugandan Omweso (Mental Counting & Strategy)")
        st.caption("Local Rules Active: Simultaneous/Turn start • Front-line capture requires seeds in BOTH opposite inner & outer pits • Reverse sowing permitted from the 4 left-corner pits.")
        game: OmwesoGame = st.session_state.omweso

        # Display Opponent Board (Player 1)
        st.markdown("**Opponent Side (Row B Outer / Row A Inner)**")
        opp_outer_cols = st.columns(8)
        for col_i in range(8):
            opp_outer_cols[col_i].metric(f"B{col_i+1}", game.board[1][col_i])
        opp_inner_cols = st.columns(8)
        for col_i in range(8):
            idx = 15 - col_i
            opp_inner_cols[col_i].metric(f"A{col_i+1}", game.board[1][idx])

        st.divider()

        # Display Learner Board (Player 0)
        st.markdown("**Your Side (Inner Row A / Outer Row B)**")
        p0_inner_cols = st.columns(8)
        for col_i in range(8):
            idx = 15 - col_i
            p0_inner_cols[col_i].metric(f"Inner {col_i+1} [#{idx}]", game.board[0][idx])
        p0_outer_cols = st.columns(8)
        for col_i in range(8):
            p0_outer_cols[col_i].metric(f"Outer {col_i+1} [#{col_i}]", game.board[0][col_i])

        # Move Controls
        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
        with ctrl_col1:
            selected_pit = st.selectbox(
                "Choose your pit to sow (must have ≥ 2 seeds):",
                options=[i for i in range(16) if game.board[0][i] >= 2],
                format_func=lambda i: f"Pit #{i} ({game.board[0][i]} seeds)"
            )
        with ctrl_col2:
            reverse_opt = st.checkbox("Reverse sow (Left-corner pits 0, 1, 14, 15 only)")
        with ctrl_col3:
            if st.button("Sow Seeds"):
                if selected_pit is not None:
                    game.sow(0, selected_pit, reverse=reverse_opt)
                    # Simple AI response for Player 1
                    valid_ai_pits = [i for i in range(16) if game.board[1][i] >= 2]
                    if valid_ai_pits:
                        game.sow(1, random.choice(valid_ai_pits), reverse=False)
                    st.rerun()
            if st.button("Reset Omweso Board"):
                st.session_state.omweso = OmwesoGame()
                st.rerun()

        st.info(f"**Latest Move Log:** {game.log[-1]}")

if __name__ == "__main__":
    main()
