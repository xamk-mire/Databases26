-- Exercise 4: Sample data for the BAD design (medal_results)
-- Run after 04_bad_schema.sql. Notice the redundancy: same athlete/country and event/venue repeated.

INSERT INTO medal_results (
  athlete_id, athlete_name, country_code, country_name,
  event_id, event_name, sport_name, venue_name, city, medal_type
) VALUES
  (1, 'Mika Virtanen',   'FIN', 'Finland',   1, 'Men''s Downhill',        'Alpine Skiing',       'Snow Peak Arena', 'Beijing',     'gold'),
  (1, 'Mika Virtanen',   'FIN', 'Finland',   3, 'Men''s 50km Classical',  'Cross-Country Skiing', 'Mountain Resort', 'Zhangjiakou', 'silver'),
  (2, 'Sara Niemi',      'FIN', 'Finland',   2, 'Women''s Slalom',       'Alpine Skiing',       'Snow Peak Arena', 'Beijing',     'gold'),
  (3, 'Erik Olsen',      'NOR', 'Norway',    1, 'Men''s Downhill',        'Alpine Skiing',       'Snow Peak Arena', 'Beijing',     'silver'),
  (3, 'Erik Olsen',      'NOR', 'Norway',    3, 'Men''s 50km Classical',  'Cross-Country Skiing', 'Mountain Resort', 'Zhangjiakou', 'gold'),
  (4, 'Anna Schmidt',    'GER', 'Germany',   2, 'Women''s Slalom',       'Alpine Skiing',       'Snow Peak Arena', 'Beijing',     'bronze'),
  (5, 'James Chen',      'USA', 'United States', 5, 'Pairs Figure Skating', 'Figure Skating',      'Ice Palace',      'Beijing',     'silver'),
  (6, 'Emma Lind',       'NOR', 'Norway',    4, 'Women''s Sprint',       'Cross-Country Skiing', 'Mountain Resort', 'Zhangjiakou', 'gold');
