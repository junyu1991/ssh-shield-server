class SSHClientContainer:
    def __init__(self):
        self._map = dict()
    
    def putClient(self, sessionid, client):
        self._map[sessionid] = client
    
    def getClient(self, sessionid):
        return self._map[sessionid]
    
    