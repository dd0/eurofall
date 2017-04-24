from flask import Flask, request, redirect, url_for
from flask import render_template
from contextlib import closing
import sqlite3
import sys
import random
import string

DATABASE = 'db/data.db'

app = Flask(__name__)
app.config.from_object(__name__)


def db():
    '''Returns a connection to the database.'''
    return sqlite3.connect(app.config['DATABASE'])


def create_db():
    with closing(db()) as database:
        with app.open_resource('schema.sql', mode='r') as schema:
            database.cursor().executescript(schema.read())
        database.commit()


@app.route('/')
def home():
    return render_template('index.html')


def show_games():
    database = db()

    # note: this will not return games with zero players
    # this is ok since games always have at least one player (the creator)
    query = ('SELECT id, name, count(*), max_players '
             'FROM games '
             'JOIN players ON id == game_id '
             'GROUP BY id;')
    cursor = database.execute(query)

    games = [{'title': row[1], 'curr_players': row[2], 'players': row[3],
              'id': row[0]} for row in cursor.fetchall()]

    return render_template('join.html', games=games)


def make_token():
    prefix = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))
    index = '%03x' % make_token.next_i  # this should guarantee uniqueness
    make_token.next_i += 1
    return prefix + index

make_token.next_i = 0


# Add a new player to the game with the id 'game' and return their token
def add_player(game):
    database = db()

    cursor = database.execute('SELECT max_players FROM games WHERE id == ?',
                              [game])
    max_players = cursor.fetchone()[0]

    query = ('SELECT count(*), sum(spy) '
             'FROM games '
             'JOIN players ON id == game_id '
             'WHERE id == ? '
             'GROUP BY id')
    cursor = database.execute(query, [game])
    res = cursor.fetchone()

    if res is None:
        # no players yet
        res = [0, 0]

    has_spy = res[1] > 0
    is_spy = 0
    if not has_spy and random.choice(range(max_players - res[0])) == 0:
        is_spy = 1

    insert_query = ('INSERT INTO players (game_id, token, spy)'
                    'VALUES (?, ?, ?)')
    token = make_token()
    database.execute(insert_query, [game, token, is_spy])
    database.commit()

    return token


@app.route('/join', methods=['GET', 'POST'])
def join_game():
    if request.method == 'GET':
        return show_games()
    else:
        database = db()
        game_id = request.form.get('id')
        password = request.form.get('pwd')

        query = ('SELECT name, count(*), max_players, password '
                 'FROM games '
                 'JOIN players ON id == game_id '
                 'WHERE id == ? '
                 'GROUP BY id')
        cursor = database.execute(query, [game_id])

        game = cursor.fetchone()
        if game is None:
            # todo: better UI for this
            return 'Nonexistent game!'

        if game[1] == game[2]:
            # todo: better UI as well
            return 'Game is full!'

        if game[3] != password:
            return 'Wrong password!'

        token = add_player(game_id)

        return redirect(url_for('play_game', token=token))


@app.route('/play', methods=['GET'])
def play_game():
    token = request.args.get('token')
    if token is None:
        return 'No token provided!'

    database = db()

    query = ('SELECT location, spy, name '
             'FROM players '
             'JOIN games ON id == game_id '
             'WHERE token = ? ')
    cursor = database.execute(query, [token])

    location = cursor.fetchone()
    if location is None:
        return 'Invalid token!'

    loc = location[0]
    if location[1]:
        loc = 'Spy'

    return render_template('play.html', location=loc, name=location[2])


def random_location():
    res = db().execute('SELECT name FROM locations ORDER BY RANDOM() LIMIT 1')
    return res.fetchone()[0]


@app.route('/create', methods=['GET', 'POST'])
def create_game():
    if request.method == 'GET':
        return render_template('create.html')
    else:
        name = request.form.get('name')
        password = request.form.get('pwd', '')
        num_players = int(request.form.get('num_players'))

        if name is None:
            return 'No name provided!'
        if num_players not in range(1, 20):
            return 'Invalid number of players!'

        loc = random_location()

        database = db()
        query = ('INSERT INTO games (name, password, max_players, location) '
                 'VALUES (?, ?, ?, ?)')
        cursor = database.execute(query, [name, password, num_players, loc])
        database.commit()

        token = add_player(cursor.lastrowid)

        return redirect(url_for('play_game', token=token))


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--makedb':
        print('Creating database... ', end='')
        create_db()
        print('Done.')
    app.run()
