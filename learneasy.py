import base64
import io
import os
import random
from typing import Any, Dict, List, Optional

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="iLearn-Uganda | Primary Maths", layout="wide")

LOGO_FILENAMES = ["ilearn_uganda_logo.png", "image_b5d6e7.png", "logo.png"]

# Clean SVG fallback emblem in iLearn-Uganda's emerald & gold palette if no PNG file is found
FALLBACK_LOGO_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="128" height="128" viewBox="0 0 128 128">'
    "<defs>"
    '<linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
    '<stop offset="0%" stop-color="#13a65b"/>'
    '<stop offset="100%" stop-color="#064e2c"/>'
    "</linearGradient>"
    "</defs>"
    '<rect x="8" y="8" width="112" height="112" rx="26" fill="url(#g)"/>'
    '<path d="M28 84 Q46 76 64 84 Q82 76 100 84 L100 42 Q82 36 64 44 Q46 36 28 42 Z" fill="none" stroke="#ffffff" stroke-width="4" stroke-linejoin="round"/>'
    '<line x1="64" y1="44" x2="64" y2="84" stroke="#ffffff" stroke-width="3.5"/>'
    '<circle cx="64" cy="48" r="14" fill="#0d7c47" stroke="#ffffff" stroke-width="3.5"/>'
    '<path d="M64 56 L64 45 M64 49 Q57 44 58 39 Q63 40 64 46 M64 49 Q71 44 70 39 Q65 40 64 46" fill="none" stroke="#FCDC04" stroke-width="2.5" stroke-linecap="round"/>'
    "</svg>"
)

# Subtle, low-tint margin and main content border accent colors per selected tab
TAB_MARGIN_STYLES: Dict[str, Dict[str, str]] = {
    "Take Quiz": {
        "accent": "rgba(11, 110, 63, 0.55)",
        "border_tint": "rgba(11, 110, 63, 0.14)",
        "pill_bg": "rgba(220, 252, 231, 0.65)",
        "pill_text": "#14532d",
        "note": "Practice & Assessment Margin",
    },
    "NCDC Syllabus": {
        "accent": "rgba(21, 128, 61, 0.55)",
        "border_tint": "rgba(21, 128, 61, 0.14)",
        "pill_bg": "rgba(224, 242, 254, 0.65)",
        "pill_text": "#075985",
        "note": "Curriculum Guide Margin",
    },
    "Dashboard": {
        "accent": "rgba(180, 83, 9, 0.55)",
        "border_tint": "rgba(180, 83, 9, 0.14)",
        "pill_bg": "rgba(254, 249, 195, 0.65)",
        "pill_text": "#854d0e",
        "note": "Standings & Analytics Margin",
    },
    "Omweso Lab": {
        "accent": "rgba(185, 28, 28, 0.55)",
        "border_tint": "rgba(185, 28, 28, 0.14)",
        "pill_bg": "rgba(254, 226, 226, 0.65)",
        "pill_text": "#991b1b",
        "note": "Strategy Board Margin",
    },
}


# ==============================================================================
# 1. LOGO & IN-MEMORY DIAGRAM RENDERER
# ==============================================================================


def get_logo_source() -> tuple[str, Any]:
    """Returns ('file', path) if a local logo file exists, else ('svg_uri', data_uri)."""
    for fname in LOGO_FILENAMES:
        if os.path.exists(fname):
            return ("file", fname)
    encoded = base64.b64encode(FALLBACK_LOGO_SVG.encode("utf-8")).decode("utf-8")
    return ("svg_uri", f"data:image/svg+xml;base64,{encoded}")


@st.cache_data(show_spinner=False)
def get_diagram_png(diagram_type: Optional[str]) -> Optional[bytes]:
    """Generates clean mathematical diagrams in memory as PNG bytes."""
    if not diagram_type:
        return None

    buf = io.BytesIO()

    if diagram_type == "venn":
        fig, ax = plt.subplots(figsize=(5.8, 4.4))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 7.6)
        ax.set_aspect("equal")
        ax.axis("off")

        univ = patches.Rectangle((0.6, 0.5), 8.8, 6.2, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(univ)
        ax.text(0.6, 6.9, "E", fontsize=14, fontweight="bold")

        circle_a = patches.Circle((3.9, 3.6), 2.1, linewidth=2, edgecolor="black", facecolor="none")
        circle_b = patches.Circle((6.1, 3.6), 2.1, linewidth=2, edgecolor="black", facecolor="none")
        ax.add_patch(circle_a)
        ax.add_patch(circle_b)

        ax.text(3.9, 5.95, "A", fontsize=13, fontweight="bold", ha="center", va="bottom")
        ax.text(6.1, 5.95, "B", fontsize=13, fontweight="bold", ha="center", va="bottom")

        ax.text(2.5, 4.0, "e", fontsize=13)
        ax.text(2.8, 2.5, "f", fontsize=13)
        ax.text(4.9, 4.1, "a", fontsize=13)
        ax.text(4.9, 2.8, "i", fontsize=13)
        ax.text(7.2, 4.0, "b", fontsize=13)
        ax.text(7.0, 2.5, "c", fontsize=13)
        ax.text(8.5, 1.0, "g", fontsize=13)

        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
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
        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
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

        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    return None


# ==============================================================================
# 2. NCDC PRIMARY MATHEMATICS CURRICULUM (P1 - P7) & UGANDA DISTRICTS
# ==============================================================================

UGANDA_DISTRICTS: List[str] = sorted([
    # Central Region
    "Buikwe", "Bukomansimbi", "Butambala", "Buvuma", "Gomba", "Kalangala",
    "Kalungu", "Kampala", "Kasanda", "Kayunga", "Kiboga", "Kyankwanzi",
    "Kyotera", "Luweero", "Lwengo", "Lyantonde", "Masaka", "Mityana",
    "Mpigi", "Mubende", "Mukono", "Nakaseke", "Nakasongola", "Rakai",
    "Sembabule", "Wakiso",
    # Eastern Region
    "Amuria", "Budaka", "Bududa", "Bugiri", "Bugweri", "Bukedea",
    "Bukwo", "Bulambuli", "Busia", "Butaleja", "Butebo", "Buyende",
    "Iganga", "Jinja", "Kaberamaido", "Kalaki", "Kaliro", "Kamuli",
    "Kapchorwa", "Kapelebyong", "Katakwi", "Kibuku", "Kumi", "Kween",
    "Luuka", "Manafwa", "Mayuge", "Mbale", "Namayingo", "Namisindwa",
    "Namutumba", "Ngora", "Pallisa", "Serere", "Sironko", "Soroti",
    "Tororo",
    # Northern Region
    "Abim", "Adjumani", "Agago", "Alebtong", "Amolatar", "Amudat",
    "Amuru", "Apac", "Arua", "Dokolo", "Gulu", "Kaabong",
    "Karenga", "Kitgum", "Koboko", "Kole", "Kotido", "Kwania",
    "Lamwo", "Lira", "Madi-Okollo", "Maracha", "Moroto", "Moyo",
    "Nabilatuk", "Nakapiripirit", "Napak", "Nebbi", "Nwoya", "Obongi",
    "Omoro", "Otuke", "Oyam", "Pader", "Pakwach", "Yumbe",
    "Zombo",
    # Western Region
    "Buhweju", "Buliisa", "Bundibugyo", "Bunyangabu", "Bushenyi", "Hoima",
    "Ibanda", "Isingiro", "Kabale", "Kabarole", "Kagadi", "Kakumiro",
    "Kamwenge", "Kanungu", "Kasese", "Kazo", "Kibaale", "Kikuube",
    "Kiruhura", "Kiryandongo", "Kisoro", "Kitagwenda", "Kyankwanzi", "Kyegegwa",
    "Kyenjojo", "Masindi", "Mbarara", "Mitooma", "Ntoroko", "Ntungamo",
    "Rubirizi", "Rukiga", "Rukungiri", "Rwampara", "Sheema",
])

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


# ==============================================================================
# 3. QUIZ BANK (ALL CLASSES P1–P7, DISTRIBUTED OPTIONS A–D)
# ==============================================================================

QUIZ_BANK: Dict[str, List[Dict[str, Any]]] = {
    "P1": [
        {
            "id": "p1_1",
            "topic": "Counting",
            "marks": 1,
            "question": "1– Add: 5 + 3 = ?",
            "options": ["7", "8", "9", "6"],
            "ans": "8",
            "explanation": "5 + 3 = 8.",
            "diagram_type": None,
        },
        {
            "id": "p1_2",
            "topic": "Number Recognition",
            "marks": 1,
            "question": "2– Which number comes right after 14?",
            "options": ["13", "16", "15", "12"],
            "ans": "15",
            "explanation": "Counting in ones: 13, 14, 15.",
            "diagram_type": None,
        },
    ],
    "P2": [
        {
            "id": "p2_1",
            "topic": "Place Value",
            "marks": 1,
            "question": "1– What is the place value of 4 in 428?",
            "options": ["Ones", "Tens", "Hundreds", "Thousands"],
            "ans": "Hundreds",
            "explanation": "In 428, 4 is in the Hundreds position.",
            "diagram_type": None,
        },
        {
            "id": "p2_2",
            "topic": "Addition",
            "marks": 1,
            "question": "2– Work out: 145 + 32.",
            "options": ["167", "187", "177", "157"],
            "ans": "177",
            "explanation": "145 + 32 = 177.",
            "diagram_type": None,
        },
    ],
    "P3": [
        {
            "id": "p3_1",
            "topic": "Division",
            "marks": 1,
            "question": "1– 24 mangoes shared equally among 4 pupils gives how many each?",
            "options": ["5", "8", "4", "6"],
            "ans": "6",
            "explanation": "24 ÷ 4 = 6 mangoes each.",
            "diagram_type": None,
        },
        {
            "id": "p3_2",
            "topic": "Fractions",
            "marks": 1,
            "question": "2– Which fraction represents one quarter?",
            "options": ["1/2", "1/4", "3/4", "1/3"],
            "ans": "1/4",
            "explanation": "One quarter means 1 out of 4 equal parts, written as 1/4.",
            "diagram_type": None,
        },
    ],
    "P4": [
        {
            "id": "p4_1",
            "topic": "Sets",
            "marks": 1,
            "question": "1– Given A = {1, 2, 3} and B = {2, 3, 4}, find A ∩ B.",
            "options": ["{1}", "{2, 3}", "{4}", "{1, 2, 3, 4}"],
            "ans": "{2, 3}",
            "explanation": "The elements common to both sets A and B are 2 and 3.",
            "diagram_type": None,
        },
        {
            "id": "p4_2",
            "topic": "Roman Numerals",
            "marks": 1,
            "question": "2– Write XXIV in Hindu-Arabic numerals.",
            "options": ["26", "16", "24", "34"],
            "ans": "24",
            "explanation": "XX = 20 and IV = 4, so XXIV = 24.",
            "diagram_type": None,
        },
    ],
    "P5": [
        {
            "id": "p5_1",
            "topic": "Factors & Multiples",
            "marks": 1,
            "question": "1– Find the Lowest Common Multiple (LCM) of 6 and 8.",
            "options": ["12", "48", "24", "2"],
            "ans": "24",
            "explanation": "Multiples of 6: 6, 12, 18, 24... Multiples of 8: 8, 16, 24... Smallest common is 24.",
            "diagram_type": None,
        },
        {
            "id": "p5_2",
            "topic": "Measurement",
            "marks": 2,
            "question": "2– Find the area of a rectangle measuring 9 cm by 4 cm.",
            "options": ["26 sq cm", "13 sq cm", "36 sq cm", "18 sq cm"],
            "ans": "36 sq cm",
            "explanation": "Area = length × width = 9 cm × 4 cm = 36 sq cm.",
            "diagram_type": None,
        },
    ],
    "P6": [
        {
            "id": "p6_q01_sets",
            "topic": "Set Concepts",
            "marks": 2,
            "question": "1– Given that the Venn diagram below, list elements of set (B–A)'.",
            "options": ["{b, c}", "{e, f, a, i, g}", "{a, i}", "{e, f, g}"],
            "ans": "{e, f, a, i, g}",
            "explanation": "B - A = {b, c}, so (B - A)' includes all elements in universal set E outside {b, c}.",
            "diagram_type": "venn",
        },
        {
            "id": "p6_q02_roman",
            "topic": "Whole Numbers & Numerals",
            "marks": 2,
            "question": "2– Write CIX in Hindu Arabic numeral.",
            "options": ["111", "99", "109", "119"],
            "ans": "109",
            "explanation": "C = 100 and IX = 9, so CIX = 100 + 9 = 109.",
            "diagram_type": None,
        },
        {
            "id": "p6_q03_base",
            "topic": "Number Bases",
            "marks": 2,
            "question": "3– Given that 21_n = 11_ten. find the base represented by n.",
            "options": ["Base six", "Base four", "Base eight", "Base five"],
            "ans": "Base five",
            "explanation": "2n + 1 = 11 -> 2n = 10 -> n = 5 (base five).",
            "diagram_type": None,
        },
        {
            "id": "p6_q04_gcf",
            "topic": "Factors & Multiples",
            "marks": 2,
            "question": "4– If Q = 2² × 3² and P = 2 × 3 × 5. find the Greatest Common Factor (G.C.F) of Q and P.",
            "options": ["6", "18", "180", "30"],
            "ans": "6",
            "explanation": "Common prime factors with the lowest powers give 2¹ × 3¹ = 6.",
            "diagram_type": None,
        },
        {
            "id": "p6_q05i_posho",
            "topic": "Fractions & Percentages",
            "marks": 2,
            "question": (
                "5– In a class of 48 pupils who attended a birthday party, 50% of the pupils ate "
                "Matooke, 3/8 ate Rice and the rest ate Posho. (i) Find the fraction of pupils who ate Posho."
            ),
            "options": ["3/8", "1/8", "1/2", "7/8"],
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
            "options": ["6", "24", "18", "42"],
            "ans": "18",
            "explanation": "Matooke = 50% of 48 = 24 pupils; Posho = 1/8 of 48 = 6 pupils; difference = 24 - 6 = 18.",
            "diagram_type": None,
        },
        {
            "id": "p6_q06_mode",
            "topic": "Data Handling & Statistics",
            "marks": 2,
            "question": "6– Given that Paul scored the marks given below in the mid-term examination. Find Paul's modal mark.",
            "options": ["70", "50", "80", "70 and 50"],
            "ans": "70 and 50",
            "explanation": "Both 70 and 50 appear twice, making the distribution bimodal with modal marks 70 and 50.",
            "diagram_type": "marks_table",
        },
        {
            "id": "p6_q07_fractions",
            "topic": "Fractions & Decimals",
            "marks": 2,
            "question": "7– Work out: 3/4 + 1/6.",
            "options": ["11/12", "4/10", "5/6", "7/12"],
            "ans": "11/12",
            "explanation": "The LCD of 4 and 6 is 12: 9/12 + 2/12 = 11/12.",
            "diagram_type": None,
        },
        {
            "id": "p6_q08_money",
            "topic": "Money & Financial Arithmetic",
            "marks": 2,
            "question": "8– A trader bought 3 books at sh 4,500 each. How much did she pay altogether?",
            "options": ["sh 12,500", "sh 13,500", "sh 14,500", "sh 7,500"],
            "ans": "sh 13,500",
            "explanation": "Total cost = 3 × sh 4,500 = sh 13,500.",
            "diagram_type": None,
        },
        {
            "id": "p6_q09_time",
            "topic": "Time & Duration",
            "marks": 2,
            "question": "9– A mathematics lesson started at 8:40 a.m. and lasted 45 minutes. At what time did it end?",
            "options": ["9:15 a.m.", "9:35 a.m.", "9:25 a.m.", "8:85 a.m."],
            "ans": "9:25 a.m.",
            "explanation": "8:40 + 20 minutes = 9:00 a.m., plus 25 minutes = 9:25 a.m.",
            "diagram_type": None,
        },
        {
            "id": "p6_q10_angles",
            "topic": "Lines, Angles & Geometric Figures",
            "marks": 2,
            "question": "10– Two angles on a straight line are 65° and x. Find the value of x.",
            "options": ["25°", "125°", "295°", "115°"],
            "ans": "115°",
            "explanation": "Angles on a straight line add up to 180°: x = 180° - 65° = 115°.",
            "diagram_type": None,
        },
        {
            "id": "p6_q11_algebra_simplify",
            "topic": "Algebra & Equations",
            "marks": 4,
            "question": "11– Simplify: 4k + 3m + 2k - m.",
            "options": ["6k + 2m", "6k + 4m", "2k + 2m", "8km"],
            "ans": "6k + 2m",
            "explanation": "Collect like terms: (4k + 2k) + (3m - m) = 6k + 2m.",
            "diagram_type": None,
        },
        {
            "id": "p6_q12i_perimeter",
            "topic": "Measurement & Geometry",
            "marks": 2,
            "question": (
                "12– The diagram below shows how Mr. Okello used his land. He used plot P to keep goats, "
                "plot Q to keep pigs and R to keep cattle. (i) Work out the total distance round the plot he used to keep pigs."
            ),
            "options": ["14 m", "18 m", "20 m", "9 m"],
            "ans": "18 m",
            "explanation": "Plot Q width = 10 m - 4 m = 6 m and height = 3 m, so perimeter = 2 × (6 + 3) = 18 m.",
            "diagram_type": "okello_land",
        },
        {
            "id": "p6_q12ii_area",
            "topic": "Measurement & Geometry",
            "marks": 4,
            "question": (
                "12– (ii) Find the size of the land area he has altogether which keeps all his goats, "
                "pigs and cattle in square metres."
            ),
            "options": ["50 sq m", "36 sq m", "80 sq m", "68 sq m"],
            "ans": "80 sq m",
            "explanation": "Total width = 10 m and total height = 3 m + 5 m = 8 m, giving 10 m × 8 m = 80 sq m.",
            "diagram_type": None,
        },
        {
            "id": "p6_q13_algebra",
            "topic": "Algebra & Equations",
            "marks": 5,
            "question": (
                "13– A boy said that they served with some cups of tea such that if a half of their "
                "total joins them, their sum could be 45. How many boys were they?"
            ),
            "options": ["22.5", "90", "15", "30"],
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
            "options": ["6 kg", "-6 kg", "144 kg", "150 kg"],
            "ans": "-6 kg",
            "explanation": "5 boys sum = 5 × 30 = 150 kg; 6 people sum = 6 × 24 = 144 kg; difference = 144 - 150 = -6 kg.",
            "diagram_type": None,
        },
        {
            "id": "p6_q16a_factors",
            "topic": "Factors & Multiples",
            "marks": 2,
            "question": "16– (a) List all the factors of 12.",
            "options": ["12, 24, 36, 48", "2, 3, 4, 6", "1, 2, 3, 4, 6, 12", "1, 3, 4, 12"],
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
            "options": ["48", "12", "2", "24"],
            "ans": "24",
            "explanation": "The least number divisible by both 6 and 8 is LCM(6, 8) = 24.",
            "diagram_type": None,
        },
    ],
    "P7": [
        {
            "id": "p7_1",
            "topic": "Speed, Distance & Time",
            "marks": 2,
            "question": "1– A car travels 180 km in 3 hours. Find its average speed.",
            "options": ["50 km/h", "90 km/h", "540 km/h", "60 km/h"],
            "ans": "60 km/h",
            "explanation": "Speed = Distance ÷ Time = 180 km ÷ 3 hr = 60 km/h.",
            "diagram_type": None,
        },
        {
            "id": "p7_2",
            "topic": "Algebra",
            "marks": 2,
            "question": "2– Solve for x: 2x + 6 = 18.",
            "options": ["12", "6", "9", "3"],
            "ans": "6",
            "explanation": "2x = 18 - 6 = 12 -> x = 6.",
            "diagram_type": None,
        },
    ],
}


# ==============================================================================
# 4. TRADITIONAL UGANDAN OMWESO ENGINE
# ==============================================================================


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


# ==============================================================================
# 5. LEADERBOARD & BADGES HELPERS
# ==============================================================================

BADGE_TIERS = [
    ("Gold Badge (1st)", "🥇"),
    ("Silver Badge (2nd)", "🥈"),
    ("Bronze Badge (3rd)", "🥉"),
]


def build_leaderboard(
    records: List[Dict[str, Any]],
    limit: int = 25,
    class_filter: str = "All",
    district_filter: str = "All",
) -> pd.DataFrame:
    """Aggregates pupil quiz attempt records into a ranked leaderboard up to `limit`."""
    if not records:
        return pd.DataFrame(
            columns=["Rank", "Badge", "Pupil Name", "School", "District", "Class", "Correct", "Attempted", "Marks"]
        )

    df = pd.DataFrame(records)
    if class_filter != "All":
        df = df[df["Class"] == class_filter]
    if district_filter != "All":
        df = df[df["District"] == district_filter]

    if df.empty:
        return pd.DataFrame(
            columns=["Rank", "Badge", "Pupil Name", "School", "District", "Class", "Correct", "Attempted", "Marks"]
        )

    grouped = (
        df.groupby(["Pupil Name", "School", "District", "Class"], as_index=False)
        .agg(
            Correct=("Correct", "sum"),
            Attempted=("Question", "count"),
            Marks=("Marks", "sum"),
        )
        .sort_values(by=["Marks", "Correct", "Attempted"], ascending=[False, False, True])
        .head(limit)
        .reset_index(drop=True)
    )

    ranks: List[int] = []
    badges: List[str] = []
    for idx in range(len(grouped)):
        rank = idx + 1
        ranks.append(rank)
        if rank == 1:
            badges.append("🥇 Gold (1st)")
        elif rank == 2:
            badges.append("🥈 Silver (2nd)")
        elif rank == 3:
            badges.append("🥉 Bronze (3rd)")
        else:
            badges.append("—")

    grouped.insert(0, "Rank", ranks)
    grouped.insert(1, "Badge", badges)
    return grouped


# ==============================================================================
# 6. MAIN STREAMLIT BLOCK
# ==============================================================================

TABS = ["Take Quiz", "NCDC Syllabus", "Dashboard", "Omweso Lab"]


def init_state() -> None:
    st.session_state.setdefault("quiz_score", {"attempted": 0, "correct": 0, "marks": 0})
    st.session_state.setdefault("answered_ids", set())
    st.session_state.setdefault("selected_class", "P6")
    st.session_state.setdefault("active_tab", "Take Quiz")
    st.session_state.setdefault("omweso_game", OmwesoGame())
    st.session_state.setdefault("pupil_info", {"name": "", "school": "", "district": "Kampala"})
    st.session_state.setdefault("attempt_records", [])


def main() -> None:
    init_state()

    active_tab = st.session_state.get("active_tab", "Take Quiz")
    margin_theme = TAB_MARGIN_STYLES.get(active_tab, TAB_MARGIN_STYLES["Take Quiz"])
    accent = margin_theme["accent"]
    border_tint = margin_theme["border_tint"]
    pill_bg = margin_theme["pill_bg"]
    pill_text = margin_theme["pill_text"]

    # Unified general app display + soft, low-tint margin & workspace frame
    st.markdown(
        "<style>"
        ".stApp {"
        "background: radial-gradient(circle at 12% 10%, rgba(11, 110, 63, 0.06), transparent 38%),"
        "radial-gradient(circle at 88% 14%, rgba(252, 220, 4, 0.04), transparent 34%),"
        "radial-gradient(circle at 75% 88%, rgba(6, 78, 44, 0.05), transparent 42%),"
        "linear-gradient(180deg, #F1F6F3 0%, #E7EFEA 55%, #DDE8E1 100%);"
        "background-attachment: fixed;"
        "}"
        f".ug-margin-rail {{"
        f"border-left: 5px solid {accent};"
        f"background: rgba(255, 255, 255, 0.92);"
        f"border-radius: 12px;"
        f"padding: 0.75rem 0.85rem;"
        f"box-shadow: 0 3px 10px rgba(15, 35, 25, 0.04);"
        f"transition: border-color 0.2s ease;"
        f"}}"
        f".ug-margin-badge {{"
        f"display: inline-block;"
        f"background: {pill_bg};"
        f"color: {pill_text};"
        f"font-size: 0.75rem;"
        f"font-weight: 700;"
        f"padding: 0.2rem 0.55rem;"
        f"border-radius: 999px;"
        f"margin-top: 0.35rem;"
        f"}}"
        ".top-left-tab-label {"
        "font-size: 0.78rem; font-weight: 700; color: #14532d; margin-bottom: 0.25rem;"
        "}"
        ".ug-title-banner {"
        "display: flex; align-items: center; gap: 0.9rem; padding: 0.8rem 1.1rem;"
        "background: rgba(255, 255, 255, 0.95); border: 1px solid rgba(15, 35, 25, 0.08);"
        f"border-left: 5px solid {accent}; border-radius: 14px;"
        "box-shadow: 0 4px 14px rgba(15, 35, 25, 0.05);"
        "}"
        ".ug-flag-stripes {"
        "display: inline-flex; flex-direction: column; width: 15px; height: 46px;"
        "border-radius: 3px; overflow: hidden; border: 1px solid #cbd5e1; flex-shrink: 0;"
        "}"
        ".ug-stripe-black { flex: 1; background-color: #000000; }"
        ".ug-stripe-yellow { flex: 1; background-color: #FCDC04; }"
        ".ug-stripe-red { flex: 1; background-color: #D90000; }"
        ".ug-main-heading { font-size: 2rem; font-weight: 700; line-height: 1.2; margin: 0; }"
        ".ug-brand-black { color: #000000; }"
        ".ug-brand-yellow { color: #C9A800; }"
        ".ug-brand-red { color: #D90000; }"
        ".badge-card {"
        "border: 1px solid rgba(15, 35, 25, 0.08); border-radius: 12px;"
        "padding: 0.8rem 0.95rem; background: rgba(255, 255, 255, 0.96); margin-bottom: 0.5rem;"
        "box-shadow: 0 2px 8px rgba(15, 35, 25, 0.04);"
        "}"
        f'[data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"]:nth-child(2) {{'
        f"background: rgba(255, 255, 255, 0.94);"
        f"border: 1px solid {border_tint};"
        f"border-left: 5px solid {accent};"
        f"border-radius: 16px;"
        f"padding: 1.35rem 1.55rem;"
        f"box-shadow: 0 5px 18px rgba(15, 35, 25, 0.05);"
        f"}}"
        "</style>",
        unsafe_allow_html=True,
    )

    class_list = list(QUIZ_BANK.keys())
    if st.session_state["selected_class"] not in class_list:
        st.session_state["selected_class"] = "P6"

    logo_kind, logo_val = get_logo_source()
    left_bar_col, header_col = st.columns([1.6, 5.4])
    with left_bar_col:
        st.markdown('<div class="ug-margin-rail">', unsafe_allow_html=True)
        if logo_kind == "file":
            st.image(logo_val, width=116)
        else:
            st.markdown(
                f'<img src="{logo_val}" alt="iLearn-Uganda Logo" width="116" style="border-radius:18px;"/>',
                unsafe_allow_html=True,
            )
        st.caption("NCDC Primary Maths Hub")
        st.markdown('<div class="top-left-tab-label">Tab Selector</div>', unsafe_allow_html=True)
        active_tab = st.selectbox(
            "Tab Selector",
            TABS,
            label_visibility="collapsed",
            key="active_tab",
        )
        margin_theme = TAB_MARGIN_STYLES.get(active_tab, TAB_MARGIN_STYLES["Take Quiz"])
        st.markdown(
            f'<div class="ug-margin-badge">● {active_tab}</div>'
            f'<div style="font-size:0.74rem; color:#374151; margin-top:0.3rem;">{margin_theme["note"]}</div>'
            "</div>",
            unsafe_allow_html=True,
        )

    with header_col:
        st.markdown(
            '<div class="ug-title-banner">'
            '<div class="ug-flag-stripes" title="Uganda Flag Colors: Black, Yellow, Red">'
            '<div class="ug-stripe-black"></div>'
            '<div class="ug-stripe-yellow"></div>'
            '<div class="ug-stripe-red"></div>'
            "</div>"
            "<div>"
            '<h1 class="ug-main-heading">'
            '<span class="ug-brand-black">iLearn</span>'
            '<span class="ug-brand-yellow">-</span>'
            '<span class="ug-brand-red">Uganda</span>'
            ": NCDC Primary Mathematics (P1 – P7)"
            "</h1>"
            '<div style="font-size:0.88rem; color:#374151; margin-top:0.2rem;">'
            "Growing bright minds from the roots up • Interactive Practice, Syllabus &amp; Omweso Lab"
            "</div>"
            "</div>"
            "</div>",
            unsafe_allow_html=True,
        )

    st.divider()

    # Unified general display container for all tabs
    _, tab_content_col = st.columns([1, 3])

    with tab_content_col:
        if active_tab == "Take Quiz":
            st.markdown("### Pupil Details")
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                pupil_name = st.text_input(
                    "Pupil Name",
                    value=st.session_state["pupil_info"]["name"],
                    placeholder="Enter full name",
                    key="input_pupil_name",
                )
            with p_col2:
                school_name = st.text_input(
                    "School Name",
                    value=st.session_state["pupil_info"]["school"],
                    placeholder="Enter school name",
                    key="input_school_name",
                )
            with p_col3:
                saved_district = st.session_state["pupil_info"]["district"]
                default_idx = UGANDA_DISTRICTS.index(saved_district) if saved_district in UGANDA_DISTRICTS else 0
                district_name = st.selectbox(
                    "District",
                    UGANDA_DISTRICTS,
                    index=default_idx,
                    key="select_district_name",
                )

            st.session_state["pupil_info"] = {
                "name": pupil_name.strip(),
                "school": school_name.strip(),
                "district": district_name,
            }

            selected_class = st.selectbox(
                "Select Class",
                class_list,
                key="selected_class",
                help="Choose P1 through P7 to load that class's mathematics quiz.",
            )
            st.subheader(f"{selected_class} Mathematics Quiz")

            if pupil_name.strip() or school_name.strip() or district_name:
                st.caption(
                    f"Candidate: **{pupil_name.strip() or 'Not provided'}** | "
                    f"School: **{school_name.strip() or 'Not provided'}** | "
                    f"District: **{district_name}**"
                )

            questions = QUIZ_BANK.get(selected_class, [])
            for idx, q in enumerate(questions):
                st.markdown(f"**{q['question']}** *({q.get('marks', 1)} mark(s))*")

                png = get_diagram_png(q.get("diagram_type"))
                if png:
                    st.image(png, caption="Diagram")

                pick = st.radio(
                    "Select answer:",
                    q["options"],
                    index=None,
                    key=f"q_{selected_class}_{idx}",
                )
                if st.button("Check Answer", key=f"btn_{selected_class}_{idx}"):
                    if not pupil_name.strip() or not school_name.strip() or not district_name:
                        st.warning("Please enter your name, school name, and select a district before checking your answer.")
                    elif pick is None:
                        st.warning("Please select an option before checking your answer.")
                    else:
                        q_uid = f"{selected_class}:{q['id']}"
                        ok = pick == q["ans"]
                        earned = q.get("marks", 1) if ok else 0
                        if q_uid not in st.session_state["answered_ids"]:
                            st.session_state["answered_ids"].add(q_uid)
                            st.session_state["quiz_score"]["attempted"] += 1
                            if ok:
                                st.session_state["quiz_score"]["correct"] += 1
                                st.session_state["quiz_score"]["marks"] += earned
                            st.session_state["attempt_records"].append({
                                "Pupil Name": pupil_name.strip(),
                                "School": school_name.strip(),
                                "District": district_name,
                                "Class": selected_class,
                                "Question": q["question"],
                                "Selected": pick,
                                "Correct": ok,
                                "Marks": earned,
                            })

                        if ok:
                            st.success(f"Correct! {q['explanation']}")
                        else:
                            st.error(f"Incorrect. Answer: **{q['ans']}** — {q['explanation']}")
                st.divider()

        elif active_tab == "NCDC Syllabus":
            active_cls = st.session_state["selected_class"]
            st.subheader(f"{active_cls} Syllabus Overview")
            for topic_row in NCDC_MATH_CURRICULUM.get(active_cls, []):
                with st.expander(f"{topic_row['topic']} ({topic_row['periods']} periods)", expanded=True):
                    st.caption(topic_row["curriculum_type"])
                    st.write(topic_row["learning_outcomes"])
                    st.markdown("**Sub-topics:** " + ", ".join(topic_row["sub_topics"]))
                    st.markdown("**Learning Aids:** " + ", ".join(topic_row["learning_aids"]))
                    st.markdown("**Life Skills & Values:** " + ", ".join(topic_row["life_skills_values"]))

        elif active_tab == "Dashboard":
            st.subheader("Progress & Coverage Dashboard")
            p_info = st.session_state["pupil_info"]
            if any(p_info.values()):
                st.info(
                    f"**Pupil:** {p_info['name'] or '—'} | "
                    f"**School:** {p_info['school'] or '—'} | "
                    f"**District:** {p_info['district'] or '—'}"
                )

            stats = st.session_state["quiz_score"]
            p6_total_marks = sum(item.get("marks", 1) for item in QUIZ_BANK["P6"])
            c1, c2, c3 = st.columns(3)
            c1.metric("Questions Attempted", stats["attempted"])
            c2.metric("Correct Answers", stats["correct"])
            c3.metric("Marks Earned (P6 Max)", f"{stats['marks']} / {p6_total_marks}")

            all_records = st.session_state["attempt_records"]
            available_classes = ["All"] + sorted({r["Class"] for r in all_records}) if all_records else ["All"] + class_list
            available_districts = (
                ["All"] + sorted({r["District"] for r in all_records}) if all_records else ["All"] + UGANDA_DISTRICTS
            )

            f_col1, f_col2 = st.columns(2)
            with f_col1:
                class_filter = st.selectbox("Filter Leaderboard by Class", available_classes, key="lb_class_filter")
            with f_col2:
                district_filter = st.selectbox("Filter Leaderboard by District", available_districts, key="lb_district_filter")

            leaderboard_df = build_leaderboard(
                all_records,
                limit=25,
                class_filter=class_filter,
                district_filter=district_filter,
            )

            st.markdown("### Top Three Badges")
            b_cols = st.columns(3)
            for i, (badge_title, icon) in enumerate(BADGE_TIERS):
                with b_cols[i]:
                    if i < len(leaderboard_df):
                        row = leaderboard_df.iloc[i]
                        st.markdown(
                            '<div class="badge-card">'
                            f'<div style="font-size:1.25rem;">{icon} <strong>{badge_title}</strong></div>'
                            f'<div style="font-size:1rem; margin-top:0.25rem;"><strong>{row["Pupil Name"]}</strong></div>'
                            f'<div style="font-size:0.85rem; color:#4b5563;">{row["School"]} ({row["District"]}) • {row["Class"]}</div>'
                            f'<div style="font-size:0.9rem; margin-top:0.35rem;"><strong>Marks: {row["Marks"]}</strong> ({row["Correct"]}/{row["Attempted"]} correct)</div>'
                            "</div>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            '<div class="badge-card">'
                            f'<div style="font-size:1.25rem;">{icon} <strong>{badge_title}</strong></div>'
                            '<div style="font-size:0.9rem; color:#6b7280; margin-top:0.35rem;">Awaiting pupil score</div>'
                            "</div>",
                            unsafe_allow_html=True,
                        )

            st.markdown("### Top 25 Performers")
            if not leaderboard_df.empty:
                st.dataframe(leaderboard_df, use_container_width=True, hide_index=True)
                lb_csv_bytes = leaderboard_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Top 25 Performers (CSV)",
                    data=lb_csv_bytes,
                    file_name="ilearn_uganda_top_25_performers.csv",
                    mime="text/csv",
                )
            else:
                st.caption("No matching pupil quiz attempts yet for the selected filters.")

            rows = [
                {
                    "Class": cls,
                    "Model": items[0]["curriculum_type"],
                    "Periods": sum(x["periods"] for x in items),
                    "Quiz Questions": len(QUIZ_BANK.get(cls, [])),
                }
                for cls, items in NCDC_MATH_CURRICULUM.items()
            ]
            st.markdown("### NCDC Syllabus Coverage")
            st.dataframe(pd.DataFrame(rows))

            if all_records:
                st.markdown("### Recorded Quiz Attempts")
                records_df = pd.DataFrame(all_records)
                st.dataframe(records_df)
                csv_bytes = records_df.to_csv(index=False).encode("utf-8")
                st.download_button(
                    label="Download Quiz Results (CSV)",
                    data=csv_bytes,
                    file_name="ilearn_uganda_quiz_results.csv",
                    mime="text/csv",
                )

        elif active_tab == "Omweso Lab":
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
                pit_choice = st.selectbox(
                    "Pick pit to sow:",
                    valid_pits,
                    format_func=lambda x: f"Pit #{x} ({game.board[0][x]})",
                )
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
