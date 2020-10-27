from flask import Flask, render_template, request,send_from_directory
from flask_socketio import SocketIO, send, emit, join_room, leave_room, Namespace

from paramikoUtil import ClientWrapper, SSHServerConfig

from ShellNameSpace import ShellNameSpace

import os

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app,  cors_allowed_origins="*")

config = SSHServerConfig(hostname='localhost', port=22, username='root', password='test')
client = None

'''
自定义namespace
'''
class MyCustomNameSpace(Namespace):
    def on_connect(self):
        print('custom name space ' + self.namespace + ' connected')
        self.emit(event='connect', data='connect success')

    def on_disconnect(self):
        print('custom name space disconnect')

    def on_my_event(self, data):
        emit('my_response', data)

socketio.on_namespace(ShellNameSpace('/ssh-test'))


@socketio.on_error()
def error_handler(e):
    print('Handle the default namespace error :' + e)

@socketio.on_error('/chat')
def error_handler_chat(e):
    print('Handle the /chat namespace error: ' + e)

@socketio.on_error_default
def default_error_handler(e):
    print('Handle all namespace without an explicit error handler:' + e)


@app.route('/') 
def index(): 
    # return 'jhe;'
    root_dir = os.path.dirname(os.getcwd())
    print(root_dir)
    return send_from_directory(os.path.join(root_dir,'flaskr', 'static'),filename='test.html')

@socketio.on('connect')
def test_connect():
    print('test_connect')
    emit('my response', {'data':'Connected'})

@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnect')

@socketio.on('connect', namespace='/test')
def handle_connect():
    print('Start connecting to ssh server')
    client = ClientWrapper(config)
    if(client.connectable):
        send('Connect to server success')
    else:
        send('Connect to server failed')

@socketio.on('message', namespace='/test')
def handle_message(message):
    print('received message: ' + message)

@socketio.on('json')
def handle_json(json):
    print('received json: ' + str(json))

'''
可使用broadcast参数来设置是否广播该消息，
当设置为True时，使用send或者emit发送的消息会发送到指定namespace的所有客户端，包括当前的发送者，
若没有指定namespace则会发送到全局的namespace

socketio.emit与socketio.send与上下文相关的send,emit是不相同的，由于没有client上下文，所以可以不用
设置broadcast参数，socketio.send与socketio.emit可用于后台线程消息通知
'''
@socketio.on('broadcast event')
def handle_broadcast(data):
    emit('broadcast message', data, broadcast=True)

'''
可使用room参数指定房间，向房间内的所有客户端发送消息
'''
@socketio.on('join')
def on_join(data):
    username = data['username']
    room = data['room']
    join_room(room)
    send(username + ' has entered the room.', room=room)

@socketio.on('leave')
def on_leave(data):
    username = data['username']
    room = data['root']
    leave_room(room)
    send(username + ' has left room.', room=room)

def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp

app.after_request(after_request)

if __name__ == '__main__':
    print('Starting the server')
    socketio.run(app, host='0.0.0.0', port=9999, debug=True)