import base64
from datetime import datetime
import io
import json
import math
import os
from typing import Any, Dict, List, Optional, Tuple
from urllib import error as urlerror
from urllib import request as urlrequest

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

st.set_page_config(page_title="iLearn-Uganda | Primary Maths", layout="wide")

TABS = ["Take Quiz", "NCDC Syllabus", "Dashboard"]

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


def _draw_angle_arc(
    ax: Any,
    vertex: Tuple[float, float],
    p1: Tuple[float, float],
    p2: Tuple[float, float],
    radius: float = 0.55,
    color: str = "#1d4ed8",
) -> None:
    """Draws a clean angle arc at `vertex` between rays toward `p1` and `p2`."""
    ang1 = math.degrees(math.atan2(p1[1] - vertex[1], p1[0] - vertex[0]))
    ang2 = math.degrees(math.atan2(p2[1] - vertex[1], p2[0] - vertex[0]))
    diff = (ang2 - ang1) % 360.0
    if diff > 180.0:
        ang1, ang2 = ang2, ang1
        diff = 360.0 - diff
    theta = np.linspace(math.radians(ang1), math.radians(ang1 + diff), 40)
    xs = vertex[0] + radius * np.cos(theta)
    ys = vertex[1] + radius * np.sin(theta)
    ax.plot(xs, ys, color=color, linewidth=1.8)


def _draw_double_tick(
    ax: Any,
    a: Tuple[float, float],
    b: Tuple[float, float],
    frac: float = 0.48,
    tick_len: float = 0.28,
    sep: float = 0.14,
) -> None:
    """Draws double equality tick marks (`||`) perpendicular to segment AB."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    length = math.hypot(dx, dy)
    ux, uy = dx / length, dy / length
    nx, ny = -uy, ux
    mx = a[0] + frac * dx
    my = a[1] + frac * dy
    for offset in (-sep / 2.0, sep / 2.0):
        cx = mx + offset * ux
        cy = my + offset * uy
        ax.plot(
            [cx - (tick_len / 2.0) * nx, cx + (tick_len / 2.0) * nx],
            [cy - (tick_len / 2.0) * ny, cy + (tick_len / 2.0) * ny],
            color="#1d4ed8",
            linewidth=1.8,
        )


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

        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    if diagram_type == "p7_q04_angles":
        fig, ax = plt.subplots(figsize=(6.8, 3.6))
        ax.set_xlim(-0.8, 11.2)
        ax.set_ylim(-0.7, 4.7)
        ax.set_aspect("equal")
        ax.axis("off")

        y_top = 3.8
        y_bot = 0.2

        ax.plot([0.2, 10.6], [y_top, y_top], color="black", linewidth=2.2)
        ax.plot([-0.4, 10.4], [y_bot, y_bot], color="black", linewidth=2.2)

        A = (3.4, y_top)
        B = (0.7, y_bot)
        C = (5.4, y_bot)
        ax.plot([B[0], A[0]], [B[1], A[1]], color="black", linewidth=2.2)
        ax.plot([A[0], C[0]], [A[1], C[1]], color="black", linewidth=2.2)

        t_d = 0.65
        D = (A[0] + t_d * (C[0] - A[0]), A[1] + t_d * (C[1] - A[1]))
        E = (9.1, y_top)
        ax.plot([D[0], E[0]], [D[1], E[1]], color="black", linewidth=2.2)

        _draw_double_tick(ax, B, A, frac=0.50)
        _draw_double_tick(ax, A, C, frac=0.36)

        _draw_angle_arc(ax, A, B, C, radius=0.45, color="#1d4ed8")
        _draw_angle_arc(ax, D, C, E, radius=0.48, color="#1d4ed8")
        _draw_angle_arc(ax, E, A, D, radius=0.65, color="#1d4ed8")

        ax.text(3.38, 2.92, "50°", fontsize=12, fontweight="bold", ha="center", color="#111827")
        ax.text(5.28, 1.38, "80°", fontsize=12, fontweight="bold", ha="left", color="#111827")
        ax.text(7.55, 3.22, "k", fontsize=13, fontweight="bold", ha="center", color="#111827")

        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    if diagram_type == "p7_q06_number_line":
        fig, ax = plt.subplots(figsize=(6.8, 1.8))
        ax.set_xlim(-5.0, 4.0)
        ax.set_ylim(-0.8, 1.2)
        ax.axis("off")

        ax.annotate("", xy=(3.7, 0), xytext=(-4.7, 0), arrowprops=dict(arrowstyle="<->", lw=1.8, color="black"))
        for x in range(-4, 4):
            ax.plot([x, x], [-0.15, 0.15], color="black", lw=1.5)
            lbl = f"+{x}" if x > 0 else str(x)
            ax.text(x, -0.45, lbl, fontsize=11, ha="center", fontweight="bold")

        circle_neg2 = patches.Circle((-2, 0), 0.26, linewidth=2, edgecolor="#b91c1c", facecolor="#fee2e2")
        ax.add_patch(circle_neg2)
        ax.annotate(
            "",
            xy=(-2, 0.32),
            xytext=(1, 0.55),
            arrowprops=dict(arrowstyle="->", lw=1.5, color="#0b6e3f", connectionstyle="arc3,rad=-0.2"),
        )
        ax.text(-0.5, 0.72, "3 steps left (+1 → -2)", fontsize=10, ha="center", fontweight="bold", color="#0b6e3f")

        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    if diagram_type == "p7_q09_venn":
        fig, ax = plt.subplots(figsize=(5.8, 4.2))
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 7.2)
        ax.set_aspect("equal")
        ax.axis("off")

        univ = patches.Rectangle((0.8, 0.6), 8.4, 5.6, linewidth=2, edgecolor="black", facecolor="white")
        ax.add_patch(univ)
        ax.text(5.0, 6.45, "n(ε)", fontsize=13, fontweight="bold", ha="center")

        circle_a = patches.Circle((4.0, 3.4), 1.9, linewidth=2, edgecolor="black", facecolor="none")
        circle_b = patches.Circle((6.0, 3.4), 1.9, linewidth=2, edgecolor="black", facecolor="none")
        ax.add_patch(circle_a)
        ax.add_patch(circle_b)

        ax.text(3.3, 5.45, "n(A)", fontsize=12, fontweight="bold", ha="center")
        ax.text(6.7, 5.45, "n(B)", fontsize=12, fontweight="bold", ha="center")

        ax.text(3.0, 3.4, "4", fontsize=13, fontweight="bold", ha="center", va="center")
        ax.text(5.0, 3.4, "3", fontsize=13, fontweight="bold", ha="center", va="center")
        ax.text(7.0, 3.4, "5", fontsize=13, fontweight="bold", ha="center", va="center")
        ax.text(8.3, 1.15, "4", fontsize=13, fontweight="bold", ha="center", va="center")

        fig.savefig(buf, format="png", dpi=150, bbox_inches="tight")
        plt.close(fig)
        return buf.getvalue()

    return None


# ==============================================================================
# 2. NCDC PRIMARY MATHEMATICS CURRICULUM (P1 - P7) & UGANDA DISTRICTS
# ==============================================================================

UGANDA_DISTRICTS: List[str] = sorted([
    "Buikwe", "Bukomansimbi", "Butambala", "Buvuma", "Gomba", "Kalangala",
    "Kalungu", "Kampala", "Kasanda", "Kayunga", "Kiboga", "Kyankwanzi",
    "Kyotera", "Luweero", "Lwengo", "Lyantonde", "Masaka", "Mityana",
    "Mpigi", "Mubende", "Mukono", "Nakaseke", "Nakasongola", "Rakai",
    "Sembabule", "Wakiso",
    "Amuria", "Budaka", "Bududa", "Bugiri", "Bugweri", "Bukedea",
    "Bukwo", "Bulambuli", "Busia", "Butaleja", "Butebo", "Buyende",
    "Iganga", "Jinja", "Kaberamaido", "Kalaki", "Kaliro", "Kamuli",
    "Kapchorwa", "Kapelebyong", "Katakwi", "Kibuku", "Kumi", "Kween",
    "Luuka", "Manafwa", "Mayuge", "Mbale", "Namayingo", "Namisindwa",
    "Namutumba", "Ngora", "Pallisa", "Serere", "Sironko", "Soroti",
    "Tororo",
    "Abim", "Adjumani", "Agago", "Alebtong", "Amolatar", "Amudat",
    "Amuru", "Apac", "Arua", "Dokolo", "Gulu", "Kaabong",
    "Karenga", "Kitgum", "Koboko", "Kole", "Kotido", "Kwania",
    "Lamwo", "Lira", "Madi-Okollo", "Maracha", "Moroto", "Moyo",
    "Nabilatuk", "Nakapiripirit", "Napak", "Nebbi", "Nwoya", "Obongi",
    "Omoro", "Otuke", "Oyam", "Pader", "Pakwach", "Yumbe",
    "Zombo",
    "Buhweju", "Buliisa", "Bundibugyo", "Bunyangabu", "Bushenyi", "Hoima",
    "Ibanda", "Isingiro", "Kabale", "Kabarole", "Kagadi", "Kakumiro",
    "Kamwenge", "Kanungu", "Kasese", "Kazo", "Kibaale", "Kikuube",
    "Kiruhura", "Kiryandongo", "Kisoro", "Kitagwenda", "Kyegegwa",
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
            "theme": "Sets, Numeracy, Geometry & Data Handling",
            "topic": "Standard Form, Direct Proportion, Ratios, Integers, GCF, Mean, Venn Subsets & Base Five",
            "periods": 30,
            "sub_topics": [
                "Simplification and standard (scientific) form",
                "Direct proportion and unitary cost",
                "Angles in triangles, straight lines, and parallel lines",
                "Ratios, fractions of a group, and additive inverses on number lines",
                "Greatest Common Factor (GCF), mean equations, Venn subsets, and base-five arithmetic",
            ],
            "learning_outcomes": "Learner consolidates upper-primary mathematics for PLE readiness with accurate set, base, integer, and proportional reasoning.",
            "learning_aids": ["Mathematical set", "Number line cards", "Venn & base-five charts"],
            "life_skills_values": ["Critical thinking", "Accuracy", "Self-reliance"],
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": "venn",
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": "marks_table",
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": "okello_land",
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
            "explanation_diagram_type": "okello_land",
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
        },
        {
            "id": "p6_q15_mean",
            "topic": "Statistics & Mean",
            "marks": 5,
            "question": (
                "15– The mean mass of 5 boys is 30 kg. When their teacher joins them, the mean mass "
                "changes to 34 kg. Find the mass of the teacher."
            ),
            "options": ["48 kg", "54 kg", "204 kg", "150 kg"],
            "ans": "54 kg",
            "explanation": "5 boys sum = 5 × 30 = 150 kg; 6 people sum = 6 × 34 = 204 kg; teacher's mass = 204 - 150 = 54 kg.",
            "step_by_step": [
                "Line 1 — Calculate total mass of the 5 boys: 5 × 30 kg = 150 kg.",
                "Line 2 — Calculate total mass of all 6 people (5 boys + 1 teacher): 6 × 34 kg = 204 kg.",
                "Line 3 — Subtract total mass of the 5 boys from total mass of the 6 people: 204 kg - 150 kg = 54 kg.",
            ],
            "diagram_type": None,
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
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
            "explanation_diagram_type": None,
        },
    ],
    "P7": [
        {
            "id": "p7_q01_simplify",
            "topic": "Whole Numbers & Operations",
            "marks": 1,
            "question": "1– Simplify: 3 × 5.",
            "options": ["8", "15", "35", "12"],
            "ans": "15",
            "explanation": "3 × 5 = 15.",
            "step_by_step": [
                "Line 1 — Identify the multiplication operation: 3 × 5.",
                "Line 2 — Add 5 three times (or count by 5s three steps): 5 + 5 + 5 = 15.",
                "Line 3 — The simplified product is 15.",
            ],
            "diagram_type": None,
            "explanation_diagram_type": None,
        },
        {
            "id": "p7_q02_standard_form",
            "topic": "Standard Form (Scientific Notation)",
            "marks": 2,
            "question": "2– Write 3.45 in standard form.",
            "options": ["3.45 × 10¹", "3.45 × 10⁰", "34.5 × 10⁻¹", "3.45 × 10⁻²"],
            "ans": "3.45 × 10⁰",
            "explanation": "Since 3.45 is already between 1 and 10, moving the decimal point 0 places gives 3.45 × 10⁰.",
            "step_by_step": [
                "Line 1 — Standard form requires a number A × 10^n where 1 ≤ A < 10 and n is an integer.",
                "Line 2 — Check 3.45: it already lies between 1 and 10 (1 ≤ 3.45 < 10).",
                "Line 3 — Since 0 decimal shifts are needed, n = 0, giving 3.45 × 10⁰ (and 10⁰ = 1).",
            ],
            "diagram_type": None,
            "explanation_diagram_type": None,
        },
        {
            "id": "p7_q03_soap_cost",
            "topic": "Fractions & Direct Proportion",
            "marks": 3,
            "question": "3– Given that 2½ bars of soap cost sh 10,000, find the cost of 8 similar bars of soap.",
            "options": ["sh 25,000", "sh 32,000", "sh 80,000", "sh 20,000"],
            "ans": "sh 32,000",
            "explanation": "2½ = 5/2 bars cost sh 10,000 -> 1 bar = sh 10,000 × 2/5 = sh 4,000 -> 8 bars = 8 × sh 4,000 = sh 32,000.",
            "step_by_step": [
                "Line 1 — Convert the mixed fraction 2½ into an improper fraction: 2½ = (2 × 2 + 1)/2 = 5/2 bars.",
                "Line 2 — Find the unit cost of 1 bar of soap: sh 10,000 ÷ (5/2) = sh 10,000 × (2/5).",
                "Line 3 — Simplify: sh 10,000 ÷ 5 = sh 2,000; then sh 2,000 × 2 = sh 4,000 per bar.",
                "Line 4 — Multiply unit cost by 8 bars: 8 × sh 4,000 = sh 32,000.",
            ],
            "diagram_type": None,
            "explanation_diagram_type": None,
        },
        {
            "id": "p7_q04_angles_k",
            "topic": "Lines, Angles & Parallel Lines",
            "marks": 3,
            "question": "4– Given the diagram below, find the value of k.",
            "options": ["15°", "30°", "50°", "65°"],
            "ans": "15°",
            "explanation": "Isosceles base angles = (180° - 50°)/2 = 65°; alternate interior angle on top parallel line = 65°; adjacent angle to 80° = 100°; so k = 180° - (65° + 100°) = 15°.",
            "step_by_step": [
                "Line 1 — The double tick marks (||) show an isosceles triangle with apex angle 50°, so each base angle on the bottom line is (180° - 50°) ÷ 2 = 65°.",
                "Line 2 — Because the top and bottom lines are parallel, the top-left interior angle inside the upper triangle is alternate interior to the 65° base angle, so it equals 65°.",
                "Line 3 — On the straight right side of the triangle, the interior angle adjacent to 80° is 180° - 80° = 100°.",
                "Line 4 — Sum of angles in the upper triangle is 180°: k = 180° - (65° + 100°) = 180° - 165° = 15°.",
            ],
            "diagram_type": "p7_q04_angles",
            "explanation_diagram_type": "p7_q04_angles",
        },
        {
            "id": "p7_q05_ratio_day_boys",
            "topic": "Ratios & Fractions",
            "marks": 4,
            "question": (
                "5– In P.6 class, the ratio of boys to girls is 2:3. If there are 600 pupils in the class "
                "and 2/3 of the boys are in boarding section, find the number of boys in day section."
            ),
            "options": ["240 boys", "160 boys", "80 boys", "360 boys"],
            "ans": "80 boys",
            "explanation": "Total boys = (2/5) × 600 = 240; boarding boys = (2/3) × 240 = 160; day boys = 240 - 160 = 80.",
            "step_by_step": [
                "Line 1 — Find the total ratio parts for boys : girls = 2 : 3 -> 2 + 3 = 5 parts.",
                "Line 2 — Find the fraction of boys in the class: 2/5.",
                "Line 3 — Calculate total boys: (2/5) × 600 = 2 × 120 = 240 boys.",
                "Line 4 — Calculate boys in the boarding section: (2/3) × 240 = 2 × 80 = 160 boys.",
                "Line 5 — Subtract boarding boys from total boys to get day boys: 240 - 160 = 80 boys.",
            ],
            "diagram_type": None,
            "explanation_diagram_type": None,
        },
        {
            "id": "p7_q06_additive_inverse",
            "topic": "Integers & Number Lines",
            "marks": 2,
            "question": "6– Work out the additive inverse of the integer which is 3 steps to the left of +1.",
            "options": ["-2", "+2", "-4", "+4"],
            "ans": "+2",
            "explanation": "Moving 3 steps left from +1 lands on -2; the additive inverse of -2 is +2 since (-2) + (+2) = 0.",
            "step_by_step": [
                "Line 1 — Start at +1 on the number line and move 3 steps to the left: +1 -> 0 -> -1
