import streamlit as st
import math
import pandas as pd
import re

# ----------------------------
# Helpers: quarter-point grid
# ----------------------------
def round_down_to_quarter(value: float) -> float:
    return math.floor(value * 4) / 4

def round_up_to_quarter(value: float) -> float:
    return math.ceil(value * 4) / 4

def round_to_nearest_quarter(value: float) -> float:
    return round(value * 4) / 4

# ----------------------------
# Teacher input parser (comma decimals)
# ----------------------------
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

# ----------------------------
# Scale definition (percent-based)
# ----------------------------
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

# ----------------------------
# Build POINT thresholds
# ----------------------------
def build_thresholds_point_first(max_points: float):
    raw = []
    for grade, p_min, p_max in SCALE:
        start_pts = round_up_to_quarter(max_points * p_min / 100)
        end_pts   = round_down_to_quarter(max_points * p_max / 100)
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
    for grade, start_pts, end_pts, *_ in thresholds:
        if start_pts <= earned_q <= end_pts:
            return grade

    if earned_q < thresholds[0][1]:
        return thresholds[0][0]

    return thresholds[-1][0]

# ----------------------------
# Percent formatting
# ----------------------------
def percent_info_str(earned_q: float, max_points: float) -> str:
    if not max_points:
        return "0%"
    return f"{(earned_q / max_points) * 100:g}%"

# ----------------------------
# UI
# ----------------------------
st.title("Kalkulator skali ocen (ćwiartki punktów)")

# 🎨 CSS – fioletowy box procentów
st.markdown(
    """
    <style>
    .percent-box {
        background-color: #6f42c1;
        color: white;
        padding: 1rem;
        border-radius: 0.6rem;
        font-weight: 600;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True
)

max_points = st.number_input(
    "Maksymalna liczba punktów",
    min_value=1.0,
    step=1.0,
    value=1.0,
)

thresholds = build_thresholds_point_first(max_points)

st.subheader("Sprawdź ocenę")

possible_points = [x / 4 for x in range(0, int(max_points * 4) + 1)]

col1, col2 = st.columns(2)

with col1:
    earned_select = st.selectbox("Zdobyte punkty", possible_points)

with col2:
    expr_input = st.text_input("Suma punktów (np. 2+1,5+0,25)")

parsed_sum = parse_points_expression(expr_input)

sum_box = st.empty()

if parsed_sum is not None:
    sum_box.info(f"Suma punktów: **{parsed_sum:g} / {max_points:g}**")
    earned_raw = min(parsed_sum, max_points)
else:
    earned_raw = float(earned_select)

earned_q = round_to_nearest_quarter(earned_raw)
found_grade = grade_for_points(earned_q, thresholds)
percent_str = percent_info_str(earned_q, max_points)

# 🧾 Wynik: ocena | procent
res_col1, res_col2 = st.columns(2)

with res_col1:
    if found_grade in ("1", "1+"):
        st.error(f"Ocena: **{found_grade}**")
    else:
        st.success(f"Ocena: **{found_grade}**")

with res_col2:
    st.markdown(
        f"""
        <div class="percent-box">
            Procent: <strong>{percent_str}</strong>
        </div>
        """,
        unsafe_allow_html=True
    )

st.caption(f"Punkty (ćwiartki): {earned_q:g} / {max_points:g}")

# ----------------------------
# Table
# ----------------------------
st.subheader("Skala ocen")

rows = [
    {
        "Punkty od": f"{start:g}",
        "Punkty do": f"{end:g}",
        "Ocena": grade,
        "Procent (źródło)": f"{p_min}–{p_max}%",
    }
    for grade, start, end, p_min, p_max in thresholds
]

df = pd.DataFrame(rows)
df.index = [""] * len(df)
st.table(df)
