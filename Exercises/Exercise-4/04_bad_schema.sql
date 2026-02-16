-- Exercise 4: BAD DESIGN — single denormalized table (do not use in production!)
-- Run this first to create the "before" state. You will analyse and then normalize it.
-- Database: winter_olympics (CREATE DATABASE winter_olympics;)

-- Single table storing athlete, country, event, sport, venue, and medal in one place.
-- Redundant: same athlete/country repeated per result; same event/sport/venue repeated.
-- Primary key (athlete_id, event_id) — one row per athlete per event (one medal).
CREATE TABLE medal_results (
  athlete_id    INTEGER NOT NULL,
  athlete_name  VARCHAR(100) NOT NULL,
  country_code  VARCHAR(3) NOT NULL,
  country_name  VARCHAR(100) NOT NULL,
  event_id      INTEGER NOT NULL,
  event_name    VARCHAR(200) NOT NULL,
  sport_name    VARCHAR(100) NOT NULL,
  venue_name    VARCHAR(200) NOT NULL,
  city          VARCHAR(100) NOT NULL,
  medal_type    VARCHAR(6) NOT NULL CHECK (medal_type IN ('gold', 'silver', 'bronze')),
  PRIMARY KEY (athlete_id, event_id)
);
