QUIZ_BANK: Dict[str, List[Dict[str, Any]]] = {
    "P1": [
        {
            "id": "p1_1",
            "topic": "Counting",
            "marks": 1,
            "question": "5 + 3 = ?",
            "options": ["7", "8", "9", "6"],
            "ans": "8",
            "explanation": "5 + 3 = 8.",
            "diagram_type": None,
        }
    ],
    "P2": [
        {
            "id": "p2_1",
            "topic": "Place Value",
            "marks": 1,
            "question": "Place value of 4 in 428?",
            "options": ["Ones", "Tens", "Hundreds", "Thousands"],
            "ans": "Hundreds",
            "explanation": "4 is in the Hundreds place.",
            "diagram_type": None,
        }
    ],
    "P3": [
        {
            "id": "p3_1",
            "topic": "Division",
            "marks": 1,
            "question": "24 mangoes shared equally among 4 pupils = ?",
            "options": ["5", "8", "4", "6"],
            "ans": "6",
            "explanation": "24 ÷ 4 = 6.",
            "diagram_type": None,
        }
    ],
    "P4": [
        {
            "id": "p4_1",
            "topic": "Sets",
            "marks": 1,
            "question": "A = {1, 2, 3}, B = {2, 3, 4}. Find A ∩ B.",
            "options": ["{2, 3}", "{1}", "{4}", "{1, 2, 3, 4}"],
            "ans": "{2, 3}",
            "explanation": "Common elements are 2 and 3.",
            "diagram_type": None,
        }
    ],
    "P5": [
        {
            "id": "p5_1",
            "topic": "LCM",
            "marks": 1,
            "question": "LCM of 6 and 8?",
            "options": ["12", "24", "48", "2"],
            "ans": "24",
            "explanation": "LCM(6, 8) = 24.",
            "diagram_type": None,
        }
    ],
    "P6": [
        {
            "id": "p6_q01_sets",
            "topic": "Set Concepts",
            "marks": 1,
            "question": "1– Given that the Venn diagram below, list elements of set (B–A)'.",
            "options": ["{b, c}", "{e, f, a, i, g}", "{a, i}", "{e, f, g}"],
            "ans": "{e, f, a, i, g}",
            "explanation": "B - A = {b, c}, so (B - A)' includes all elements in universal set E outside {b, c}.",
            "diagram_type": "venn",
        },
        {
            "id": "p6_q02_roman",
            "topic": "Whole Numbers & Numerals",
            "marks": 1,
            "question": "2– Write CIX in Hindu Arabic numeral.",
            "options": ["111", "99", "109", "119"],
            "ans": "109",
            "explanation": "C = 100 and IX = 9, so CIX = 100 + 9 = 109.",
            "diagram_type": None,
        },
        {
            "id": "p6_q03_base",
            "topic": "Number Bases",
            "marks": 1,
            "question": "3– Given that 21_n = 11_ten. find the base represented by n.",
            "options": ["Base six", "Base four", "Base eight", "Base five"],
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
            "marks": 1,
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
            "marks": 2,
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
                "12– (ii) Find the size of the land area he has altogether which keep all his goats, "
                "pigs and cattle in square metres."
            ),
            "options": ["50 sq m", "36 sq m", "80 sq m", "68 sq m"],
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
            "options": ["12, 24, 36, 48", "2, 3, 4, 6", "1, 2, 3, 4, 6, 12", "1, 2, 3, 6, 12"],
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
            "topic": "Speed",
            "marks": 2,
            "question": "180 km in 3 hours. Speed = ?",
            "options": ["50 km/h", "60 km/h", "90 km/h", "540 km/h"],
            "ans": "60 km/h",
            "explanation": "180 ÷ 3 = 60 km/h.",
            "diagram_type": None,
        }
    ],
}
