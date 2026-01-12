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
    """
    Parsuje np. '2,25+4,5+1+0,25'
    Przecinek = separator dziesiętny
    """
    if not expr:
        return None

    expr = expr.replace(" ", "")

    # Dozwolone tylko cyfry, + i przecinki
    if not re.fullmatch(r"[0-9+,]+", expr):
        return None

    try:
        parts = []
        for part in expr.split("+"):
            if part == "":
                continue
            parts.append(float(part.replace(",", ".")))
        return sum(parts)
    except ValueError:
        return None

# ----------------------------
# Scale definition (percent-based source of truth)
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
# Build POINT thresholds (quarter-first)
# ----------------------------
def build_thresholds_point_first(max_points: float):
    raw = []
    for grade, p_min, p_max in SCALE:
        start_pts = round_up_to_quarter(max_points * (p_min / 100))
        end_pts   = round_down_to_quarter(max_points * (p_max / 100))
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

def grade_for_points(earned_pts_q: float, thresholds):
    if not thresholds:
        return "N/A"

    for grade, start_pts, end_pts, *_ in thresholds:
        if start_pts <= earned_pts_q <= end_pts:
            return grade

    first_grade, first_start, *_ = thresholds[0]
    last_grade, _, last_end, *_ = thresholds[-1]

    if earned_pts_q < first_start:
        return first_grade

    if earned_pts_q > last_end:
        return last_grade

    for grade, start_pts, *_ in thresholds:
        if earned_pts_q < start_pts:
            return grade

    return last_grade

# ----------------------------
# UI
# ----------------------------
st.title("Kalkulator skali ocen (wierność punktom / ćwiartkom)")

max_points = st.number_input(
    "Maksymalna liczba punktów",
    min_value=1.0,
    step=1.0,
    value=1.0,
)

thresholds = build_thresholds_point_first(max_points)

st.subheader("Sprawdź ocenę")

possible_points = [x / 4 for x in range(0, int(max_points * 4) + 1)]

st.markdown("### Wprowadzanie punktów")

col1, col2 = st.columns(2)

with col1:
    earned_select = st.selectbox(
        "Zdobyte punkty (ręcznie)",
        possible_points,
        help="Wybór bezpośredni – tylko ćwiartki"
    )

with col2:
    expr_input = st.text_input(
        "Suma zadań (np. 2,25+4,5+1)",
        help="Używaj przecinków jako separatora dziesiętnego"
    )

parsed_sum = parse_points_expression(expr_input)

if parsed_sum is not None:
    earned_raw = min(parsed_sum, max_points)
else:
    earned_raw = float(earned_select)

earned_q = round_to_nearest_quarter(earned_raw)

percent = (earned_q / max_points) * 100 if max_points else 0.0
found_grade = grade_for_points(earned_q, thresholds)

result_box = st.empty()
caption_box = st.empty()

if found_grade in ("1", "1+"):
    result_box.error(f"Ocena: **{found_grade}**")
else:
    result_box.success(f"Ocena: **{found_grade}**")

caption_box.caption(
    f"Punkty (ćwiartki): {earned_q:g} / {max_points:g} | "
    f"Procent (informacyjnie): {percent:.2f}%"
)

st.subheader("Skala ocen (tabela: punkty → ocena)")

rows = []
for grade, start_pts, end_pts, p_min, p_max in thresholds:
    rows.append({
        "Punkty od": start_pts,
        "Punkty do": end_pts,
        "Ocena": grade,
        "Procent (źródło)": f"{p_min}–{p_max}%",
    })

df = pd.DataFrame(rows)
df["Punkty od"] = df["Punkty od"].map(lambda x: f"{x:g}")
df["Punkty do"] = df["Punkty do"].map(lambda x: f"{x:g}")
df = df[["Punkty od", "Punkty do", "Ocena", "Procent (źródło)"]]
df.index = [""] * len(df)

st.table(df)

# ----------------------------
# Diagnostics
# ----------------------------
with st.expander("Diagnostyka (opcjonalnie)"):
    if not thresholds:
        st.warning("Brak poprawnych progów (sprawdź max_points).")
    else:
        gaps = []
        for i in range(len(thresholds) - 1):
            _, _, end_i, *_ = thresholds[i]
            _, start_j, _, *_ = thresholds[i + 1]
            if start_j > end_i + 0.25:
                gaps.append((end_i + 0.25, start_j - 0.25))

        if gaps:
            st.warning("Wykryto luki (ćwiartki, które nie należą do żadnej oceny):")
            st.write(gaps)
        else:
            st.success("Brak luk między progami na siatce 0.25.")

        first_start = thresholds[0][1]
        last_end = thresholds[-1][2]
        st.write(f"Najniższy próg zaczyna się od: {first_start:g}")
        st.write(f"Najwyższy próg kończy się na: {last_end:g}")
        st.write(
            "Uwaga: jeśli max_points nie jest wielokrotnością 0.25, "
            "skala nadal działa, ale wybór punktów jest ograniczony do ćwiartek."
        )
