import streamlit as st
import math


def round_down_to_quarter(value):
    return math.floor(value * 4) / 4


st.title("Kalkulator skali ocen")

max_points = st.number_input(
    "Maksymalna liczba punktów",
    min_value=1,
    step=1
)

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
    ("6", 95, 100)
]

if max_points:
    step = 0.25

    st.subheader("Skala ocen")

    for i, (grade, p_min, p_max) in enumerate(scale):
        pts_min = round_down_to_quarter(max_points * p_min / 100)
        pts_max = round_down_to_quarter(max_points * p_max / 100)

        # sprawdź, czy następny zakres zaczyna się dokładnie tam, gdzie ten się kończy
        if i < len(scale) - 1:
            next_p_min = scale[i + 1][1]
            next_pts_min = round_down_to_quarter(max_points * next_p_min / 100)

            if pts_max == next_pts_min:
                pts_max -= step

        st.write(f"**{grade}**: {pts_min}–{pts_max} pkt")
