import base64
from datetime import datetime
import io
import json
import os
import random
from typing import Any, Dict, List, Optional, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

st.set_page_config(page_title="iLearn-Uganda | Primary Maths", layout="wide")

SPREADSHEET_ID = "12Kv-84apVPF5BRDF84wiWJ5l3j8X9rAYHpu3A9KAhWo"
QUIZ_LOG_SHEET_NAME = "Quiz_Marks_Log"
QUIZ_LOG_HEADERS = [
    "Timestamp",
    "Pupil Name",
    "School",
    "District",
    "Class",
    "Question ID",
    "Question",
    "Selected Answer",
    "Correct",
    "Marks Earned",
    "Max Marks",
]

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

# Balanced margin and workspace accent colors per selected tab
TAB_MARGIN_STYLES: Dict[str, Dict[str, str]] = {
    "Take Quiz": {
        "accent": "rgba(11, 110, 63, 0.72)",
        "border_tint": "rgba(11, 110, 63, 0.22)",
        "pill_bg": "rgba(220, 252, 231, 0.80)",
        "pill_text": "#064e2c",
        "note": "Practice & Assessment Margin",
    },
    "NCDC Syllabus": {
        "accent": "rgba(21, 128, 61, 0.72)",
        "border_tint": "rgba(21, 128, 61, 0.22)",
        "pill_bg": "rgba(224, 242, 254, 0.80)",
        "pill_text": "#075985",
        "note": "Curriculum Guide Margin",
    },
    "Dashboard": {
        "accent": "rgba(180, 83, 9, 0.72)",
        "border_tint": "rgba(180, 83, 9, 0.22)",
        "pill_bg": "rgba(254, 249, 195, 0.80)",
        "pill_text": "#854d0e",
        "note": "Standings & Analytics Margin",
    },
    "Omweso Lab": {
        "accent": "rgba(185, 28, 28, 0.72)",
        "border_tint": "rgba(185, 28, 28, 0.22)",
        "pill_bg": "rgba(254, 226, 226, 0.80)",
        "pill_text": "#991b1b",
        "note": "Strategy Board Margin",
    },
}


# ==============================================================================
# 1. LOGO & IN-MEMORY DIAGRAM RENDERER
# ==============================================================================


def get_logo_source() -> Tuple[str, Any]:
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
# 3. QUIZ BANK (ALL CLASSES P1–P7, WITH LINE-BY-LINE DETAILED EXPLANATIONS)
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
            "step_by_step": [
                "Line 1 — Start with the first number: 5.",
                "Line 2 — Count forward by 3 steps (ones): 6, 7, 8.",
                "Line 3 — The final sum is 8.",
            ],
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
            "step_by_step": [
                "Line 1 — Locate 14 on the counting sequence in ones.",
                "Line 2 — Add 1 to move to the immediate next number: 14 + 1 = 15.",
                "Line 3 — Therefore, 15 comes right after 14.",
            ],
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
            "step_by_step": [
                "Line 1 — Break 428 into place-value positions from right to left.",
                "Line 2 — 8 is in the Ones place, 2 is in the Tens place, and 4 is in the Hundreds place.",
                "Line 3 — So the place value of 4 in 428 is Hundreds.",
            ],
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
            "step_by_step": [
                "Line 1 — Add the Ones column: 5 + 2 = 7.",
                "Line 2 — Add the Tens column: 4 + 3 = 7.",
                "Line 3 — Bring down the Hundreds digit: 1.",
                "Line 4 — Combine the digits to get 177.",
            ],
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
            "step_by_step": [
                "Line 1 — Identify total mangoes = 24 and number of pupils = 4.",
                "Line 2 — Divide equally: 24 ÷ 4.",
                "Line 3 — Since 4 × 6 = 24, each pupil gets 6 mangoes.",
            ],
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
            "step_by_step": [
                "Line 1 — Divide a whole into 4 equal parts (denominator = 4).",
                "Line 2 — Take 1 of those equal parts (numerator = 1).",
                "Line 3 — Write as a fraction: 1/4.",
            ],
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
            "step_by_step": [
                "Line 1 — Recall that A ∩ B (intersection) means members found in BOTH A and B.",
                "Line 2 — Check elements of A ({1, 2, 3}) against B ({2, 3, 4}): 2 and 3 appear in both.",
                "Line 3 — Write the intersection set: {2, 3}.",
            ],
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
            "step_by_step": [
                "Line 1 — Split XXIV into recognizable Roman parts: XX and IV.",
                "Line 2 — Convert each part: XX = 10 + 10 = 20, and IV = 5 - 1 = 4.",
                "Line 3 — Add them together: 20 + 4 = 24.",
            ],
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
            "step_by_step": [
                "Line 1 — List multiples of 6: 6, 12, 18, 24, 30...",
                "Line 2 — List multiples of 8: 8, 16, 24, 32...",
                "Line 3 — Identify the smallest number appearing in both lists: 24.",
            ],
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
            "step_by_step": [
                "Line 1 — State the formula for area of a rectangle: Area = Length × Width.",
                "Line 2 — Substitute the given measurements: Area = 9 cm × 4 cm.",
                "Line 3 — Multiply: 9 × 4 = 36 sq cm.",
            ],
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
            "step_by_step": [
                "Line 1 — List all elements in the universal set E from the Venn diagram: E = {e, f, a, i, b, c, g}.",
                "Line 2 — Find set B - A (elements in B that are not in A): {b, c}.",
                "Line 3 — Take the complement (B - A)' by excluding {b, c} from E: {e, f, a, i, g}.",
            ],
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
            "step_by_step": [
                "Line 1 — Separate CIX into C and IX.",
                "Line 2 — Convert C = 100 and IX = 10 - 1 = 9.",
                "Line 3 — Add the values: 100 + 9 = 109.",
            ],
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
            "step_by_step": [
                "Line 1 — Expand 21_n in base ten: (2 × n^1) + (1 × n^0) = 2n + 1.",
                "Line 2 — Set up the equation: 2n + 1 = 11.",
                "Line 3 — Subtract 1 from both sides: 2n = 10.",
                "Line 4 — Divide by 2: n = 5, which is Base five.",
            ],
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
            "step_by_step": [
                "Line 1 — Write prime factors of Q = 2² × 3² and P = 2¹ × 3¹ × 5¹.",
                "Line 2 — Identify common prime bases in both Q and P: 2 and 3 (5 is only in P).",
                "Line 3 — Pick the lowest power of each common prime: 2¹ × 3¹ = 2 × 3 = 6.",
            ],
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
            "step_by_step": [
                "Line 1 — Convert 50% to a fraction with denominator 8: 50% = 1/2 = 4/8.",
                "Line 2 — Add the fraction for Matooke and Rice: 4/8 + 3/8 = 7/8.",
                "Line 3 — Subtract from 1 whole class: 1 - 7/8 = 8/8 - 7/8 = 1/8.",
            ],
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
            "step_by_step": [
                "Line 1 — Find pupils who ate Matooke: 50% of 48 = (50/100) × 48 = 24 pupils.",
                "Line 2 — Find pupils who ate Posho: (1/8) × 48 = 6 pupils.",
                "Line 3 — Subtract Posho pupils from Matooke pupils: 24 - 6 = 18 more pupils.",
            ],
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
            "step_by_step": [
                "Line 1 — List Paul's marks from the table: 70, 80, 70, 50, 90, 50.",
                "Line 2 — Count how often each mark appears: 70 appears 2 times; 50 appears 2 times; 80 and 90 appear 1 time each.",
                "Line 3 — Since 70 and 50 tie for the highest frequency (2), the modal marks are 70 and 50.",
            ],
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
            "step_by_step": [
                "Line 1 — Find the Lowest Common Denominator (LCD) of 4 and 6, which is 12.",
                "Line 2 — Convert to equivalent fractions: 3/4 = 9/12 and 1/6 = 2/12.",
                "Line 3 — Add the numerators over 12: (9 + 2)/12 = 11/12.",
            ],
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
            "step_by_step": [
                "Line 1 — Note the cost of 1 book = sh 4,500 and number of books = 3.",
                "Line 2 — Multiply: 3 × sh 4,000 = sh 12,000.",
                "Line 3 — Multiply the remaining sh 500: 3 × sh 500 = sh 1,500.",
                "Line 4 — Add both parts: sh 12,000 + sh 1,500 = sh 13,500.",
            ],
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
            "step_by_step": [
                "Line 1 — Start time is 8:40 a.m. and duration is 45 minutes.",
                "Line 2 — Add 20 minutes to reach the next full hour: 8:40 a.m. + 20 min = 9:00 a.m.",
                "Line 3 — Subtract 20 from 45 to find remaining minutes: 45 - 20 = 25 minutes.",
                "Line 4 — Add the remaining 25 minutes to 9:00 a.m. to get 9:25 a.m.",
            ],
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
            "step_by_step": [
                "Line 1 — Recall that adjacent angles on a straight line sum to 180°.",
                "Line 2 — Set up the equation: 65° + x = 180°.",
                "Line 3 — Subtract 65° from 180°: x = 180° - 65° = 115°.",
            ],
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
            "step_by_step": [
                "Line 1 — Group like terms with variable k: 4k + 2k.",
                "Line 2 — Group like terms with variable m: 3m - m.",
                "Line 3 — Simplify k terms: 4k + 2k = 6k.",
                "Line 4 — Simplify m terms: 3m - 1m = 2m, giving 6k + 2m.",
            ],
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
            "step_by_step": [
                "Line 1 — Find the horizontal length (width) of plot Q: total top span is 10 m and plot P takes 4 m, so 10 m - 4 m = 6 m.",
                "Line 2 — Find the vertical height of plot Q, which matches plot P at 3 m.",
                "Line 3 — Calculate perimeter of rectangular plot Q: 2 × (Length + Width) = 2 × (6 m + 3 m) = 2 × 9 m = 18 m.",
            ],
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
            "step_by_step": [
                "Line 1 — Find total horizontal width across the whole land: 10 m.",
                "Line 2 — Find total vertical height: upper section (P/Q) is 3 m + lower section (R) is 5 m = 8 m.",
                "Line 3 — Multiply total width by total height: 10 m × 8 m = 80 sq m.",
            ],
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
            "step_by_step": [
                "Line 1 — Let the number of boys be x.",
                "Line 2 — Write the equation from the statement: x + (1/2)x = 45.",
                "Line 3 — Combine like terms: (3/2)x = 45.",
                "Line 4 — Multiply both sides by 2: 3x = 90.",
                "Line 5 — Divide by 3: x = 90 ÷ 3 = 30 boys.",
            ],
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
            "step_by_step": [
                "Line 1 — List numbers leaving remainder 5 when divided by 7: 5, 12, 19, 26, 33...",
                "Line 2 — List numbers leaving remainder 2 when divided by 6: 2, 8, 14, 20, 26, 32...",
                "Line 3 — Find the common number in both sequences: 26.",
                "Line 4 — Verify: 26 ÷ 7 = 3 rem 5, and 26 ÷ 6 = 4 rem 2.",
            ],
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
            "step_by_step": [
                "Line 1 — Calculate total mass of the 5 boys: 5 × 30 kg = 150 kg.",
                "Line 2 — Calculate total mass of all 6 people (5 boys + 1 teacher): 6 × 24 kg = 144 kg.",
                "Line 3 — Subtract total mass of the 5 boys from total mass of the 6 people: 144 kg - 150 kg = -6 kg.",
            ],
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
            "step_by_step": [
                "Line 1 — Find pairs of whole numbers that multiply to 12: 1 × 12, 2 × 6, and 3 × 4.",
                "Line 2 — Arrange all distinct factors in ascending order: 1, 2, 3, 4, 6, 12.",
            ],
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
            "step_by_step": [
                "Line 1 — 'Least number shared equally by either 6 or 8 without remainder' means LCM(6, 8).",
                "Line 2 — Multiples of 6: 6, 12, 18, 24...; Multiples of 8: 8, 16, 24...",
                "Line 3 — The smallest common multiple is 24 sweets.",
            ],
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
            "step_by_step": [
                "Line 1 — Identify Distance = 180 km and Time = 3 hours.",
                "Line 2 — Apply the formula: Average Speed = Distance ÷ Time.",
                "Line 3 — Divide: 180 ÷ 3 = 60 km/h.",
            ],
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
            "step_by_step": [
                "Line 1 — Start with the equation: 2x + 6 = 18.",
                "Line 2 — Subtract 6 from both sides: 2x = 18 - 6 = 12.",
                "Line 3 — Divide both sides by 2: x = 12 ÷ 2 = 6.",
            ],
            "diagram_type": None,
        },
    ],
}


def build_question_lookup() -> Dict[str, Dict[str, Any]]:
    lookup: Dict[str, Dict[str, Any]] = {}
    for cls_code, q_list in QUIZ_BANK.items():
        for q_item in q_list:
            q_id = str(q_item.get("id", ""))
            lookup[f"{cls_code}:{q_id}"] = {**q_item, "class": cls_code}
            lookup[q_item["question"]] = {**q_item, "class": cls_code}
    return lookup


QUESTION_LOOKUP = build_question_lookup()


def get_detailed_lines_for_record(record: Dict[str, Any]) -> List[str]:
    q_uid = str(record.get("q_uid", "") or "")
    q_id = str(record.get("Question ID", "") or "")
    cls_code = str(record.get("Class", "") or "")
    q_text = str(record.get("Question", "") or "")

    matched = (
        QUESTION_LOOKUP.get(q_uid)
        or QUESTION_LOOKUP.get(f"{cls_code}:{q_id}")
        or QUESTION_LOOKUP.get(q_text)
    )
    if matched and matched.get("step_by_step"):
        return list(matched["step_by_step"])
    if matched and matched.get("explanation"):
        return [f"Line 1 — {matched['explanation']}"]
    return [f"Line 1 — Evaluated answer '{record.get('Selected', '')}' for {q_text}."]


def render_line_by_line_explanation(record: Dict[str, Any], correct_ans: Optional[str] = None) -> None:
    lines = get_detailed_lines_for_record(record)
    st.markdown("**Line-by-Line Detailed Explanation:**")
    for line in lines:
        st.markdown(f"- {line}")
    if correct_ans is not None:
        st.markdown(f"- **Correct Answer:** `{correct_ans}` | **Marks Earned:** `{record.get('Marks', 0)}/{record.get('Max Marks', 1)}`")


# ==============================================================================
# 4. GOOGLE SHEETS PERSISTENCE LAYER (ALL CLASSES P1–P7)
# ==============================================================================


def _get_secret_or_env(key: str, default: Any = None) -> Any:
    try:
        if key in st.secrets:
            return st.secrets[key]
    except Exception:
        pass
    return os.environ.get(key, default)


def _get_webhook_url() -> Optional[str]:
    url = _get_secret_or_env("GSHEET_WEBHOOK_URL") or _get_secret_or_env("GOOGLE_SHEETS_WEBHOOK_URL")
    return str(url).strip() if url else None


def _get_service_account_dict() -> Optional[Dict[str, Any]]:
    raw = _get_secret_or_env("GCP_SERVICE_ACCOUNT") or _get_secret_or_env("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw:
        return None
    if isinstance(raw, dict):
        return dict(raw)
    try:
        return json.loads(str(raw))
    except Exception:
        return None


@st.cache_resource(show_spinner=False)
def _get_gspread_worksheet():
    sa_info = _get_service_account_dict()
    if not sa_info:
        return None
    try:
        import gspread  # type: ignore
        from google.oauth2.service_account import Credentials  # type: ignore

        scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        creds = Credentials.from_service_account_info(sa_info, scopes=scopes)
        client = gspread.authorize(creds)
        sheet_id = str(_get_secret_or_env("GSHEET_SPREADSHEET_ID", SPREADSHEET_ID)).strip()
        spreadsheet = client.open_by_key(sheet_id)
        try:
            return spreadsheet.worksheet(QUIZ_LOG_SHEET_NAME)
        except Exception:
            return spreadsheet.add_worksheet(title=QUIZ_LOG_SHEET_NAME, rows=500, cols=len(QUIZ_LOG_HEADERS))
    except Exception:
        return None


def _parse_bool(val: Any) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).strip().upper() in {"TRUE", "1", "YES", "Y"}


def _parse_int(val: Any, fallback: int = 0) -> int:
    try:
        return int(float(str(val).strip()))
    except Exception:
        return fallback


def _rows_to_records(rows: List[List[Any]]) -> List[Dict[str, Any]]:
    if not rows:
        return []
    start_idx = 1 if rows[0] and str(rows[0][0]).strip().lower() == "timestamp" else 0
    records: List[Dict[str, Any]] = []
    for r in rows[start_idx:]:
        if not isinstance(r, list) or len(r) < 10 or not str(r[1] or "").strip():
            continue
        cls_val = str(r[4] or "").strip()
        if cls_val not in QUIZ_BANK:
            continue
        q_text = str(r[6] or "").strip()
        q_id = str(r[5] or "").strip()
        q_uid = f"{cls_val}:{q_id}" if q_id else f"{cls_val}:{q_text}"
        records.append({
            "Timestamp": str(r[0] or "").strip(),
            "Pupil Name": str(r[1] or "").strip(),
            "School": str(r[2] or "").strip(),
            "District": str(r[3] or "").strip(),
            "Class": cls_val,
            "Question ID": q_id,
            "q_uid": q_uid,
            "Question": q_text,
            "Selected": str(r[7] or "").strip(),
            "Correct": _parse_bool(r[8]),
            "Marks": _parse_int(r[9], 0),
            "Max Marks": _parse_int(r[10] if len(r) > 10 else 1, 1),
        })
    return records


@st.cache_data(ttl=30, show_spinner=False)
def load_records_from_google_sheet() -> Tuple[List[Dict[str, Any]], str]:
    """Reads Quiz_Marks_Log from Google Sheets so marks survive Streamlit app reboots."""
    ws = _get_gspread_worksheet()
    if ws is not None:
        try:
            values = ws.get_all_values()
            return _rows_to_records(values), "Google Sheets (Live Sync Connected)"
        except Exception as exc:
            return [], f"Google Sheets read fallback ({exc})"

    webhook_url = _get_webhook_url()
    if webhook_url:
        try:
            req_url = f"{webhook_url}{'&' if '?' in webhook_url else '?'}sheet={QUIZ_LOG_SHEET_NAME}"
            with urlrequest.urlopen(req_url, timeout=8) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
                rows = payload.get("rows", []) if isinstance(payload, dict) else []
                return _rows_to_records(rows), "Google Sheets (Webhook Sync Connected)"
        except Exception as exc:
            return [], f"Webhook read fallback ({exc})"

    return [], "Session Memory Only (Add service account or webhook secret to sync Google Sheets)"


def append_attempt_to_google_sheet(record: Dict[str, Any]) -> Tuple[bool, str]:
    """Appends a single pupil quiz attempt row across any class (P1–P7) to Quiz_Marks_Log."""
    row_values = [
        record["Timestamp"],
        record["Pupil Name"],
        record["School"],
        record["District"],
        record["Class"],
        record["Question ID"],
        record["Question"],
        record["Selected"],
        "TRUE" if record["Correct"] else "FALSE",
        int(record["Marks"]),
        int(record["Max Marks"]),
    ]

    ws = _get_gspread_worksheet()
    if ws is not None:
        try:
            existing = ws.get_all_values()
            if not existing:
                ws.append_row(QUIZ_LOG_HEADERS, value_input_option="USER_ENTERED")
            ws.append_row(row_values, value_input_option="USER_ENTERED")
            load_records_from_google_sheet.clear()
            return True, "Saved to Google Sheet (Quiz_Marks_Log)"
        except Exception as exc:
            return False, f"Could not write to Google Sheet: {exc}"

    webhook_url = _get_webhook_url()
    if webhook_url:
        try:
            payload = json.dumps({"sheet": QUIZ_LOG_SHEET_NAME, "row": row_values}).encode("utf-8")
            req = urlrequest.Request(
                webhook_url,
                data=payload,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            with urlrequest.urlopen(req, timeout=8) as resp:
                if 200 <= resp.status < 300:
                    load_records_from_google_sheet.clear()
                    return True, "Saved to Google Sheet via webhook"
                return False, f"Webhook returned HTTP {resp.status}"
        except (urlerror.URLError, TimeoutError, Exception) as exc:
            return False, f"Webhook write failed: {exc}"

    return False, "Saved in app session (configure Google Sheet credentials for reboot persistence)"


def _sync_state_from_records(records: List[Dict[str, Any]]) -> None:
    answered_ids = {r["q_uid"] for r in records if r.get("q_uid")}
    total_attempted = len(records)
    total_correct = sum(1 for r in records if r.get("Correct"))
    total_marks = sum(int(r.get("Marks", 0)) for r in records)
    st.session_state["attempt_records"] = records
    st.session_state["answered_ids"] = answered_ids
    st.session_state["quiz_score"] = {
        "attempted": total_attempted,
        "correct": total_correct,
        "marks": total_marks,
    }


def record_single_answer(
    q: Dict[str, Any],
    idx: int,
    selected_class: str,
    pick: Any,
    pupil_name: str,
    school_name: str,
    district_name: str,
) -> Dict[str, Any]:
    q_id = str(q.get("id", f"{selected_class}_q{idx + 1}"))
    q_uid = f"{selected_class}:{q_id}"
    ok = pick == q.get("ans")
    max_marks = int(q.get("marks", 1))
    earned = max_marks if ok else 0

    record = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Pupil Name": (pupil_name or "").strip(),
        "School": (school_name or "").strip(),
        "District": district_name,
        "Class": selected_class,
        "Question ID": q_id,
        "q_uid": q_uid,
        "Question": q["question"],
        "Selected": pick,
        "Correct": ok,
        "Marks": earned,
        "Max Marks": max_marks,
    }

    is_new = q_uid not in st.session_state["answered_ids"]
    if is_new:
        st.session_state["answered_ids"].add(q_uid)
        st.session_state["quiz_score"]["attempted"] += 1
        if ok:
            st.session_state["quiz_score"]["correct"] += 1
            st.session_state["quiz_score"]["marks"] += earned
        st.session_state["attempt_records"].append(record)

    synced, sync_msg = append_attempt_to_google_sheet(record)
    st.session_state["sync_status"] = sync_msg

    feedback_item = {
        "ok": ok,
        "ans": q.get("ans"),
        "record": record,
        "sync_msg": sync_msg if synced else "",
    }
    st.session_state["last_checked_feedback"][q_uid] = feedback_item
    return feedback_item


# ==============================================================================
# 5. TRADITIONAL UGANDAN OMWESO ENGINE
# ==============================================================================


class OmwesoGame:
    def __init__(self) -> None:
        self.board = [
            [4] * 8 + [0] * 8,
            [4] * 8 + [0] * 8,
        ]
        self.turn = 0
        self.log = ["Board initialized with 32 seeds per player."]

    def get_opposite_enemy_pits(self, inner_idx: int) -> Tuple[int, int]:
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
# 6. LEADERBOARD & BADGES HELPERS
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
    """Aggregates pupil quiz attempt records across P1–P7 into a ranked leaderboard up to `limit`."""
    if not records:
        return pd.DataFrame(
            columns=["Rank", "Badge", "Pupil Name", "School", "District", "Class", "Correct", "Attempted", "Marks"]
        )

    df = pd.DataFrame(records)
    if df.empty:
        return pd.DataFrame(
            columns=["Rank", "Badge", "Pupil Name", "School", "District", "Class", "Correct", "Attempted", "Marks"]
        )

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
# 7. MAIN STREAMLIT BLOCK
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
    st.session_state.setdefault("last_checked_feedback", {})
    st.session_state.setdefault("submitted_quiz_summary", None)
    st.session_state.setdefault("sync_status", "")

    if not st.session_state.get("sheet_hydrated", False):
        persisted_records, status_msg = load_records_from_google_sheet()
        st.session_state["sync_status"] = status_msg
        if persisted_records:
            _sync_state_from_records(persisted_records)
        st.session_state["sheet_hydrated"] = True


def main() -> None:
    init_state()

    active_tab = st.session_state.get("active_tab", "Take Quiz")
    if active_tab not in TABS:
        active_tab = "Take Quiz"
    margin_theme = TAB_MARGIN_STYLES.get(active_tab, TAB_MARGIN_STYLES["Take Quiz"])
    accent = margin_theme["accent"]
    border_tint = margin_theme["border_tint"]
    pill_bg = margin_theme["pill_bg"]
    pill_text = margin_theme["pill_text"]

    st.markdown(
        "<style>"
        ".stApp {"
        "background: radial-gradient(circle at 12% 10%, rgba(11, 110, 63, 0.11), transparent 39%),"
        "radial-gradient(circle at 88% 14%, rgba(252, 220, 4, 0.06), transparent 35%),"
        "radial-gradient(circle at 75% 88%, rgba(6, 78, 44, 0.10), transparent 44%),"
        "linear-gradient(180deg, #E3EFE8 0%, #D6E7DD 55%, #C9DFD2 100%);"
        "background-attachment: fixed;"
        "}"
        f".ug-margin-rail {{"
        f"border-left: 6px solid {accent};"
        f"background: rgba(255, 255, 255, 0.90);"
        f"border-radius: 12px;"
        f"padding: 0.75rem 0.85rem;"
        f"box-shadow: 0 3px 12px rgba(6, 45, 25, 0.06);"
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
        "font-size: 0.78rem; font-weight: 700; color: #064e2c; margin-bottom: 0.25rem;"
        "}"
        ".ug-title-banner {"
        "display: flex; align-items: center; gap: 0.9rem; padding: 0.8rem 1.1rem;"
        "background: rgba(255, 255, 255, 0.94); border: 1px solid rgba(6, 78, 44, 0.14);"
        f"border-left: 6px solid {accent}; border-radius: 14px;"
        "box-shadow: 0 5px 16px rgba(6, 45, 25, 0.08);"
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
        "border: 1px solid rgba(6, 78, 44, 0.14); border-radius: 12px;"
        "padding: 0.8rem 0.95rem; background: rgba(255, 255, 255, 0.95); margin-bottom: 0.5rem;"
        "box-shadow: 0 3px 10px rgba(6, 45, 25, 0.06);"
        "}"
        f'[data-testid="stHorizontalBlock"]:last-of-type > [data-testid="stColumn"]:nth-child(2) {{'
        f"background: rgba(255, 255, 255, 0.92);"
        f"border: 1.5px solid {border_tint};"
        f"border-left: 6px solid {accent};"
        f"border-radius: 16px;"
        f"padding: 1.35rem 1.55rem;"
        f"box-shadow: 0 6px 20px rgba(6, 45, 25, 0.08);"
        f"}}"
        "</style>",
        unsafe_allow_html=True,
    )

    class_list = list(QUIZ_BANK.keys())
    if st.session_state.get("selected_class") not in class_list:
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
        st.caption("NCDC Primary Maths Hub (P1–P7)")
        st.markdown('<div class="top-left-tab-label">Tab Selector</div>', unsafe_allow_html=True)
        active_tab = st.selectbox(
            "Tab Selector",
            TABS,
            index=TABS.index(active_tab),
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

    _, tab_content_col = st.columns([1, 3])

    with tab_content_col:
        if active_tab == "Take Quiz":
            st.markdown("### Pupil Details")
            p_col1, p_col2, p_col3 = st.columns(3)
            with p_col1:
                pupil_name = st.text_input(
                    "Pupil Name",
                    value=st.session_state["pupil_info"].get("name", ""),
                    placeholder="Enter full name",
                    key="input_pupil_name",
                )
            with p_col2:
                school_name = st.text_input(
                    "School Name",
                    value=st.session_state["pupil_info"].get("school", ""),
                    placeholder="Enter school name",
                    key="input_school_name",
                )
            with p_col3:
                saved_district = st.session_state["pupil_info"].get("district", "Kampala")
                default_idx = UGANDA_DISTRICTS.index(saved_district) if saved_district in UGANDA_DISTRICTS else 0
                district_name = st.selectbox(
                    "District",
                    UGANDA_DISTRICTS,
                    index=default_idx,
                    key="select_district_name",
                )

            clean_name = (pupil_name or "").strip()
            clean_school = (school_name or "").strip()
            st.session_state["pupil_info"] = {
                "name": clean_name,
                "school": clean_school,
                "district": district_name,
            }

            selected_class = st.selectbox(
                "Select Class",
                class_list,
                key="selected_class",
                help="Choose P1 through P7 to load that class's mathematics quiz.",
            )
            st.subheader(f"{selected_class} Mathematics Quiz")

            if clean_name or clean_school or district_name:
                st.caption(
                    f"Candidate: **{clean_name or 'Not provided'}** | "
                    f"School: **{clean_school or 'Not provided'}** | "
                    f"District: **{district_name}**"
                )

            questions = QUIZ_BANK.get(selected_class, [])
            selected_picks: Dict[int, Any] = {}

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
                selected_picks[idx] = pick
                q_id = str(q.get("id", f"{selected_class}_q{idx + 1}"))
                q_uid = f"{selected_class}:{q_id}"

                if st.button("Check Answer", key=f"btn_{selected_class}_{idx}"):
                    if not clean_name or not clean_school or not district_name:
                        st.warning("Please enter your name, school name, and select a district before checking your answer.")
                    elif pick is None:
                        st.warning("Please select an option before checking your answer.")
                    else:
                        fb_item = record_single_answer(
                            q=q,
                            idx=idx,
                            selected_class=selected_class,
                            pick=pick,
                            pupil_name=clean_name,
                            school_name=clean_school,
                            district_name=district_name,
                        )
                        st.session_state["last_checked_feedback"][q_uid] = fb_item

                fb = st.session_state["last_checked_feedback"].get(q_uid)
                if fb:
                    if fb["ok"]:
                        st.success(f"Correct! Selected: **{fb['record']['Selected']}**")
                    else:
                        st.error(f"Incorrect. Selected: **{fb['record']['Selected']}** | Answer: **{fb['ans']}**")
                    render_line_by_line_explanation(fb["record"], correct_ans=fb["ans"])
                    if fb.get("sync_msg"):
                        st.caption(fb["sync_msg"])
                st.divider()

            st.markdown("### Submit Quiz")
            sub_col1, sub_col2 = st.columns([1.4, 1.6])
            with sub_col1:
                submit_clicked = st.button("Submit Quiz", type="primary", use_container_width=True, key="btn_submit_quiz")
            with sub_col2:
                open_dash_clicked = st.button("Open Dashboard & Leaderboard", use_container_width=True, key="btn_go_dashboard")

            if submit_clicked:
                if not clean_name or not clean_school or not district_name:
                    st.warning("Please enter your name, school name, and select a district before submitting the quiz.")
                else:
                    answered_items: List[Dict[str, Any]] = []
                    unanswered_count = 0
                    for idx, q in enumerate(questions):
                        chosen = selected_picks.get(idx)
                        if chosen is None:
                            unanswered_count += 1
                            continue
                        fb_item = record_single_answer(
                            q=q,
                            idx=idx,
                            selected_class=selected_class,
                            pick=chosen,
                            pupil_name=clean_name,
                            school_name=clean_school,
                            district_name=district_name,
                        )
                        answered_items.append(fb_item)

                    if not answered_items:
                        st.warning("Select at least one answer above before clicking Submit Quiz.")
                    else:
                        total_earned = sum(int(item["record"]["Marks"]) for item in answered_items)
                        total_possible = sum(int(item["record"]["Max Marks"]) for item in answered_items)
                        total_right = sum(1 for item in answered_items if item["ok"])
                        st.session_state["submitted_quiz_summary"] = {
                            "class": selected_class,
                            "pupil_name": clean_name,
                            "school_name": clean_school,
                            "district_name": district_name,
                            "submitted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "earned": total_earned,
                            "possible": total_possible,
                            "right": total_right,
                            "count": len(answered_items),
                            "unanswered": unanswered_count,
                            "items": answered_items,
                        }

            if open_dash_clicked:
                st.session_state["active_tab"] = "Dashboard"
                st.rerun()

            summary = st.session_state.get("submitted_quiz_summary")
            if isinstance(summary, dict):
                st.success(
                    f"Quiz submitted for **{summary['pupil_name']}** ({summary['class']}) — "
                    f"Score: **{summary['earned']} / {summary['possible']} marks** "
                    f"({summary['right']}/{summary['count']} answered correctly)"
                )
                if summary.get("unanswered", 0) > 0:
                    st.caption(f"Note: {summary['unanswered']} question(s) in {summary['class']} had no option selected and were not scored.")
                for item in summary.get("items", []):
                    rec = item["record"]
                    mark_status = "Correct" if item["ok"] else "Incorrect"
                    with st.expander(f"{rec['Question']} — {mark_status} ({rec['Marks']}/{rec['Max Marks']} marks)", expanded=True):
                        st.markdown(f"- **Your Answer:** `{rec['Selected']}` | **Correct Answer:** `{item['ans']}`")
                        render_line_by_line_explanation(rec, correct_ans=item["ans"])

        elif active_tab == "NCDC Syllabus":
            active_cls = st.session_state.get("selected_class", "P6")
            st.subheader(f"{active_cls} Syllabus Overview")
            for topic_row in NCDC_MATH_CURRICULUM.get(active_cls, []):
                with st.expander(f"{topic_row['topic']} ({topic_row['periods']} periods)", expanded=True):
                    st.caption(topic_row["curriculum_type"])
                    st.write(topic_row["learning_outcomes"])
                    st.markdown("**Sub-topics:** " + ", ".join(topic_row["sub_topics"]))
                    st.markdown("**Learning Aids:** " + ", ".join(topic_row["learning_aids"]))
                    st.markdown("**Life Skills & Values:** " + ", ".join(topic_row["life_skills_values"]))

        elif active_tab == "Dashboard":
            st.subheader("Progress & Coverage Dashboard (P1 – P7)")
            if st.session_state.get("sync_status"):
                st.caption(f"Persistence Status: {st.session_state['sync_status']}")

            if st.button("Reload Marks from Google Sheet", key="btn_reload_sheet"):
                load_records_from_google_sheet.clear()
                refreshed_records, status_msg = load_records_from_google_sheet()
                st.session_state["sync_status"] = status_msg
                if refreshed_records:
                    _sync_state_from_records(refreshed_records)
                st.rerun()

            p_info = st.session_state.get("pupil_info", {})
            if any(p_info.values()):
                st.info(
                    f"**Pupil:** {p_info.get('name') or '—'} | "
                    f"**School:** {p_info.get('school') or '—'} | "
                    f"**District:** {p_info.get('district') or '—'}"
                )

            all_records = st.session_state.get("attempt_records", [])
            stats = st.session_state.get("quiz_score", {"attempted": 0, "correct": 0, "marks": 0})
            all_classes_max_marks = sum(
                int(item.get("marks", 1))
                for cls_items in QUIZ_BANK.values()
                for item in cls_items
            )
            c1, c2, c3 = st.columns(3)
            c1.metric("Questions Attempted", stats.get("attempted", 0))
            c2.metric("Correct Answers", stats.get("correct", 0))
            c3.metric("Marks Earned (P1–P7 Bank)", f"{stats.get('marks', 0)} / {all_classes_max_marks}")

            available_classes = ["All"] + class_list
            available_districts = (
                ["All"] + sorted({r["District"] for r in all_records if r.get("District")})
                if all_records
                else ["All"] + UGANDA_DISTRICTS
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

            st.markdown("### Top 25 Performers (P1 – P7)")
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
                    "Recorded Attempts": sum(1 for r in all_records if r.get("Class") == cls),
                    "Recorded Marks": sum(int(r.get("Marks", 0)) for r in all_records if r.get("Class") == cls),
                }
                for cls, items in NCDC_MATH_CURRICULUM.items()
            ]
            st.markdown("### NCDC Syllabus & Marks Coverage (P1 – P7)")
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            if all_records:
                st.markdown("### Line-by-Line Detailed Explanations for Attempted Questions")
                for idx_rec, rec in enumerate(reversed(all_records)):
                    status_tag = "Correct" if rec.get("Correct") else "Incorrect"
                    title_label = (
                        f"{rec.get('Class', '')} • {rec.get('Pupil Name', 'Pupil')} — "
                        f"{rec.get('Question', '')} [{status_tag}]"
                    )
                    with st.expander(title_label, expanded=(idx_rec == 0)):
                        st.caption(
                            f"School: {rec.get('School', '—')} | District: {rec.get('District', '—')} | "
                            f"Selected Answer: {rec.get('Selected', '—')} | Timestamp: {rec.get('Timestamp', '—')}"
                        )
                        matched_q = QUESTION_LOOKUP.get(str(rec.get("q_uid", ""))) or QUESTION_LOOKUP.get(str(rec.get("Question", "")))
                        correct_val = matched_q.get("ans") if matched_q else None
                        render_line_by_line_explanation(rec, correct_ans=correct_val)

                st.markdown("### Recorded Quiz Attempts")
                records_df = pd.DataFrame(all_records)
                st.dataframe(records_df, use_container_width=True, hide_index=True)
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
                    key="omweso_pit_select",
                )
                rev = st.checkbox("Reverse sow (left-corner pits 0, 1, 14, 15)", key="omweso_rev_check")
                if st.button("Sow", key="btn_omweso_sow"):
                    game.sow(0, pit_choice, reverse=rev)
                    opp_pits = [i for i in range(16) if game.board[1][i] >= 2]
                    if opp_pits:
                        game.sow(1, random.choice(opp_pits), reverse=False)
            if st.button("Reset Board", key="btn_omweso_reset"):
                st.session_state["omweso_game"] = OmwesoGame()
            st.info(game.log[-1])


if __name__ == "__main__":
    main()
