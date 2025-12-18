import streamlit as st
import math


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

    earned = st.number_input(
        "Zdobyte punkty",
        min_value=0.0,
        max_value=float(max_points),
        step=0.25
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

    st.success(f"Ocena: **{found_grade}**")
    st.caption(
        f"Procent: {percent:.2f}% | "
        f"Punkty (zaokr. w dół do 0.25): {earned_rounded}"
    )

    st.subheader("Skala ocen")

    for i, (grade, p_min, p_max) in enumerate(scale):
        pts_min = round_down_to_quarter(max_points * p_min / 100)
        pts_max = round_down_to_quarter(max_points * p_max / 100)

        if i < len(scale) - 1:
            next_p_min = scale[i + 1][1]
            next_pts_min = round_down_to_quarter(max_points * next_p_min / 100)

            if pts_max == next_pts_min:
                pts_max -= step

        st.write(f"**{grade}**: {pts_min}–{pts_max} pkt")

