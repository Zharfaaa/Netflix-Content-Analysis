import pandas as pd
import streamlit as st
# from numpy.random import default_rng as rng
# import numpy as np
# import matplotlib.pyplot as plt

import plotly.express as px
df = pd.read_csv('netlix_titles.csv')


    # Data Cleaning
# Datatime convert
df['date_added'] = df['date_added'].str.strip()
df['date_added'] = pd.to_datetime(df['date_added'],format='mixed',errors='coerce')
df['year_added'] = df['date_added'].dt.year

# tukar 3 value rating yang duration nya kosong ke kolom duration
mask = df['duration'].isna()
df['duration'] = df['duration'].fillna(df['rating'])
df.loc[mask, 'rating'] = None

# rating kosong di isi NR
df['rating'] = df['rating'].fillna("NR")

    # dashboard 
st.set_page_config(
    page_title="Netflix Dashboard",
    layout="wide"
)


# st.title("Netflix Content Dashboard")
st.markdown(
    """
    <h1 style='text-align: center; 
        color:'white'; 
        font-size: 3rem; 
        padding-bottom: 3rem;'>
        Netflix Content Dashboard
    </h1>
    """,
    unsafe_allow_html=True
)

# ==========================================
# FILTER
# ==========================================
col_year , col_type = st.columns(2 , gap='large')
with col_year:
    min_year = int(df['year_added'].min())
    max_year = int(df["year_added"].max())
    year_range = st.slider(
        "Select Year Range",
        min_value=min_year,
        max_value=max_year,
        value=(min_year,max_year)
    )

with col_type:
    content_type = st.selectbox(
        "Select Content Type",
        ["All", "Movie", "TV Show"]
    )
# ==========================================
# FILTER DATA
# ==========================================
filtered_df = df[df['year_added'].between(year_range[0] , year_range[1])].copy()
if content_type != "All":
    filtered_df = filtered_df[filtered_df["type"] == content_type]


# membuat kolom year added agar year bisa di ekstrak dari kolom date_added
# filtered_df["year_added"] = (
#     filtered_df["date_added"]
#     .dt.year
# )


# chart line dan pie
col1, col2 = st.columns([4, 1], gap="large")
movie_per_year = (
    filtered_df[filtered_df["type"] == "Movie"]
    ["year_added"]
    .value_counts()
    .sort_index()
)

tvshow_per_year = (
    filtered_df[filtered_df["type"] == "TV Show"]
    ["year_added"]
    .value_counts()
    .sort_index()
)
with col1:
    st.subheader("Added Content Over Time")
    # Gabungkan Movie dan TV Show
    plot_df = pd.DataFrame({
        "Year": list(movie_per_year.index) + list(tvshow_per_year.index),
        "Added Shows": list(movie_per_year.values) + list(tvshow_per_year.values),
        "Type": (
            ["Movie"] * len(movie_per_year)
            + ["TV Show"] * len(tvshow_per_year)
        )
    })
    fig_line = px.line(
        plot_df,
        x="Year",
        y="Added Shows",
        color="Type",
        markers=True,
        text="Added Shows",
        labels={
            "Year": "Year",
            "Added Shows": "Added Shows",
            "Type": "Content Type"
        },
        color_discrete_map={
            "Movie": "#E50914",
            "TV Show": "#ff7723"
        }
    )
    # Posisi angka di atas titik
    fig_line.update_traces(
        textposition="top center"
    )
    # Layout
    fig_line.update_layout(
        height=500,
        legend_title_text="Type"
    )
    st.plotly_chart(
        fig_line,
        use_container_width=True
    )


# ==========================================
# PIE CHART
# ==========================================

with col2:
    st.subheader("Type Distribution")
    type_counts = filtered_df["type"].value_counts()
    fig_pie = px.pie(
        values=type_counts.values,
        names=type_counts.index,
        hole=0.4,
        color=type_counts.index,
        color_discrete_map={
            "Movie": "#BA0E0E",
            "TV Show": "#CB7020"
        }
    )

    fig_pie.update_layout(
        height=400,
        margin=dict(l=0, r=0, t=10, b=0),
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.05,
            xanchor="center",
            x=0.5
        )
    )

    st.plotly_chart(
        fig_pie,
        use_container_width=True
    )

# atur gap
st.markdown("<div style='margin-top:3rem;'></div>", unsafe_allow_html=True)
# chart 3 dan 4
# ==========================================
# TOP COUNTRY & TOP RATING
# ==========================================
col3, col4 = st.columns(2, gap="large")

with col3:
    st.subheader("Top 6 Countries with Most Shows Release")

    df_country = filtered_df.dropna(subset=["country"]).copy()
    df_country["country"] = df_country["country"].str.split(", ")
    df_country = df_country.explode("country")
    top_country = df_country["country"].value_counts().head(6)

    fig_country = px.bar(
        x=top_country.values,
        y=top_country.index,
        orientation="h",
        text=top_country.values,
        color_discrete_sequence=["#E50914"]
    )
    fig_country.update_traces(textposition="outside", cliponaxis=False)
    fig_country.update_layout(
        xaxis_title="Shows Release",
        yaxis_title=None,
        yaxis=dict(autorange="reversed"),
        height=400,
        margin=dict(l=0, r=30, t=10, b=0)
    )
    st.plotly_chart(fig_country, use_container_width=True)

with col4:
    st.subheader("Rating with Most Audience")
    df_rating = filtered_df.dropna(subset=["rating"]).copy()
    top_rating = df_rating["rating"].value_counts().head(5)
    fig_rating = px.bar(
        x=top_rating.index,
        y=top_rating.values,
        text=top_rating.values,
        color_discrete_sequence=["#ff7723"]
    )
    fig_rating.update_traces(textposition="outside", cliponaxis=False)
    fig_rating.update_layout(
        xaxis_title="Shows Release",
        yaxis_title=None,
        height=400,
        margin=dict(l=0, r=30, t=10, b=0)
    )
    st.plotly_chart(fig_rating, use_container_width=True)