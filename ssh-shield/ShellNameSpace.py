import threading
import time

from flask_socketio import send, emit, Namespace, join_room
from flask import request
import flask

from paramikoUtil import ClientWrapper, SSHServerConfig
from SSHClientContainer import SSHClientContainer
from Message import SSHMessage
import util

class ShellNameSpace(Namespace):
    def __init__(self, namespace=None, sshConfig=None, messageQueue=None):
        super(ShellNameSpace, self).__init__(namespace)
        self.sshConfig = sshConfig
        self.messageQueue = messageQueue
        self.thread_lock = threading.Lock()
        self.encode = 'utf-8'
        self.clientMap = {}
        self.testString = b''

    '''
    处理ssh连接请求
    '''
    def on_connect(self):
        # print('Get new connection from: ' + str(request))
        print('New conncetion args: ' + str(request.args.get('id')))
        emit('sshStatus','Connect to server success')
        room = util.getRoomID(request.args.get('id'))
        client = ClientWrapper(self.sshConfig)
        sshClient = SSHClient(client)
        self.clientMap.update({room:sshClient})
        #socketio = flask.current_app.extensions['socketio']
        join_room(room)
        if(client.connectable):
            emit('sshStatus','Connect to server success')
            emit('setRoom', room)
            #self.messageThread = GetMessageThread(self.client, room=self.room, namespace=self.namespace, messageQueue=self.messageQueue)
            #self.messageThread.start()
            self.socketio.start_background_task(get_sshmessage_thread, socketio=(self.socketio), sshclient=(sshClient), room=(room), namespace=(self.namespace))
        else:
            emit('sshStatus','Connect to server failed')

    '''
    处理ssh断开连接请求
    '''
    def on_disconnect(self):
        print('custom name space disconnect')
        #self.messageThread.stop()

    def on_sendtossh(self, data):
        '''
        发送信息至ssh server
        '''
        client = self.clientMap.get(data.get('room')).client
        if client:
            temp = data.get('data')
            client.sendCmdBytes(temp)
            print(temp.encode())
            if(temp == '\r'):
                print('----------cmd:'+self.testString.decode())
                self.testString = b''
            else:
                self.testString+=temp.encode()
                print('----------current cmd:'+self.testString.decode())
       

    def on_setencoding(self, data):
        '''
        设置ssh message编码方式
        '''
        encode = data.get('encode')
        client = self.clientMap.get(data.get('room'))
        if client:
            client.encode = encode
            client.set_encodable(True)
        
    def on_resetencoding(self, data):
        '''
        关闭ssh message的编码处理
        '''
        client = self.clientMap.get(data.get('room'))
        if client:
            client.set_encodable(False)


class SSHClient:
    '''
    用于封装ssh client以及client的字符编码方式
    '''
    def __init__(self, client, encode=None, encodable=False):
        self.client = client
        self.encode = encode
        self._encodable = encodable
    
    def encodable(self):
        return self._encodable
    
    def set_encodable(self, encodable):
        self._encodable = encodable
    


def get_sshmessage_thread(socketio, room, namespace, sshclient):
    while not sshclient.client.getShell().exit_status_ready():
        message = sshclient.client.getShell().recv(1024*1024)
        if(sshclient.encodable()):
            message = message.decode(sshclient.encode).encode()
            print('message:'+message.decode(sshclient.encode))
        socketio.emit('cmdResult', message, namespace=namespace, room=room)


class GetMessageThread(threading.Thread):
    def __init__(self, sshClient, room=None, namespace=None, messageQueue=None):
        threading.Thread.__init__(self)
        self.sshClient = sshClient
        self.room = room
        self.namespace = namespace
        self.messageQueue = messageQueue
        self._stop = False
    
    def stop(self):
        self._stop = True

    def run(self):
        while not self.sshClient.getShell().exit_status_ready() and not self.stop():
            message = self.sshClient.getShell().recv(1024*1024)
            print(message)
            sshMessage = SSHMessage(namespace=self.namespace, room=self.room, message=message)
            self.messageQueue.put(sshMessage)