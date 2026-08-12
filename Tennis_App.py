import streamlit as st
import pandas as pd
import altair as alt

from config import get_engine
import sql_query

st.set_page_config(page_title="🎾 Tennis Analysis", layout="wide")

engine = get_engine()


@st.cache_data(ttl=300)
def cached_summary(_engine):
    return sql_query.fetch_summary(_engine)


@st.cache_data(ttl=300)
def cached_leaderboard(_engine, limit):
    return sql_query.fetch_leaderboard(_engine, limit)


@st.cache_data(ttl=300)
def cached_search(_engine, name, country, min_points):
    return sql_query.fetch_search_and_filter_competitors(_engine, name, country, min_points)


@st.cache_data(ttl=300)
def cached_top_competitors(_engine, start_rank, end_rank):
    return sql_query.fetch_top_competitors(_engine, start_rank, end_rank)


@st.cache_data(ttl=300)
def cached_movement_breakdown(_engine):
    return sql_query.fetch_movement_breakdown(_engine)


@st.cache_data(ttl=300)
def cached_country_stats(_engine):
    return sql_query.fetch_country_wise_stats(_engine)


@st.cache_data(ttl=300)
def cached_category_gender_type(_engine):
    return sql_query.fetch_category_gender_type(_engine)


@st.cache_data(ttl=300)
def cached_category_competition(_engine, category_name, gender, type_t):
    return sql_query.fetch_category_competition(_engine, category_name, gender, type_t)


@st.cache_data(ttl=300)
def cached_country_city(_engine):
    return sql_query.fetch_country_city(_engine)


@st.cache_data(ttl=300)
def cached_venues_complexes(_engine, complex_name, venues_name, city_name, country_name):
    return sql_query.fetch_venues_complexes(_engine, complex_name, venues_name, city_name, country_name)


@st.cache_data(ttl=300)
def cached_venues_per_country(_engine):
    return sql_query.fetch_venues_per_country(_engine)


def download_button(df: pd.DataFrame, filename: str, key: str):
    """One-line CSV export, reused on every page that shows a table."""
    st.download_button(
        "⬇ Download as CSV",
        df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
        key=key,
    )


def paginate(df: pd.DataFrame, page_size: int, key: str) -> pd.DataFrame:
    """Slice a DataFrame with a page-number widget instead of rendering
    everything at once -- keeps large tables responsive."""
    total_rows = len(df)
    if total_rows <= page_size:
        return df

    total_pages = (total_rows + page_size - 1) // page_size
    page_num = st.number_input(
        "Page", min_value=1, max_value=total_pages, value=1, step=1, key=key
    )
    st.caption(f"Showing page {page_num} of {total_pages} ({total_rows} rows total)")
    start = (page_num - 1) * page_size
    return df.iloc[start:start + page_size]

# Sidebar Navigation

NAV = {
    "🏠 Dashboard": "dashboard",
    "🔍 Search & Filter Competitors": "search",
    "🏅 Competitors by Rank": "rank",
    "📁 Categories & Competitions": "categories",
    "🏟️ Venues & Complexes": "venues",
    "🌍 Country-wise Analysis": "country",
}

st.sidebar.title("Content")
selected_label = st.sidebar.radio("", list(NAV.keys()))
page = NAV[selected_label]

with st.sidebar.expander("ℹ️ About this app"):
    st.write(
        "Explore SportRadar tennis competition, venue, and ranking data. "
        "Filters update the tables and charts live; use the download "
        "buttons to export any table as CSV."
    )

# Dashboard

if page == "dashboard":
    st.markdown("<h1 style='text-align:center;'>🎾 Tennis Dashboard</h1>", unsafe_allow_html=True)

    overview_tab, charts_tab = st.tabs(["📊 Overview", "📈 Charts"])

    with overview_tab:
        st.header("📊 Summary Statistics")
        summary = cached_summary(engine)

        competitors, countries, points = st.columns(3, border=True)
        competitors.metric("Total Competitors 👥", summary["total_competitors"])
        countries.metric("Countries Represented 🌍", summary["total_countries"])
        points.metric("Highest Points 🏆", summary["highest_points"])

        st.subheader("Leaderboard")
        top_n = st.slider("Show top N", 3, 20, 5, key="dash_top_n")
        df_leaderboard = cached_leaderboard(engine, top_n)

        medal_map = {1: "🥇", 2: "🥈", 3: "🥉"}
        df_leaderboard["Medal"] = df_leaderboard["rank_position"].map(medal_map).fillna("")
        df_leaderboard = df_leaderboard.rename(columns={"rank_position": "Rank"})
        st.dataframe(
            df_leaderboard[["Medal", "Rank", "Name", "Country", "Points"]],
            hide_index=True,
            use_container_width=True,
        )
        download_button(df_leaderboard, "leaderboard.csv", "dl_dashboard")

    with charts_tab:
        st.subheader("Points distribution — top 15")
        df_top15 = cached_leaderboard(engine, 15)
        chart = (
            alt.Chart(df_top15)
            .mark_bar()
            .encode(
                x=alt.X("Name", sort="-y", title="Competitor"),
                y=alt.Y("Points", title="Points"),
                color=alt.Color("Country", legend=None),
                tooltip=["Name", "Country", "Points", "rank_position"],
            )
            .properties(height=400)
        )
        st.altair_chart(chart, use_container_width=True)

        st.subheader("Competitors by country (top 15)")
        df_country = cached_country_stats(engine).head(15)
        donut = (
            alt.Chart(df_country)
            .mark_arc(innerRadius=60)
            .encode(
                theta="Competitor Count",
                color=alt.Color("Country", legend=alt.Legend(title="Country")),
                tooltip=["Country", "Competitor Count", "Total Points"],
            )
            .properties(height=400)
        )
        st.altair_chart(donut, use_container_width=True)

# Search and Filters

elif page == "search":
    st.header("🔍 Search & Filter Competitors")

    f1, f2, f3 = st.columns(3)
    with f1:
        name_input = st.text_input("Search by name")
    with f2:
        country_filter = st.text_input("Filter by country")
    with f3:
        min_points = st.slider("Minimum points", 0, 10000, 0)

    df_results = cached_search(engine, name_input, country_filter, min_points)

    if df_results.empty:
        st.info("No results found. Try lowering the minimum points or clearing a filter.")
    else:
        sort_choice = st.radio("Sort by points", ["Highest first", "Lowest first"], horizontal=True)
        df_results = df_results.sort_values(
            "Points", ascending=(sort_choice == "Lowest first")
        ).reset_index(drop=True)

        st.caption(f"{len(df_results)} competitor(s) matched.")
        page_df = paginate(df_results, page_size=15, key="search_page")
        st.dataframe(page_df, hide_index=True, use_container_width=True)
        download_button(df_results, "search_results.csv", "dl_search")

        if len(df_results) > 1:
            st.subheader("Points comparison")
            chart = (
                alt.Chart(df_results.head(20))
                .mark_bar()
                .encode(
                    x=alt.X("Name", sort="-y"),
                    y="Points",
                    color=alt.Color("Country", legend=None),
                    tooltip=["Name", "Country", "Points", "Movement"],
                )
                .properties(height=350)
            )
            st.altair_chart(chart, use_container_width=True)

# Competitors by Rank

elif page == "rank":
    st.header("🏅 Competitors by Rank")

    ranks_range = st.slider("Ranks", min_value=1, max_value=600, value=(1, 10))
    start_rank, end_rank = ranks_range

    try:
        df_top = cached_top_competitors(engine, start_rank, end_rank)

        if df_top.empty:
            st.info(f"No competitors found for ranks {start_rank}–{end_rank}.")
        else:
            page_df = paginate(df_top, page_size=20, key="rank_page")
            st.dataframe(page_df, use_container_width=True, hide_index=True)
            download_button(df_top, "competitors_by_rank.csv", "dl_rank")

            chart_col1, chart_col2 = st.columns(2)

            with chart_col1:
                st.subheader("Points vs. rank")
                line = (
                    alt.Chart(df_top)
                    .mark_line(point=True)
                    .encode(
                        x=alt.X("Rank Position", title="Rank"),
                        y=alt.Y("Points", title="Points"),
                        tooltip=["Name", "Country", "Rank Position", "Points"],
                    )
                    .properties(height=350)
                )
                st.altair_chart(line, use_container_width=True)

            with chart_col2:
                st.subheader("Rank movement in this range")
                df_movement = cached_movement_breakdown(engine)
                bar = (
                    alt.Chart(df_movement)
                    .mark_bar()
                    .encode(
                        x="Direction",
                        y="Count",
                        color=alt.Color("Direction", legend=None,
                                        scale=alt.Scale(domain=["Up", "Stable", "Down"],
                                                        range=["#2ecc71", "#95a5a6", "#e74c3c"])),
                        tooltip=["Direction", "Count"],
                    )
                    .properties(height=350)
                )
                st.altair_chart(bar, use_container_width=True)

    except Exception as e:
        st.error("Unable to load competitors by rank.")
        st.exception(e)

# Categories and Competitions

elif page == "categories":
    st.header("📁 Categories & Competitions")

    categories, types, genders = cached_category_gender_type(engine)
    categories = ["None"] + categories
    types = ["None"] + types
    genders = ["None"] + genders

    category_name = st.sidebar.selectbox("Category name", categories)
    gender = st.sidebar.selectbox("Gender", genders)
    type_t = st.sidebar.selectbox("Type", types)

    df = cached_category_competition(engine, category_name, gender, type_t)

    if df.empty:
        st.info("No results found.")
    else:
        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            gender_counts = df["Gender"].value_counts().reset_index()
            gender_counts.columns = ["Gender", "Count"]
            chart = (
                alt.Chart(gender_counts)
                .mark_bar()
                .encode(x="Gender", y="Count", color="Gender",
                        tooltip=["Gender", "Count"])
                .properties(title="Event count by gender", height=350)
            )
            st.altair_chart(chart, use_container_width=True)

        with chart_col2:
            type_counts = df["Type"].value_counts().reset_index()
            type_counts.columns = ["Type", "Count"]
            donut = (
                alt.Chart(type_counts)
                .mark_arc(innerRadius=50)
                .encode(theta="Count", color="Type", tooltip=["Type", "Count"])
                .properties(title="Event count by type", height=350)
            )
            st.altair_chart(donut, use_container_width=True)

        st.subheader("Matching competitions")
        page_df = paginate(df, page_size=15, key="categories_page")
        st.dataframe(page_df, hide_index=True, use_container_width=True)
        download_button(df, "categories_competitions.csv", "dl_categories")

# Venues and Complexes

elif page == "venues":
    st.header("🏟️ Venues & Complexes")

    complexes, venues, city, country = cached_country_city(engine)
    complexes = ["None"] + complexes
    venues = ["None"] + venues
    city = ["None"] + city
    country = ["None"] + country

    complex_name = st.sidebar.selectbox("Complex name", complexes)
    venues_name = st.sidebar.selectbox("Venue name", venues)
    city_name = st.sidebar.selectbox("City", city)
    country_name = st.sidebar.selectbox("Country name", country)

    df = cached_venues_complexes(engine, complex_name, venues_name, city_name, country_name)

    if df.empty:
        st.info("No results found.")
    else:
        page_df = paginate(df, page_size=15, key="venues_page")
        st.dataframe(page_df, hide_index=True, use_container_width=True)
        download_button(df, "venues_complexes.csv", "dl_venues")

    st.divider()
    st.subheader("Venues per country")
    df_vpc = cached_venues_per_country(engine)
    chart = (
        alt.Chart(df_vpc)
        .mark_bar()
        .encode(
            x=alt.X("Country", sort="-y"),
            y="Venue Count",
            color=alt.Color("Country", legend=None),
            tooltip=["Country", "Venue Count"],
        )
        .properties(height=350)
    )
    st.altair_chart(chart, use_container_width=True)

# Country Wise Analysis

elif page == "country":
    st.header("🌍 Country-wise Analysis")

    df_country = cached_country_stats(engine)
    st.dataframe(df_country, hide_index=True, use_container_width=True)
    download_button(df_country, "country_stats.csv", "dl_country")

    top_n = st.slider("Countries to chart", 5, min(30, len(df_country)), 10, key="country_top_n")
    df_chart = df_country.sort_values("Total Points", ascending=False).head(top_n)

    metric_choice = st.radio(
        "Metric", ["Total Points", "Competitor Count", "Average Points"], horizontal=True
    )
    chart = (
        alt.Chart(df_chart)
        .mark_bar()
        .encode(
            x=alt.X("Country", sort="-y"),
            y=alt.Y(metric_choice),
            color=alt.Color("Country", legend=None),
            tooltip=["Country", "Competitor Count", "Total Points", "Average Points"],
        )
        .properties(height=400)
    )
    st.altair_chart(chart, use_container_width=True)