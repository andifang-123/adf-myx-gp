import streamlit as st
import pandas as pd
import numpy as np
import geopandas as gpd
import matplotlib.pyplot as plt
import altair as alt

from pathlib import Path
from shapely import wkt
from shapely.geometry import Point
from scipy.stats import linregress

st.set_page_config(page_title="CPS Dashboard", layout="wide")
st.title("CPS Dashboard")

alt.data_transformers.disable_max_rows()

@st.cache_data
def load_data():
    try:
        project_root = Path(__file__).resolve().parent.parent
    except NameError:
        project_root = Path.cwd().parent

    raw_community = project_root / "data" / "raw-data" / "community_boundaries.csv"
    raw_schools = project_root / "data" / "derived-data" / "cps_df.csv"

    comm_df = pd.read_csv(raw_community, sep=";", encoding="utf-8-sig")
    schools_df = pd.read_csv(raw_schools)

    comm_df.columns = comm_df.columns.str.strip().str.strip('"')
    schools_df.columns = schools_df.columns.str.strip()

    if "the_geom" not in comm_df.columns:
        raise KeyError(f"'the_geom' not found. Columns found: {list(comm_df.columns)}")

    comm_df["geometry"] = comm_df["the_geom"].apply(wkt.loads)
    comm_gdf = gpd.GeoDataFrame(comm_df, geometry="geometry", crs="EPSG:4326")

    if "COMMUNITY" in comm_gdf.columns:
        comm_gdf["COMMUNITY"] = comm_gdf["COMMUNITY"].astype(str).str.strip()

    return schools_df, comm_gdf

def find_first_existing_column(df, candidates, label_for_error):
    for c in candidates:
        if c in df.columns:
            return c
    raise KeyError(
        f"Cannot find a valid column for {label_for_error}. "
        f"Tried: {candidates}. Available columns: {list(df.columns)}"
    )


def to_numeric_if_exists(df, cols):
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce")
    return df


def prepare_school_geo(schools_df):
    df = schools_df.copy()

    lat_col = find_first_existing_column(
        df, ["School_Latitude", "Latitude", "lat", "LATITUDE"], "latitude"
    )
    lon_col = find_first_existing_column(
        df, ["School_Longitude", "Longitude", "lon", "lng", "LONGITUDE"], "longitude"
    )

    df = to_numeric_if_exists(df, [lat_col, lon_col])
    df = df.dropna(subset=[lat_col, lon_col]).copy()

    school_gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df[lon_col], df[lat_col])],
        crs="EPSG:4326",
    )
    return school_gdf


def spatial_join_schools_to_communities(schools_df, comm_gdf):
    school_gdf = prepare_school_geo(schools_df)

    keep_cols = [c for c in ["COMMUNITY", "AREA_NUMBE", "AREA_NUM_1", "geometry"] if c in comm_gdf.columns]
    comm_subset = comm_gdf[keep_cols].copy()

    joined = gpd.sjoin(school_gdf, comm_subset, how="left", predicate="within")
    return joined


def detect_metric_columns(cps_df):
    col_map = {}

    col_map["RI"] = find_first_existing_column(
        cps_df, ["RI", "ri", "Readiness Index", "readiness_index"], "RI"
    )

    col_map["OI"] = find_first_existing_column(
        cps_df, ["Opportunity Index", "OI", "oi", "opportunity_index"], "OI / Opportunity Index"
    )

    col_map["ELA"] = find_first_existing_column(
        cps_df,
        ["IAR ELA %", "ELA %At or Above Proficient", "ELA % At or Above Proficient", "ELA"],
        "ELA"
    )

    col_map["Math"] = find_first_existing_column(
        cps_df,
        ["IAR MATH %", "Math %At or Above Proficient", "MATH %At or Above Proficient",
         "Math % At or Above Proficient", "Math"],
        "Math"
    )

    return col_map


def get_school_name_column(df):
    for c in ["Short_Name", "Long_Name", "School_Name", "Name", "school_name", "SCHOOL_NM", "School_ID", "ID"]:
        if c in df.columns:
            return c
    return None


def compute_community_metric_mean(joined_gdf, comm_gdf, metric_col):
    tmp = joined_gdf.copy()
    tmp[metric_col] = pd.to_numeric(tmp[metric_col], errors="coerce")

    if "COMMUNITY" not in tmp.columns:
        raise KeyError("COMMUNITY column not found after spatial join.")

    mean_df = (
        tmp.dropna(subset=["COMMUNITY", metric_col])
        .groupby("COMMUNITY", as_index=False)[metric_col]
        .mean()
        .rename(columns={metric_col: "community_mean"})
    )

    merged = comm_gdf.copy()
    merged["COMMUNITY"] = merged["COMMUNITY"].astype(str).str.strip()
    merged = merged.merge(mean_df, on="COMMUNITY", how="left")

    return merged, mean_df


def plot_choropleth(comm_metric_gdf, metric_label):
    fig = plt.figure(figsize=(8, 8))
    gs = fig.add_gridspec(nrows=1, ncols=2, width_ratios=[0.06, 0.94], wspace=0.05)

    cax = fig.add_subplot(gs[0, 0])
    ax = fig.add_subplot(gs[0, 1])

    comm_metric_gdf.plot(
        column="community_mean",
        cmap="viridis",
        linewidth=0.7,
        edgecolor="black",
        legend=True,
        legend_kwds={"cax": cax},
        missing_kwds={
            "color": "lightgray",
            "edgecolor": "black",
            "hatch": "///",
            "label": "No data",
        },
        ax=ax,
    )

    ax.set_title(f"{metric_label} Mean by Chicago Community", fontsize=14)
    ax.set_axis_off()

    cax.yaxis.set_ticks_position("left")
    cax.yaxis.set_label_position("left")

    plt.tight_layout()
    return fig


def build_scatter_df(df, x_col, y_col, x_label, y_label, school_name_col=None):
    plot_df = df.copy()

    needed_cols = [x_col, y_col]
    if school_name_col and school_name_col in plot_df.columns:
        needed_cols = [school_name_col] + needed_cols
    plot_df = plot_df[needed_cols].copy()

    plot_df[x_col] = pd.to_numeric(plot_df[x_col], errors="coerce")
    plot_df[y_col] = pd.to_numeric(plot_df[y_col], errors="coerce")
    plot_df = plot_df.dropna(subset=[x_col, y_col]).copy()

    if school_name_col and school_name_col in plot_df.columns:
        plot_df["School"] = plot_df[school_name_col].astype(str)
    else:
        plot_df["School"] = "Unknown"

    plot_df = plot_df.rename(columns={x_col: x_label, y_col: y_label})
    plot_df = plot_df[["School", x_label, y_label]].copy()

    return plot_df


def compute_regression_stats(plot_df, x_label, y_label):
    if len(plot_df) < 3:
        return None

    x = pd.to_numeric(plot_df[x_label], errors="coerce")
    y = pd.to_numeric(plot_df[y_label], errors="coerce")
    valid = np.isfinite(x) & np.isfinite(y)

    x = x[valid]
    y = y[valid]

    if len(x) < 3:
        return None

    res = linregress(x, y)
    return {
        "slope": res.slope,
        "pvalue": res.pvalue,
        "n": int(len(x)),
    }


def format_pvalue(p):
    if p is None or pd.isna(p):
        return "NA"
    if p < 0.001:
        return "< 0.001"
    return f"{p:.3f}"


def plot_scatter_altair(plot_df, x_label, y_label):
    points = (
        alt.Chart(plot_df)
        .mark_circle(size=60, opacity=0.65)
        .encode(
            x=alt.X(f"{x_label}:Q", title=x_label),
            y=alt.Y(f"{y_label}:Q", title=y_label),
            tooltip=[
                alt.Tooltip("School:N", title="School"),
                alt.Tooltip(f"{x_label}:Q", title=x_label, format=".4f"),
                alt.Tooltip(f"{y_label}:Q", title=y_label, format=".2f"),
            ],
        )
    )

    reg_line = (
        alt.Chart(plot_df)
        .transform_regression(x_label, y_label)
        .mark_line(color="red", size=2)
        .encode(
            x=alt.X(f"{x_label}:Q"),
            y=alt.Y(f"{y_label}:Q"),
        )
    )

    chart = (
        (points + reg_line)
        .properties(height=500, title=f"{y_label} vs {x_label}")
        .interactive()
    )

    return chart

try:
    cps_df, comm_gdf = load_data()

    cps_df = to_numeric_if_exists(
        cps_df.copy(),
        [
            "RI", "OI", "Opportunity Index",
            "IAR ELA %", "IAR MATH %",
            "School_Latitude", "School_Longitude",
            "Latitude", "Longitude",
        ]
    )

    col_map = detect_metric_columns(cps_df)
    joined_schools_gdf = spatial_join_schools_to_communities(cps_df, comm_gdf)

except Exception as e:
    st.error(f"Data preparation failed: {e}")
    st.stop()


st.sidebar.header("Choose a Metric")
main_section = st.sidebar.selectbox("", ["Spatial Distribution", "Scatter Plot"])


if main_section == "Spatial Distribution":
    st.header("Spatial Distribution")

    spatial_metric = st.selectbox("Select indicator", ["RI", "OI"], key="spatial_metric")
    metric_col = col_map[spatial_metric]

    left, right = st.columns([1.2, 1])

    try:
        comm_metric_gdf, comm_mean_df = compute_community_metric_mean(
            joined_schools_gdf, comm_gdf, metric_col
        )
        fig_map = plot_choropleth(comm_metric_gdf, spatial_metric)

        display_mean_df = comm_mean_df.rename(columns={"community_mean": f"{spatial_metric}_mean"}).copy()

        if spatial_metric == "RI":
            display_mean_df = display_mean_df.sort_values(by=f"{spatial_metric}_mean", ascending=True)
            table_title = "**Bottom 10 communities (lowest average)**"
        else:  
            display_mean_df = display_mean_df.sort_values(by=f"{spatial_metric}_mean", ascending=False)
            table_title = "**Top 10 communities (highest average)**"

        display_mean_df = display_mean_df.reset_index(drop=True)

    except Exception as e:
        st.error(f"Failed to build spatial distribution section: {e}")
        st.stop()

    with left:
        st.markdown(
            f"<h2 style='text-align: center; margin-bottom: 0.5rem;'>{spatial_metric} Spatial Distribution</h2>",
            unsafe_allow_html=True,
        )
        st.pyplot(fig_map, use_container_width=True)

    with right:
        st.markdown(
            f"<h2 style='text-align: center; margin-bottom: 0.5rem;'>{spatial_metric} Community Averages</h2>",
            unsafe_allow_html=True,
        )

        top_or_bottom_10 = display_mean_df.head(10).copy()
        top_or_bottom_10.index = range(1, len(top_or_bottom_10) + 1)

        st.markdown(table_title)
        st.dataframe(top_or_bottom_10, use_container_width=True)

elif main_section == "Scatter Plot":
    st.header("Scatter Plot")

    st.info(
        "Resource Index (RI) = 0.5*Hard Resources + 0.5*Soft Resources\n"
        "Hard Resources: Space Utilization, facility capacity etc.\n"
        "Soft Resources: 5Essentials Survey dimensions (Instruction, Leaders, Teachers, Families, Environment)\n\n"
        "Opportunity Index (OI) = avg(Z-scores of ED, EL, DIS, RACE)\n"
        "Higher OI = greater structural disadvantage"
    )

    c1, c2 = st.columns(2)
    with c1:
        x_choice = st.selectbox("Select index (RI / OI)", ["RI", "OI"], key="scatter_x")
    with c2:
        y_choice = st.selectbox("Select score (ELA / Math)", ["ELA", "Math"], key="scatter_y")

    x_col = col_map[x_choice]
    y_col = col_map[y_choice]
    name_col = get_school_name_column(cps_df)

    try:
        scatter_plot_df = build_scatter_df(
            cps_df,
            x_col=x_col,
            y_col=y_col,
            x_label=x_choice,
            y_label=y_choice,
            school_name_col=name_col,
        )

        alt_chart = plot_scatter_altair(scatter_plot_df, x_label=x_choice, y_label=y_choice)

        reg_stats = compute_regression_stats(scatter_plot_df, x_label=x_choice, y_label=y_choice)

    except Exception as e:
        st.error(f"Failed to build scatter plot section: {e}")
        st.stop()

    st.markdown(
        f"<h2 style='text-align: center; margin-bottom: 0.25rem;'>{y_choice} vs {x_choice}</h2>",
        unsafe_allow_html=True,
    )

    st.altair_chart(alt_chart, use_container_width=True)

    if reg_stats is not None:
        p_text = format_pvalue(reg_stats["pvalue"])
        slope_text = f"{reg_stats['slope']:.3f}"
        n_text = reg_stats["n"]

        st.markdown(
            f"""
            <div style="font-size: 0.88rem; color: #666666; margin-top: -0.35rem; text-align: left;">
                Linear regression: slope = {slope_text}, p-value = {p_text}, n = {n_text}.<br>
                Interpretation: {"Low correlation suggests misalignment of resources and student needs." if abs(reg_stats["slope"]) < 0.1 else "Slope indicates positive association between index and score."}
            </div>
            """,
            unsafe_allow_html=True,
        )
    else:
        st.markdown(
            """
            <div style="font-size: 0.88rem; color: #666666; margin-top: -0.35rem; text-align: left;">
                Not enough valid observations to compute regression statistics.
            </div>
            """,
            unsafe_allow_html=True,
        )