import pandas as pd

# Dashboard

def fetch_summary(conn) -> dict:
    """Top-line stats for the dashboard header."""
    sql = """
        SELECT
            (SELECT COUNT(*) FROM competitions) AS total_competitors,
            (SELECT COUNT(DISTINCT country) FROM competitors)  AS total_countries,
            (SELECT MAX(points) FROM competitor_rankings) AS highest_points
    """
    row = pd.read_sql_query(sql, conn).iloc[0]
    return {
        "total_competitors": int(row["total_competitors"]),
        "total_countries": int(row["total_countries"]),
        "highest_points": int(row["highest_points"]) if pd.notna(row["highest_points"]) else 0,
    }

def fetch_leaderboard(conn, limit: int = 5) -> pd.DataFrame:
    """Top-N competitors by rank, used for the medal leaderboard."""
    sql = """
        SELECT c.name AS Name, c.country AS Country,
               r.rank_position AS rank_position, r.points AS Points
        FROM competitor_rankings r
        JOIN competitors c ON c.competitor_id = r.competitor_id
        ORDER BY r.rank_position ASC
        LIMIT %(limit)s
    """
    return pd.read_sql_query(sql, conn, params={"limit": limit})

# Search and Filters

def fetch_search_and_filter_competitors(conn, name: str, country: str, min_points: int) -> pd.DataFrame:
    where = ["r.points >= %(min_points)s"]
    params = {"min_points": min_points}

    if name:
        where.append("c.name LIKE %(name)s")
        params["name"] = f"%{name}%"
    if country:
        where.append("c.country LIKE %(country)s")
        params["country"] = f"%{country}%"

    sql = f"""
        SELECT c.name AS Name, c.country AS Country,
               r.rank_position AS `Rank Position`, r.points AS Points,
               r.movement AS Movement
        FROM competitor_rankings r
        JOIN competitors c ON c.competitor_id = r.competitor_id
        WHERE {' AND '.join(where)}
        ORDER BY r.points DESC
    """
    return pd.read_sql_query(sql, conn, params=params)

# Competitor by Rank

def fetch_top_competitors(conn, start_rank: int, end_rank: int) -> pd.DataFrame:
    sql = """
        SELECT c.name AS Name, c.country AS Country,
               r.rank_position AS `Rank Position`, r.points AS Points
        FROM competitor_rankings r
        JOIN competitors c ON c.competitor_id = r.competitor_id
        WHERE r.rank_position BETWEEN %(start_rank)s AND %(end_rank)s
        ORDER BY r.rank_position ASC
    """
    return pd.read_sql_query(sql, conn, params={"start_rank": start_rank, "end_rank": end_rank})


def fetch_movement_breakdown(conn) -> pd.DataFrame:
    """Up / down / stable counts, used for a chart on the rank-range page."""
    sql = """
        SELECT CASE
                   WHEN movement > 0 THEN 'Up'
                   WHEN movement < 0 THEN 'Down'
                   ELSE 'Stable'
               END AS Direction,
               COUNT(*) AS Count
        FROM competitor_rankings
        GROUP BY Direction
    """
    return pd.read_sql_query(sql, conn)

# Country wise Analysis

def fetch_country_wise_stats(conn) -> pd.DataFrame:
    sql = """
        SELECT c.country AS Country,
               COUNT(*) AS `Competitor Count`,
               SUM(r.points) AS `Total Points`,
               ROUND(AVG(r.points), 1) AS `Average Points`
        FROM competitors c
        JOIN competitor_rankings r ON r.competitor_id = c.competitor_id
        GROUP BY c.country
        ORDER BY `Total Points` DESC
    """
    return pd.read_sql_query(sql, conn)

# Category and Competitions


def fetch_category_gender_type(conn):
    """Distinct dropdown option lists for the Categories & Competitions page."""
    categories = pd.read_sql_query(
        "SELECT DISTINCT category_name FROM categories ORDER BY category_name", conn
    )["category_name"].tolist()
    types = pd.read_sql_query(
        "SELECT DISTINCT type FROM competitions ORDER BY type", conn
    )["type"].tolist()
    genders = pd.read_sql_query(
        "SELECT DISTINCT gender FROM competitions ORDER BY gender", conn
    )["gender"].tolist()
    return categories, types, genders


def fetch_category_competition(conn, category_name: str, gender: str, type_t: str) -> pd.DataFrame:
    where, params = ["1=1"], {}

    if category_name and category_name != "None":
        where.append("cat.category_name = %(category_name)s")
        params["category_name"] = category_name
    if gender and gender != "None":
        where.append("comp.gender = %(gender)s")
        params["gender"] = gender
    if type_t and type_t != "None":
        where.append("comp.type = %(type_t)s")
        params["type_t"] = type_t

    sql = f"""
        SELECT comp.competition_name AS Competition,
               cat.category_name AS Category,
               comp.type AS Type,
               comp.gender AS Gender
        FROM competitions comp
        JOIN categories cat ON cat.category_id = comp.category_id
        WHERE {' AND '.join(where)}
        ORDER BY comp.competition_name
    """
    return pd.read_sql_query(sql, conn, params=params)

# Venues and Complexes


def fetch_country_city(conn):
    """Distinct dropdown option lists for the Venues & Complexes page."""
    complexes = pd.read_sql_query(
        "SELECT DISTINCT complex_name FROM complexes ORDER BY complex_name", conn
    )["complex_name"].tolist()
    venues = pd.read_sql_query(
        "SELECT DISTINCT venue_name FROM venues ORDER BY venue_name", conn
    )["venue_name"].tolist()
    city = pd.read_sql_query(
        "SELECT DISTINCT city_name FROM venues ORDER BY city_name", conn
    )["city_name"].tolist()
    country = pd.read_sql_query(
        "SELECT DISTINCT country_name FROM venues ORDER BY country_name", conn
    )["country_name"].tolist()
    return complexes, venues, city, country


def fetch_venues_complexes(conn, complex_name, venues_name, city_name, country_name) -> pd.DataFrame:
    where, params = ["1=1"], {}

    if complex_name and complex_name != "None":
        where.append("cx.complex_name = %(complex_name)s")
        params["complex_name"] = complex_name
    if venues_name and venues_name != "None":
        where.append("v.venue_name = %(venues_name)s")
        params["venues_name"] = venues_name
    if city_name and city_name != "None":
        where.append("v.city_name = %(city_name)s")
        params["city_name"] = city_name
    if country_name and country_name != "None":
        where.append("v.country_name = %(country_name)s")
        params["country_name"] = country_name

    sql = f"""
        SELECT v.venue_name AS Venue, cx.complex_name AS Complex,
               v.city_name AS City, v.country_name AS Country, v.timezone AS Timezone
        FROM venues v
        JOIN complexes cx ON cx.complex_id = v.complex_id
        WHERE {' AND '.join(where)}
        ORDER BY v.country_name, v.venue_name
    """
    return pd.read_sql_query(sql, conn, params=params)


def fetch_venues_per_country(conn) -> pd.DataFrame:
    """Used for the bar chart on the Venues & Complexes page."""
    sql = """
        SELECT country_name AS Country, COUNT(*) AS `Venue Count`
        FROM venues
        GROUP BY country_name
        ORDER BY `Venue Count` DESC
    """
    return pd.read_sql_query(sql, conn)
