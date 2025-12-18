import streamlit as st
import math
import pandas as pd

def round_down_to_quarter(value: float) -> float:
    return math.floor(value * 4) / 4


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

if max_points:
    step = 0.25

    st.subheader("Sprawdź ocenę")

possible_points = [
    round_down_to_quarter(x / 4)
    for x in range(0, int(max_points * 4) + 1)
]

earned = st.selectbox(
    "Zdobyte punkty",
    possible_points
)

percent = (earned / max_points) * 100
earned_rounded = round_down_to_quarter(earned)

found_grade = None
for grade, p_min, p_max in scale:
    if p_min <= percent <= p_max:
        found_grade = grade
        break

    if found_grade is None:
        for grade, p_min, p_max in reversed(scale):
            if percent >= p_min:
                found_grade = grade
                break
result_box = st.empty()
caption_box = st.empty()
if found_grade in ("1", "1+"):
    result_box.error(f"Ocena: **{found_grade}**")
else:
    result_box.success(f"Ocena: **{found_grade}**")

caption_box.caption(
    f"Procent: {percent:.2f}% | Punkty (zaokr. w dół do 0.25): {earned_rounded}"
)



st.subheader("Skala ocen (tabela)")

rows = []
for i, (grade, p_min, p_max) in enumerate(scale):
    pts_min = round_down_to_quarter(max_points * p_min / 100)
    pts_max = round_down_to_quarter(max_points * p_max / 100)

    # usuń „styk” tylko w prezentacji
    if i < len(scale) - 1:
        next_p_min = scale[i + 1][1]
        next_pts_min = round_down_to_quarter(max_points * next_p_min / 100)
        if pts_max == next_pts_min and (pts_max - step) >= pts_min:
            pts_max -= step

    pts_max = max(pts_max, pts_min)  # zabezpieczenie: nigdy "do" < "od"


    rows.append({
        "Ocena": grade,
        "Punkty od": pts_min,
        "Punkty do": pts_max,
    })

df = pd.DataFrame(rows)
df["Punkty od"] = df["Punkty od"].map(lambda x: f"{x:g}")
df["Punkty do"] = df["Punkty do"].map(lambda x: f"{x:g}")

df.index = [""] * len(df)
df = df[["Punkty od", "Punkty do", "Ocena"]]
st.table(df)


