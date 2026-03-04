import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patheffects as path_effects
from pathlib import Path
import numpy as np

st.set_page_config(layout="wide")
st.title("IAR Proficiency Distribution")
st.write("")
st.write("### Comparison: ELA vs Math")
st.write("")

project_root = Path(__file__).resolve().parents[1]
raw_dir = project_root / "data" / "raw-data"

@st.cache_data
def load_data():
    df = pd.read_csv(raw_dir / "iar_proficiency.csv")
    df = df[df["School Code"] == "--"]
    df.columns = df.columns.str.strip()
    for col in ["%At or Above Proficient", "%Approaching Proficient", "%Below Proficient"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df

df = load_data()

group_map = {
    "Economic Disadvantage": "Economic Disadvantage",
    "English Learner": "English Learner Status",
    "Gender": "Gender",
    "Race": "Race/Ethnicity",
}
group_choice = st.sidebar.selectbox("Select Subgroup (X Axis)", list(group_map.keys()))
group_col = group_map[group_choice]

def draw_proficiency_chart(data, title, subgroup_name):
    plot_df = data.copy()

    if subgroup_name == "Race":
        plot_df["Student Group"] = plot_df["Student Group"].replace({
            "White": "White",
            "Black/African American": "Black",
            "Latinx": "Latinx"
        })
        keep = ["White", "Black", "Latinx"]
        plot_df["Student Group"] = plot_df["Student Group"].apply(lambda x: x if x in keep else "Others")
        plot_df["Student Group"] = pd.Categorical(plot_df["Student Group"], categories=keep + ["Others"], ordered=True)

    plot_df = plot_df.groupby("Student Group").mean(numeric_only=True).reset_index()

    proficiency_order = ["%Below Proficient", "%Approaching Proficient", "%At or Above Proficient"]
    colors = ["#e74c3c", "#f1c40f", "#2ecc71"]  

    x_labels = plot_df["Student Group"]
    bottom = np.zeros(len(plot_df))

    fig, ax = plt.subplots(figsize=(8, 7))

    for i, prof in enumerate(proficiency_order):
        values = plot_df[prof].values
        bars = ax.bar(x_labels, values, bottom=bottom, color=colors[i], label=prof, edgecolor='white', linewidth=0.8)

        for bar, val, btm in zip(bars, values, bottom):
            if val > 5: 
                ax.text(
                    bar.get_x() + bar.get_width() / 2,
                    btm + val / 2,
                    f"{val:.1f}%",
                    ha="center", va="center", fontsize=9, color="black",
                    path_effects=[path_effects.withStroke(linewidth=2, foreground="white")]
                )
        bottom += values

    ax.set_ylabel("Percent of Students", fontsize=12, weight='bold')
    ax.set_xlabel(subgroup_name, fontsize=12, weight='bold')
    ax.set_title(title, fontsize=14, weight='bold', pad=15)
    ax.set_ylim(0, 105)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.tick_params(axis='x', pad=10)
    ax.tick_params(axis='y', pad=10)

    handles, labels = ax.get_legend_handles_labels()
    leg = ax.legend(
        handles[::-1], labels[::-1],  
        title="Proficiency Level",
        loc='upper center',
        bbox_to_anchor=(0.5, -0.12),
        ncol=3,
        fontsize=10,
        title_fontsize=11
    )
    leg._legend_box.sep = 9

    return fig

col1, col2 = st.columns(2)

ela_data = df[(df["Test Name"].str.contains("ELA", case=False, na=False)) & (df["Category"] == group_col)]
math_data = df[(df["Test Name"].str.contains("Math", case=False, na=False)) & (df["Category"] == group_col)]

with col1:
    if not ela_data.empty:
        fig_ela = draw_proficiency_chart(ela_data, f"ELA Proficiency by {group_choice}", group_choice)
        st.pyplot(fig_ela)
    else:
        st.warning("No ELA data found.")

with col2:
    if not math_data.empty:
        fig_math = draw_proficiency_chart(math_data, f"Math Proficiency by {group_choice}", group_choice)
        st.pyplot(fig_math)
    else:
        st.warning("No Math data found.")