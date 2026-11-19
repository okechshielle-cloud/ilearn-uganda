import io
import random
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")  # Headless backend required for Streamlit Community Cloud
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

# Must be the very first Streamlit call
st.set_page_config(page_title="iLearn-Uganda | Primary Maths", layout="wide")


# ==============================================================================
# 1. IN-MEMORY DIAGRAM GENERATOR (CACHED PNG BYTES)
# ==============================================================================

@st.cache_data(show_spinner=False)
def get_diagram_png(diagram_type: str) -> Optional[bytes]:
    """Generates clean mathematical diagrams in memory as PNG bytes."""
    buf = io.BytesIO()

    if diagram_type == "venn":
        fig, ax = plt.subplots(figsize=(5.8, 4.2))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 7.5)
        ax.set_aspect("equal")
        ax.axis("off")

        univ = patches.Rectangle((0.6, 0.5), 8.8, 6.2, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(univ)
        ax.text(0.6, 6.85, "E", fontsize=14, fontweight="bold")

        circle_a = patches.Circle((3.9, 3.6), 2.1, linewidth=2, edgecolor="black", facecolor="none")
        circle_b = patches.Circle((6.1, 3.6), 2.1, linewidth=2, edgecolor="black", facecolor="none")
        ax.add_patch(circle_a)
        ax.add_patch(circle_b)

        ax.text(2.7, 5.1, "A", fontsize=13, fontweight="bold")
        ax.text(7.1, 5.1, "B", fontsize=13, fontweight="bold")

        ax.text(2.5, 4.0, "e", fontsize=13)
        ax.text(2.8, 2.5, "f", fontsize=13)
        ax.text(4.9, 4.1, "a", fontsize=13)
        ax.text(4.9, 2.8, "i", fontsize=13)
        ax.text(7.2, 4.0, "b", fontsize=13)
        ax.text(7.0, 2.5, "c", fontsize=13)
        ax.text(8.5, 1.0, "g", fontsize=13)

        plt.tight_layout()
        fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    if diagram_type == "marks_table":
        fig, ax = plt.subplots(figsize=(7.2, 1.8))
        ax.axis("off")
        columns = ["Maths", "Eng", "SST", "SCI", "CAPE 1", "Kiswahili"]
        rows = [["70", "80", "70", "50", "90", "50"]]
        table = ax.table(cellText=rows, colLabels=columns, cellLoc="center", loc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1.1, 1.8)
        plt.tight_layout()
        fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    if diagram_type == "okello_land":
        fig, ax = plt.subplots(figsize=(6.2, 4.5))
        ax.set_xlim(-1.3, 11.6)
        ax.set_ylim(-1.2, 9.0)
        ax.set_aspect("equal")
        ax.axis("off")

        # Bottom plot R (Cattle): 10m x 5m
        plot_r = patches.Rectangle((0, 0), 10, 5, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(plot_r)
        ax.text(5.0, 2.3, "R", fontsize=14, fontweight="bold", ha="center")
        ax.text(5.0, -0.75, "10 m", fontsize=12, fontweight="bold", ha="center")
        ax.text(10.35, 2.4, "5 m", fontsize=12, fontweight="bold", va="center")

        # Top-left plot P (Goats): 4m x 3m
        plot_p = patches.Rectangle((0, 5), 4, 3, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(plot_p)
        ax.text(2.0, 6.3, "P", fontsize=14, fontweight="bold", ha="center")
        ax.text(2.0, 5.25, "4 m", fontsize=11, ha="center")
        ax.text(-1.05, 6.4, "3 m", fontsize=12, fontweight="bold", va="center")

        # Top-right plot Q (Pigs): 6m x 3m
        plot_q = patches.Rectangle((4, 5), 6, 3, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(plot_q)
        ax.text(7.0, 6.3, "Q", fontsize=14, fontweight="bold", ha="center")

        plt.tight_layout()
        fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    return None


# ==============================================================================
# 2. NCDC PRIMARY MATHEMATICS CURRICULUM (P1 - P7)
# ==============================================================================

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
            "language_competences": ["Pronounces and spells number names one to twenty"],
            "learning_aids": ["Bottle tops", "Beans/seeds", "Number flash cards", "Sticks"],
            "life_skills_values": ["Sharing", "Orderliness", "Cooperation"],
            "assessment": ["Oral counting drills", "Sorting observation checklist"],
        },
    ],
    "P2": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Our Environment & Things We Make",
            "topic": "Place Value & Numbers up to 999",
            "periods": 22,
            "sub_topics": ["Tens and Ones", "Introducing Hundreds", "Ordering numbers up to 999"],
            "learning_outcomes": "Learner identifies place values of Hundreds, Tens, and Ones.",
            "subject_competences": ["Bundles sticks in tens and hundreds", "Writes expanded form of 3-digit numbers"],
            "language_competences": ["Reads and writes number words up to nine hundred ninety-nine"],
            "learning_aids": ["Bundles of 10 sticks", "Place value tins", "Abacus"],
            "life_skills_values": ["Critical thinking", "Neatness"],
            "assessment": ["Abacus reading test", "Written place-value exercises"],
        },
    ],
    "P3": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Managing Resources in Our Sub-County",
            "topic": "Multiplication, Division & Basic Fractions",
            "periods": 24,
            "sub_topics": ["Multiplication tables 2, 3, 4, 5, 10", "Sharing equally", "Halves, quarters, and thirds"],
            "learning_outcomes": "Learner applies multiplication and division to real-life sharing.",
            "subject_competences": ["Multiplies 2-digit numbers by 1-digit numbers", "Shades halves, quarters, and thirds"],
            "language_competences": ["Explains terms: multiply, share equally, half, quarter, third"],
            "learning_aids": ["Multiplication grid", "Oranges/paper strips", "Bottle tops"],
            "life_skills_values": ["Fairness", "Resourcefulness"],
            "assessment": ["Speed multiplication test", "Fraction paper-folding task"],
        },
    ],
    "P4": [
        {
            "curriculum_type": "Subject-Based Syllabus (Transition Class)",
            "theme": "Sets & Numeracy",
            "topic": "Set Concepts, Whole Numbers & Fractions",
            "periods": 40,
            "sub_topics": ["Venn diagrams (Union & Intersection)", "Place value up to 99,999", "Roman numerals (I to L)", "Fractions"],
            "learning_outcomes": "Learner forms sets using Venn diagrams and manipulates numbers up to 99,999.",
            "subject_competences": ["Represents union and intersection on a Venn diagram", "Converts Hindu-Arabic and Roman numerals"],
            "language_competences": ["Uses English set and fraction vocabulary accurately"],
            "learning_aids": ["Hula hoops/strings", "Place value chart", "Fraction strips"],
            "life_skills_values": ["Classification skills", "Logical reasoning"],
            "assessment": ["Venn diagram drawing exercise", "Weekly continuous assessment"],
        },
    ],
    "P5": [
        {
            "curriculum_type": "Subject-Based Syllabus",
            "theme": "Numeracy & Geometry",
            "topic": "Number Patterns, Angles, Perimeter & Area",
            "periods": 46,
            "sub_topics": ["Place value up to Millions", "Prime factorization, LCM and GCF", "Lines, angles, perimeter and area"],
            "learning_outcomes": "Learner finds LCM/GCF and computes perimeter, area, and profit/loss.",
            "subject_competences": ["Finds LCM and GCF using prime factors", "Calculates area of triangles and rectangles"],
            "language_competences": ["Articulates mathematical reasoning in English"],
            "learning_aids": ["Abacus (7 spikes)", "Factor tree charts", "Mathematical set"],
            "life_skills_values": ["Analytical thinking", "Accuracy"],
            "assessment": ["Power test on LCM/GCF", "Geometry construction practical"],
        },
    ],
    "P6": [
        {
            "curriculum_type": "Subject-Based Syllabus",
            "theme": "Sets, Numeracy, Measurement & Data Handling",
            "topic": "Sets, Bases, Fractions, Perimeter/Area, Statistics & Algebra",
            "periods": 48,
            "sub_topics": [
                "Complements and differences of sets on Venn diagrams",
                "Roman numerals and non-decimal number bases",
                "GCF, LCM, and remainder problems",
                "Fractions, percentages, mean, and mode",
                "Perimeter and area of combined rectangles",
                "Simple linear equations",
            ],
            "learning_outcomes": "Learner solves multi-step problems in sets, bases, measurement, statistics, and algebra.",
            "subject_competences": [
                "Lists complements of set differences from Venn diagrams",
                "Converts between base ten and base n",
                "Computes perimeter and area of composite land plots",
                "Calculates mean and identifies modal values",
            ],
            "language_competences": ["Interprets multi-step English word problems accurately"],
            "learning_aids": ["Venn diagram charts", "Base blocks", "Grid paper", "Mid-term mark sheets"],
            "life_skills_values": ["Problem solving", "Financial prudence", "Data interpretation"],
            "assessment": ["Topical competency quiz with diagrams", "Continuous assessment"],
        },
    ],
    "P7": [
        {
            "curriculum_type": "Subject-Based Syllabus (PLE Consolidation)",
            "theme": "Geometry, Measurement & Algebra",
            "topic": "Bearings, Speed-Distance-Time, Volume & Equations",
            "periods": 30,
            "sub_topics": ["Scale drawing and compass bearings", "Speed, distance, and time", "Volume of cylinders and prisms", "Linear equations"],
            "learning_outcomes": "Learner synthesizes upper-primary mathematics for PLE readiness.",
            "subject_competences": ["Calculates average speed and interprets travel graphs", "Solves algebraic equations"],
            "language_competences": ["Justifies multi-step solutions clearly in written English"],
            "learning_aids": ["Mathematical set", "3D solid nets", "Past PLE papers"],
            "life_skills_values": ["Critical thinking", "Self-reliance"],
            "assessment": ["PLE-standard mock topical papers"],
        },
    ],
}


# ==============================================================================
# 3. QUIZ BANK (INCLUDING FULL 14-QUESTION P6 SET WITH DIAGRAMS)
# ==============================================================================

QUIZ_BANK: Dict[str, List[Dict[str, Any]]] = {
    "P1": [
        {"id": "p1_q1", "topic": "Addition up to 20", "marks": 1, "question": "Count the bottle tops: 5 + 3 = ?", "options": ["7", "8", "9", "6"], "ans": "8", "explanation": "5 and 3 altogether make 8.", "diagram_type": None},
    ],
    "P2": [
        {"id": "p2_q1", "topic": "Place Value", "marks": 1, "question": "What is the place value of 4 in 428?", "options": ["Ones", "Tens", "Hundreds", "Thousands"], "ans": "Hundreds", "explanation": "4 is in the Hundreds place.", "diagram_type": None},
    ],
    "P3": [
        {"id": "p3_q1", "topic": "Division", "marks": 1, "question": "Share 24 mangoes equally among 4 pupils. How many does each get?", "options": ["5", "6", "8", "4"], "ans": "6", "explanation": "24 ÷ 4 = 6 mangoes.", "diagram_type": None},
    ],
    "P4": [
        {"id": "p4_q1", "topic": "Set Concepts", "marks": 1, "question": "If Set A = {1, 2, 3, 4} and Set B = {3, 4, 5, 6}, find A ∩ B.", "options": ["{1, 2}", "{3, 4}", "{5, 6}", "{1, 2, 3, 4, 5, 6}"], "ans": "{3, 4}", "explanation": "Common elements are 3 and 4.", "diagram_type": None},
    ],
    "P5": [
        {"id": "p5_q1", "topic": "Number Patterns", "marks": 1, "question": "Find the Lowest Common Multiple (LCM) of 6 and 8.", "options": ["12", "24", "48", "2"], "ans": "24", "explanation": "LCM(6, 8) = 24.", "diagram_type": None},
    ],
    "P6": [
        {
            "id": "p6_q01_sets",
            "topic": "Set Concepts",
            "marks": 1,
            "question": "1– Given that the Venn diagram below, list elements of set (B–A)'.",
            "options": ["{e, f, a, i, g}", "{b, c}", "{a, i}", "{e, f, g}"],
            "ans": "{e, f, a, i, g}",
            "explanation": "B - A = {b, c}, so (B - A)' includes all elements in universal set E outside {b, c}.",
            "diagram_type": "venn",
        },
        {
            "id": "p6_q02_roman",
            "topic": "Whole Numbers & Numerals",
            "marks": 1,
            "question": "2– Write CIX in Hindu Arabic numeral.",
            "options": ["109", "111", "99", "119"],
            "ans": "109",
            "explanation": "C = 100 and IX = 9, so CIX = 100 + 9 = 109.",
            "diagram_type": None,
        },
        {
            "id": "p6_q03_base",
            "topic": "Number Bases",
            "marks": 1,
            "question": "3– Given that 21_n = 11_ten. find the base represented by n.",
            "options": ["Base five", "Base six", "Base four", "Base eight"],
            "ans": "Base five",
            "explanation": "2n + 1 = 11 -> 2n = 10 -> n = 5 (base five).",
            "diagram_type": None,
        },
        {
            "id": "p6_q04_gcf",
            "topic": "Factors & Multiples",
            "marks": 1,
            "question": "4– If Q = 2² × 3² and P = 2 × 3 × 5. find the Greatest Common Factor (G.C.F) of Q and P.",
            "options": ["6", "18", "180", "30"],
            "ans": "6",
            "explanation": "Common prime factors with the lowest powers give 2¹ × 3¹ = 6.",
            "diagram_type": None,
        },
        {
            "id": "p6_q05i_posho",
            "topic": "Fractions & Percentages",
            "marks": 1,
            "question": (
                "5– In a class of 48 pupils who attended a birthday party, 50% of the pupils ate "
                "Matooke, 3/8 ate Rice and the rest ate Posho. (i) Find the fraction of pupils who ate Posho."
            ),
            "options": ["1/8", "3/8", "1/2", "7/8"],
            "ans": "1/8",
            "explanation": "50% = 4/8; 4/8 + 3/8 = 7/8; remaining fraction for Posho = 1 - 7/8 = 1/8.",
            "diagram_type": None,
        },
        {
            "id": "p6_q05ii_diff",
            "topic": "Fractions & Percentages",
            "marks": 2,
            "question": (
                "5– In a class of 48 pupils who attended a birthday party, 50% of the pupils ate "
                "Matooke, 3/8 ate Rice and the rest ate Posho. (ii) How many more pupils ate Matooke than Rice?"
            ),
            "options": ["6", "18", "24", "42"],
            "ans": "6",
            "explanation": "Matooke = 1/2 × 48 = 24; Rice = 3/8 × 48 = 18; difference = 24 - 18 = 6.",
            "diagram_type": None,
        },
        {
            "id": "p6_q06_mode",
            "topic": "Data Handling & Statistics",
            "marks": 1,
            "question": "6– Given that Paul scored the marks given below in the mid-term examination. Find Paul's modal mark.",
            "options": ["70 and 50", "70", "50", "80"],
            "ans": "70 and 50",
            "explanation": "Both 70 and 50 appear twice, making the distribution bimodal with modal marks 70 and 50.",
            "diagram_type": "marks_table",
        },
        {
            "id": "p6_q12i_perimeter",
            "topic": "Measurement & Geometry",
            "marks": 2,
            "question": (
                "12– The diagram below shows how Mr. Okello used his land. He used plot P to keep goats, "
                "plot Q to keep pigs and R to keep cattle. (i) Work out the total distance round the plot he used to keep pigs."
            ),
            "options": ["18 m", "14 m", "20 m", "9 m"],
            "ans": "18 m",
            "explanation": "Plot Q width = 10 m - 4 m = 6 m and height = 3 m, so perimeter = 2 × (6 + 3) = 18 m.",
            "diagram_type": "okello_land",
        },
        {
            "id": "p6_q12ii_area",
            "topic": "Measurement & Geometry",
            "marks": 4,
            "question": (
                "12– (ii) Find the size of the land area he has altogether which keep all his goats, "
                "pigs and cattle in square metres."
            ),
            "options": ["80 sq m", "50 sq m", "36 sq m", "68 sq m"],
            "ans": "80 sq m",
            "explanation": "Total width = 10 m and total height = 3 m + 5 m = 8 m, giving 10 m × 8 m = 80 sq m.",
            "diagram_type": "okello_land",
        },
        {
            "id": "p6_q13_algebra",
            "topic": "Algebra & Equations",
            "marks": 5,
            "question": (
                "13– A boy said that they served with some cups of tea such that if a half of their "
                "total joins them, their sum could be 45. How many boys were they?"
            ),
            "options": ["30", "22.5", "90", "15"],
            "ans": "30",
            "explanation": "x + 0.5x = 45 -> 1.5x = 45 -> x = 30 boys.",
            "diagram_type": None,
        },
        {
            "id": "p6_q14_remainders",
            "topic": "Number Patterns & Remainders",
            "marks": 5,
            "question": (
                "14– Sarah dug two lines of 7 pits and 6 pits respectively. She had some bean seeds in her "
                "hands whereby if she distributes them in the 7 pits equally, 5 seeds remain and if she "
                "distributes them in the one of 6 pits, 2 seeds remain. How many seeds was she having?"
            ),
            "options": ["26", "12", "19", "47"],
            "ans": "26",
            "explanation": "26 ÷ 7 = 3 remainder 5, and 26 ÷ 6 = 4 remainder 2.",
            "diagram_type": None,
        },
        {
            "id": "p6_q15_mean",
            "topic": "Statistics & Mean",
            "marks": 5,
            "question": (
                "15– The mean mass of 5 boys is 30 kg. When their teacher joins them, the mean mass "
                "changes to 24. Find the mass of the teacher."
            ),
            "options": ["-6 kg", "6 kg", "144 kg", "150 kg"],
            "ans": "-6 kg",
            "explanation": "5 boys sum = 5 × 30 = 150 kg; 6 people sum = 6 × 24 = 144 kg; difference = 144 - 150 = -6 kg.",
            "diagram_type": None,
        },
        {
            "id": "p6_q16a_factors",
            "topic": "Factors & Multiples",
            "marks": 2,
            "question": "16– (a) List all the factors of 12.",
            "options": ["1, 2, 3, 4, 6, 12", "12, 24, 36, 48", "2, 3, 4, 6", "1, 2, 3, 6, 12"],
            "ans": "1, 2, 3, 4, 6, 12",
            "explanation": "The factors of 12 are 1, 2, 3, 4, 6, and 12.",
            "diagram_type": None,
        },
        {
            "id": "p6_q16b_lcm",
            "topic": "Factors & Multiples (LCM)",
            "marks": 3,
            "question": (
                "16– (b) What is the least number of sweets that can be shared by either "
                "6 or 8 boys equally without a remainder?"
            ),
            "options": ["24", "48", "12", "2"],
            "ans": "24",
            "explanation": "The least number divisible by both 6 and 8 is LCM(6, 8) = 24.",
            "diagram_type": None,
        },
    ],
    "P7": [
        {"id": "p7_q1", "topic": "Speed, Distance & Time", "marks": 2, "question": "A bus travels 180 km in 3 hours. Calculate its average speed.", "options": ["50 km/h", "60 km/h", "90 km/h", "540 km/h"], "ans": "60 km/h", "explanation": "Speed = 180 ÷ 3 = 60 km/h.", "diagram_type": None},
    ],
}


# ==============================================================================
# 4. TRADITIONAL UGANDAN OMWESO ENGINE
# ==============================================================================

class OmwesoGame:
    def __init__(self):
        self.board = [
            [4] * 8 + [0] * 8,
            [4] * 8 + [0] * 8,
        ]
        self.turn = 0
        self.log = ["Board set with 32 seeds each. Ready for play!"]

    def get_opposite_enemy_pits(self, inner_idx: int):
        col_from_left = 15 - inner_idx
        opp_inner = 8 + col_from_left
        opp_outer = 7 - col_from_left
        return opp_inner, opp_outer

    def sow(self, player: int, pit_idx: int, reverse: bool = False) -> bool:
        seeds = self.board[player][pit_idx]
        if seeds < 2:
            self.log.append("Invalid move: Pick a pit with at least 2 seeds.")
            return False

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

            if self.board[player][curr] > 1:
                if 8 <= curr <= 15:
                    opp_inner, opp_outer = self.get_opposite_enemy_pits(curr)
                    if self.board[opp][opp_inner] > 0 and self.board[opp][opp_outer] > 0:
                        captured = self.board[opp][opp_inner] + self.board[opp][opp_outer]
                        self.board[opp][opp_inner] = 0
                        self.board[opp][opp_outer] = 0
                        seeds = captured
                        self.log.append(f"Player {player+1} captured {captured} seeds from opposite inner & outer pits!")
                        continue

                seeds = self.board[player][curr]
                self.board[player][curr] = 0
            else:
                break

        self.turn = opp
        return True


# ==============================================================================
# 5. STREAMLIT UI
# ==============================================================================

def main() -> None:
    st.title("🇺🇬 iLearn-Uganda: NCDC Primary Mathematics (P1 – P7)")

    if "quiz_scores" not in st.session_state:
        st.session_state.quiz_scores = {
            cls: {"attempted": 0, "correct": 0, "marks_earned": 0, "marks_total": 0}
            for cls in NCDC_MATH_CURRICULUM
        }
    if "answered_q_ids" not in st.session_state:
        st.session_state.answered_q_ids = set()
    if "omweso" not in st.session_state:
        st.session_state.omweso = OmwesoGame()

    # Default to P6 (index 5) so your P6 illustrated quiz opens immediately
    selected_class = st.sidebar.selectbox("Select Class Level", list(NCDC_MATH_CURRICULUM.keys()), index=5)

    tab_quiz, tab_syllabus, tab_dashboard, tab_omweso = st.tabs([
        "📝 Class Quiz (With Diagrams)",
        "📚 NCDC Syllabus Explorer",
        "📊 Learner & Teacher Dashboard",
        "🎲 Traditional Omweso Lab",
    ])

    # --- TAB 1: CLASS-SPECIFIC QUIZ WITH IN-MEMORY DIAGRAMS ---
    with tab_quiz:
        st.subheader(f"{selected_class} Competency Quiz")
        questions = QUIZ_BANK.get(selected_class, [])

        for i, q_data in enumerate(questions):
            st.markdown(f"**{q_data['question']}** *(Topic: {q_data['topic']} | {q_data.get('marks', 1)} mark(s))*")

            # Render diagram directly from cached PNG bytes
            diag_type = q_data.get("diagram_type")
            if diag_type:
                png_bytes = get_diagram_png(diag_type)
                if png_bytes:
                    st.image(png_bytes, caption=f"Diagram for {q_data['topic']}", width=480)

            choice = st.radio("Choose your answer:", q_data["options"], key=f"q_{selected_class}_{i}")
            if st.button("Check Answer", key=f"btn_{selected_class}_{i}"):
                q_key = f"{selected_class}:{q_data['id']}"
                is_correct = choice == q_data["ans"]
                marks = q_data.get("marks", 1)

                if q_key not in st.session_state.answered_q_ids:
                    st.session_state.answered_q_ids.add(q_key)
                    st.session_state.quiz_scores[selected_class]["attempted"] += 1
                    st.session_state.quiz_scores[selected_class]["marks_total"] += marks
                    if is_correct:
                        st.session_state.quiz_scores[selected_class]["correct"] += 1
                        st.session_state.quiz_scores[selected_class]["marks_earned"] += marks

                if is_correct:
                    st.success(f"Correct! {q_data['explanation']}")
                else:
                    st.error(f"Not quite. The correct answer is **{q_data['ans']}**. {q_data['explanation']}")
            st.divider()

    # --- TAB 2: NCDC SYLLABUS EXPLORER ---
    with tab_syllabus:
        st.subheader(f"{selected_class} Mathematics — Official NCDC Structure")
        for idx, item in enumerate(NCDC_MATH_CURRICULUM[selected_class], 1):
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

    # --- TAB 3: LEARNER & TEACHER DASHBOARD ---
    with tab_dashboard:
        st.subheader("📊 Curriculum Coverage & Quiz Analytics")
        p6_stats = st.session_state.quiz_scores["P6"]
        p6_max_marks = sum(q.get("marks", 1) for q in QUIZ_BANK["P6"])
        c1, c2, c3 = st.columns(3)
        c1.metric("P6 Questions Attempted", f"{p6_stats['attempted']} / {len(QUIZ_BANK['P6'])}")
        c2.metric("P6 Correct Answers", p6_stats["correct"])
        c3.metric("P6 Marks Scored", f"{p6_stats['marks_earned']} / {p6_max_marks}")

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
                "Accuracy (%)": accuracy,
            })
        df_dash = pd.DataFrame(summary_rows)
        st.dataframe(df_dash, use_container_width=True)

    # --- TAB 4: TRADITIONAL UGANDAN OMWESO ---
    with tab_omweso:
        st.subheader("🎲 Traditional Ugandan Omweso")
        game: OmwesoGame = st.session_state.omweso

        st.markdown("**Opponent Side (Row B Outer / Row A Inner)**")
        opp_outer_cols = st.columns(8)
        for col_i in range(8):
            opp_outer_cols[col_i].metric(f"B{col_i+1}", game.board[1][col_i])
        opp_inner_cols = st.columns(8)
        for col_i in range(8):
            idx = 15 - col_i
            opp_inner_cols[col_i].metric(f"A{col_i+1}", game.board[1][idx])

        st.divider()

        st.markdown("**Your Side (Inner Row A / Outer Row B)**")
        p0_inner_cols = st.columns(8)
        for col_i in range(8):
            idx = 15 - col_i
            p0_inner_cols[col_i].metric(f"Inner {col_i+1} [#{idx}]", game.board[0][idx])
        p0_outer_cols = st.columns(8)
        for col_i in range(8):
            p0_outer_cols[col_i].metric(f"Outer {col_i+1} [#{col_i}]", game.board[0][col_i])

        ctrl_col1, ctrl_col2, ctrl_col3 = st.columns([2, 1, 1])
        with ctrl_col1:
            valid_pits = [i for i in range(16) if game.board[0][i] >= 2]
            selected_pit = st.selectbox(
                "Choose your pit to sow (≥ 2 seeds):",
                options=valid_pits,
                format_func=lambda i: f"Pit #{i} ({game.board[0][i]} seeds)",
            )
        with ctrl_col2:
            reverse_opt = st.checkbox("Reverse sow (Left-corner pits 0, 1, 14, 15 only)")
        with ctrl_col3:
            if st.button("Sow Seeds") and selected_pit is not None:
                game.sow(0, selected_pit, reverse=reverse_opt)
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
