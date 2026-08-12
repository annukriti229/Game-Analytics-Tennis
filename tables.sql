CREATE DATABASE tennis_db;

USE tennis_db;

-- Creating Categories Table

CREATE TABLE categories (
    category_id     VARCHAR(50) PRIMARY KEY,
    category_name   VARCHAR(100) NOT NULL
);

SELECT*FROM categories;
 
 -- Creating Competitions Table 
 
CREATE TABLE competitions (
    competition_id      VARCHAR(50) PRIMARY KEY,
    competition_name    VARCHAR(100) NOT NULL,
    parent_id            VARCHAR(50) NULL,
    type                 VARCHAR(20) NOT NULL,
    gender               VARCHAR(10) NOT NULL,
    category_id          VARCHAR(50) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES categories(category_id)
);
 
SELECT*FROM competitions;

-- Creating Complexes Table

CREATE TABLE complexes (
    complex_id      VARCHAR(50) PRIMARY KEY,
    complex_name    VARCHAR(100) NOT NULL
);
 
SELECT*FROM complexes;
 
 -- Creating Venues Table
 
CREATE TABLE venues (
    venue_id        VARCHAR(50) PRIMARY KEY,
    venue_name      VARCHAR(100) NOT NULL,
    city_name       VARCHAR(100) NOT NULL,
    country_name    VARCHAR(100) NOT NULL,
    country_code    CHAR(3) NOT NULL,
    timezone        VARCHAR(100) NOT NULL,
    complex_id      VARCHAR(50) NOT NULL,
    FOREIGN KEY (complex_id) REFERENCES complexes(complex_id)
);
 
SELECT*FROM venues;
 
 -- Creating Competitors Table
 
CREATE TABLE competitors (
    competitor_id   VARCHAR(50) PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    country         VARCHAR(100) NOT NULL,
    country_code    CHAR(3) NULL,
    abbreviation    VARCHAR(10) NOT NULL
);

SELECT*FROM competitors;

-- Creating Competitor Ranking Table

CREATE TABLE competitor_rankings (
    rank_id               INT AUTO_INCREMENT PRIMARY KEY,
    rank_position         INT NOT NULL,                    -- "rank" replaced to "rank_position": 'rank' is a MySQL reserved word
    movement              INT NOT NULL,
    points                INT NOT NULL,
    competitions_played   INT NOT NULL,
    competitor_id         VARCHAR(50) NOT NULL,
    FOREIGN KEY (competitor_id) REFERENCES competitors(competitor_id)
);
 
SELECT*FROM competitor_rankings;

-- Helpful indexes for query performance

CREATE INDEX idx_competitions_category ON competitions(category_id);
CREATE INDEX idx_venues_complex ON venues(complex_id);
CREATE INDEX idx_rankings_competitor ON competitor_rankings(competitor_id);
CREATE INDEX idx_rankings_rank ON competitor_rankings(rank_position);
 
 SELECT 'Schema created successfully' AS status;