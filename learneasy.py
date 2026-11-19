import io
from typing import Any, Dict, List, Optional

import matplotlib
matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


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

        plot_r = patches.Rectangle((0, 0), 10, 5, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(plot_r)
        ax.text(5.0, 2.3, "R", fontsize=14, fontweight="bold", ha="center")
        ax.text(5.0, -0.75, "10 m", fontsize=12, fontweight="bold", ha="center")
        ax.text(10.35, 2.4, "5 m", fontsize=12, fontweight="bold", va="center")

        plot_p = patches.Rectangle((0, 5), 4, 3, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(plot_p)
        ax.text(2.0, 6.3, "P", fontsize=14, fontweight="bold", ha="center")
        ax.text(2.0, 5.25, "4 m", fontsize=11, ha="center")
        ax.text(-1.05, 6.4, "3 m", fontsize=12, fontweight="bold", va="center")

        plot_q = patches.Rectangle((4, 5), 6, 3, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(plot_q)
        ax.text(7.0, 6.3, "Q", fontsize=14, fontweight="bold", ha="center")
        ax.text(7.0, 5.25, "6 m", fontsize=11, ha="center")

        plt.tight_layout()
        fig.savefig(buf, format="png", dpi=180, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    return None


P6_QUESTIONS: List[Dict[str, Any]] = [
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
        "id": "p6_q05ii_matooke_vs_posho",
        "topic": "Fractions & Percentages",
        "marks": 2,
        "question": (
            "5– In a class of 48 pupils who attended a birthday party, 50% of the pupils ate "
            "Matooke, 3/8 ate Rice and the rest ate Posho. (ii) How many more pupils ate Matooke than Posho?"
        ),
        "options": ["18", "6", "24", "42"],
        "ans": "18",
        "explanation": "Matooke = 50% of 48 = 24 pupils; Posho = 1/8 of 48 = 6 pupils; difference = 24 - 6 = 18.",
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
]


def render_p6_quiz_tab() -> None:
    """Renders the P6 quiz with diagrams and session-state score tracking."""
    st.session_state.setdefault("p6_score", {"attempted": 0, "correct": 0, "marks": 0})
    st.session_state.setdefault("p6_answered", set())

    for i, q in enumerate(P6_QUESTIONS):
        st.markdown(f"**{q['question']}** *(Topic: {q['topic']} | {q['marks']} mark(s))*")

        if q.get("diagram_type"):
            png = get_diagram_png(q["diagram_type"])
            if png:
                st.image(png, caption=f"{q['topic']} Diagram", width=480)

        choice = st.radio("Choose your answer:", q["options"], key=f"p6_opt_{i}")
        if st.button("Check Answer", key=f"p6_chk_{i}"):
            is_correct = choice == q["ans"]
            if q["id"] not in st.session_state["p6_answered"]:
                st.session_state["p6_answered"].add(q["id"])
                st.session_state["p6_score"]["attempted"] += 1
                if is_correct:
                    st.session_state["p6_score"]["correct"] += 1
                    st.session_state["p6_score"]["marks"] += q["marks"]

            if is_correct:
                st.success(f"Correct! {q['explanation']}")
            else:
                st.error(f"Incorrect. Correct answer: **{q['ans']}** — {q['explanation']}")
        st.divider()


def render_p6_dashboard_card() -> None:
    """Displays P6 quiz performance summary for the dashboard."""
    stats = st.session_state.get("p6_score", {"attempted": 0, "correct": 0, "marks": 0})
    total_marks = sum(q["marks"] for q in P6_QUESTIONS)
    st.metric("P6 Quiz Score", f"{stats['marks']} / {total_marks} marks")
    st.caption(f"Attempted: {stats['attempted']}/{len(P6_QUESTIONS)} | Correct: {stats['correct']}")
    st.dataframe(
        pd.DataFrame([{"ID": q["id"], "Topic": q["topic"], "Marks": q["marks"]} for q in P6_QUESTIONS]),
        use_container_width=True,
    )
