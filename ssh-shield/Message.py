
class SSHMessage:
    def __init__(self, namespace, room, message):
        self.namespace = namespace
        self.room = room
        self.message = message

    def __str__(self):
        return str(self.namespace + " " + self.room + ' ' + self.message.decode('GB18030'))