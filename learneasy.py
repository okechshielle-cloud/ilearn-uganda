from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import pandas as pd
import streamlit as st


# ==============================================================================
# 1. GENERATE LOCAL DIAGRAM ASSETS IN assets/p6/
# ==============================================================================

def generate_p6_diagrams(output_dir: str = "assets/p6") -> None:
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # --- A. Question 1: Venn Diagram (Sets A, B, Universal E) ---
    fig, ax = plt.subplots(figsize=(6, 4.5))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 7.5)
    ax.set_aspect("equal")
    ax.axis("off")

    # Universal set rectangle E
    univ = patches.Rectangle((0.6, 0.5), 8.8, 6.2, linewidth=2, edgecolor="black", facecolor="white")
    ax.add_patch(univ)
    ax.text(0.6, 6.85, "E", fontsize=14, fontweight="bold")

    # Circles A and B
    circle_a = patches.Circle((3.9, 3.6), 2.1, linewidth=2, edgecolor="black", facecolor="none")
    circle_b = patches.Circle((6.1, 3.6), 2.1, linewidth=2, edgecolor="black", facecolor="none")
    ax.add_patch(circle_a)
    ax.add_patch(circle_b)

    ax.text(2.7, 5.1, "A", fontsize=13, fontweight="bold")
    ax.text(7.1, 5.1, "B", fontsize=13, fontweight="bold")

    # Elements
    ax.text(2.5, 4.0, "e", fontsize=13)
    ax.text(2.8, 2.5, "f", fontsize=13)
    ax.text(4.9, 4.1, "a", fontsize=13)
    ax.text(4.9, 2.8, "i", fontsize=13)
    ax.text(7.2, 4.0, "b", fontsize=13)
    ax.text(7.0, 2.5, "c", fontsize=13)
    ax.text(8.5, 1.0, "g", fontsize=13)

    plt.tight_layout()
    plt.savefig(out_path / "q01_venn_diagram.png", dpi=200)
    plt.close(fig)

    # --- B. Question 6: Mid-Term Marks Table ---
    fig, ax = plt.subplots(figsize=(7.5, 2.0))
    ax.axis("off")
    columns = ["Maths", "Eng", "SST", "SCI", "CAPE 1", "Kiswahili"]
    rows = [["70", "80", "70", "50", "90", "50"]]
    table = ax.table(cellText=rows, colLabels=columns, cellLoc="center", loc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.1, 1.8)
    plt.tight_layout()
    plt.savefig(out_path / "q06_marks_table.png", dpi=200)
    plt.close(fig)

    # --- C. Question 12: Mr. Okello's Land Diagram ---
    fig, ax = plt.subplots(figsize=(6.5, 4.8))
    ax.set_xlim(-1.2, 11.5)
    ax.set_ylim(-1.2, 9.2)
    ax.set_aspect("equal")
    ax.axis("off")

    # Bottom plot R: width 10m (x: 0..10), height 5m (y: 0..5)
    plot_r = patches.Rectangle((0, 0), 10, 5, linewidth=2, edgecolor="black", facecolor="white")
    ax.add_patch(plot_r)
    ax.text(5.0, 2.3, "R", fontsize=14, fontweight="bold", ha="center")
    ax.text(5.0, -0.7, "10 m", fontsize=12, fontweight="bold", ha="center")
    ax.text(10.3, 2.4, "5 m", fontsize=12, fontweight="bold", va="center")

    # Top-left plot P: width 4m (x: 0..4), height 3m (y: 5..8)
    plot_p = patches.Rectangle((0, 5), 4, 3, linewidth=2, edgecolor="black", facecolor="white")
    ax.add_patch(plot_p)
    ax.text(2.0, 6.3, "P", fontsize=14, fontweight="bold", ha="center")
    ax.text(2.0, 5.25, "4 m", fontsize=11, ha="center")
    ax.text(-0.95, 6.4, "3 m", fontsize=12, fontweight="bold", va="center")

    # Top-right plot Q: width 6m (x: 4..10), height 3m (y: 5..8)
    plot_q = patches.Rectangle((4, 5), 6, 3, linewidth=2, edgecolor="black", facecolor="white")
    ax.add_patch(plot_q)
    ax.text(7.0, 6.3, "Q", fontsize=14, fontweight="bold", ha="center")
    ax.text(7.0, 5.25, "6 m", fontsize=11, ha="center")

    plt.tight_layout()
    plt.savefig(out_path / "q12_okello_land.png", dpi=200)
    plt.close(fig)


# ==============================================================================
# 2. MERGED P6 QUIZ SET (14 QUESTIONS)
# ==============================================================================

MERGED_P6_QUIZ = [
    {
        "id": "p6_q01_sets",
        "topic": "Set Concepts",
        "marks": 1,
        "question": "1– Given that the Venn diagram below, list elements of set (B–A)'.",
        "options": ["{e, f, a, i, g}", "{b, c}", "{a, i}", "{e, f, g}"],
        "ans": "{e, f, a, i, g}",
        "explanation": "B - A = {b, c}, so (B - A)' contains all elements in E outside {b, c}.",
        "image": "assets/p6/q01_venn_diagram.png",
    },
    {
        "id": "p6_q02_roman",
        "topic": "Whole Numbers & Numerals",
        "marks": 1,
        "question": "2– Write CIX in Hindu Arabic numeral.",
        "options": ["109", "111", "99", "119"],
        "ans": "109",
        "explanation": "C = 100 and IX = 9, so CIX = 100 + 9 = 109.",
        "image": None,
    },
    {
        "id": "p6_q03_base",
        "topic": "Number Bases",
        "marks": 1,
        "question": "3– Given that 21_n = 11_ten. find the base represented by n.",
        "options": ["Base five", "Base six", "Base four", "Base eight"],
        "ans": "Base five",
        "explanation": "2n + 1 = 11 -> 2n = 10 -> n = 5 (base five).",
        "image": None,
    },
    {
        "id": "p6_q04_gcf",
        "topic": "Factors & Multiples",
        "marks": 1,
        "question": "4– If Q = 2^2 × 3^2 and P = 2 × 3 × 5. find the Greatest Common Factor (G.C.F) of Q and P.",
        "options": ["6", "18", "180", "30"],
        "ans": "6",
        "explanation": "Common prime factors with lowest powers give 2^1 × 3^1 = 6.",
        "image": None,
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
        "explanation": "50% = 1/2 = 4/8; 4/8 + 3/8 = 7/8; remaining fraction for Posho = 1 - 7/8 = 1/8.",
        "image": None,
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
        "image": None,
    },
    {
        "id": "p6_q06_mode",
        "topic": "Data Handling & Statistics",
        "marks": 1,
        "question": (
            "6– Given that Paul scored the marks given below in the mid-term examination "
            "(Maths 70, Eng 80, SST 70, SCI 50, CAPE 1 90, Kiswahili 50). Find Paul's modal mark."
        ),
        "options": ["70 and 50", "70", "50", "80"],
        "ans": "70 and 50",
        "explanation": "Both 70 and 50 appear twice, making the distribution bimodal with modal marks 70 and 50.",
        "image": "assets/p6/q06_marks_table.png",
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
        "image": "assets/p6/q12_okello_land.png",
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
        "image": "assets/p6/q12_okello_land.png",
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
        "image": None,
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
        "image": None,
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
        "image": None,
    },
    {
        "id": "p6_q16a_factors",
        "topic": "Factors & Multiples",
        "marks": 2,
        "question": "16– (a) List all the factors of 12.",
        "options": ["1, 2, 3, 4, 6, 12", "12, 24, 36, 48", "2, 3, 4, 6", "1, 2, 3, 6, 12"],
        "ans": "1, 2, 3, 4, 6, 12",
        "explanation": "The factors of 12 are 1, 2, 3, 4, 6, and 12.",
        "image": None,
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
        "image": None,
    },
]


# ==============================================================================
# 3. DASHBOARD SCORING & QUIZ RENDERER
# ==============================================================================

def init_p6_scoring_state(classes: list[str]) -> None:
    if "quiz_scores" not in st.session_state:
        st.session_state.quiz_scores = {
            cls: {"attempted": 0, "correct": 0, "marks_earned": 0, "marks_total": 0}
            for cls in classes
        }
    if "answered_q_ids" not in st.session_state:
        st.session_state.answered_q_ids = set()


def record_answer(class_level: str, q: dict, chosen_option: str) -> bool:
    q_key = f"{class_level}:{q['id']}"
    is_correct = chosen_option == q["ans"]
    marks = q.get("marks", 1)

    # Prevent double-counting the same question if the learner clicks Submit again
    if q_key not in st.session_state.answered_q_ids:
        st.session_state.answered_q_ids.add(q_key)
        st.session_state.quiz_scores[class_level]["attempted"] += 1
        st.session_state.quiz_scores[class_level]["marks_total"] += marks
        if is_correct:
            st.session_state.quiz_scores[class_level]["correct"] += 1
            st.session_state.quiz_scores[class_level]["marks_earned"] += marks
    return is_correct


def render_p6_dashboard_summary(class_level: str = "P6") -> None:
    stats = st.session_state.quiz_scores[class_level]
    max_possible_marks = sum(q.get("marks", 1) for q in MERGED_P6_QUIZ)
    accuracy = round((stats["correct"] / stats["attempted"]) * 100, 1) if stats["attempted"] > 0 else 0.0

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Questions Attempted", f"{stats['attempted']} / {len(MERGED_P6_QUIZ)}")
    col2.metric("Correct Answers", stats["correct"])
    col3.metric("Marks Scored", f"{stats['marks_earned']} / {max_possible_marks}")
    col4.metric("Accuracy (%)", f"{accuracy}%")

    df_topics = pd.DataFrame([
        {
            "Question ID": q["id"],
            "Topic": q["topic"],
            "Marks": q.get("marks", 1),
            "Has Diagram": "Yes" if q.get("image") else "No",
        }
        for q in MERGED_P6_QUIZ
    ])
    st.dataframe(df_topics, use_container_width=True)


if __name__ == "__main__":
    generate_p6_diagrams("assets/p6")
    print("Generated P6 diagrams in assets/p6/")
