import eventlet
import socketio
import time
from threading import Lock
from aiohttp import web
import mysql.connector
import json
import sys

sio = socketio.Server(cors_allowed_origins='*', async_mode='eventlet')
app = socketio.WSGIApp(sio)

thread = None
thread_lock = Lock()

current_player = None
team = None
extra_time = 0
auction_id = sys.argv[1]
print(auction_id)

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Tomorrow@2021",
    database="auction"
)

cursor = mydb.cursor(dictionary=True)


@sio.on('connect')
def connect(sid, environ):
    global thread
    with thread_lock:
        if thread is None:
            thread = sio.start_background_task(background_thread)

    print("connected: ", sid)

@sio.on('bid')
def bid(sid, data):
    global current_player
    global extra_time
    global cursor
    global team
    global auction_id

    if int(current_player['BidPrice']) == int(data['bid_price']):
        print(data)
        team = data['team'].replace("%20", " ")
        print("bid placed: ", team, current_player['Name'], current_player['BidPrice'])
        sio.emit('bid', {'name':current_player['Name'], 'team':team, 'price':current_player['BidPrice'], 'next': int(current_player['BidPrice'])+1000000})
        current_player['BidPrice'] = int(current_player['BidPrice']) + 1000000
        extra_time=10
    else:
        print(data['bid_price'], current_player['BidPrice'], "proba")



@sio.on('disconnect')
def disconnect(sid):
    print('disconnect ', sid)

def background_thread():
    sio.sleep(5)

    global cursor
    cursor.execute("SELECT * FROM players LIMIT 6;")
    players = cursor.fetchall()

    sio.emit('message', {'data': 'match has started'})
    # db = mysql.connection.cursor(cursorclass=DictCursor)
    # players = db.execute("SELECT * FROM players").fetchall()

    global current_player
    global extra_time
    global team
    global mydb

    for player in players:
        current_player = player
        team = None
        sell_price = 0
        current_player['BidPrice'] = current_player['BasePrice']
        stats = {}

        if player['Type'] == 'Bowler':
            stats = {'wickets': str(player['Wickets']), 'average': str(player['BowlingAVG']), 'economy': str(player['EconomyRate'])}
        else:
            stats = {'runs': str(player['RunsScored']), 'average': str(player['BattingAVG']), 'sr': str(player['BattingS_R'])}

        sio.emit("player", {'name': player['Name'], 'image': player['Image'],  'type': player['Type'], 'base_price': str(player['BasePrice']), 'rating': str(player['Rating']), 'bid_price': str(player['BasePrice']), 'matches': str(player['MatchPlayed']), 'stats': stats})
        sio.sleep(5)

        if extra_time > 0:
            sio.sleep(extra_time)
            extra_time = 0
        
        # player sold 
        # record sale in db and emit purse to all clients
        if team is not None:
            sell_price = int(current_player['BidPrice'])-1000000
            cursor.execute("SELECT * FROM teams WHERE team_name = %s", (team,))
            team1 = cursor.fetchone()
            cursor.execute(f"INSERT INTO team_players (team, player, cost, auction) VALUES ({team1['id']}, {player['playerid']}, {sell_price}, {int(auction_id)})")
            cursor.execute(f"UPDATE teams SET purse = {int(team1['purse'] - sell_price)}, points = {int(int(team1['points']) + int(player['Rating']))} WHERE id = {team1['id']}")
            mydb.commit()

        cursor.execute(f"SELECT * FROM teams WHERE auction_id='{auction_id}' ORDER BY points DESC;")
        teams = cursor.fetchall()

        cursor.execute(f"SELECT * FROM auction.team_players INNER JOIN teams ON team_players.team=teams.id INNER JOIN players ON team_players.player=players.playerid WHERE auction_id='{auction_id}'")
        team_players = cursor.fetchall()

        team_players = [{'team': x['team_name'], 'player': x['Name'], 'cost': str(x['cost'])} for x in team_players]

        for x in teams:
            x['purse'] = str(x['purse'])            
            x['points'] = str(x['points'])
        sio.emit("sold", {'name':player['Name'], 'team':team, 'price':sell_price, 'purse':teams, 'team_players':team_players})
        sio.sleep(5)
    
    # update auction status in database
    cursor.execute(f"UPDATE auctions SET status='completed' WHERE id={auction_id}")
    mydb.commit()

    sio.emit("end", {'data': 'match has ended', 'auction_id': auction_id})

if __name__ == '__main__':
    print ("Starting server")
    eventlet.wsgi.server(eventlet.listen(('192.168.29.165', 3000)), app)
