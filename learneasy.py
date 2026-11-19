import random
from typing import Any, Dict, List

import pandas as pd
import streamlit as st

st.set_page_config(page_title="iLearn-Uganda | Primary Maths", layout="wide")

try:
    from p6_quiz_module import P6_QUESTIONS, render_p6_dashboard_card, render_p6_quiz_tab

    P6_MODULE_AVAILABLE = True
    P6_MODULE_ERROR = ""
except Exception as exc:
    P6_QUESTIONS = []
    P6_MODULE_AVAILABLE = False
    P6_MODULE_ERROR = str(exc)


NCDC_MATH_CURRICULUM: Dict[str, List[Dict[str, Any]]] = {
    "P1": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Our School and Neighbourhood",
            "topic": "Pre-Number Activities & Counting (1–20)",
            "periods": 18,
            "sub_topics": ["Sorting and grouping objects", "Matching sets", "Counting 1 to 20"],
            "learning_outcomes": "Learner counts, sorts, and relates real objects to numbers up to 20.",
            "learning_aids": ["Bottle tops", "Beans/seeds", "Number cards"],
            "life_skills_values": ["Sharing", "Orderliness", "Cooperation"],
        }
    ],
    "P2": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Our Environment & Things We Make",
            "topic": "Place Value & Numbers up to 999",
            "periods": 22,
            "sub_topics": ["Tens and Ones", "Introducing Hundreds", "Ordering up to 999"],
            "learning_outcomes": "Learner identifies place values of Hundreds, Tens, and Ones.",
            "learning_aids": ["Bundles of sticks", "Place value tins", "Abacus"],
            "life_skills_values": ["Critical thinking", "Neatness"],
        }
    ],
    "P3": [
        {
            "curriculum_type": "Thematic Curriculum",
            "theme": "Managing Resources in Our Sub-County",
            "topic": "Multiplication, Division & Basic Fractions",
            "periods": 24,
            "sub_topics": ["Tables 2, 3, 4, 5, 10", "Sharing equally", "Halves, quarters, thirds"],
            "learning_outcomes": "Learner applies multiplication and division to everyday sharing.",
            "learning_aids": ["Multiplication grid", "Paper strips", "Bottle tops"],
            "life_skills_values": ["Fairness", "Resourcefulness"],
        }
    ],
    "P4": [
        {
            "curriculum_type": "Subject-Based Syllabus (Transition Class)",
            "theme": "Sets & Numeracy",
            "topic": "Set Concepts, Whole Numbers & Fractions",
            "periods": 40,
            "sub_topics": ["Venn diagrams", "Place value up to 99,999", "Roman numerals (I–L)"],
            "learning_outcomes": "Learner represents sets on Venn diagrams and works with numbers to 99,999.",
            "learning_aids": ["Strings/hoops", "Place value chart", "Fraction strips"],
            "life_skills_values": ["Classification", "Logical reasoning"],
        }
    ],
    "P5": [
        {
            "curriculum_type": "Subject-Based Syllabus",
            "theme": "Numeracy & Geometry",
            "topic": "Number Patterns, Angles, Perimeter & Area",
            "periods": 46,
            "sub_topics": ["Place value to Millions", "Prime factors, LCM and GCF", "Perimeter and area"],
            "learning_outcomes": "Learner finds LCM/GCF and calculates perimeter and area.",
            "learning_aids": ["Abacus", "Factor charts", "Mathematical set"],
            "life_skills_values": ["Analytical thinking", "Accuracy"],
        }
    ],
    "P6": [
        {
            "curriculum_type": "Subject-Based Syllabus",
            "theme": "Sets, Numeracy, Measurement & Data Handling",
            "topic": "Sets, Bases, Fractions, Perimeter/Area, Statistics & Algebra",
            "periods": 48,
            "sub_topics": [
                "Set complements and Venn diagrams",
                "Roman numerals and number bases",
                "GCF, LCM, and remainder problems",
                "Fractions, percentages, mean, and mode",
                "Perimeter and area of land plots",
                "Simple linear equations",
            ],
            "learning_outcomes": "Learner solves multi-step problems in sets, bases, measurement, statistics, and algebra.",
            "learning_aids": ["Venn charts", "Grid paper", "Mid-term mark sheets"],
            "life_skills_values": ["Problem solving", "Data interpretation"],
        }
    ],
    "P7": [
        {
            "curriculum_type": "Subject-Based Syllabus (PLE Consolidation)",
            "theme": "Geometry, Measurement & Algebra",
            "topic": "Bearings, Speed-Distance-Time, Volume & Equations",
            "periods": 30,
            "sub_topics": ["Scale drawing and bearings", "Speed, distance, and time", "Volume and equations"],
            "learning_outcomes": "Learner consolidates upper-primary mathematics for PLE readiness.",
            "learning_aids": ["Mathematical set", "3D nets", "Past papers"],
            "life_skills_values": ["Critical thinking", "Self-reliance"],
        }
    ],
}

OTHER_CLASS_QUIZZES: Dict[str, List[Dict[str, Any]]] = {
    "P1": [{"id": "p1_1", "topic": "Counting", "marks": 1, "question": "5 + 3 = ?", "options": ["7", "8", "9", "6"], "ans": "8", "explanation": "5 + 3 = 8."}],
    "P2": [{"id": "p2_1", "topic": "Place Value", "marks": 1, "question": "Place value of 4 in 428?", "options": ["Ones", "Tens", "Hundreds", "Thousands"], "ans": "Hundreds", "explanation": "4 is in the Hundreds place."}],
    "P3": [{"id": "p3_1", "topic": "Division", "marks": 1, "question": "24 mangoes shared equally among 4 pupils = ?", "options": ["5", "6", "8", "4"], "ans": "6", "explanation": "24 ÷ 4 = 6."}],
    "P4": [{"id": "p4_1", "topic": "Sets", "marks": 1, "question": "A = {1, 2, 3}, B = {2, 3, 4}. Find A ∩ B.", "options": ["{1}", "{2, 3}", "{4}", "{1, 2, 3, 4}"], "ans": "{2, 3}", "explanation": "Common elements are 2 and 3."}],
    "P5": [{"id": "p5_1", "topic": "LCM", "marks": 1, "question": "LCM of 6 and 8?", "options": ["12", "24", "48", "2"], "ans": "24", "explanation": "LCM(6, 8) = 24."}],
    "P7": [{"id": "p7_1", "topic": "Speed", "marks": 2, "question": "180 km in 3 hours. Speed = ?", "options": ["50 km/h", "60 km/h", "90 km/h", "540 km/h"], "ans": "60 km/h", "explanation": "180 ÷ 3 = 60 km/h."}],
}


class OmwesoGame:
    def __init__(self) -> None:
        self.board = [
            [4] * 8 + [0] * 8,
            [4] * 8 + [0] * 8,
        ]
        self.turn = 0
        self.log = ["Board initialized with 32 seeds per player."]

    def get_opposite_enemy_pits(self, inner_idx: int):
        col_from_left = 15 - inner_idx
        return 8 + col_from_left, 7 - col_from_left

    def sow(self, player: int, pit_idx: int, reverse: bool = False) -> bool:
        seeds = self.board[player][pit_idx]
        if seeds < 2:
            self.log.append("Choose a pit with at least 2 seeds.")
            return False

        if reverse and pit_idx not in {0, 1, 14, 15}:
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
                        self.log.append(f"Player {player + 1} captured {captured} seeds!")
                        continue
                seeds = self.board[player][curr]
                self.board[player][curr] = 0
            else:
                break

        self.turn = opp
        return True


def init_state() -> None:
    st.session_state.setdefault("general_score", {"attempted": 0, "correct": 0})
    st.session_state.setdefault("general_answered", set())
    st.session_state.setdefault("omweso_game", OmwesoGame())


def main() -> None:
    init_state()
    st.title("iLearn-Uganda: NCDC Primary Mathematics (P1 – P7)")

    class_list = list(NCDC_MATH_CURRICULUM.keys())
    selected_class = st.sidebar.selectbox("Select Class", class_list, index=5)

    tab_quiz, tab_syllabus, tab_dashboard, tab_omweso = st.tabs([
        "Class Quiz",
        "NCDC Syllabus",
        "Dashboard",
        "Omweso Lab",
    ])

    with tab_quiz:
        st.subheader(f"{selected_class} Mathematics Quiz")
        if selected_class == "P6":
            if P6_MODULE_AVAILABLE:
                render_p6_quiz_tab()
            else:
                st.error(f"Could not load p6_quiz_module.py: {P6_MODULE_ERROR}")
        else:
            for idx, q in enumerate(OTHER_CLASS_QUIZZES.get(selected_class, [])):
                st.markdown(f"**{q['question']}** *(Topic: {q['topic']})*")
                pick = st.radio("Select answer:", q["options"], key=f"gen_{selected_class}_{idx}")
                if st.button("Check Answer", key=f"gen_btn_{selected_class}_{idx}"):
                    q_uid = f"{selected_class}:{q['id']}"
                    ok = pick == q["ans"]
                    if q_uid not in st.session_state["general_answered"]:
                        st.session_state["general_answered"].add(q_uid)
                        st.session_state["general_score"]["attempted"] += 1
                        if ok:
                            st.session_state["general_score"]["correct"] += 1
                    if ok:
                        st.success(f"Correct! {q['explanation']}")
                    else:
                        st.error(f"Incorrect. Answer: **{q['ans']}** — {q['explanation']}")
                st.divider()

    with tab_syllabus:
        st.subheader(f"{selected_class} Syllabus Overview")
        for topic_row in NCDC_MATH_CURRICULUM[selected_class]:
            with st.expander(f"{topic_row['topic']} ({topic_row['periods']} periods)", expanded=True):
                st.caption(topic_row["curriculum_type"])
                st.write(topic_row["learning_outcomes"])
                st.markdown("**Sub-topics:** " + ", ".join(topic_row["sub_topics"]))
                st.markdown("**Learning Aids:** " + ", ".join(topic_row["learning_aids"]))
                st.markdown("**Life Skills & Values:** " + ", ".join(topic_row["life_skills_values"]))

    with tab_dashboard:
        st.subheader("Progress & Coverage Dashboard")
        if P6_MODULE_AVAILABLE:
            render_p6_dashboard_card()
        rows = [
            {
                "Class": cls,
                "Model": items[0]["curriculum_type"],
                "Periods": sum(x["periods"] for x in items),
            }
            for cls, items in NCDC_MATH_CURRICULUM.items()
        ]
        st.dataframe(pd.DataFrame(rows))

    with tab_omweso:
        st.subheader("Traditional Ugandan Omweso")
        game: OmwesoGame = st.session_state["omweso_game"]
        cols = st.columns(8)
        for c in range(8):
            cols[c].metric(f"Outer {c + 1}", game.board[0][c])
        inner_cols = st.columns(8)
        for c in range(8):
            idx = 15 - c
            inner_cols[c].metric(f"Inner {c + 1} [#{idx}]", game.board[0][idx])

        valid_pits = [i for i in range(16) if game.board[0][i] >= 2]
        if valid_pits:
            pit_choice = st.selectbox("Pick pit to sow:", valid_pits, format_func=lambda x: f"Pit #{x} ({game.board[0][x]})")
            rev = st.checkbox("Reverse sow (left-corner pits 0, 1, 14, 15)")
            if st.button("Sow"):
                game.sow(0, pit_choice, reverse=rev)
                opp_pits = [i for i in range(16) if game.board[1][i] >= 2]
                if opp_pits:
                    game.sow(1, random.choice(opp_pits), reverse=False)
        if st.button("Reset Board"):
            st.session_state["omweso_game"] = OmwesoGame()
        st.info(game.log[-1])


if __name__ == "__main__":
    main()
