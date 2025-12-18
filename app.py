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
    ("1 (niedostateczny)", 0, 25),
    ("1+ (niedostateczny plus)", 26, 27),
    ("2- (dopuszczający minus)", 28, 29),
    ("2 (dopuszczający)", 30, 45),
    ("2+ (dopuszczający plus)", 46, 47),
    ("3- (dostateczny minus)", 48, 49),
    ("3 (dostateczny)", 50, 65),
    ("3+ (dostateczny plus)", 66, 67),
    ("4- (dobry minus)", 68, 69),
    ("4 (dobry)", 70, 80),
    ("4+ (dobry plus)", 81, 82),
    ("5- (bardzo dobry minus)", 83, 84),
    ("5 (bardzo dobry)", 85, 91),
    ("5+ (bardzo dobry plus)", 92, 93),
    ("6- (celujący minus)", 94, 99),
    ("6 (celujący)", 100, 100),
]

if max_points:
    st.subheader("Skala ocen")
    for grade, p_min, p_max in scale:
        pts_min = round_down_to_quarter(max_points * p_min / 100)
        pts_max = round_down_to_quarter(max_points * p_max / 100)

        st.write(
            f"**{grade}**: {pts_min}–{pts_max} pkt ({p_min}–{p_max}%)"
        )
