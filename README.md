# eurofall

This is a small, browser-based implementation of the board game
Spyfall. It was created to make the process of trying new locations
easier, so that it doesn't require creating the cards (the original
inspiration was trying Spyfall with European countries as location).

The players connect to the server using their mobile phones' browsers,
where they can create a new game or join an already existing
one. After joining a game, they are redirected to a page showing the
location (or that they are the spy).

Note: currently under development.


# Usage

To set up the server, clone the repository and run it with the
`--makedb` switch to create the database. This requires first creating
the `db` directory (in which the database files are kept):

    git clone https://github.com/dd0/eurofall.git
    cd eurofall
    mkdir db
    python eurofall.py --makedb

This will initialise the database and run the server on
`localhost:5000`. To run the server afterwards, just run the script:

    python eurofall.py

## Adding locations

The locations are stored in the `locations` table, which is populated
from the `schema.sql` script. After adding or removing locations, the
database needs to be rebuilt by running the script with the `--makedb`
switch.

Note that this will overwrite the database, which will delete all
games that are currently in progress.