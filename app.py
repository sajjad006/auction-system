from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send, emit
from flask_mysqldb import MySQL

app = Flask(__name__)
socketio = SocketIO(app)
mysql = MySQL(app)

app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'DB_PASSWORD'
app.config['MYSQL_DB'] = 'auction'

def get_db():
  db = mysql.connection.cursor()
  return db

def get_upcoming_auctions():
  return [
    {
      'id': 1,
      'title': 'Auction 1',
      'description': 'This is auction 1',
      'start_time': '2021-06-01 12:00:00',
      'end_time': '2021-06-01 13:00:00',
      'status': 'upcoming'
    },
    {
      'id': 2,
      'title': 'Auction 2',
      'description': 'This is auction 2',
      'start_time': '2021-06-01 12:00:00',
      'end_time': '2021-06-01 13:00:00',
      'status': 'upcoming'
    },

    
  ]

def get_auction_by_id(id):
  return {
    'id': id,
    'title': 'Auction 1',
    'description': 'This is auction 1',
    'start_time': '2021-06-01 12:00:00',
    'end_time': '2021-06-01 13:00:00',
    'status': 'upcoming'
  }

def get_participants_by_auction_id(id):
  return [
    {
      'id': 1,
      'name': 'Participant 1',
    },
    {
      'id': 2,
      'name': 'Participant 2',
    },
    {
      'id': 3,
      'name': 'Participant 3',
    },
  ]

@app.route('/')
def home():
  upcoming_auctions = get_upcoming_auctions()
  return render_template('./index.html', auctions=upcoming_auctions)

# @socketio.on('message')
# def handle_message(data):
#   print('received message: ' + str(data))

# @socketio.on('room')
# def join_room(data):
#   print('joining room: ' + str(data))

@socketio.on('join')
def on_join(data):
  username = data['username']
  room = data['room']
  join_room(room)
  print(socketio.adapter.rooms)
  send(username + ' has entered the room.', to=room)

@socketio.on('leave')
def on_leave(data):
  username = data['username']
  room = data['room']
  leave_room(room)
  send(username + ' has left the room.', to=room)


if __name__ == '__main__':
  socketio.run(app)

# if __name__ == "__main__":
#   app.run()
