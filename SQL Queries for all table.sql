# COMPETITIONS QUERIES 

# 1) List all competitions along with their category name

SELECT competitions.competition_id, 
	competitions.competition_name, 
	competitions.type, 
	competitions.gender, 
    categories.category_name
FROM competitions 
JOIN categories ON competitions.category_id = categories.category_id;

# 2) Count the number of competitions in each category

SELECT categories.category_name, COUNT(*) AS total_competitions
FROM competitions 
JOIN categories categories ON competitions.category_id = categories.category_id
GROUP BY categories.category_name
ORDER BY total_competitions DESC;

# 3) Find all competitions of type 'doubles'

SELECT competition_id, competition_name, gender
FROM competitions
WHERE type = 'doubles';

# 4) Get competitions that belong to a specific category (e.g., ITF Men)

SELECT 
	competitions.competition_id, 
    competitions.competition_name, 
    competitions.type, 
    competitions.gender
FROM competitions 
JOIN categories ON competitions.category_id = categories.category_id
WHERE categories.category_name = 'ITF Men';

# 5) Identify parent competitions and their sub-competitions

SELECT parent.competition_name AS parent_competition,
       child.competition_name  AS sub_competition
FROM competitions child
JOIN competitions parent ON child.parent_id = parent.competition_id
ORDER BY parent.competition_name;

# 6) Analyze the distribution of competition types by category

SELECT categories.category_name, competitions.type, COUNT(*) AS total
FROM competitions 
JOIN categories  ON competitions.category_id = categories.category_id
GROUP BY categories.category_name, competitions.type
ORDER BY categories.category_name, total DESC;

# 7) List all competitions with no parent (top-level competitions)

SELECT competition_id, competition_name
FROM competitions
WHERE parent_id IS NULL OR parent_id = '';

# COMPLEXES AND VENUES QUERIES

# 1) List all venues along with their associated complex name

SELECT venues.venue_name, venues.city_name, venues.country_name, complexes.complex_name
FROM venues 
JOIN complexes ON venues.complex_id = complexes.complex_id;

# 2) Count the number of venues in each complex

SELECT complexes.complex_name, COUNT(*) AS total_venues
FROM venues 
JOIN complexes ON venues.complex_id = complexes.complex_id
GROUP BY complexes.complex_name
ORDER BY total_venues DESC;

# 3) Get details of venues in a specific country (e.g., Chile)

SELECT country_name, venue_name, city_name, timezone
FROM venues
WHERE country_name = 'Chile';

# 4)  Identify all venues and their timezones

SELECT venue_name, timezone
FROM venues
ORDER BY venue_name;

# 5)  Find complexes that have more than one venue

SELECT complexes.complex_name, COUNT(*) AS venue_count
FROM venues 
JOIN complexes ON venues.complex_id = complexes.complex_id
GROUP BY complexes.complex_name
HAVING COUNT(*) > 1;

# 6)  List venues grouped by country

SELECT country_name, GROUP_CONCAT(venue_name, ', ') AS venues
FROM venues
GROUP BY country_name
ORDER BY country_name;

# 7) Find all venues for a specific complex (e.g., Nacional)

SELECT venues.venue_name, venues.city_name, venues.country_name
FROM venues 
JOIN complexes ON venues.complex_id = complexes.complex_id
WHERE complexes.complex_name = 'Nacional';

# COMPETITORS AND RANKING QUERIES

# 1) Get all competitors with their rank and points

SELECT 
	competitors.name, 
    competitors.country, 
    competitor_rankings.rank_position, 
    competitor_rankings.points
FROM competitor_rankings 
JOIN competitors ON competitor_rankings.competitor_id = competitors.competitor_id
ORDER BY competitor_rankings.rank_position;

# 2)  Find competitors ranked in the top 5

SELECT 
	competitors.name, 
	competitors.country, 
    competitor_rankings.rank_position, 
    competitor_rankings.points
FROM competitor_rankings
JOIN competitors ON competitor_rankings.competitor_id = competitors.competitor_id
WHERE competitor_rankings.rank_position <= 5
ORDER BY competitor_rankings.rank_position;

# 3) List competitors with no rank movement (stable rank)

SELECT 
	competitors.name, 
    competitor_rankings.rank_position, 
    competitor_rankings.movement
FROM competitor_rankings 
JOIN competitors ON competitor_rankings.competitor_id = competitors.competitor_id
WHERE competitor_rankings.movement = 0;

# 4) Get the total points of competitors from a specific country (e.g., Croatia)

SELECT 
	competitors.country, 
    SUM(competitor_rankings.points) AS total_points
FROM competitor_rankings 
JOIN competitors ON competitor_rankings.competitor_id = competitors.competitor_id
WHERE competitors.country = 'Croatia'
GROUP BY competitors.country;

# 5) Count the number of competitors per country

SELECT country, COUNT(*) AS total_competitors
FROM competitors
GROUP BY country
ORDER BY total_competitors DESC;

# 6) Find competitors with the highest points in the current week

SELECT 
	competitors.name, 
    competitors.country, 
    competitor_rankings.points
FROM competitor_rankings
JOIN competitors ON competitor_rankings.competitor_id = competitors.competitor_id
ORDER BY competitor_rankings.points DESC
LIMIT 1;
