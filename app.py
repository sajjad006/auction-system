from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_mysqldb import MySQL
from MySQLdb.cursors import DictCursor
from flask_session import Session
import datetime
import pytz

app = Flask(__name__)
mysql = MySQL(app)
sess = Session()

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Tomorrow@2021'
app.config['MYSQL_DB'] = 'auction'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'



def get_db():
    db = mysql.connection.cursor(cursorclass=DictCursor)
    return db


def get_upcoming_auctions():
    cursor = get_db()
    cursor.execute(
        "SELECT id, title, start_time  FROM auctions WHERE start_time >= NOW()")
    auctions = cursor.fetchall()
    return auctions

def get_teams (id):
    db = get_db()
    db.execute(f"SELECT * FROM teams WHERE auction_id = {id} ORDER BY points DESC")
    teams = db.fetchall()
    return teams

def get_auction_winner(id):
    db = get_db()
    db.execute(f"SELECT * FROM teams WHERE auction_id = {id} ORDER BY points DESC LIMIT 1")
    winner = db.fetchone()
    return winner

def get_auction_by_id(id):
    cursor = get_db()
    cursor.execute(
        f"SELECT id, title, start_time, Status  FROM auctions WHERE id={id}")
    auctions = cursor.fetchall()
    return auctions[0]

def get_players_by_team_name(id, team_name):
    db = get_db()
    db.execute(f"SELECT * from team_players INNER JOIN teams ON team_players.team=teams.id INNER JOIN players ON team_players.player=players.playerid WHERE team_name='{team_name}' AND auction_id='{id}';")
    players = db.fetchall()
    return players


@app.route('/')
def home():
    upcoming_auctions = get_upcoming_auctions()
    return render_template('./registration.html', auctions=upcoming_auctions)

# handle post request for register


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    auction_id = int(request.form['auction-id'])
    team_name = request.form['team_name']
    password = request.form['password']

    # check if user already exists
    db = get_db()
    db.execute(
        f"SELECT * FROM teams WHERE username = '{username}' AND auction_id = {auction_id}")
    user = db.fetchone()

    if user:
        flash('This user is already registered for this auction')
        return redirect(url_for('home'))
    else:
        db.execute(
            f"INSERT INTO teams (team_name, auction_id, username, password) VALUES ('{team_name}', {auction_id}, '{username}', '{password}')")
        mysql.connection.commit()
        db.close()
        session['username'] = username
        session['team_name'] = team_name
        session['auction_id'] = auction_id
        return redirect(url_for('gameplay', id=auction_id))


@app.route('/gameplay/<int:id>')
def gameplay(id):
    auction = get_auction_by_id(id)

    if 'username' in session:
        if auction['start_time'] >= datetime.datetime.now():
            return render_template('./waiting.html', auction=auction)
        else:
            # check if auction has port
            # port = None
            # db = get_db()
            # db.execute(f"SELECT * FROM auctions WHERE id = {id}")
            # auction = db.fetchone()
            # if auction['port'] is None:
            #   port = get_free_port()
            #   db.execute(f"UPDATE auctions SET port = {port} WHERE id = {id}")
            #   mysql.connection.commit()
            #   db.close()
            # else:
            #   port = auction['port']

            # team = get_db().execute(f"SELECT * FROM teams WHERE username = '{session['username']}' AND auction_id = {id}").fetchone()

            return render_template('./gameplay.html', auction=auction, username=session['username'], team_name=session['team_name'])
    else:
        return redirect(url_for('home'))

@app.route('/final/<int:id>')
def final(id):
    auction = get_auction_by_id(id)
    my_players = get_players_by_team_name(id, session['team_name'])	
    winner = get_auction_winner(id)
    teams = get_teams(id)
    if auction['Status'] == 'completed':
        return render_template('./final.html', auction=auction, username=session['username'], team_name=session['team_name'], my_players=my_players, winner=winner, teams=teams)
    else:
        return redirect(url_for('home'))

if __name__ == '__main__':
    # app.secret_key = 'lzhsddsofhweohw80vw4ohwiv'
    sess.init_app(app)
    app.debug = True
    app.run()
