DROP TABLE IF EXISTS games;
CREATE TABLE games (
    id integer primary key autoincrement,
    name text not null,
    password text not null,
    max_players integer not null,
    location text not null
);

DROP TABLE IF EXISTS players;
CREATE TABLE players (
    game_id integer not null,
    token text not null,
    spy integer not null
);

DROP TABLE IF EXISTS locations;
CREATE TABLE locations (
    name text not null
);

-- The values for games and players are just for testing, an initial
-- production database would have empty tables.

INSERT INTO games (name, password, max_players, location)
VALUES ('Game #1', 'game1', 4, 'Cinema'),
       ('PMF NS + Cam', 'blah', 7, 'Crusader Army');

INSERT INTO players (game_id, token, spy)
VALUES (1, 'asdf', 0),
       (1, 'fda', 0),
       (2, '1', 0),
       (2, '2', 0),
       (2, '3', 0),
       (2, '4', 1),
       (2, '5', 0),
       (2, '6', 0),
       (2, '7', 0);

INSERT INTO locations (name)
VALUES ('Somewhere'),
       ('Nowhere'),
       ('Lost');
