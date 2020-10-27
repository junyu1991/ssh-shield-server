from flask import Flask, render_template, request,send_from_directory
from flask_socketio import SocketIO, send, emit, join_room, leave_room, Namespace

from paramikoUtil import ClientWrapper, SSHServerConfig

from ShellNameSpace import ShellNameSpace,GetMessageThread

import queue

app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app,  cors_allowed_origins="*", async_mode="threading")
config = SSHServerConfig(hostname='127.0.0.1', port=22, username='test', password='password')
messageQueue = queue.Queue()

socketio.on_namespace(ShellNameSpace(namespace='/ssh-test', sshConfig=config, messageQueue=messageQueue))
def after_request(resp):
    resp.headers['Access-Control-Allow-Origin'] = '*'
    return resp
app.after_request(after_request)

if __name__ == '__main__':
    print('Starting the server')
    socketio.run(app, host='192.168.1.102', port=9999, debug=True)