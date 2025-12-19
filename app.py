import streamlit as st
import math
import pandas as pd

def round_down_to_quarter(value):
    return math.floor(value * 4) / 4

def round_up_to_quarter(value):
    return math.ceil(value * 4) / 4

def round_to_nearest_quarter(value):
    return round(value * 4) / 4


st.title("Kalkulator skali ocen")

max_points = st.number_input(
    "Maksymalna liczba punktów",
    min_value=1,
    step=1
)

# (ocena, %min, %max)
scale = [
    ("1", 0, 25),
    ("1+", 26, 27),
    ("2-", 28, 29),
    ("2", 30, 45),
    ("2+", 46, 47),
    ("3-", 48, 49),
    ("3", 50, 65),
    ("3+", 66, 67),
    ("4-", 68, 69),
    ("4", 70, 80),
    ("4+", 81, 82),
    ("5-", 83, 84),
    ("5", 85, 91),
    ("5+", 92, 93),
    ("6-", 94, 94),
    ("6", 95, 100),
]
# thresholds trzymamy jako (ocena, start_w_punktach, p_min, p_max)
thresholds = []
for grade, p_min, p_max in scale:
    start_pts = round_up_to_quarter(max_points * (p_min / 100))
    end_pts   = round_down_to_quarter(max_points * (p_max / 100))
    thresholds.append((grade, start_pts, end_pts, p_min, p_max))

if max_points:
    step = 0.25

    st.subheader("Sprawdź ocenę")

possible_points = [x / 4 for x in range(0, int(max_points * 4) + 1)]

earned = st.selectbox(
    "Zdobyte punkty",
    possible_points
)

percent = (earned / max_points) * 100
earned_rounded = round_to_nearest_quarter(earned)

found_grade = None
for grade, start_pts, end_pts, p_min, p_max in thresholds:
    if p_min <= percent <= p_max:
        found_grade = grade
        break
else:
    if found_grade is None:
        found_grade = thresholds[-1][0]


result_box = st.empty()
caption_box = st.empty()
if found_grade in ("1", "1+"):
    result_box.error(f"Ocena: **{found_grade}**")
else:
    result_box.success(f"Ocena: **{found_grade}**")

caption_box.caption(
    f"Procent: {percent:.2f}% | Punkty (zaokr do 0.25): {earned_rounded}"
)


st.subheader("Skala ocen (tabela)")

rows = []
for grade, start_pts, end_pts, p_min, p_max in thresholds:
    rows.append({"Punkty od": start_pts, "Punkty do": end_pts, "Ocena": grade})

df = pd.DataFrame(rows)
df["Punkty od"] = df["Punkty od"].map(lambda x: f"{x:g}")
df["Punkty do"] = df["Punkty do"].map(lambda x: f"{x:g}")
df = df[["Punkty od", "Punkty do", "Ocena"]]
df.index = [""] * len(df)
st.table(df)

