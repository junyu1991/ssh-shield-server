import paramiko
import time

class SSHServerConfig:
    def __init__(self, hostname, port, username, password):
        self.hostname = hostname
        self.port = port
        self.password = password
        self.username = username

class ClientWrapper:
    def __init__(self, config):
        self._config = config
        self.connectable = False
        self.__initialize()

    def __initialize(self):
        try:
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.client.AutoAddPolicy())
            client.connect(hostname=self._config.hostname, port=self._config.port, username=self._config.username, password=self._config.password)
            self._client = client
            self._shell = self._client.invoke_shell()
            self.connectable = True
        except Exception:
            self.connectable = False

    def sendCmdBytes(self, data=''):
        self._shell.send(data)
        return self.receiveMessage()
    
    
    def receiveMessage(self):
        if(self._shell.recv_ready()):
            return self._shell.recv(1024*1024)
    
    def getEvent(self):
        return self._shell.event
    
    def getShell(self):
        return self._shell
