import streamlit as st
import math
import pandas as pd
import re

# ============================
# Helpers: quarter-point grid
# ============================
def round_down_to_quarter(value: float) -> float:
    return math.floor(value * 4) / 4

def round_up_to_quarter(value: float) -> float:
    return math.ceil(value * 4) / 4

def round_to_nearest_quarter(value: float) -> float:
    return round(value * 4) / 4

# ============================
# Teacher input parser
# ============================
def parse_points_expression(expr: str) -> float | None:
    if not expr:
        return None

    expr = expr.replace(" ", "")
    if not re.fullmatch(r"[0-9+,]+", expr):
        return None

    try:
        return sum(float(p.replace(",", ".")) for p in expr.split("+") if p)
    except ValueError:
        return None

# ============================
# Scale definition
# ============================
SCALE = [
    ("1",   0, 25),
    ("1+", 26, 27),
    ("2-", 28, 29),
    ("2",  30, 45),
    ("2+", 46, 47),
    ("3-", 48, 49),
    ("3",  50, 65),
    ("3+", 66, 67),
    ("4-", 68, 69),
    ("4",  70, 80),
    ("4+", 81, 82),
    ("5-", 83, 84),
    ("5",  85, 91),
    ("5+", 92, 93),
    ("6-", 94, 94),
    ("6",  95, 100),
]

# ============================
# Thresholds
# ============================
def build_thresholds_point_first(max_points: float):
    raw = []
    for grade, p_min, p_max in SCALE:
        start_pts = round_up_to_quarter(max_points * p_min / 100)
        end_pts = round_down_to_quarter(max_points * p_max / 100)
        raw.append((grade, start_pts, end_pts, p_min, p_max))

    raw.sort(key=lambda x: x[1])

    fixed = []
    last_end = None

    for grade, start_pts, end_pts, p_min, p_max in raw:
        if start_pts > end_pts:
            continue
        if last_end is not None and start_pts <= last_end:
            start_pts = round_up_to_quarter(last_end + 0.25)
        if start_pts > end_pts:
            continue

        fixed.append((grade, start_pts, end_pts, p_min, p_max))
        last_end = end_pts

    return fixed

def grade_for_points(earned_q: float, thresholds):
    for grade, start, end, *_ in thresholds:
        if start <= earned_q <= end:
            return grade
    if earned_q < thresholds[0][1]:
        return thresholds[0][0]
    return thresholds[-1][0]

# ============================
# Percent formatting
# ============================
def percent_info_str(earned_q: float, max_points: float) -> str:
    if not max_points:
        return "0%"
    return f"{(earned_q / max_points) * 100:g}%"

# ============================
# UI
# ============================
st.title("Kalkulator ocen")
st.markdown(
    """
    <style>
    /* centruj tylko główny tytuł */
    h1 {
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- CSS ----------
st.markdown(
    """
    <style>
    .result-box {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 70px;
        border-radius: 0.6rem;
        font-weight: 600;
        text-align: center;
        color: white;
        margin-top: 0.25rem;
    }

    .box-sum {
        background-color: #1f4b6e;
    }

    .box-grade {
        background-color: #1f6e3f;
    }

    .box-grade-fail {
        background-color: #8b1e1e;
    }

    .box-percent {
        background-color: #6f42c1;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ---------- Inputs ----------
max_points = st.number_input(
    "Maksymalna liczba punktów",
    min_value=1.0,
    step=1.0,
    value=25.0
)

thresholds = build_thresholds_point_first(max_points)

col1, col2 = st.columns(2)

possible_points = [x / 4 for x in range(0, int(max_points * 4) + 1)]

with col1:
    earned_select = st.selectbox("Zdobyte punkty", possible_points)

with col2:
    expr_input = st.text_input("Kalkulator punktów (np. 2+3+2,5)")

parsed_sum = parse_points_expression(expr_input)

# ---------- SUMA ----------
if parsed_sum is not None:
    st.markdown(
        f"""
        <div class="result-box box-sum">
            Suma punktów: {parsed_sum:g} / {max_points:g}
        </div>
        """,
        unsafe_allow_html=True
    )
    earned_raw = min(parsed_sum, max_points)
else:
    earned_raw = float(earned_select)

earned_q = round_to_nearest_quarter(earned_raw)
found_grade = grade_for_points(earned_q, thresholds)
percent_str = percent_info_str(earned_q, max_points)

# ---------- RESULT ----------
res_col1, res_col2 = st.columns(2)

with res_col1:
    grade_class = "box-grade-fail" if found_grade in ("1", "1+") else "box-grade"
    st.markdown(
        f"""
        <div class="result-box {grade_class}">
            Ocena: {found_grade}
        </div>
        """,
        unsafe_allow_html=True
    )

with res_col2:
    st.markdown(
        f"""
        <div class="result-box box-percent">
            Procent: {percent_str}
        </div>
        """,
        unsafe_allow_html=True
    )


# ---------- TABLE ----------
st.markdown(
    "<h2 style='text-align: center;'>Skala ocen</h2>",
    unsafe_allow_html=True
)

rows = [
    {
        "Punkty od": f"{start:g}",
        "Punkty do": f"{end:g}",
        "Ocena": grade,
        "Procent": f"{p_min}–{p_max}%",
    }
    for grade, start, end, p_min, p_max in thresholds
]

df = pd.DataFrame(rows)
df.index = [""] * len(df)
st.table(df)
