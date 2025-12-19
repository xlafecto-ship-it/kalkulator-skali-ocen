import streamlit as st
import math
import pandas as pd

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
thresholds = []
for grade, p_min, p_max in scale:
    pts_min = round_to_nearest_quarter(max_points * p_min / 100)
    thresholds.append((grade, pts_min))

if max_points:
    step = 0.25

    st.subheader("Sprawdź ocenę")

possible_points = [
    round_to_nearest_quarter(x / 4)
    for x in range(0, int(max_points * 4) + 1)
]

earned = st.selectbox(
    "Zdobyte punkty",
    possible_points
)

percent = (earned / max_points) * 100
earned_rounded = round_to_nearest_quarter(earned)

found_grade = thresholds[0][0]  # domyślnie najniższa
for i in range(len(thresholds) - 1):
    grade, start = thresholds[i]
    _, next_start = thresholds[i + 1]

    if start <= earned_rounded < next_start:
        found_grade = grade
        break
else:
    # jeśli nie złapało żadnego przedziału, to znaczy że jesteśmy w ostatnim
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

step = 0.25
rows = []

for i, (grade, start) in enumerate(thresholds):
    if i < len(thresholds) - 1:
        end_exclusive = thresholds[i + 1][1]
        end_display = end_exclusive - step
    else:
        # ostatnia ocena: do max_points normalnie
        end_display = float(max_points)

    rows.append({"Punkty od": start, "Punkty do": end_display, "Ocena": grade})

df = pd.DataFrame(rows)
df["Punkty od"] = df["Punkty od"].map(lambda x: f"{x:g}")
df["Punkty do"] = df["Punkty do"].map(lambda x: f"{x:g}")
df = df[["Punkty od", "Punkty do", "Ocena"]]
df.index = [""] * len(df)
st.table(df)


